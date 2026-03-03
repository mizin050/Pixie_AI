import os
import subprocess
import sys
import threading
import time
import urllib.request
from collections import deque

import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "hand_landmarker.task")


class ExpSmoother:
    def __init__(self, alpha=0.35):
        self.alpha = alpha
        self.value = None

    def update(self, sample):
        if self.value is None:
            self.value = sample
            return sample

        sx, sy = sample
        vx, vy = self.value
        self.value = (vx + self.alpha * (sx - vx), vy + self.alpha * (sy - vy))
        return self.value


class GestureEngine:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.landmarker = self._create_landmarker()

        self.center_smoother = ExpSmoother(alpha=0.4)
        self.palm_history = deque(maxlen=20)

        self.last_action_time = {
            "window": 0.0,
            "tab": 0.0,
            "scroll": 0.0,
            "minimize": 0.0,
            "zoom": 0.0,
        }

        self.cooldowns = {
            "window": 0.55,
            "tab": 0.35,
            "scroll": 0.06,
            "minimize": 2.0,
            "zoom": 0.03,
        }

        self.fist_started_at = None
        self.fist_hold_seconds = 0.8

        self.pinch_active = False
        self.last_pinch_ratio = None

        self.window_swipe_anchor = None
        self.tab_swipe_anchor = None

        pyautogui.FAILSAFE = False

    def _ensure_model(self):
        if os.path.exists(_MODEL_PATH):
            return _MODEL_PATH
        os.makedirs(os.path.dirname(_MODEL_PATH), exist_ok=True)
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        return _MODEL_PATH

    def _create_landmarker(self):
        model_path = self._ensure_model()
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            min_hand_presence_confidence=0.6,
        )
        return vision.HandLandmarker.create_from_options(options)

    def _dist(self, a, b):
        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

    def _angle_degrees(self, a, b, c):
        import math

        abx = a.x - b.x
        aby = a.y - b.y
        cbx = c.x - b.x
        cby = c.y - b.y

        ab_len = max((abx * abx + aby * aby) ** 0.5, 1e-6)
        cb_len = max((cbx * cbx + cby * cby) ** 0.5, 1e-6)
        dot = (abx * cbx + aby * cby) / (ab_len * cb_len)
        dot = max(-1.0, min(1.0, dot))
        return math.degrees(math.acos(dot))

    def _finger_states(self, lm):
        wrist = lm[0]
        middle_mcp = lm[9]
        palm_scale = max(self._dist(wrist, middle_mcp), 1e-6)

        thumb_straight = self._angle_degrees(lm[2], lm[3], lm[4]) > 145.0
        thumb_far = (self._dist(lm[4], lm[5]) / palm_scale) > 0.70
        thumb_extended = thumb_straight and thumb_far

        index_extended = lm[8].y < lm[6].y and (lm[6].y - lm[8].y) > 0.03
        middle_extended = lm[12].y < lm[10].y and (lm[10].y - lm[12].y) > 0.03
        ring_extended = lm[16].y < lm[14].y and (lm[14].y - lm[16].y) > 0.03
        pinky_extended = lm[20].y < lm[18].y and (lm[18].y - lm[20].y) > 0.03

        return {
            "thumb": thumb_extended,
            "index": index_extended,
            "middle": middle_extended,
            "ring": ring_extended,
            "pinky": pinky_extended,
        }

    def _is_open_palm(self, lm, fingers):
        extended = sum(1 for v in fingers.values() if v)
        if extended < 4:
            return False

        wrist = lm[0]
        palm_scale = max(self._dist(wrist, lm[9]), 1e-6)
        tip_ids = [4, 8, 12, 16, 20]
        avg_tip = sum(self._dist(wrist, lm[i]) for i in tip_ids) / 5.0
        return (avg_tip / palm_scale) > 1.58

    def _is_closed_fist(self, lm, fingers):
        if any(fingers.values()):
            return False

        wrist = lm[0]
        palm_scale = max(self._dist(wrist, lm[9]), 1e-6)
        tip_ids = [4, 8, 12, 16, 20]
        avg_tip = sum(self._dist(wrist, lm[i]) for i in tip_ids) / 5.0
        curled = lm[8].y > lm[6].y and lm[12].y > lm[10].y and lm[16].y > lm[14].y and lm[20].y > lm[18].y
        return curled and (avg_tip / palm_scale) < 1.30

    def _is_two_finger_pose(self, fingers):
        return (
            fingers["index"]
            and fingers["middle"]
            and not fingers["ring"]
            and not fingers["pinky"]
        )

    def _primary_palm_center(self, lm):
        ids = [0, 5, 9, 13, 17]
        x = sum(lm[i].x for i in ids) / len(ids)
        y = sum(lm[i].y for i in ids) / len(ids)
        return self.center_smoother.update((x, y))

    def _velocity(self):
        if len(self.palm_history) < 2:
            return 0.0, 0.0
        t1, x1, y1 = self.palm_history[-1]
        t0, x0, y0 = self.palm_history[-4] if len(self.palm_history) >= 4 else self.palm_history[0]
        dt = max(t1 - t0, 1e-3)
        return (x1 - x0) / dt, (y1 - y0) / dt

    def _can_fire(self, key, now):
        return (now - self.last_action_time[key]) >= self.cooldowns[key]

    def _trigger(self, key, now):
        self.last_action_time[key] = now

    def _handle_pinch_zoom(self, lm, fingers, now):
        # Do not require "thumb extended": true pinch bends the thumb.
        if not fingers["index"]:
            self.pinch_active = False
            self.last_pinch_ratio = None
            return False

        palm_scale = max(self._dist(lm[0], lm[9]), 1e-6)
        pinch_ratio = self._dist(lm[4], lm[8]) / palm_scale
        pinching = pinch_ratio < 0.90

        if not pinching:
            self.pinch_active = False
            self.last_pinch_ratio = None
            return False

        if not self.pinch_active:
            self.pinch_active = True
            self.last_pinch_ratio = pinch_ratio
            return True

        if self.last_pinch_ratio is None:
            self.last_pinch_ratio = pinch_ratio
            return True

        if not self._can_fire("zoom", now):
            return True

        delta = pinch_ratio - self.last_pinch_ratio
        self.last_pinch_ratio = pinch_ratio

        if abs(delta) < 0.008:
            return True

        amount = int(delta * 2400)
        if amount != 0:
            pyautogui.keyDown("ctrl")
            pyautogui.scroll(amount)
            pyautogui.keyUp("ctrl")
            self._trigger("zoom", now)
        return True

    def _handle_window_swipe(self, center_x, vx, vy, open_palm, now):
        if not open_palm:
            self.window_swipe_anchor = None
            return False

        if self.window_swipe_anchor is None:
            self.window_swipe_anchor = center_x
            return False

        dx = center_x - self.window_swipe_anchor
        # Optimized for reliable intent: strong horizontal movement + low vertical drift.
        if abs(dx) > 0.12 and abs(vx) > 0.18 and abs(vy) < 0.22 and self._can_fire("window", now):
            if dx > 0:
                pyautogui.hotkey("alt", "tab")
            else:
                pyautogui.hotkey("alt", "shift", "tab")
            self._trigger("window", now)
            self.window_swipe_anchor = center_x
            return True

        if abs(dx) < 0.015:
            self.window_swipe_anchor = center_x
        return False

    def _handle_tab_swipe(self, center_x, vx, vy, two_finger, now):
        if not two_finger:
            self.tab_swipe_anchor = None
            return False

        if self.tab_swipe_anchor is None:
            self.tab_swipe_anchor = center_x
            return False

        dx = center_x - self.tab_swipe_anchor
        if abs(dx) > 0.09 and abs(vx) > 0.14 and abs(vy) < 0.26 and self._can_fire("tab", now):
            if dx > 0:
                pyautogui.hotkey("ctrl", "tab")
            else:
                pyautogui.hotkey("ctrl", "shift", "tab")
            self._trigger("tab", now)
            self.tab_swipe_anchor = center_x
            return True

        if abs(dx) < 0.015:
            self.tab_swipe_anchor = center_x
        return False

    def _handle_scroll(self, vy, open_palm, now):
        if not open_palm:
            return False
        if not self._can_fire("scroll", now):
            return False

        if vy < -0.16:
            pyautogui.scroll(40)
            self._trigger("scroll", now)
            return True
        if vy > 0.16:
            pyautogui.scroll(-40)
            self._trigger("scroll", now)
            return True
        return False

    def _handle_minimize(self, closed_fist, now):
        if not closed_fist:
            self.fist_started_at = None
            return False, ""

        if self.fist_started_at is None:
            self.fist_started_at = now
            return True, "Closed Fist - Hold"

        held = now - self.fist_started_at
        if held >= self.fist_hold_seconds and self._can_fire("minimize", now):
            pyautogui.hotkey("win", "m")
            self._trigger("minimize", now)
            self.fist_started_at = None
            return True, "Closed Fist - Minimize"

        remaining = max(0.0, self.fist_hold_seconds - held)
        return True, f"Closed Fist - Hold {remaining:.1f}s"

    def _draw_info(self, frame, text):
        h, _ = frame.shape[:2]
        cv2.putText(frame, f"Gesture: {text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        lines = [
            "Pinch: Zoom",
            "Palm Swipe: Switch Window",
            "2-Finger Swipe: Switch Tab",
            "Palm Up/Down: Scroll",
            "Closed Fist: Minimize",
            "Press q to quit camera",
        ]
        for i, line in enumerate(lines):
            cv2.putText(frame, line, (10, h - 120 + i * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _draw_landmarks(self, frame, lm):
        h, w = frame.shape[:2]
        for p in lm:
            cv2.circle(frame, (int(p.x * w), int(p.y * h)), 2, (0, 255, 255), -1)

    def run(self):
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera for gesture control.")

        try:
            while not self.stop_event.is_set():
                ok, frame = self.cap.read()
                if not ok:
                    break

                frame = cv2.flip(frame, 1)
                ts = int(time.time() * 1000)
                result = self.landmarker.detect_for_video(
                    mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)),
                    ts,
                )

                gesture_text = ""
                now = time.time()

                if result.hand_landmarks:
                    # Use the first detected hand for gesture driving to avoid conflicts.
                    lm = result.hand_landmarks[0]
                    self._draw_landmarks(frame, lm)

                    fingers = self._finger_states(lm)
                    open_palm = self._is_open_palm(lm, fingers)
                    closed_fist = self._is_closed_fist(lm, fingers)
                    two_finger = self._is_two_finger_pose(fingers)

                    cx, cy = self._primary_palm_center(lm)
                    self.palm_history.append((now, cx, cy))
                    vx, vy = self._velocity()

                    if self._handle_pinch_zoom(lm, fingers, now):
                        gesture_text = "Pinch Zoom"
                    else:
                        minimized, min_text = self._handle_minimize(closed_fist, now)
                        if minimized and min_text:
                            gesture_text = min_text
                        else:
                            did_window = self._handle_window_swipe(cx, vx, vy, open_palm, now)
                            if did_window:
                                gesture_text = "Palm Swipe - Window"
                            else:
                                did_tab = self._handle_tab_swipe(cx, vx, vy, two_finger, now)
                                if did_tab:
                                    gesture_text = "2-Finger Swipe - Tab"
                                elif self._handle_scroll(vy, open_palm, now):
                                    gesture_text = "Palm Vertical - Scroll"
                                elif open_palm:
                                    gesture_text = "Open Palm"
                                elif two_finger:
                                    gesture_text = "Two Fingers"
                else:
                    self.palm_history.clear()
                    self.fist_started_at = None
                    self.window_swipe_anchor = None
                    self.tab_swipe_anchor = None
                    self.pinch_active = False
                    self.last_pinch_ratio = None

                self._draw_info(frame, gesture_text)
                cv2.imshow("Pixie Gesture Control", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.stop_event.set()
                    break
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.landmarker.close()


class GestureService:
    def __init__(self):
        self._process = None
        self._lock = threading.Lock()
        self._last_error = None

    def start(self):
        with self._lock:
            if self.is_running():
                return True, "Gesture control is already running."

            self._last_error = None
            cmd = [sys.executable, os.path.abspath(__file__), "--run-worker"]
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
            )

            time.sleep(0.6)
            if not self.is_running():
                self._capture_worker_error()
                if self._last_error:
                    return False, f"Gesture failed to start: {self._last_error}"
                return False, "Gesture failed to start."
            return True, "Gesture control started."

    def stop(self):
        with self._lock:
            if not self.is_running():
                return True, "Gesture control is not running."

            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)
            self._capture_worker_error()
            return True, "Gesture control stopped."

    def is_running(self):
        return bool(self._process and self._process.poll() is None)

    def last_error(self):
        if self._process and self._process.poll() is not None:
            self._capture_worker_error()
        return self._last_error

    def _capture_worker_error(self):
        if not self._process:
            return
        if self._process.stderr:
            try:
                err = self._process.stderr.read().decode("utf-8", errors="ignore").strip()
                if err:
                    self._last_error = err.splitlines()[-1]
            except Exception:
                pass
        self._process = None


def _run_worker():
    stop_event = threading.Event()
    engine = GestureEngine(stop_event)
    engine.run()


if __name__ == "__main__":
    if "--run-worker" in sys.argv:
        _run_worker()
