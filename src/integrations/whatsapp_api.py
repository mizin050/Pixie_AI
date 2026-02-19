"""
WhatsApp Business API Integration
Official API for reliable message sending
"""
import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class WhatsAppAPI:
    """WhatsApp Business API client"""
    
    def __init__(self):
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        if not self.phone_number_id or not self.access_token:
            print("⚠️  WhatsApp API credentials not configured")
            print("   Set WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN in .env")
    
    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return bool(self.phone_number_id and self.access_token)
    
    def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp Business API
        
        Args:
            to: Phone number in international format (e.g., "1234567890")
            message: Text message to send
            
        Returns:
            Response dict with success status
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "WhatsApp API not configured"
            }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }
    
    def send_image(self, to: str, image_url: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an image via WhatsApp Business API
        
        Args:
            to: Phone number in international format
            image_url: URL of the image to send
            caption: Optional caption for the image
            
        Returns:
            Response dict with success status
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "WhatsApp API not configured"
            }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url
            }
        }
        
        if caption:
            payload["image"]["caption"] = caption
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }
    
    def send_document(self, to: str, document_url: str, filename: Optional[str] = None, caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a document via WhatsApp Business API
        
        Args:
            to: Phone number in international format
            document_url: URL of the document to send
            filename: Optional filename
            caption: Optional caption
            
        Returns:
            Response dict with success status
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "WhatsApp API not configured"
            }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url
            }
        }
        
        if filename:
            payload["document"]["filename"] = filename
        if caption:
            payload["document"]["caption"] = caption
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }
    
    def send_template(self, to: str, template_name: str, language_code: str = "en_US", components: Optional[list] = None) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp Business API
        
        Args:
            to: Phone number in international format
            template_name: Name of the approved template
            language_code: Language code (default: en_US)
            components: Optional template components
            
        Returns:
            Response dict with success status
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "WhatsApp API not configured"
            }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }


# Global instance
_whatsapp_api = None

def get_whatsapp_api() -> WhatsAppAPI:
    """Get or create the global WhatsApp API instance"""
    global _whatsapp_api
    if _whatsapp_api is None:
        _whatsapp_api = WhatsAppAPI()
    return _whatsapp_api


# Convenience functions
def send_whatsapp_message(to: str, message: str) -> Dict[str, Any]:
    """Send a WhatsApp message"""
    api = get_whatsapp_api()
    return api.send_message(to, message)


def send_whatsapp_image(to: str, image_url: str, caption: Optional[str] = None) -> Dict[str, Any]:
    """Send a WhatsApp image"""
    api = get_whatsapp_api()
    return api.send_image(to, image_url, caption)


def send_whatsapp_document(to: str, document_url: str, filename: Optional[str] = None, caption: Optional[str] = None) -> Dict[str, Any]:
    """Send a WhatsApp document"""
    api = get_whatsapp_api()
    return api.send_document(to, document_url, filename, caption)
