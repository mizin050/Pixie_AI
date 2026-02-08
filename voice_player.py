import os
import io
import random
import threading
import asyncio
import edge_tts
import sounddevice as sd
import soundfile as sf
from PIL import Image, ImageTk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import re

def normalize_punctuation(text: str) -> str:
    text = re.sub(r'\.\s+', ', ', text) #period
    text = re.sub(r'!\s+', ', ', text) #exclamation point
    text = re.sub(r'\?\s+', ', ', text) #question mark

    if text.endswith("."):
        text = text[:-1]

    return text.strip()

class VoiceImagePlayer:
    def __init__(self, face_path, size=(760, 760), master=None):
        if master is None:
            master = tk._default_root
        self.root = tk.Toplevel(master)
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.resizable(False, False)
        
        # Load original image without resizing
        original_image = Image.open(face_path)
        orig_w, orig_h = original_image.size
        
        # Scale to 1/10th the size
        self.original_width = orig_w // 10
        self.original_height = orig_h // 10
        

# 3D Fox window using pyglet
import pyglet
class Fox3DWindow:
    def __init__(self, glb_path, width=600, height=600):
        self.window = pyglet.window.Window(width=width, height=height, caption='Pixie Fox 3D', style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.window.set_location(100, 100)
        self.drag = False
        self.drag_offset = (0, 0)
        self.model = None
        self.rotation = 0
        self.load_model(glb_path)
        self.setup_events()
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def load_model(self, glb_path):
        try:
            import trimesh
            self.mesh = trimesh.load(glb_path)
        except ImportError:
            self.mesh = None
            print('Install trimesh for better 3D support: pip install trimesh')
        except Exception as e:
            self.mesh = None
            print(f'Error loading GLB: {e}')

    def setup_events(self):
        @self.window.event
        def on_draw():
            self.window.clear()
            if self.mesh:
                self.draw_mesh()
            else:
                pyglet.text.Label('3D Model failed to load', font_size=18, x=20, y=300, color=(255,100,100,255)).draw()

        @self.window.event
        def on_close():
            # Only close this window, do not exit the app
            self.window.close()

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.drag = True
            self.drag_offset = (x, y)

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.drag = False

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            if self.drag:
                wx, wy = self.window.get_location()
                self.window.set_location(wx + dx, wy - dy)

    def draw_mesh(self):
        try:
            import trimesh.viewer
            self.rotation += 1
        except Exception as e:
            pass

    def update(self, dt):
        self.window.dispatch_events()
        self.window.flip()

    def show(self):
        pyglet.app.run()