"""
UI State Detection - Detect errors, loading states, and UI elements
"""
from PIL import Image
from typing import Dict, List, Optional
from .ocr import extract_text


class UIDetector:
    """Detect UI states and elements"""
    
    def __init__(self):
        # Common error keywords
        self.error_keywords = [
            "error", "failed", "failure", "exception", "crash",
            "not found", "404", "500", "timeout", "connection",
            "unable", "cannot", "denied", "forbidden", "invalid"
        ]
        
        # Loading indicators
        self.loading_keywords = [
            "loading", "please wait", "processing", "buffering",
            "connecting", "initializing", "preparing"
        ]
        
        # Success indicators
        self.success_keywords = [
            "success", "complete", "done", "finished", "sent",
            "saved", "created", "updated", "confirmed"
        ]
        
        # Login/auth indicators
        self.auth_keywords = [
            "sign in", "log in", "login", "password", "username",
            "authenticate", "credentials", "access denied"
        ]
        
        print("✓ UI Detector initialized")
    
    def detect_state(self, img: Image.Image) -> Dict[str, any]:
        """
        Detect the current UI state
        
        Args:
            img: PIL Image of screen
        
        Returns:
            Dict with 'type', 'message', 'confidence', 'keywords'
        """
        # Extract text from image
        text = extract_text(img).lower()
        
        if not text:
            return {
                "type": "unknown",
                "message": "No text detected",
                "confidence": 0.0,
                "keywords": []
            }
        
        # Check for errors
        error_matches = [kw for kw in self.error_keywords if kw in text]
        if error_matches:
            return {
                "type": "error",
                "message": f"Error detected: {', '.join(error_matches)}",
                "confidence": min(len(error_matches) * 0.3, 1.0),
                "keywords": error_matches,
                "full_text": text[:200]
            }
        
        # Check for loading
        loading_matches = [kw for kw in self.loading_keywords if kw in text]
        if loading_matches:
            return {
                "type": "loading",
                "message": f"Loading: {', '.join(loading_matches)}",
                "confidence": min(len(loading_matches) * 0.4, 1.0),
                "keywords": loading_matches,
                "full_text": text[:200]
            }
        
        # Check for success
        success_matches = [kw for kw in self.success_keywords if kw in text]
        if success_matches:
            return {
                "type": "success",
                "message": f"Success: {', '.join(success_matches)}",
                "confidence": min(len(success_matches) * 0.4, 1.0),
                "keywords": success_matches,
                "full_text": text[:200]
            }
        
        # Check for auth/login
        auth_matches = [kw for kw in self.auth_keywords if kw in text]
        if auth_matches:
            return {
                "type": "auth_required",
                "message": f"Authentication needed: {', '.join(auth_matches)}",
                "confidence": min(len(auth_matches) * 0.3, 1.0),
                "keywords": auth_matches,
                "full_text": text[:200]
            }
        
        # Normal state
        return {
            "type": "normal",
            "message": "No special state detected",
            "confidence": 0.5,
            "keywords": [],
            "full_text": text[:200]
        }
    
    def detect_buttons(self, img: Image.Image) -> List[str]:
        """
        Detect button text on screen
        
        Returns:
            List of button labels
        """
        from .ocr import get_ocr_engine
        
        ocr = get_ocr_engine()
        results = ocr.extract_text_with_positions(img)
        
        # Common button words
        button_keywords = [
            "ok", "cancel", "submit", "send", "save", "delete",
            "close", "open", "yes", "no", "continue", "next",
            "back", "finish", "apply", "confirm"
        ]
        
        buttons = []
        for result in results:
            text_lower = result['text'].lower().strip()
            if text_lower in button_keywords:
                buttons.append(result['text'])
        
        return buttons
    
    def detect_inputs(self, img: Image.Image) -> List[str]:
        """
        Detect input field labels
        
        Returns:
            List of input labels
        """
        from .ocr import get_ocr_engine
        
        ocr = get_ocr_engine()
        results = ocr.extract_text_with_positions(img)
        
        # Common input labels
        input_keywords = [
            "email", "password", "username", "name", "address",
            "phone", "search", "message", "subject", "to", "from"
        ]
        
        inputs = []
        for result in results:
            text_lower = result['text'].lower().strip()
            if any(kw in text_lower for kw in input_keywords):
                inputs.append(result['text'])
        
        return inputs
    
    def is_browser_active(self, img: Image.Image) -> bool:
        """Check if a browser window is active"""
        text = extract_text(img).lower()
        
        browser_indicators = [
            "http", "https", "www", ".com", ".org",
            "chrome", "firefox", "edge", "safari"
        ]
        
        return any(indicator in text for indicator in browser_indicators)
    
    def get_active_app(self, img: Image.Image) -> Optional[str]:
        """Try to detect the active application"""
        text = extract_text(img).lower()
        
        # Common app indicators
        apps = {
            "chrome": ["chrome", "google chrome"],
            "firefox": ["firefox", "mozilla"],
            "edge": ["edge", "microsoft edge"],
            "notepad": ["notepad", "untitled"],
            "word": ["word", "microsoft word", ".docx"],
            "excel": ["excel", "microsoft excel", ".xlsx"],
            "outlook": ["outlook", "microsoft outlook"],
            "vscode": ["visual studio code", "vscode"],
        }
        
        for app_name, indicators in apps.items():
            if any(indicator in text for indicator in indicators):
                return app_name
        
        return None


# Global instance
_ui_detector = None

def get_ui_detector() -> UIDetector:
    """Get or create global UI detector"""
    global _ui_detector
    if _ui_detector is None:
        _ui_detector = UIDetector()
    return _ui_detector


# Convenience functions
def detect_state(img: Image.Image) -> Dict[str, any]:
    """Detect UI state"""
    return get_ui_detector().detect_state(img)


def detect_buttons(img: Image.Image) -> List[str]:
    """Detect buttons"""
    return get_ui_detector().detect_buttons(img)


def is_browser_active(img: Image.Image) -> bool:
    """Check if browser is active"""
    return get_ui_detector().is_browser_active(img)
