"""
Free WhatsApp Integration Options
Multiple free alternatives to official API
"""
import os
import time
from typing import Optional, Dict, Any


class WhatsAppFree:
    """Free WhatsApp integration using multiple methods"""
    
    def __init__(self):
        self.method = self._detect_best_method()
        print(f"✓ WhatsApp Free initialized with method: {self.method}")
    
    def _detect_best_method(self) -> str:
        """Detect which free method is available"""
        try:
            import pywhatkit
            return "pywhatkit"
        except ImportError:
            pass
        
        try:
            from selenium import webdriver
            return "selenium"
        except ImportError:
            pass
        
        return "gui"
    
    def send_message_pywhatkit(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send message using pywhatkit (100% free, no API needed)
        
        Pros:
        - Completely free
        - No API setup needed
        - Works with WhatsApp Web
        
        Cons:
        - Opens browser tab
        - Requires WhatsApp Web to be logged in
        - 2-minute delay before sending
        """
        try:
            import pywhatkit as kit
            
            # Get current time + 2 minutes
            now = time.localtime()
            hour = now.tm_hour
            minute = now.tm_min + 2
            
            if minute >= 60:
                hour += 1
                minute -= 60
            
            print(f"📱 Scheduling message for {hour}:{minute:02d}...")
            
            # Send message
            kit.sendwhatmsg(phone, message, hour, minute, wait_time=15, tab_close=True)
            
            return {
                "success": True,
                "method": "pywhatkit",
                "message": "Message scheduled and sent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "pywhatkit"
            }
    
    def send_message_instant_pywhatkit(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send message instantly using pywhatkit
        Opens WhatsApp Web and sends immediately
        """
        try:
            import pywhatkit as kit
            
            print(f"📱 Sending instant message...")
            
            # Send instantly (opens browser)
            kit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True)
            
            return {
                "success": True,
                "method": "pywhatkit_instant",
                "message": "Message sent instantly"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "pywhatkit_instant"
            }
    
    def send_message_selenium(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send message using Selenium (free, more control)
        
        Pros:
        - Free
        - More control
        - Can send to groups
        
        Cons:
        - Requires Chrome/Firefox
        - Needs WhatsApp Web login
        - Slower than API
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print(f"📱 Opening WhatsApp Web...")
            
            # Setup Chrome in headless mode
            options = webdriver.ChromeOptions()
            options.add_argument('--user-data-dir=./whatsapp_session')  # Save session
            
            driver = webdriver.Chrome(options=options)
            driver.get('https://web.whatsapp.com')
            
            print("⏳ Waiting for WhatsApp Web to load...")
            print("   (Scan QR code if first time)")
            
            # Wait for chat to load
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            
            print(f"✓ WhatsApp Web loaded")
            print(f"📱 Sending message to {phone}...")
            
            # Open chat with phone number
            driver.get(f'https://web.whatsapp.com/send?phone={phone}')
            
            # Wait for message box
            message_box = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            
            # Type and send message
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            
            print("✓ Message sent!")
            
            time.sleep(2)
            driver.quit()
            
            return {
                "success": True,
                "method": "selenium",
                "message": "Message sent via Selenium"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "selenium"
            }
    
    def send_message(self, phone: str, message: str, instant: bool = True) -> Dict[str, Any]:
        """
        Send message using best available free method
        
        Args:
            phone: Phone number with country code (e.g., "+1234567890")
            message: Message to send
            instant: If True, send instantly (pywhatkit only)
        
        Returns:
            Result dict with success status
        """
        # Ensure phone has + prefix
        if not phone.startswith('+'):
            phone = '+' + phone
        
        if self.method == "pywhatkit":
            if instant:
                return self.send_message_instant_pywhatkit(phone, message)
            else:
                return self.send_message_pywhatkit(phone, message)
        
        elif self.method == "selenium":
            # Remove + for selenium
            phone_clean = phone.replace('+', '')
            return self.send_message_selenium(phone_clean, message)
        
        else:
            return {
                "success": False,
                "error": "No free method available. Install pywhatkit or selenium.",
                "install": "pip install pywhatkit selenium"
            }


# Global instance
_whatsapp_free = None

def get_whatsapp_free() -> WhatsAppFree:
    """Get or create the global WhatsApp Free instance"""
    global _whatsapp_free
    if _whatsapp_free is None:
        _whatsapp_free = WhatsAppFree()
    return _whatsapp_free


def send_whatsapp_free(phone: str, message: str, instant: bool = True) -> Dict[str, Any]:
    """
    Send WhatsApp message using free methods
    
    Args:
        phone: Phone number with country code (e.g., "+1234567890")
        message: Message to send
        instant: Send instantly (True) or schedule (False)
    
    Returns:
        Result dict with success status
    """
    wa = get_whatsapp_free()
    return wa.send_message(phone, message, instant)


# Convenience function for Pixie integration
def send_whatsapp_message_free(to: str, message: str) -> Dict[str, Any]:
    """Send WhatsApp message using free method (Pixie integration)"""
    return send_whatsapp_free(to, message, instant=True)
