import pygame
import sys
import os
import threading
import asyncio
from PIL import Image
import pystray
from speech_to_text import record_voice
from groq_ai import get_response
import subprocess
import platform as system_platform

# Initialize pygame
pygame.init()

class PixieAssistant:
    def __init__(self):
        self.is_mic_running = False
        self.is_ui_running = False
        self.fox_process = None
        self.ai_thread = None
        
        # Path to the GLB file for the 3D fox
        self.FOX_GLTF_PATH = r"C:\Users\mizin\pixie\foxxyy.glb"
        
        # Setup system tray
        self.setup_tray()

    async def get_voice_input(self):
        return await asyncio.to_thread(record_voice)

    async def ai_loop(self):
        while self.is_mic_running:
            user_text = await self.get_voice_input()
            
            if not self.is_mic_running:
                break
                
            if not user_text:
                continue

            print(f"You: {user_text}")
            response = get_response(user_text)
            print(f"AI: {response}")

    def start_fox_window(self):
        """Start the 3D fox window using pygame"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fox_script = os.path.join(script_dir, "fox_pygame.py")
            
            if not os.path.exists(self.FOX_GLTF_PATH):
                print(f"3D model not found at {self.FOX_GLTF_PATH}")
                return None
            
            print(f"Starting 3D fox window: {fox_script}")
            return subprocess.Popen([sys.executable, fox_script, self.FOX_GLTF_PATH])
            
        except Exception as e:
            print(f"Failed to start fox window: {e}")
            return None

    def toggle_ui(self, icon, item):
        if not self.is_ui_running:
            self.is_ui_running = True
            print("Turning ON UI...")
            self.fox_process = self.start_fox_window()
            print("UI windows created")
        else:
            self.is_ui_running = False
            if self.fox_process:
                try:
                    self.fox_process.terminate()
                except:
                    pass
                self.fox_process = None
            print("UI turned OFF")

    def toggle_mic(self, icon, item):
        if not self.is_mic_running:
            self.is_mic_running = True
            print("Turning ON microphone...")
            
            def thread_target():
                asyncio.run(self.ai_loop())

            self.ai_thread = threading.Thread(target=thread_target, daemon=True)
            self.ai_thread.start()
            print("Microphone is ON🎙 I'm listening, sir...")
        else:
            self.is_mic_running = False
            print("Turning OFF microphone...")

    def quit_app(self, icon, item):
        self.is_mic_running = False
        self.is_ui_running = False
        if self.fox_process:
            try:
                self.fox_process.terminate()
            except:
                pass
        icon.stop()
        os._exit(0)

    def setup_tray(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        face_path = os.path.join(script_dir, "fox.png")
        image = Image.open(face_path)
        menu = pystray.Menu(
            pystray.MenuItem("Pixie UI", self.toggle_ui),
            pystray.MenuItem("Mic", self.toggle_mic),
            pystray.MenuItem("Quit", self.quit_app)
        )
        icon = pystray.Icon("pixie", image, "Pixie AI Assistant", menu)
        icon.run()

if __name__ == "__main__":
    assistant = PixieAssistant()