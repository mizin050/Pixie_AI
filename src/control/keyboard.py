"""
Keyboard Control - Type text and keyboard shortcuts
"""
import pyautogui
import keyboard as kb
import time
from typing import List


class KeyboardController:
    """Control keyboard input"""
    
    def __init__(self):
        print("✓ Keyboard controller initialized")
    
    def type_text(self, text: str, interval: float = 0.01):
        """
        Type text character by character
        
        Args:
            text: Text to type
            interval: Delay between keystrokes (seconds) - reduced for speed
        """
        try:
            pyautogui.write(text, interval=interval)
            print(f"✓ Typed: {text[:50]}{'...' if len(text) > 50 else ''}")
        except Exception as e:
            print(f"❌ Type failed: {e}")
            raise
    
    def press_key(self, key: str):
        """
        Press a single key
        
        Args:
            key: Key name (e.g., 'enter', 'esc', 'tab')
        """
        try:
            pyautogui.press(key)
            print(f"✓ Pressed: {key}")
        except Exception as e:
            print(f"❌ Press failed: {e}")
            raise
    
    def hotkey(self, *keys: str):
        """
        Press a keyboard shortcut
        
        Args:
            keys: Keys to press together (e.g., 'ctrl', 'c')
        """
        try:
            pyautogui.hotkey(*keys)
            print(f"✓ Hotkey: {'+'.join(keys)}")
        except Exception as e:
            print(f"❌ Hotkey failed: {e}")
            raise
    
    def hold_key(self, key: str, duration: float = 0.5):
        """
        Hold a key for duration
        
        Args:
            key: Key to hold
            duration: How long to hold (seconds)
        """
        try:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            print(f"✓ Held {key} for {duration}s")
        except Exception as e:
            print(f"❌ Hold failed: {e}")
            raise
    
    def paste_text(self, text: str):
        """
        Paste text using clipboard (faster for long text)
        
        Args:
            text: Text to paste
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            self.hotkey('ctrl', 'v')
            print(f"✓ Pasted: {text[:50]}{'...' if len(text) > 50 else ''}")
        except Exception as e:
            print(f"❌ Paste failed: {e}")
            # Fallback to typing
            self.type_text(text)
    
    def keyboard_shortcut(self, shortcut: str):
        """
        Execute a keyboard shortcut from string
        
        Args:
            shortcut: Shortcut like "ctrl+c", "alt+tab", "win+r"
        """
        keys = shortcut.lower().replace(' ', '').split('+')
        self.hotkey(*keys)
    
    # Common shortcuts
    def copy(self):
        """Copy (Ctrl+C)"""
        self.hotkey('ctrl', 'c')
    
    def paste(self):
        """Paste (Ctrl+V)"""
        self.hotkey('ctrl', 'v')
    
    def cut(self):
        """Cut (Ctrl+X)"""
        self.hotkey('ctrl', 'x')
    
    def select_all(self):
        """Select All (Ctrl+A)"""
        self.hotkey('ctrl', 'a')
    
    def undo(self):
        """Undo (Ctrl+Z)"""
        self.hotkey('ctrl', 'z')
    
    def redo(self):
        """Redo (Ctrl+Y)"""
        self.hotkey('ctrl', 'y')
    
    def save(self):
        """Save (Ctrl+S)"""
        self.hotkey('ctrl', 's')
    
    def find(self):
        """Find (Ctrl+F)"""
        self.hotkey('ctrl', 'f')
    
    def new_tab(self):
        """New Tab (Ctrl+T)"""
        self.hotkey('ctrl', 't')
    
    def close_tab(self):
        """Close Tab (Ctrl+W)"""
        self.hotkey('ctrl', 'w')
    
    def refresh(self):
        """Refresh (F5)"""
        self.press_key('f5')
    
    def alt_tab(self):
        """Switch windows (Alt+Tab)"""
        self.hotkey('alt', 'tab')


# Global instance
_keyboard_controller = None

def get_keyboard_controller() -> KeyboardController:
    """Get or create global keyboard controller"""
    global _keyboard_controller
    if _keyboard_controller is None:
        _keyboard_controller = KeyboardController()
    return _keyboard_controller


# Convenience functions
def type_text(text: str, interval: float = 0.01):
    """Type text"""
    get_keyboard_controller().type_text(text, interval)


def press_key(key: str):
    """Press a key"""
    get_keyboard_controller().press_key(key)


def hotkey(*keys: str):
    """Press keyboard shortcut"""
    get_keyboard_controller().hotkey(*keys)


def paste_text(text: str):
    """Paste text"""
    get_keyboard_controller().paste_text(text)
