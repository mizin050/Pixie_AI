"""
Test WhatsApp Business API Integration
"""
import os
from dotenv import load_dotenv
from src.integrations.whatsapp_api import WhatsAppAPI, get_whatsapp_api

load_dotenv()

def test_whatsapp_api():
    print("="*70)
    print("  TESTING WHATSAPP BUSINESS API")
    print("="*70)
    print()
    
    api = get_whatsapp_api()
    
    # Check configuration
    if not api.is_configured():
        print("❌ WhatsApp API not configured")
        print()
        print("To configure:")
        print("1. Get credentials from: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started")
        print("2. Add to .env file:")
        print("   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id")
        print("   WHATSAPP_ACCESS_TOKEN=your_access_token")
        print()
        print("See WHATSAPP_API_SETUP.md for detailed instructions")
        return
    
    print("✅ WhatsApp API configured")
    print(f"   Phone Number ID: {api.phone_number_id[:10]}...")
    print(f"   Access Token: {api.access_token[:20]}...")
    print()
    
    # Get test phone number
    test_number = input("Enter test phone number (format: 1234567890, no +): ").strip()
    
    if not test_number:
        print("❌ No phone number provided")
        return
    
    print()
    print("📱 Sending test message...")
    
    result = api.send_message(
        to=test_number,
        message="🤖 Hello from Pixie AI!\n\nThis is a test message from the WhatsApp Business API."
    )
    
    print()
    if result["success"]:
        print("✅ MESSAGE SENT SUCCESSFULLY!")
        print(f"   Message ID: {result['message_id']}")
        print()
        print("Check your WhatsApp to see the message!")
    else:
        print("❌ MESSAGE FAILED")
        print(f"   Error: {result['error']}")
        if result.get('status_code'):
            print(f"   Status Code: {result['status_code']}")
        print()
        print("Common issues:")
        print("  • Phone number not in test numbers list (add in Meta dashboard)")
        print("  • Invalid phone number format (use: 1234567890, no + or spaces)")
        print("  • Access token expired (generate new one)")
        print("  • API quota exceeded")
    
    print()
    print("="*70)

if __name__ == "__main__":
    test_whatsapp_api()
