"""
WhatsApp Tools - High-level tools for WhatsApp Desktop operations
"""
import time
from typing import Dict, Any, Optional
from src.tools.computer_tools import get_computer_tools
from src.vision.capture import capture_screen
import tempfile
import os


class WhatsAppTools:
    """High-level tools for WhatsApp Desktop"""
    
    def __init__(self):
        self.computer = get_computer_tools()
        print("✓ WhatsApp tools initialized")
    
    def open_whatsapp(self) -> Dict[str, Any]:
        """
        Open WhatsApp Desktop using Windows search
        
        Returns:
            Result dict
        """
        print("📱 Opening WhatsApp Desktop...")
        
        # Step 1: Open Windows search (Win+S)
        self.computer.hotkey_press("win", "s")
        time.sleep(0.5)
        
        # Step 2: Type "whatsapp"
        self.computer.type("whatsapp")
        time.sleep(0.5)
        
        # Step 3: Press Enter to open
        self.computer.key("enter")
        time.sleep(3)  # Wait for WhatsApp to load
        
        return {
            "success": True,
            "message": "WhatsApp Desktop opened"
        }
    
    def search_contact(self, contact_name: str) -> Dict[str, Any]:
        """
        Search for a contact in WhatsApp search bar
        
        Args:
            contact_name: Name of contact to search
        
        Returns:
            Result dict
        """
        print(f"🔍 Searching for contact: {contact_name}")
        
        # Click WhatsApp search bar (usually Ctrl+F or click at top)
        self.computer.hotkey_press("ctrl", "f")
        time.sleep(0.3)
        
        # Type contact name
        self.computer.type(contact_name)
        time.sleep(0.8)  # Wait for search results
        
        # Press Enter to select first result
        self.computer.key("enter")
        time.sleep(0.5)
        
        return {
            "success": True,
            "message": f"Searched and selected {contact_name}"
        }
    
    def send_text_message(self, message: str) -> Dict[str, Any]:
        """
        Type and send a text message in current chat
        
        Args:
            message: Message text to send
        
        Returns:
            Result dict
        """
        print(f"💬 Sending message: {message[:50]}...")
        
        # Type message (cursor should already be in message box)
        self.computer.type(message)
        time.sleep(0.3)
        
        # Press Enter to send
        self.computer.key("enter")
        time.sleep(0.3)
        
        return {
            "success": True,
            "message": f"Message sent: {message[:50]}"
        }
    
    def send_screenshot_message(self, contact_name: str) -> Dict[str, Any]:
        """
        Take screenshot and send to WhatsApp contact
        
        Args:
            contact_name: Name of contact to send to
        
        Returns:
            Result dict
        """
        print(f"📸 Taking screenshot and sending to {contact_name}...")
        
        # Step 1: Take screenshot (Win+PrintScreen)
        print("  Taking screenshot (Win+PrintScreen)...")
        self.computer.hotkey_press("win", "printscreen")
        time.sleep(1.5)  # Wait for screenshot to be saved and copied to clipboard
        
        # Step 2: Open WhatsApp
        print("  Opening WhatsApp...")
        result = self.open_whatsapp()
        if not result["success"]:
            return result
        
        # Step 3: Search contact
        print(f"  Searching for {contact_name}...")
        result = self.search_contact(contact_name)
        if not result["success"]:
            return result
        
        # Step 4: Paste screenshot (Ctrl+V)
        print("  Pasting screenshot...")
        self.computer.hotkey_press("ctrl", "v")
        time.sleep(0.8)
        
        # Step 5: Send (Enter)
        print("  Sending...")
        self.computer.key("enter")
        time.sleep(0.5)
        
        print("✅ Screenshot sent!")
        return {
            "success": True,
            "message": f"Screenshot sent to {contact_name}"
        }
    
    def send_whatsapp_message(self, contact_name: str, message: str, is_screenshot: bool = False) -> Dict[str, Any]:
        """
        Complete workflow: Open WhatsApp, find contact, send message
        
        Args:
            contact_name: Name of contact
            message: Message to send (or ignored if screenshot)
            is_screenshot: If True, send screenshot instead of text
        
        Returns:
            Result dict with all steps
        """
        print(f"\n📱 WhatsApp: Sending to {contact_name}")
        print("="*60)
        
        if is_screenshot:
            return self.send_screenshot_message(contact_name)
        
        steps = []
        
        # Step 1: Open WhatsApp via Windows search
        result = self.open_whatsapp()
        steps.append(("Open WhatsApp", result["success"]))
        if not result["success"]:
            return {"success": False, "message": "Failed to open WhatsApp", "steps": steps}
        
        # Step 2: Search contact in WhatsApp
        result = self.search_contact(contact_name)
        steps.append(("Search contact", result["success"]))
        if not result["success"]:
            return {"success": False, "message": "Failed to search contact", "steps": steps}
        
        # Step 3: Send message
        result = self.send_text_message(message)
        steps.append(("Send message", result["success"]))
        if not result["success"]:
            return {"success": False, "message": "Failed to send message", "steps": steps}
        
        print("="*60)
        print("✅ Message sent successfully!\n")
        
        return {
            "success": True,
            "message": f"Sent '{message}' to {contact_name}",
            "steps": steps
        }


# Global instance
_whatsapp_tools = None

def get_whatsapp_tools() -> WhatsAppTools:
    """Get or create global WhatsApp tools instance"""
    global _whatsapp_tools
    if _whatsapp_tools is None:
        _whatsapp_tools = WhatsAppTools()
    return _whatsapp_tools


# Convenience functions
def send_whatsapp_message(contact: str, message: str) -> Dict[str, Any]:
    """Send a WhatsApp text message"""
    return get_whatsapp_tools().send_whatsapp_message(contact, message, is_screenshot=False)


def send_whatsapp_screenshot(contact: str) -> Dict[str, Any]:
    """Send a screenshot on wahtsapp"""
    return get_whatsapp_tools().send_whatsapp_message(contact, "", is_screenshot=True)
