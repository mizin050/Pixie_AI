"""
Screen Capture - Fast screenshot capability using mss
"""
import mss
import mss.tools
from PIL import Image
import io
from typing import Optional, Tuple
import time


class ScreenCapture:
    """Fast screen capture using mss"""
    
    def __init__(self):
        # Don't store mss instance - create fresh for each capture to avoid threading issues
        print("✓ Screen capture initialized")
    
    def capture_screen(self, monitor: int = 1) -> Image.Image:
        """
        Capture the entire screen
        
        Args:
            monitor: Monitor number (1 = primary, 0 = all monitors)
        
        Returns:
            PIL Image
        """
        start_time = time.time()
        
        # Create fresh mss instance to avoid threading issues
        with mss.mss() as sct:
            # Capture screenshot
            screenshot = sct.grab(sct.monitors[monitor])
            
            # Convert to PIL Image
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )
        
        elapsed = (time.time() - start_time) * 1000
        print(f"✓ Screen captured in {elapsed:.1f}ms")
        
        return img
    
    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> Image.Image:
        """
        Capture a specific region of the screen
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Region width
            height: Region height
        
        Returns:
            PIL Image
        """
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }
        
        # Create fresh mss instance
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            
            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )
        
        return img
    
    def capture_active_window(self) -> Optional[Image.Image]:
        """
        Capture the active window (Windows only)
        
        Returns:
            PIL Image or None if failed
        """
        try:
            import win32gui
            import win32ui
            import win32con
            
            # Get active window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Capture the window region
            return self.capture_region(left, top, width, height)
            
        except ImportError:
            print("⚠ win32gui not available, falling back to full screen")
            return self.capture_screen()
        except Exception as e:
            print(f"⚠ Error capturing active window: {e}")
            return None
    
    def save_screenshot(self, img: Image.Image, filename: str):
        """Save screenshot to file"""
        img.save(filename)
        print(f"✓ Screenshot saved to {filename}")
    
    def get_screen_size(self, monitor: int = 1) -> Tuple[int, int]:
        """Get screen dimensions"""
        with mss.mss() as sct:
            mon = sct.monitors[monitor]
            return (mon["width"], mon["height"])
    
    def get_monitor_count(self) -> int:
        """Get number of monitors"""
        with mss.mss() as sct:
            return len(sct.monitors) - 1  # -1 because index 0 is all monitors


# Global instance
_screen_capture = None

def get_screen_capture() -> ScreenCapture:
    """Get or create global screen capture instance"""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCapture()
    return _screen_capture


# Convenience functions
def capture_screen(monitor: int = 1) -> Image.Image:
    """Capture the entire screen"""
    return get_screen_capture().capture_screen(monitor)


def capture_region(x: int, y: int, width: int, height: int) -> Image.Image:
    """Capture a specific region"""
    return get_screen_capture().capture_region(x, y, width, height)


def capture_active_window() -> Optional[Image.Image]:
    """Capture the active window"""
    return get_screen_capture().capture_active_window()


def save_screenshot(img: Image.Image, filename: str):
    """Save screenshot to file"""
    get_screen_capture().save_screenshot(img, filename)
