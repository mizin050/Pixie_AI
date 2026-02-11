"""
Action Executor - Execute actions from the planner
"""
import time
import sys
import os
from typing import Dict, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agent.schemas import Action
from src.vision.capture import capture_screen
from src.vision.vision_summary import create_summary, verify_action_result


class ActionExecutor:
    """Execute actions and verify results"""
    
    def __init__(self):
        self.last_action = None
        self.last_result = None
        print("✓ Action executor initialized")
    
    def execute(self, action: Action) -> Dict[str, any]:
        """
        Execute an action and verify result
        
        Args:
            action: Action to execute
        
        Returns:
            Dict with success, confidence, message
        """
        print(f"\n▶️ Executing: {action.description}")
        
        # Capture screen before action
        before_img = capture_screen()
        
        # Execute based on action type
        success = False
        message = ""
        
        try:
            if action.type == "open_app":
                success, message = self._execute_open_app(action)
            
            elif action.type == "navigate":
                success, message = self._execute_navigate(action)
            
            elif action.type == "click":
                success, message = self._execute_click(action)
            
            elif action.type in ["type", "type_text"]:
                success, message = self._execute_type(action)
            
            elif action.type in ["press_key", "keyboard_shortcut"]:
                success, message = self._execute_key(action)
            
            elif action.type == "wait":
                success, message = self._execute_wait(action)
            
            elif action.type == "scroll":
                success, message = self._execute_scroll(action)
            
            else:
                message = f"Unknown action type: {action.type}"
                print(f"⚠ {message}")
        
        except Exception as e:
            message = f"Execution error: {e}"
            print(f"❌ {message}")
        
        # Wait a moment for UI to update (reduced from 0.5s to 0.2s for speed)
        time.sleep(0.2)
        
        # Capture screen after action
        after_img = capture_screen()
        
        # Verify result
        verification = verify_action_result(
            before_img,
            after_img,
            action.description
        )
        
        # Combine results
        result = {
            "success": success and verification["success"],
            "confidence": verification["confidence"],
            "message": message,
            "verification": verification,
            "action": action.description
        }
        
        self.last_action = action
        self.last_result = result
        
        if result["success"]:
            print(f"✅ Success (confidence: {result['confidence']:.2f})")
        else:
            print(f"❌ Failed: {message}")
        
        return result
    
    def _execute_open_app(self, action: Action) -> tuple[bool, str]:
        """Execute open_app action"""
        from src.control.system import open_app
        
        app_name = action.target or action.value
        if not app_name:
            return False, "No app name specified"
        
        success = open_app(app_name)
        return success, f"Opened {app_name}" if success else f"Failed to open {app_name}"
    
    def _execute_navigate(self, action: Action) -> tuple[bool, str]:
        """Execute navigate action"""
        from src.browser.playwright_ctrl import get_browser_controller
        
        url = action.target or action.value
        if not url:
            return False, "No URL specified"
        
        browser = get_browser_controller()
        
        # Launch browser if not already running
        if not browser.page:
            browser.launch(headless=False)
        
        success = browser.navigate(url)
        return success, f"Navigated to {url}" if success else f"Failed to navigate to {url}"
    
    def _execute_click(self, action: Action) -> tuple[bool, str]:
        """Execute click action"""
        # Try browser click first
        if action.target and not action.coordinates:
            from src.browser.playwright_ctrl import get_browser_controller
            browser = get_browser_controller()
            
            if browser.page:
                success = browser.click(action.target)
                if success:
                    return True, f"Clicked {action.target}"
        
        # Fall back to mouse click
        if action.coordinates:
            from src.control.mouse import click
            x, y = action.coordinates
            click(x, y)
            return True, f"Clicked at ({x}, {y})"
        
        # Try to find text and click
        if action.target:
            from src.control.mouse import click_at_text
            success = click_at_text(action.target)
            return success, f"Clicked '{action.target}'" if success else f"Could not find '{action.target}'"
        
        return False, "No click target specified"
    
    def _execute_type(self, action: Action) -> tuple[bool, str]:
        """Execute type action"""
        text = action.value
        if not text:
            return False, "No text specified"
        
        # Try browser type first
        if action.target:
            from src.browser.playwright_ctrl import get_browser_controller
            browser = get_browser_controller()
            
            if browser.page:
                success = browser.type_text(action.target, text)
                if success:
                    return True, f"Typed into {action.target}"
        
        # Fall back to keyboard type
        from src.control.keyboard import type_text
        type_text(text)
        return True, f"Typed: {text[:50]}"
    
    def _execute_key(self, action: Action) -> tuple[bool, str]:
        """Execute key press action"""
        from src.control.keyboard import press_key, hotkey
        
        key = action.value or action.target
        if not key:
            return False, "No key specified"
        
        # Check if it's a shortcut (contains +)
        if '+' in key:
            keys = key.split('+')
            hotkey(*keys)
            return True, f"Pressed {key}"
        else:
            press_key(key)
            return True, f"Pressed {key}"
    
    def _execute_wait(self, action: Action) -> tuple[bool, str]:
        """Execute wait action"""
        duration = float(action.value) if action.value else 1.0
        time.sleep(duration)
        return True, f"Waited {duration}s"
    
    def _execute_scroll(self, action: Action) -> tuple[bool, str]:
        """Execute scroll action"""
        from src.control.mouse import scroll
        
        amount = int(action.value) if action.value else 3
        scroll(amount)
        return True, f"Scrolled {amount}"


# Global instance
_executor = None

def get_executor() -> ActionExecutor:
    """Get or create global executor"""
    global _executor
    if _executor is None:
        _executor = ActionExecutor()
    return _executor


def execute_action(action: Action) -> Dict[str, any]:
    """Execute an action"""
    return get_executor().execute(action)
