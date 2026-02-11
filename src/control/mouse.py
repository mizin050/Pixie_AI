"""
Mouse Control - Click, move, drag operations
"""
import pyautogui
import time
from typing import Tuple, Optional

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.05  # Reduced from 0.1 for speed


class MouseController:
    """Control mouse movements and clicks"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"✓ Mouse controller initialized ({self.screen_width}x{self.screen_height})")
    
    def click(self, x: int, y: int, button: str = "left", clicks: int = 1):
        """
        Click at coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: "left", "right", or "middle"
            clicks: Number of clicks (1 = single, 2 = double)
        """
        try:
            pyautogui.click(x, y, clicks=clicks, button=button)
            print(f"✓ Clicked at ({x}, {y}) with {button} button")
        except Exception as e:
            print(f"❌ Click failed: {e}")
            raise
    
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """
        Move mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to move (seconds)
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            print(f"✓ Moved to ({x}, {y})")
        except Exception as e:
            print(f"❌ Move failed: {e}")
            raise
    
    def drag_to(self, x: int, y: int, duration: float = 0.5):
        """
        Drag mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to drag (seconds)
        """
        try:
            pyautogui.dragTo(x, y, duration=duration)
            print(f"✓ Dragged to ({x}, {y})")
        except Exception as e:
            print(f"❌ Drag failed: {e}")
            raise
    
    def scroll(self, amount: int):
        """
        Scroll mouse wheel
        
        Args:
            amount: Positive = scroll up, Negative = scroll down
        """
        try:
            pyautogui.scroll(amount)
            direction = "up" if amount > 0 else "down"
            print(f"✓ Scrolled {direction} ({abs(amount)} units)")
        except Exception as e:
            print(f"❌ Scroll failed: {e}")
            raise
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()
    
    def click_at_text(self, text: str, confidence: float = 0.8) -> bool:
        """
        Find text on screen and click it
        
        Args:
            text: Text to find
            confidence: OCR confidence threshold
        
        Returns:
            True if clicked, False if not found
        """
        try:
            from src.vision.capture import capture_screen
            from src.vision.ocr import find_text
            
            # Capture screen
            img = capture_screen()
            
            # Find text
            coords = find_text(img, text)
            
            if coords:
                self.click(coords[0], coords[1])
                return True
            else:
                print(f"⚠ Text '{text}' not found on screen")
                return False
                
        except Exception as e:
            print(f"❌ Click at text failed: {e}")
            return False


# Global instance
_mouse_controller = None

def get_mouse_controller() -> MouseController:
    """Get or create global mouse controller"""
    global _mouse_controller
    if _mouse_controller is None:
        _mouse_controller = MouseController()
    return _mouse_controller


# Convenience functions
def click(x: int, y: int, button: str = "left", clicks: int = 1):
    """Click at coordinates"""
    get_mouse_controller().click(x, y, button, clicks)


def move_to(x: int, y: int, duration: float = 0.5):
    """Move mouse to coordinates"""
    get_mouse_controller().move_to(x, y, duration)


def scroll(amount: int):
    """Scroll mouse wheel"""
    get_mouse_controller().scroll(amount)


def click_at_text(text: str) -> bool:
    """Find and click text"""
    return get_mouse_controller().click_at_text(text)
