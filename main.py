import sys
import asyncio
import threading
import os
import tkinter as tk
from PIL import Image
import pystray
import subprocess
from speech_to_text import record_voice
from groq_ai import get_response


# Tkinter root and UI state
root = tk.Tk()
root.withdraw()  # Hide the main window
fox_proc = None
chat_proc = None
ai_thread = None
is_mic_running = False
is_ui_running = False

# Path to the GLB file for the 3D fox
FOX_GLTF_PATH = r"C:\Users\mizin\pixie\foxxyy.glb"

async def get_voice_input():
    return await asyncio.to_thread(record_voice)

async def ai_loop(use_ui=False):
    global is_mic_running
    while is_mic_running:
        user_text = await get_voice_input()
        
        # Check if mic was turned off while waiting for input
        if not is_mic_running:
            break
            
        if not user_text:
            continue

        print(f"You: {user_text}")
        response = get_response(user_text)
        print(f"AI: {response}")

def toggle_ui(icon, item):
    global fox_proc, chat_proc, is_ui_running
    
    def show_ui():
        global fox_proc, chat_proc, is_ui_running
        if not is_ui_running:
            is_ui_running = True
            print("Turning ON UI...")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Start the fox image window
            fox_script = os.path.join(script_dir, "fox_image.py")
            if os.path.exists(fox_script):
                print(f"Launching fox image window: {fox_script}")
                fox_proc = subprocess.Popen([sys.executable, fox_script])
            else:
                print(f"fox_image.py not found at {fox_script}")
            
            # Start the web chat window
            chat_script = os.path.join(script_dir, "pixie_web_chat.py")
            if os.path.exists(chat_script):
                print(f"Launching web chat window: {chat_script}")
                chat_proc = subprocess.Popen([sys.executable, chat_script])
            else:
                print(f"pixie_web_chat.py not found at {chat_script}")
            
            print("UI windows created (chat + fox)")
        else:
            # Turn OFF UI - close both chat and fox
            is_ui_running = False
            
            # Close fox process
            if fox_proc:
                try:
                    fox_proc.terminate()
                    print("Fox window closed")
                except:
                    pass
                fox_proc = None
            
            # Close chat process
            if chat_proc:
                try:
                    chat_proc.terminate()
                    print("Chat window closed")
                except:
                    pass
                chat_proc = None
            
            print("UI turned OFF (both chat and fox closed)")
    
    # Schedule show_ui to run in the Tk main thread
    root.after(0, show_ui)

def toggle_mic(icon, item):
    global is_mic_running, ai_thread
    
    if not is_mic_running:
        # Turn ON mic
        is_mic_running = True
        print("Turning ON microphone...")
        
        def thread_target():
            asyncio.run(ai_loop(use_ui=is_ui_running))

        ai_thread = threading.Thread(target=thread_target, daemon=True)
        ai_thread.start()
        print("Microphone is ON")
    else:
        # Turn OFF mic
        is_mic_running = False
        print("Turning OFF microphone...")
        # The ai_loop will exit on its next iteration

def quit_app(icon, item):
    global is_mic_running, is_ui_running, fox_proc, chat_proc
    is_mic_running = False
    is_ui_running = False
    
    if fox_proc:
        try:
            fox_proc.terminate()
        except:
            pass
    
    if chat_proc:
        try:
            chat_proc.terminate()
        except:
            pass
    
    icon.stop()
    os._exit(0)  # Forcefully terminate the whole assistant

def setup_tray():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    face_path = os.path.join(script_dir, "fox.png")
    image = Image.open(face_path)
    menu = pystray.Menu(
        pystray.MenuItem("Pixie UI", toggle_ui),
        pystray.MenuItem("Mic", toggle_mic),
        pystray.MenuItem("Quit", quit_app)
    )
    icon = pystray.Icon("pixie", image, "Pixie AI Assistant", menu)
    icon.run_detached()

if __name__ == "__main__":
    setup_tray()
    # Start with just the system tray - no windows shown
    root.mainloop()


