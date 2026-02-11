"""
Vision Summary - Create compact screen descriptions for Gemini
"""
from PIL import Image
from typing import Dict
from .capture import capture_screen
from .ocr import extract_text
from .ui_detect import detect_state, detect_buttons, is_browser_active


class VisionSummarizer:
    """Create compact, informative screen summaries"""
    
    def __init__(self):
        print("✓ Vision Summarizer initialized")
    
    def create_summary(self, img: Image.Image) -> str:
        """
        Create a compact summary of the screen
        
        Args:
            img: PIL Image of screen
        
        Returns:
            Compact text summary (< 500 chars)
        """
        # Get UI state
        state = detect_state(img)
        
        # Get visible text (first 300 chars)
        text = extract_text(img)
        text_preview = text[:300] if text else "No text visible"
        
        # Detect buttons
        buttons = detect_buttons(img)
        
        # Detect active app
        from .ui_detect import get_ui_detector
        active_app = get_ui_detector().get_active_app(img)
        
        # Build summary
        summary = []
        
        # State
        if state['type'] != 'normal':
            summary.append(f"State: {state['type']} - {state['message']}")
        
        # Active app
        if active_app:
            summary.append(f"App: {active_app}")
        elif is_browser_active(img):
            summary.append("App: Browser")
        
        # Visible text
        if text_preview:
            summary.append(f"Text: {text_preview}")
        
        # Buttons
        if buttons:
            summary.append(f"Buttons: {', '.join(buttons[:5])}")
        
        # Combine
        result = " | ".join(summary)
        
        # Truncate if too long
        if len(result) > 500:
            result = result[:497] + "..."
        
        return result
    
    def create_detailed_summary(self, img: Image.Image) -> Dict[str, any]:
        """
        Create a detailed summary with all information
        
        Returns:
            Dict with all detected information
        """
        from .ui_detect import get_ui_detector
        state = detect_state(img)
        text = extract_text(img)
        buttons = detect_buttons(img)
        active_app = get_ui_detector().get_active_app(img)
        is_browser = is_browser_active(img)
        
        return {
            "state": state,
            "text": text,
            "text_length": len(text),
            "buttons": buttons,
            "active_app": active_app,
            "is_browser": is_browser,
            "summary": self.create_summary(img)
        }
    
    def verify_action_result(
        self,
        before_img: Image.Image,
        after_img: Image.Image,
        expected_change: str
    ) -> Dict[str, any]:
        """
        Verify if an action had the expected result
        
        Args:
            before_img: Screen before action
            after_img: Screen after action
            expected_change: What should have changed
        
        Returns:
            Dict with verification result
        """
        before_text = extract_text(before_img).lower()
        after_text = extract_text(after_img).lower()
        
        before_state = detect_state(before_img)
        after_state = detect_state(after_img)
        
        # Check if text changed
        text_changed = before_text != after_text
        
        # Check if state changed
        state_changed = before_state['type'] != after_state['type']
        
        # Check for expected keywords
        expected_lower = expected_change.lower()
        expected_found = expected_lower in after_text
        
        # Calculate confidence
        confidence = 0.0
        if text_changed:
            confidence += 0.3
        if state_changed:
            confidence += 0.3
        if expected_found:
            confidence += 0.4
        
        success = confidence >= 0.6
        
        return {
            "success": success,
            "confidence": confidence,
            "text_changed": text_changed,
            "state_changed": state_changed,
            "expected_found": expected_found,
            "before_state": before_state['type'],
            "after_state": after_state['type'],
            "changes": {
                "text_diff": len(after_text) - len(before_text),
                "new_buttons": [b for b in detect_buttons(after_img) if b not in detect_buttons(before_img)]
            }
        }


# Global instance
_vision_summarizer = None

def get_vision_summarizer() -> VisionSummarizer:
    """Get or create global vision summarizer"""
    global _vision_summarizer
    if _vision_summarizer is None:
        _vision_summarizer = VisionSummarizer()
    return _vision_summarizer


# Convenience functions
def create_summary(img: Image.Image) -> str:
    """Create compact screen summary"""
    return get_vision_summarizer().create_summary(img)


def create_detailed_summary(img: Image.Image) -> Dict[str, any]:
    """Create detailed screen summary"""
    return get_vision_summarizer().create_detailed_summary(img)


def verify_action_result(
    before_img: Image.Image,
    after_img: Image.Image,
    expected_change: str
) -> Dict[str, any]:
    """Verify action result"""
    return get_vision_summarizer().verify_action_result(
        before_img,
        after_img,
        expected_change
    )


def capture_and_summarize() -> str:
    """Capture screen and create summary in one call"""
    img = capture_screen()
    return create_summary(img)
