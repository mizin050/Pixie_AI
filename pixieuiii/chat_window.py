import os
import sys
import threading
import tempfile
import base64
import logging
from PIL import Image

# Reduce pywebview noise and avoid debug/devtools behavior.
os.environ.setdefault("PYWEBVIEW_LOG", "error")
os.environ.setdefault("PYWEBVIEW_GUI", "edgechromium")

import webview

logging.getLogger("pywebview").setLevel(logging.ERROR)

# Add project root to path if running as subprocess``
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.ai_engine_gemini import get_response, get_chat_history, reset_history
from src.utils.files import fs_tools
from src.utils.documents import process_document

class ChatAPI:
    def __init__(self):
        self.window = None
        self.temp_files = []
        self.operator_mode = False
    
    def set_window(self, window):
        self.window = window
    
    def toggle_operator_mode(self):
        """Operator mode disabled in this runtime."""
        self.operator_mode = False
        return {"mode": "Chat", "operator_mode": False}    
    def send_message(self, message, files=None):
        """Called from JavaScript when user sends a message with optional files"""
        print(f"User: {message}")
        print(f"Files received: {files}")
        
        image_paths = []
        document_paths = []
        
        # Handle file uploads
        if files and len(files) > 0:
            print(f"Processing {len(files)} file(s)...")
            for file_data in files:
                try:
                    file_name = file_data.get('name', 'unknown')
                    file_content = file_data.get('data', '')
                    
                    # Remove data URL prefix if present
                    if ',' in file_content:
                        file_content = file_content.split(',')[1]
                    
                    # Decode base64
                    file_bytes = base64.b64decode(file_content)
                    
                    # Save to temp file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1])
                    temp_file.write(file_bytes)
                    temp_file.close()
                    
                    self.temp_files.append(temp_file.name)
                    
                    # Determine file type
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico']:
                        image_paths.append(temp_file.name)
                        print(f"âœ“ Image: {file_name} -> {temp_file.name}")
                    else:
                        document_paths.append(temp_file.name)
                        print(f"âœ“ Document: {file_name} -> {temp_file.name}")
                        
                except Exception as e:
                    print(f"Error processing file: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Chat-only response path (Kimi text + Ollama vision).
        response = get_response(
            message,
            image_paths=image_paths if image_paths else None,
            document_paths=document_paths if document_paths else None
        )
        print(f"AI: {response}")
        
        # Clean up temp files
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        self.temp_files = []
        
        # Send response back to JavaScript
        if self.window:
            self.window.evaluate_js(f'window.addAIMessage({repr(response)})')
    
    def get_history(self):
        """Get chat history for loading on startup"""
        return get_chat_history()
    
    def clear_history(self):
        """Clear all chat history"""
        reset_history()
        print("Chat history cleared")
    
    def browse_file(self):
        """Open file browser and return selected file path"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            file_path = filedialog.askopenfilename(
                title="Select a file",
                filetypes=[
                    ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.ico"),
                    ("Text files", "*.txt *.md *.log *.json *.xml *.csv"),
                    ("Code files", "*.py *.js *.html *.css *.java *.cpp *.c"),
                    ("All files", "*.*")
                ]
            )
            
            root.destroy()
            return file_path if file_path else None
        except Exception as e:
            print(f"Error browsing file: {e}")
            return None
    
    # File system operations
    def read_file(self, file_path):
        """Read a file"""
        return fs_tools.read_file(file_path)
    
    def list_directory(self, dir_path):
        """List directory contents"""
        return fs_tools.list_directory(dir_path)
    
    def search_files(self, search_path, pattern):
        """Search for files"""
        return fs_tools.search_files(search_path, pattern)
    
    def get_file_info(self, file_path):
        """Get file information"""
        return fs_tools.get_file_info(file_path)

def _build_window(api):
    """Create and return a webview window with the chat interface (no webview.start)."""
    # Get the HTML file path - use 3D version
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "chat_3d.html")
    
    # Find fox.png - try multiple locations
    fox_path = None
    possible_paths = [
        os.path.join(project_root, "fox.png"),  # Project root
        "C:\\Users\\mizin\\pixie\\AI-Assistant-for-Computer\\fox.png",  # Exact path you provided
        os.path.join(script_dir, "fox.png"),  # Same directory as script
        os.path.join(os.path.dirname(script_dir), "fox.png"),  # Parent directory
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        print(f"Checking: {abs_path}")
        if os.path.exists(abs_path):
            fox_path = abs_path
            print(f"âœ“ Found fox.png at: {fox_path}")
            break
    
    if not fox_path:
        print("âœ— Warning: fox.png not found in any location!")
        print("Searched:")
        for p in possible_paths:
            print(f"  - {os.path.abspath(p)}")
    
    # Read HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Embed the 3D fox model as base64
    glb_path = os.path.join(script_dir, "Fox_draco.glb")
    if os.path.exists(glb_path):
        try:
            import base64
            with open(glb_path, 'rb') as glb_file:
                glb_data = base64.b64encode(glb_file.read()).decode('utf-8')
                glb_data_url = f'data:model/gltf-binary;base64,{glb_data}'
            
            # Replace the GLB path in the loader.load() call
            html_content = html_content.replace(
                'loader.load(\n        "Fox_draco.glb",',
                f'loader.load(\n        "{glb_data_url}",'
            )
            print(f"âœ“ Fox 3D model embedded in HTML ({len(glb_data)} chars)")
        except Exception as e:
            print(f"âœ— Error embedding 3D model: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"âœ— Fox_draco.glb not found at: {glb_path}")
    
    # Save modified HTML to temp file (NavigateToString has size limits)
    temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
    temp_html.write(html_content)
    temp_html.close()
    print(f"âœ“ Saved modified HTML to: {temp_html.name}")
    
    # Get screen dimensions to center window
    import tkinter as tk
    temp_root = tk.Tk()
    temp_root.withdraw()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()
    
    window_width = 1400
    window_height = 825
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Create window with API and file URL instead of HTML string
    window = webview.create_window(
        'Pixie AI',
        url=temp_html.name,
        width=window_width,
        height=window_height,
        x=x,
        y=y,
        resizable=True,
        frameless=True,
        on_top=False,  # Disable always on top
        js_api=api
    )
    
    return window


def _set_window_icon():
    """Set the window icon and enable taskbar minimize/restore using Windows API"""
    import time
    
    try:
        import ctypes
        from ctypes import wintypes
        
        # Get icon path
        fox_png_path = os.path.join(project_root, "fox.png")
        if not os.path.exists(fox_png_path):
            print("âœ— fox.png not found for icon")
            return
        
        # Convert PNG to ICO
        icon_path = os.path.join(tempfile.gettempdir(), "pixie_icon.ico")
        img = Image.open(fox_png_path)
        img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        print(f"âœ“ Created icon: {icon_path}")
        
        # Windows API constants
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x00000010
        ICON_SMALL = 0
        ICON_BIG = 1
        WM_SETICON = 0x0080
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        GWL_STYLE = -16
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_SYSMENU = 0x00080000
        WS_CAPTION = 0x00C00000
        SWP_FRAMECHANGED = 0x0020
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        
        # Try multiple times to find the window (it might not be ready immediately)
        hwnd = None
        for attempt in range(10):
            hwnd = ctypes.windll.user32.FindWindowW(None, "Pixie")
            if hwnd:
                print(f"âœ“ Found window (hwnd: {hwnd}) on attempt {attempt + 1}")
                break
            time.sleep(0.1)
        
        if not hwnd:
            print("âœ— Could not find window by title after 10 attempts")
            return
        
        # Set extended window style to ensure it appears in taskbar properly
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_APPWINDOW)
        
        # Enable minimize/maximize and system menu for taskbar functionality
        # DO NOT add WS_CAPTION - that creates the title bar (we want frameless)
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        new_style = current_style | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        
        # Force window to update with new styles
        ctypes.windll.user32.SetWindowPos(
            hwnd, None, 0, 0, 0, 0,
            SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
        )
        print(f"âœ“ Window style updated to enable taskbar minimize/restore (frameless)")
        
        # Load icon using LoadImage (more reliable than ExtractIcon)
        hicon_small = ctypes.windll.user32.LoadImageW(
            None,
            icon_path,
            IMAGE_ICON,
            16, 16,
            LR_LOADFROMFILE
        )
        
        hicon_big = ctypes.windll.user32.LoadImageW(
            None,
            icon_path,
            IMAGE_ICON,
            32, 32,
            LR_LOADFROMFILE
        )
        
        if hicon_small and hicon_big:
            # Set both small and large icons
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
            print(f"âœ“ Window icon set successfully!")
        else:
            print(f"âœ— Could not load icons (small: {hicon_small}, big: {hicon_big})")
            
    except Exception as e:
        print(f"âœ— Error setting window icon: {e}")
        import traceback
        traceback.print_exc()


def create_chat_window():
    """Create and return a webview window with the chat interface"""
    api = ChatAPI()
    window = _build_window(api)
    api.set_window(window)
    
    # Start webview with callback to set icon after window is ready
    def on_ready():
        # Run icon setting in a separate thread to avoid blocking
        threading.Thread(target=_set_window_icon, daemon=True).start()
    
    webview.start(on_ready, debug=False, private_mode=False)
    return window


class PixieWebChatWindow:
    def __init__(self):
        self.window = None
        self.api = ChatAPI()
        self._ready = False
        self._pending_js = []
        self._thread = None

    def _on_ready(self):
        self._ready = True
        if self._pending_js and self.window:
            for js in self._pending_js:
                self.window.evaluate_js(js)
            self._pending_js.clear()

    def _eval_js(self, js):
        if not self.window:
            return
        if self._ready:
            self.window.evaluate_js(js)
        else:
            self._pending_js.append(js)

    def start(self):
        if self.window:
            return
        self.window = _build_window(self.api)
        self.api.set_window(self.window)

        def on_ready_with_icon():
            # Run icon setting in a separate thread to avoid blocking
            threading.Thread(target=_set_window_icon, daemon=True).start()
            self._on_ready()

        def run():
            webview.start(on_ready_with_icon, debug=False, private_mode=False)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def add_user_message(self, text):
        safe_text = repr(text)
        js = (
            "(() => {"
            "const messagesContainer = document.getElementById('chatMessages');"
            "if (!messagesContainer) return;"
            "const messageDiv = document.createElement('div');"
            "messageDiv.className = 'message user';"
            "messageDiv.innerHTML = "
            "`<div class=\\\"message-bubble\\\"><div class=\\\"message-text\\\">${" + safe_text + "}</div></div>` +"
            "`<div class=\\\"message-time\\\">${new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</div>`;"
            "messagesContainer.appendChild(messageDiv);"
            "messagesContainer.scrollTop = messagesContainer.scrollHeight;"
            "})()"
        )
        self._eval_js(js)

    def add_ai_message(self, text):
        safe_text = repr(text)
        js = f"window.addAIMessage({safe_text});"
        self._eval_js(js)

    def hide(self):
        if self.window and hasattr(self.window, "hide"):
            self.window.hide()

    def show(self):
        if self.window and hasattr(self.window, "show"):
            self.window.show()

if __name__ == "__main__":
    create_chat_window()


