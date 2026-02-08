import webview
import os
from groq_ai import get_response

class ChatAPI:
    def __init__(self):
        self.window = None
    
    def set_window(self, window):
        self.window = window
    
    def send_message(self, message):
        """Called from JavaScript when user sends a message"""
        print(f"User: {message}")
        
        # Get AI response
        response = get_response(message)
        print(f"AI: {response}")
        
        # Send response back to JavaScript
        if self.window:
            self.window.evaluate_js(f'window.addAIMessage({repr(response)})')

def create_chat_window():
    """Create and return a webview window with the chat interface"""
    # Get the HTML file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "chat.html")
    
    # Find fox.png - try multiple locations
    fox_path = None
    possible_paths = [
        "C:\\Users\\mizin\\pixie\\AI-Assistant-for-Computer\\fox.png",  # Exact path you provided
        os.path.join(script_dir, "fox.png"),  # Same directory as script
        os.path.join(os.path.dirname(script_dir), "fox.png"),  # Parent directory
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        print(f"Checking: {abs_path}")
        if os.path.exists(abs_path):
            fox_path = abs_path
            print(f"✓ Found fox.png at: {fox_path}")
            break
    
    if not fox_path:
        print("✗ Warning: fox.png not found in any location!")
        print("Searched:")
        for p in possible_paths:
            print(f"  - {os.path.abspath(p)}")
    
    # Read HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Inject fox image if found - use base64 encoding for reliability
    if fox_path:
        try:
            import base64
            with open(fox_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                img_src = f'data:image/png;base64,{img_data}'
                
            # Replace the fox image element - match the actual HTML format
            old_img = '<img id="foxImage" alt="Fox" style="display: none" />'
            new_img = f'<img id="foxImage" alt="Fox" src="{img_src}" style="display:block; width:100%; height:100%; object-fit:contain;" />'
            
            if old_img in html_content:
                html_content = html_content.replace(old_img, new_img)
                print("✓ Fox image embedded in HTML")
                print(f"  Image data length: {len(img_data)} characters")
                
                # Save modified HTML for debugging
                debug_path = os.path.join(script_dir, "chat_debug.html")
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"  Debug HTML saved to: {debug_path}")
            else:
                print("✗ Could not find image placeholder in HTML")
                print(f"  Looking for: {old_img}")
        except Exception as e:
            print(f"✗ Error embedding fox image: {e}")
            import traceback
            traceback.print_exc()
    
    # Create API instance
    api = ChatAPI()
    
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
    
    # Create window with API and modified HTML
    window = webview.create_window(
        'Pixie AI',
        html=html_content,
        width=window_width,
        height=window_height,
        x=x,
        y=y,
        resizable=True,
        frameless=True,
        js_api=api
    )
    
    # Set window reference in API
    api.set_window(window)
    
    # Start webview (debug=False to avoid recursion errors)
    webview.start(debug=False, private_mode=False)
    
    return window

if __name__ == "__main__":
    create_chat_window()
