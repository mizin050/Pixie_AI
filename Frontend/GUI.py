import base64
import os
import tempfile
import threading
import time
import subprocess
from asyncio import run

from PIL import Image, ImageDraw
import pystray
import webview
from dotenv import dotenv_values

# ---------------- DIRECTORY PATHS ----------------

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TempDirPath = os.path.join(PROJECT_DIR, "Frontend", "Files")
GraphicsDirPath = os.path.join(PROJECT_DIR, "Frontend", "Graphics")
PixieUIDir = os.path.join(PROJECT_DIR, "pixieuiii")

os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

for file_name in ["Mic.data", "Status.data", "Responses.data", "Database.data"]:
    open(os.path.join(TempDirPath, file_name), "a", encoding="utf-8").close()


# ---------------- STATUS & MIC CONTROL ----------------

def _ensure_state_file(file_name, default_value=""):
    os.makedirs(TempDirPath, exist_ok=True)
    file_path = os.path.join(TempDirPath, file_name)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(default_value)
    return file_path

def SetMicrophoneStatus(Command):
    file_path = _ensure_state_file("Mic.data", "False")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(Command)


def GetMicrophoneStatus():
    file_path = _ensure_state_file("Mic.data", "False")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def SetAssistantStatus(Status):
    file_path = _ensure_state_file("Status.data", "Available ...")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(Status)


def GetAssistantStatus():
    file_path = _ensure_state_file("Status.data", "Available ...")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def MicButtonInitialized():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


# ---------------- PATH HELPERS ----------------

def GraphicsDirectoryPath(filename):
    return os.path.join(GraphicsDirPath, filename)


def TempDirectoryPath(filename):
    return os.path.join(TempDirPath, filename)


def ShowTextToScreen(text):
    file_path = _ensure_state_file("Responses.data", "")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)


# ---------------- PIXIE WEB UI ----------------

os.environ.setdefault("PYWEBVIEW_LOG", "error")
os.environ.setdefault("PYWEBVIEW_GUI", "edgechromium")
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

env_vars = dotenv_values(os.path.join(PROJECT_DIR, ".env"))
Username = env_vars.get("Username") or "User"
Assistantname = env_vars.get("Assistantname") or "Assistant"
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


