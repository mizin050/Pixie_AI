import sys
import asyncio
import threading
import os
import tkinter as tk
from PIL import Image, ImageDraw
import pystray
import subprocess
from src.utils.speech import record_voice, speak_text
from src.core.ai_engine_gemini import get_response


# Tkinter root and UI state
root = tk.Tk()
root.withdraw()  # Hide the main window
chat_proc = None
ai_thread = None
telegram_thread = None
is_mic_running = False
is_ui_running = False
is_telegram_running = False
tray_icon = None
base_icon_image = None

async def get_voice_input():
    return await asyncio.to_thread(record_voice)

async def ai_loop(use_ui=False):
    global is_mic_running, is_ui_running
    while is_mic_running:
        user_text = await get_voice_input()
        
        # Check if mic was turned off while waiting for input
        if not is_mic_running:
            break
            
        if not user_text:
            continue

        print(f"You: {user_text}")
        
        # Check for voice commands
        user_text_lower = user_text.lower()
        if "pixie ui" in user_text_lower or "pixie you i" in user_text_lower:
            print("Voice command detected: Opening UI...")
            if not is_ui_running:
                root.after(0, lambda: toggle_ui_programmatic())
            continue
        
        response = get_response(user_text)
        print(f"AI: {response}")
        
        # Speak the response back when using voice input
        speak_text(response)

def toggle_ui_programmatic():
    """Toggle UI programmatically (called from voice commands)"""
    global chat_proc, is_ui_running
    
    if not is_ui_running:
        is_ui_running = True
        print("Turning ON UI...")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Start the web chat window
        chat_script = os.path.join(script_dir, "src", "ui", "chat_window.py")
        if os.path.exists(chat_script):
            print(f"Launching web chat window: {chat_script}")
            chat_proc = subprocess.Popen([sys.executable, chat_script])
        else:
            print(f"chat_window.py not found at {chat_script}")
        
        print("UI windows created (chat)")
    else:
        # Turn OFF UI - close chat
        is_ui_running = False
        
        # Close chat process
        if chat_proc:
            try:
                chat_proc.terminate()
                print("Chat window closed")
            except:
                pass
            chat_proc = None
        
        print("UI turned OFF (chat closed)")

def toggle_ui(icon, item):
    """Toggle UI from system tray menu"""
    # Schedule toggle_ui_programmatic to run in the Tk main thread
    root.after(0, toggle_ui_programmatic)

def update_tray_icon():
    """Update the tray icon to show mic status"""
    global tray_icon, base_icon_image, is_mic_running
    
    if tray_icon is None or base_icon_image is None:
        return
    
    # Create a copy of the base icon
    icon_image = base_icon_image.copy()
    
    # If mic is on, add a green dot at the bottom-right corner
    if is_mic_running:
        draw = ImageDraw.Draw(icon_image)
        # Get icon size
        width, height = icon_image.size
        # Draw green circle at bottom-right corner
        dot_radius = max(width // 6, 4)  # Slightly larger, at least 4 pixels
        dot_x = width - dot_radius - 2
        dot_y = height - dot_radius - 2
        
        # Draw the green dot with a glow effect
        # Outer glow
        draw.ellipse(
            [dot_x - dot_radius - 1, dot_y - dot_radius - 1, 
             dot_x + dot_radius + 1, dot_y + dot_radius + 1],
            fill='#00DD00'  # Slightly darker green for glow
        )
        # Main dot
        draw.ellipse(
            [dot_x - dot_radius, dot_y - dot_radius, 
             dot_x + dot_radius, dot_y + dot_radius],
            fill='#00FF00',  # Bright green
            outline='#FFFFFF'  # White outline for contrast
        )
    
    # Update the icon
    tray_icon.icon = icon_image

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
        
        # Update icon to show green dot
        update_tray_icon()
    else:
        # Turn OFF mic
        is_mic_running = False
        print("Turning OFF microphone...")
        # The ai_loop will exit on its next iteration
        
        # Update icon to remove green dot
        update_tray_icon()

def toggle_telegram(icon, item):
    """Toggle Telegram bot from system tray menu"""
    global is_telegram_running, telegram_thread
    
    if not is_telegram_running:
        # Turn ON Telegram bot
        is_telegram_running = True
        print("🤖 Starting Telegram bot...")
        
        def run_telegram():
            try:
                from src.integrations.telegram_bot import start_telegram_bot
                start_telegram_bot()
            except Exception as e:
                print(f"❌ Telegram bot error: {e}")
                global is_telegram_running
                is_telegram_running = False
        
        telegram_thread = threading.Thread(target=run_telegram, daemon=True)
        telegram_thread.start()
        print("✅ Telegram bot started")
    else:
        # Turn OFF Telegram bot
        is_telegram_running = False
        print("🛑 Telegram bot stopped (restart app to start again)")


def quit_app(icon, item):
    global is_mic_running, is_ui_running, is_telegram_running, chat_proc
    is_mic_running = False
    is_ui_running = False
    is_telegram_running = False
    
    if chat_proc:
        try:
            chat_proc.terminate()
        except:
            pass
    
    icon.stop()
    os._exit(0)  # Forcefully terminate the whole assistant

def setup_tray():
    global tray_icon, base_icon_image
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    face_path = os.path.join(script_dir, "fox.png")
    base_icon_image = Image.open(face_path)
    
    menu = pystray.Menu(
        pystray.MenuItem("Pixie UI", toggle_ui),
        pystray.MenuItem("Mic", toggle_mic),
        pystray.MenuItem("Quit", quit_app)
    )
    tray_icon = pystray.Icon("pixie", base_icon_image, "Pixie AI Assistant", menu)
    tray_icon.run_detached()

def start_telegram_bot_background():
    """Start Telegram bot automatically in background"""
    global is_telegram_running, telegram_thread
    
    try:
        # Check if token is configured
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not token or token == "your_telegram_bot_token_here":
            print("ℹ️  Telegram bot not configured (no token in .env)")
            return
        
        print("🤖 Starting Telegram bot...")
        is_telegram_running = True
        
        def run_telegram():
            try:
                from src.integrations.telegram_bot import start_telegram_bot
                start_telegram_bot()
            except Exception as e:
                print(f"❌ Telegram bot error: {e}")
                global is_telegram_running
                is_telegram_running = False
        
        telegram_thread = threading.Thread(target=run_telegram, daemon=True)
        telegram_thread.start()
        print("✅ Telegram bot running in background")
        
    except Exception as e:
        print(f"ℹ️  Telegram bot not started: {e}")

if __name__ == "__main__":
    # Start Telegram bot automatically
    start_telegram_bot_background()
    
    setup_tray()
    # Start with just the system tray - no windows shown
    root.mainloop()
