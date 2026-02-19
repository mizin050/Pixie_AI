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
    
    def send_file(self, recipient: str, file_path: str, caption: str = "") -> Dict[str, Any]:
        """
        Send file (photo, video, document) via WhatsApp
        
        Args:
            recipient: Phone number or contact name
            file_path: Path to file on desktop (e.g., "C:/Users/You/Desktop/photo.jpg")
            caption: Optional caption for the file
        
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
            
            print(f"\n📎 Sending file via WhatsApp...")
            print(f"   To: {recipient}")
            print(f"   File: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Detect if recipient is phone or name
            is_phone_number = recipient.replace('+', '').replace('-', '').replace(' ', '').isdigit()
            
            # Setup Chrome
            chrome_options = Options()
            chrome_options.add_argument(f'--user-data-dir={self.session_dir}')
            chrome_options.add_argument('--profile-directory=Default')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Open WhatsApp Web
                print("   Opening WhatsApp Web...")
                self.driver.get('https://web.whatsapp.com')
                
                # Wait for load
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                
                print("   ✓ WhatsApp Web loaded")
                
                # Open chat
                if is_phone_number:
                    phone_clean = recipient.replace('+', '').replace('-', '').replace(' ', '')
                    self.driver.get(f'https://web.whatsapp.com/send?phone={phone_clean}')
                else:
                    # Search by name
                    search_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                    )
                    search_box.click()
                    time.sleep(0.5)
                    search_box.send_keys(recipient)
                    time.sleep(1.5)
                    
                    first_result = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@role="listitem"]'))
                    )
                    first_result.click()
                    time.sleep(1)
                
                # Click attach button
                print("   Clicking attach button...")
                attach_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]'))
                )
                attach_btn.click()
                time.sleep(1)
                
                # Click appropriate option based on file type
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    print("   Selecting photo/video option...")
                    # Photos & Videos
                    media_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                    )
                else:
                    print("   Selecting document option...")
                    # Document
                    media_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@accept="*"]'))
                    )
                
                # Send file path
                print("   Uploading file...")
                media_input.send_keys(os.path.abspath(file_path))
                time.sleep(2)
                
                # Add caption if provided
                if caption:
                    print(f"   Adding caption: {caption[:30]}...")
                    caption_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    caption_box.send_keys(caption)
                    time.sleep(0.5)
                
                # Click send
                print("   Sending...")
                send_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]'))
                )
                send_btn.click()
                
                # Wait for send
                time.sleep(3)
                
                print("   ✅ File sent!")
                
                self.driver.quit()
                
                return {
                    "success": True,
                    "method": "selenium",
                    "recipient": recipient,
                    "file": file_path,
                    "message": "File sent successfully"
                }
                
            except Exception as e:
                if self.driver:
                    self.driver.quit()
                raise e
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "method": "selenium"
            }
    
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp message using Selenium
        
        Args:
            phone: Phone number (e.g., "1234567890" or "+1234567890") OR contact name (e.g., "John")
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
            
            # Detect if it's a phone number or contact name
            is_phone_number = phone.replace('+', '').replace('-', '').replace(' ', '').isdigit()
            
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
                
                if is_phone_number:
                    # Method 1: Direct URL with phone number
                    phone_clean = phone.replace('+', '').replace('-', '').replace(' ', '')
                    print(f"   Opening chat by phone number...")
                    self.driver.get(f'https://web.whatsapp.com/send?phone={phone_clean}')
                else:
                    # Method 2: Search by contact name
                    print(f"   Searching for contact: {phone}...")
                    
                    # Click search box
                    search_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                    )
                    search_box.click()
                    time.sleep(0.5)
                    
                    # Type contact name
                    search_box.send_keys(phone)
                    time.sleep(1.5)  # Wait for search results
                    
                    # Click first result
                    print(f"   Clicking first search result...")
                    first_result = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@role="listitem"]'))
                    )
                    first_result.click()
                    time.sleep(1)
                
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
                    "recipient": phone,
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
            elif not is_phone_number:
                error_msg += f"\n   Contact '{phone}' not found. Make sure the name is exact."
            
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
        phone: Phone number (e.g., "+1234567890") OR contact name (e.g., "John")
        message: Message to send
    
    Returns:
        Success/error message string
    
    Examples:
        send_whatsapp_message("+1234567890", "Hello!")  # By phone
        send_whatsapp_message("John", "Hello!")  # By name
        send_whatsapp_message("Mom", "Love you!")  # By name
    """
    wa = get_whatsapp_selenium()
    result = wa.send_message(phone, message)
    
    if result["success"]:
        return f"✅ WhatsApp message sent to {phone}"
    else:
        return f"❌ Failed: {result['error']}"


def send_whatsapp_file(recipient: str, file_path: str, caption: str = "") -> str:
    """
    Send file via WhatsApp (photos, videos, documents)
    
    Args:
        recipient: Phone number or contact name
        file_path: Path to file (e.g., "C:/Users/You/Desktop/photo.jpg")
        caption: Optional caption
    
    Returns:
        Success/error message string
    
    Examples:
        send_whatsapp_file("John", "C:/Users/Me/Desktop/photo.jpg")
        send_whatsapp_file("+1234567890", "report.pdf", "Here's the report")
        send_whatsapp_file("Mom", "vacation.jpg", "Miss you!")
    """
    wa = get_whatsapp_selenium()
    result = wa.send_file(recipient, file_path, caption)
    
    if result["success"]:
        return f"✅ File sent to {recipient}"
    else:
        return f"❌ Failed: {result['error']}"
