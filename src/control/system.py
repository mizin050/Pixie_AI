"""
System Control - Launch apps, manage windows, file operations
"""
import subprocess
import os
import time
from typing import Optional


class SystemController:
    """Control system operations"""
    
    def __init__(self):
        self.common_apps = {
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "vscode": "code.exe",
            "whatsapp": "WhatsApp.exe",
            "whatsapp desktop": "WhatsApp.exe",
        }
        print("✓ System controller initialized")
    
    def open_app(self, app_name: str) -> bool:
        """
        Open an application using Windows search (most reliable method)
        
        Args:
            app_name: App name or path
        
        Returns:
            True if successful
        """
        try:
            # Always use Windows search for reliability
            print(f"🔍 Opening {app_name} via Windows search...")
            return self._open_via_search(app_name)
            
        except Exception as e:
            print(f"❌ Failed to open {app_name}: {e}")
            return False
    
    def _open_via_search(self, app_name: str) -> bool:
        """
        Open app using Windows search (Win+S)
        
        Args:
            app_name: App name to search for
        
        Returns:
            True if successful
        """
        try:
            from src.control.keyboard import hotkey, type_text, press_key
            
            print(f"🔍 Opening {app_name} via Windows search...")
            
            # Open Windows search
            hotkey('win', 's')
            time.sleep(0.3)
            
            # Type app name
            type_text(app_name)
            time.sleep(0.3)
            
            # Press Enter to open
            press_key('enter')
            time.sleep(1)
            
            print(f"✓ Opened {app_name} via search")
            return True
            
        except Exception as e:
            print(f"❌ Failed to open via search: {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """
        Open URL in default browser
        
        Args:
            url: URL to open
        
        Returns:
            True if successful
        """
        try:
            import webbrowser
            webbrowser.open(url)
            print(f"✓ Opened URL: {url}")
            time.sleep(2)  # Wait for browser
            return True
        except Exception as e:
            print(f"❌ Failed to open URL: {e}")
            return False
    
    def run_command(self, command: str) -> Optional[str]:
        """
        Run a system command
        
        Args:
            command: Command to run
        
        Returns:
            Command output or None if failed
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"✓ Ran command: {command}")
            return result.stdout
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return None
    
    def open_file(self, file_path: str) -> bool:
        """
        Open a file with default application
        
        Args:
            file_path: Path to file
        
        Returns:
            True if successful
        """
        try:
            os.startfile(file_path)
            print(f"✓ Opened file: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to open file: {e}")
            return False
    
    def create_folder(self, path: str) -> bool:
        """
        Create a folder
        
        Args:
            path: Folder path
        
        Returns:
            True if successful
        """
        try:
            os.makedirs(path, exist_ok=True)
            print(f"✓ Created folder: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create folder: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file (HIGH RISK - requires approval)
        
        Args:
            path: File path
        
        Returns:
            True if successful
        """
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"✓ Deleted file: {path}")
                return True
            else:
                print(f"⚠ File not found: {path}")
                return False
        except Exception as e:
            print(f"❌ Failed to delete file: {e}")
            return False
    
    def get_active_window_title(self) -> Optional[str]:
        """Get the title of the active window"""
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title
        except ImportError:
            print("⚠ win32gui not available")
            return None
        except Exception as e:
            print(f"⚠ Failed to get window title: {e}")
            return None


# Global instance
_system_controller = None

def get_system_controller() -> SystemController:
    """Get or create global system controller"""
    global _system_controller
    if _system_controller is None:
        _system_controller = SystemController()
    return _system_controller


# Convenience functions
def open_app(app_name: str) -> bool:
    """Open an application"""
    return get_system_controller().open_app(app_name)


def open_url(url: str) -> bool:
    """Open URL in browser"""
    return get_system_controller().open_url(url)


def run_command(command: str) -> Optional[str]:
    """Run system command"""
    return get_system_controller().run_command(command)
