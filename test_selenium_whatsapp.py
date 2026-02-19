"""
Test Selenium WhatsApp Integration
"""
from src.tools.whatsapp_selenium import send_whatsapp_message

def test_selenium_whatsapp():
    print("="*70)
    print("  TESTING SELENIUM WHATSAPP")
    print("="*70)
    print()
    
    print("✓ Selenium WhatsApp is ready!")
    print()
    print("How it works:")
    print("  1. Opens Chrome with WhatsApp Web")
    print("  2. First time: Scan QR code")
    print("  3. After that: Session saved, works automatically!")
    print("  4. Sends message in 10-15 seconds")
    print()
    print("="*70)
    print()
    
    # Get test details
    phone = input("Enter phone number (e.g., +1234567890): ").strip()
    
    if not phone:
        print("❌ No phone number provided")
        return
    
    message = input("Enter message (or press Enter for default): ").strip()
    if not message:
        message = "🤖 Hello from Pixie AI!\n\nThis is a test message via Selenium."
    
    print()
    print("="*70)
    print("  SENDING MESSAGE")
    print("="*70)
    print()
    
    # Send message
    result = send_whatsapp_message(phone, message)
    
    print()
    print("="*70)
    print("  RESULT")
    print("="*70)
    print()
    print(result)
    print()
    
    if "✅" in result:
        print("SUCCESS! Check your WhatsApp to see the message.")
        print()
        print("Next time it will be even faster (session saved)!")
    else:
        print("FAILED. Common issues:")
        print("  • Chrome not installed")
        print("  • QR code not scanned")
        print("  • Invalid phone number format")
        print("  • Internet connection issue")
    
    print()
    print("="*70)

if __name__ == "__main__":
    test_selenium_whatsapp()
