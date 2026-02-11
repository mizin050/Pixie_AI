"""
Computer Tools - Claude-style tool interface for computer control
"""
import time
from typing import Dict, Any, Optional
from PIL import Image

from src.vision.capture import capture_screen
from src.vision.ocr import extract_text
from src.control.mouse import click, move_to, scroll
from src.control.keyboard import type_text, press_key, hotkey
from src.control.system import open_app


class ComputerTools:
    """Tool interface for computer control"""
    
    def __init__(self):
        self.last_screenshot = None
        self.action_history = []
        print("✓ Computer tools initialized")
    
    def screenshot(self) -> Dict[str, Any]:
        """
        Take a screenshot of the current screen
        
        Returns:
            Dict with image and text content
        """
        try:
            img = capture_screen()
            self.last_screenshot = img
            
            # Extract text for AI to read
            text = extract_text(img)
            
            return {
                "success": True,
                "image": img,
                "text": text[:1000],  # Limit text for AI context
                "message": "Screenshot captured"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to capture screenshot: {e}"
            }
    
    def mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        """
        Move mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Result dict
        """
        try:
            move_to(x, y)
            return {
                "success": True,
                "message": f"Moved mouse to ({x}, {y})"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to move mouse: {e}"
            }
    
    def left_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """
        Click at coordinates or current position
        
        Args:
            x: X coordinate (optional)
            y: Y coordinate (optional)
        
        Returns:
            Result dict
        """
        try:
            if x is not None and y is not None:
                click(x, y)
                msg = f"Clicked at ({x}, {y})"
            else:
                click()
                msg = "Clicked at current position"
            
            time.sleep(0.2)  # Wait for UI to respond
            return {
                "success": True,
                "message": msg
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to click: {e}"
            }
    
    def type(self, text: str) -> Dict[str, Any]:
        """
        Type text at current cursor position
        
        Args:
            text: Text to type
        
        Returns:
            Result dict
        """
        try:
            type_text(text)
            time.sleep(0.1)
            return {
                "success": True,
                "message": f"Typed: {text[:50]}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to type: {e}"
            }
    
    def key(self, key_name: str) -> Dict[str, Any]:
        """
        Press a key
        
        Args:
            key_name: Key to press (e.g., 'enter', 'escape', 'tab')
        
        Returns:
            Result dict
        """
        try:
            press_key(key_name)
            time.sleep(0.1)
            return {
                "success": True,
                "message": f"Pressed key: {key_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to press key: {e}"
            }
    
    def hotkey_press(self, *keys: str) -> Dict[str, Any]:
        """
        Press a keyboard shortcut
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
        
        Returns:
            Result dict
        """
        try:
            hotkey(*keys)
            time.sleep(0.1)
            return {
                "success": True,
                "message": f"Pressed hotkey: {'+'.join(keys)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to press hotkey: {e}"
            }
    
    def scroll_down(self, clicks: int = 3) -> Dict[str, Any]:
        """
        Scroll down
        
        Args:
            clicks: Number of scroll clicks
        
        Returns:
            Result dict
        """
        try:
            scroll(clicks)
            time.sleep(0.2)
            return {
                "success": True,
                "message": f"Scrolled down {clicks} clicks"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to scroll: {e}"
            }
    
    def scroll_up(self, clicks: int = 3) -> Dict[str, Any]:
        """
        Scroll up
        
        Args:
            clicks: Number of scroll clicks
        
        Returns:
            Result dict
        """
        try:
            scroll(-clicks)
            time.sleep(0.2)
            return {
                "success": True,
                "message": f"Scrolled up {clicks} clicks"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to scroll: {e}"
            }
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Open an application
        
        Args:
            app_name: Name of application to open
        
        Returns:
            Result dict
        """
        try:
            success = open_app(app_name)
            if success:
                return {
                    "success": True,
                    "message": f"Opened {app_name}"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to open {app_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error opening {app_name}: {e}"
            }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available tools"""
        return {
            "screenshot": "Take a screenshot and read text from screen",
            "mouse_move": "Move mouse to (x, y) coordinates",
            "left_click": "Click at coordinates or current position",
            "type": "Type text at cursor position",
            "key": "Press a single key (enter, escape, tab, etc.)",
            "hotkey_press": "Press keyboard shortcut (ctrl+c, win+s, etc.)",
            "scroll_down": "Scroll down on screen",
            "scroll_up": "Scroll up on screen",
            "open_application": "Open an application by name"
        }


# Global instance
_computer_tools = None

def get_computer_tools() -> ComputerTools:
    """Get or create global computer tools instance"""
    global _computer_tools
    if _computer_tools is None:
        _computer_tools = ComputerTools()
    return _computer_tools
