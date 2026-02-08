import tkinter as tk
from PIL import Image, ImageTk
import os

def create_fox_window():
    """Create a transparent, draggable window with the fox image"""
    
    # Create window
    window = tk.Tk()
    window.title("Pixie Fox")
    
    # Make window frameless and always on top
    window.overrideredirect(True)
    window.attributes('-topmost', True)
    
    # Try to make window transparent (Windows)
    try:
        window.attributes('-transparentcolor', 'white')
        window.wm_attributes('-alpha', 1.0)
    except:
        pass
    
    # Load fox image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fox_path = os.path.join(script_dir, "fox.png")
    
    if not os.path.exists(fox_path):
        print(f"Error: fox.png not found at {fox_path}")
        window.destroy()
        return
    
    # Load and resize image
    img = Image.open(fox_path)
    # Resize to reasonable size (adjust as needed)
    img = img.resize((400, 400), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    
    # Create label with image
    label = tk.Label(window, image=photo, bg='white', borderwidth=0)
    label.image = photo  # Keep reference
    label.pack()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Position window (left side, centered vertically)
    window_width = 400
    window_height = 400
    x = 100  # Left side with some margin
    y = (screen_height - window_height) // 2
    
    window.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Make window draggable
    def start_move(event):
        window.x = event.x
        window.y = event.y
    
    def do_move(event):
        deltax = event.x - window.x
        deltay = event.y - window.y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f"+{x}+{y}")
    
    label.bind('<Button-1>', start_move)
    label.bind('<B1-Motion>', do_move)
    
    # Add close button on right-click
    def close_window(event):
        window.destroy()
    
    label.bind('<Button-3>', close_window)
    
    print(f"Fox window created at position ({x}, {y})")
    print("Left-click and drag to move, right-click to close")
    
    window.mainloop()

if __name__ == "__main__":
    create_fox_window()