class ChatAPI:
    def __init__(self):
        self.operator_mode = False
        self._query_lock = threading.Lock()

    def toggle_operator_mode(self):
        self.operator_mode = not self.operator_mode
        return {"mode": "Operator" if self.operator_mode else "Chat", "operator_mode": self.operator_mode}

    def send_message(self, message, files=None):
        query = (message or "").strip()
        if not query:
            return
        if self._query_lock.locked():
            ShowTextToScreen(f"{Assistantname} : Please wait, still processing previous message.")
            return
        threading.Thread(target=self._handle_text_query, args=(query,), daemon=True).start()

    def _handle_text_query(self, query):
        with self._query_lock:
            try:
                # Lazy imports: speed up tray/UI startup and avoid heavy backend init on launch.
                from Backend.Chatbot import chatBot
                from Backend.SpeechToText import QueryModifier
                from Backend.Model import FirstLayerDMM
                from Backend.RealtimeSearchEngine import RealtimeSearchEngine
                from Backend.Automation import TranslateAndExecute
                from Backend.FolderContext import handle_folder_command
                from Backend.TelegramBridge import handle_local_telegram_command

                telegram_command_response = handle_local_telegram_command(query)
                if telegram_command_response:
                    SetAssistantStatus("Answering...")
                    ShowTextToScreen(f"{Assistantname} : {telegram_command_response}")
                    SetAssistantStatus("Available ...")
                    return

                folder_command_response = handle_folder_command(query)
                if folder_command_response:
                    SetAssistantStatus("Answering...")
                    ShowTextToScreen(f"{Assistantname} : {folder_command_response}")
                    SetAssistantStatus("Available ...")
                    return

                SetAssistantStatus("Thinking...")
                decisions = FirstLayerDMM(query)

                task_execution = False
                image_execution = False
                image_generation_query = ""
                answer = ""

                is_general = any(i.startswith("general") for i in decisions)
                is_realtime = any(i.startswith("realtime") for i in decisions)
                merged_query = " and ".join(
                    [" ".join(i.split()[1:]) for i in decisions if i.startswith("general") or i.startswith("realtime")]
                )

                for decision in decisions:
                    if "generate " in decision:
                        image_generation_query = str(decision)
                        image_execution = True

                for decision in decisions:
                    if not task_execution and any(decision.startswith(func) for func in Functions):
                        for each_query in decisions:
                            run(TranslateAndExecute(each_query))
                        task_execution = True
                if task_execution:
                    answer = "Done."

                if image_execution:
                    with open(r"Frontend\Files\ImageGeneration.data", "w", encoding="utf-8") as file:
                        file.write(f"{image_generation_query},True")
                    try:
                        subprocess.Popen(
                            ["python", r"Backend\ImageGeneration.py"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            shell=False,
                        )
                    except Exception:
                        pass
                    answer = "Image generation started."

                if (is_general and is_realtime or is_realtime) and not answer:
                    SetAssistantStatus("Searching...")
                    answer = RealtimeSearchEngine(QueryModifier(merged_query))
                elif not answer:
                    for decision in decisions:
                        if decision.startswith("general"):
                            SetAssistantStatus("Thinking...")
                            query_final = decision.replace("general ", "")
                            answer = chatBot(QueryModifier(query_final))
                            break
                        if decision.startswith("realtime"):
                            SetAssistantStatus("Searching...")
                            query_final = decision.replace("realtime ", "")
                            answer = RealtimeSearchEngine(QueryModifier(query_final))
                            break
                        if decision.startswith("exit"):
                            answer = "Okay, Bye!"
                            break

                if not answer:
                    answer = chatBot(QueryModifier(query))

                SetAssistantStatus("Answering...")
                ShowTextToScreen(f"{Assistantname} : {answer}")
                SetAssistantStatus("Available ...")
            except Exception as exc:
                SetAssistantStatus("Available ...")
                error_msg = f"Error: {exc}"
                ShowTextToScreen(f"{Assistantname} : {error_msg}")


class PixieWebChatWindow:
    def __init__(self):
        self.window = None
        self.api = ChatAPI()
        self._ready = False
        self._pending_js = []

    def build_window(self):
        if self.window:
            return self.window

        html_path = self._resolve_chat_html()
        with open(html_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()

        glb_path = GraphicsDirectoryPath("Fox_draco.glb")
        if os.path.exists(glb_path):
            with open(glb_path, "rb") as glb_file:
                glb_data = base64.b64encode(glb_file.read()).decode("utf-8")
                glb_data_url = f"data:model/gltf-binary;base64,{glb_data}"
            html_content = html_content.replace(
                'loader.load(\n        "Fox_draco.glb",',
                f'loader.load(\n        "{glb_data_url}",',
            )

        temp_html = tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        )
        temp_html.write(html_content)
        temp_html.close()

        self.window = webview.create_window(
            "Pixie",
            url=temp_html.name,
            width=1400,
            height=825,
            resizable=True,
            hidden=True,
            frameless=True,
            on_top=False,
            js_api=self.api,
        )
        return self.window

    def _resolve_chat_html(self):
        candidate_paths = [
            os.path.join(PixieUIDir, "chat_3d.html"),
            os.path.join(PROJECT_DIR, "chat_3d.html"),
            os.path.join(PROJECT_DIR, "Frontend", "chat_3d.html"),
        ]
        for candidate in candidate_paths:
            if os.path.exists(candidate):
                return candidate

        fallback_html = """<!doctype html>
<html><head><meta charset='utf-8'><title>Pixie</title></head>
<body style='font-family:Segoe UI;background:#111;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh;'>
<div id='chatMessages' style='flex:1;overflow:auto;padding:12px;'></div>
<div style='display:flex;gap:8px;padding:12px;border-top:1px solid #333;'>
<input id='messageInput' style='flex:1;padding:8px;' placeholder='Type a message...' />
<button id='sendButton'>Send</button>
</div>
<script>
const input=document.getElementById('messageInput');
const btn=document.getElementById('sendButton');
const messages=document.getElementById('chatMessages');
function addLine(text){const d=document.createElement('div');d.textContent=text;d.style.margin='6px 0';messages.appendChild(d);messages.scrollTop=messages.scrollHeight;}
function send(){const t=input.value.trim();if(!t)return;addLine('You: '+t);input.value='';if(window.pywebview){window.pywebview.api.send_message(t);}}
btn.onclick=send;input.addEventListener('keypress',e=>{if(e.key==='Enter'){send();}});
window.addAIMessage=function(t){addLine('Pixie: '+t);};
</script></body></html>"""
        temp_html = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
        temp_html.write(fallback_html)
        temp_html.close()
        return temp_html.name

    def _on_ready(self):
        global is_ui_running, desired_ui_visible
        self._ready = True
        if self._pending_js and self.window:
            for js in self._pending_js:
                self.window.evaluate_js(js)
            self._pending_js.clear()
        if desired_ui_visible:
            self.show()
            is_ui_running = True

    def start(self):
        self.build_window()

        def on_ready_callback():
            self._on_ready()

        webview.start(on_ready_callback, debug=False, private_mode=False)

    def _eval_js(self, js):
        if not self.window:
            return
        if self._ready:
            self.window.evaluate_js(js)
        else:
            self._pending_js.append(js)

    def add_user_message(self, text):
        safe_text = repr(text)
        js = (
            "(() => {"
            "const messagesContainer = document.getElementById('chatMessages');"
            "if (!messagesContainer) return;"
            "const messageDiv = document.createElement('div');"
            "messageDiv.className = 'message user';"
            "messageDiv.innerHTML = "
            "`<div class=\\\"message-bubble\\\"><div class=\\\"message-text\\\">${"
            + safe_text
            + "}</div></div>` +"
            "`<div class=\\\"message-time\\\">${new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</div>`;"
            "messagesContainer.appendChild(messageDiv);"
            "messagesContainer.scrollTop = messagesContainer.scrollHeight;"
            "})()"
        )
        self._eval_js(js)

    def add_ai_message(self, text):
        safe_text = repr(text)
        self._eval_js(f"window.addAIMessage({safe_text});")

    def hide(self):
        if self.window and self._ready and hasattr(self.window, "hide"):
            self.window.hide()

    def show(self):
        if self.window and self._ready and hasattr(self.window, "show"):
            self.window.show()


# ---------------- TRAY (PIXIE STYLE) ----------------

chat_window = None
tray_icon = None
base_icon_image = None

is_ui_running = False
is_mic_running = False
is_app_running = True
start_ui_requested = False
desired_ui_visible = False

ui_lock = threading.Lock()
last_response_blob = ""
seen_lines = set()


def toggle_ui_programmatic():
    global is_ui_running, start_ui_requested, desired_ui_visible
    with ui_lock:
        if not chat_window:
            desired_ui_visible = True
            start_ui_requested = True
            return
        if not chat_window._ready:
            return

        if not is_ui_running:
            desired_ui_visible = True
            chat_window.show()
            is_ui_running = True
        else:
            desired_ui_visible = False
            chat_window.hide()
            is_ui_running = False


def toggle_ui(icon, item):
    toggle_ui_programmatic()


def update_tray_icon():
    global tray_icon, base_icon_image, is_mic_running
    if tray_icon is None or base_icon_image is None:
        return

    icon_image = base_icon_image.copy()
    if is_mic_running:
        draw = ImageDraw.Draw(icon_image)
        width, height = icon_image.size
        dot_radius = max(width // 6, 4)
        dot_x = width // 2
        dot_y = height - dot_radius - 2

        draw.ellipse(
            [
                dot_x - dot_radius - 1,
                dot_y - dot_radius - 1,
                dot_x + dot_radius + 1,
                dot_y + dot_radius + 1,
            ],
            fill="#008844",
        )
        draw.ellipse(
            [
                dot_x - dot_radius,
                dot_y - dot_radius,
                dot_x + dot_radius,
                dot_y + dot_radius,
            ],
            fill="#00AA55",
            outline="#FFFFFF",
        )

    tray_icon.icon = icon_image


def toggle_mic(icon, item):
    global is_mic_running
    is_mic_running = not is_mic_running
    SetMicrophoneStatus("True" if is_mic_running else "False")
    update_tray_icon()


def quit_app(icon, item):
    global is_app_running
    is_app_running = False
    if icon:
        icon.stop()
    os._exit(0)


def setup_tray():
    global tray_icon, base_icon_image

    face_path = GraphicsDirectoryPath("fox.png")
    base_icon_image = Image.open(face_path)

    menu = pystray.Menu(
        pystray.MenuItem("Pixie UI", toggle_ui),
        pystray.MenuItem("Mic", toggle_mic),
        pystray.MenuItem("Quit", quit_app),
    )

    tray_icon = pystray.Icon("pixie", base_icon_image, "Pixie AI Assistant", menu)
    tray_icon.run_detached()


def _sync_mic_state_from_file():
    global is_mic_running
    mic_state = GetMicrophoneStatus() == "True"
    if mic_state != is_mic_running:
        is_mic_running = mic_state
        update_tray_icon()


def _sync_chat_from_files():
    global last_response_blob

    _sync_mic_state_from_file()

    if not chat_window:
        return

    with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as response_file:
        blob = response_file.read()

    if blob == last_response_blob:
        return

    last_response_blob = blob
    for line in blob.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        if normalized in seen_lines:
            continue

        seen_lines.add(normalized)

        lower_name = normalized.split(":", 1)[0].strip().lower() if ":" in normalized else ""
        if lower_name in ["assistant", "pixie"]:
            payload = normalized.split(":", 1)[1].strip() if ":" in normalized else normalized
            chat_window.add_ai_message(payload)
        elif ":" in normalized:
            payload = normalized.split(":", 1)[1].strip()
            chat_window.add_user_message(payload)
        else:
            chat_window.add_ai_message(normalized)


def _file_sync_loop():
    while is_app_running:
        try:
            _sync_chat_from_files()
        except Exception:
            pass
        time.sleep(0.5)


# ---------------- ENTRYPOINT ----------------

def GraphicalUserInterface():
    MicButtonInitialized()
    global chat_window, is_ui_running, start_ui_requested

    is_ui_running = False
    setup_tray()

    sync_thread = threading.Thread(target=_file_sync_loop, daemon=True)
    sync_thread.start()

    while is_app_running:
        if start_ui_requested and not chat_window:
            start_ui_requested = False
            try:
                chat_window = PixieWebChatWindow()
                chat_window.build_window()
                chat_window.start()
                break
            except Exception:
                chat_window = None
                is_ui_running = False
        time.sleep(0.1)


if __name__ == "__main__":
    GraphicalUserInterface()
