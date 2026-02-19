"""
WhatsApp Selenium Integration - Simple & Reliable
Default WhatsApp method for Pixie
"""
from typing import Dict, Any
import time
import os


class WhatsAppSelenium:
    """WhatsApp automation using Selenium"""
    
    def __init__(self):
        self.session_dir = os.path.join(os.getcwd(), 'whatsapp_session')
        self.driver = None
        print("✓ WhatsApp Selenium initialized")
    
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp message using Selenium
        
        Args:
            phone: Phone number (e.g., "1234567890" or "+1234567890")
            message: Message to send
        
        Returns:
            Result dict with success status
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            
            print(f"\n📱 Sending WhatsApp message...")
            print(f"   To: {phone}")
            print(f"   Message: {message[:50]}...")
            
            # Clean phone number
            phone_clean = phone.replace('+', '').replace('-', '').replace(' ', '')
            
            # Setup Chrome
            chrome_options = Options()
            chrome_options.add_argument(f'--user-data-dir={self.session_dir}')
            chrome_options.add_argument('--profile-directory=Default')
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Open WhatsApp Web
                print("   Opening WhatsApp Web...")
                self.driver.get('https://web.whatsapp.com')
                
                # Wait for WhatsApp to load
                print("   Waiting for WhatsApp Web...")
                print("   (Scan QR code if first time)")
                
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                
                print("   ✓ WhatsApp Web loaded")
                
                # Open chat
                print(f"   Opening chat...")
                self.driver.get(f'https://web.whatsapp.com/send?phone={phone_clean}')
                
                # Wait for message box
                print("   Waiting for message box...")
                message_box = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                
                # Type and send
                print("   Typing message...")
                message_box.click()
                time.sleep(0.5)
                message_box.send_keys(message)
                time.sleep(0.5)
                message_box.send_keys(Keys.ENTER)
                
                # Wait for send
                time.sleep(2)
                
                print("   ✅ Message sent!")
                
                self.driver.quit()
                
                return {
                    "success": True,
                    "method": "selenium",
                    "phone": phone,
                    "message": "Message sent successfully"
                }
                
            except Exception as e:
                if self.driver:
                    self.driver.quit()
                raise e
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            
            # Provide helpful error messages
            if "chrome" in error_msg.lower():
                error_msg += "\n   Install Chrome: https://www.google.com/chrome/"
            elif "qr" in error_msg.lower() or "scan" in error_msg.lower():
                error_msg += "\n   Please scan QR code in WhatsApp Web"
            
            return {
                "success": False,
                "error": error_msg,
                "method": "selenium"
            }


# Global instance
_whatsapp_selenium = None

def get_whatsapp_selenium() -> WhatsAppSelenium:
    """Get or create global WhatsApp Selenium instance"""
    global _whatsapp_selenium
    if _whatsapp_selenium is None:
        _whatsapp_selenium = WhatsAppSelenium()
    return _whatsapp_selenium


def send_whatsapp_message(phone: str, message: str) -> str:
    """
    Send WhatsApp message (main function for Pixie)
    
    Args:
        phone: Phone number (e.g., "+1234567890")
        message: Message to send
    
    Returns:
        Success/error message string
    """
    wa = get_whatsapp_selenium()
    result = wa.send_message(phone, message)
    
    if result["success"]:
        return f"✅ WhatsApp message sent to {phone}"
    else:
        return f"❌ Failed: {result['error']}"
