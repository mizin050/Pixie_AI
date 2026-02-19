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
    print("You can send by:")
    print("  • Phone number: +1234567890")
    print("  • Contact name: John, Mom, Boss, etc.")
    print()
    print("="*70)
    print()
    
    # Get test details
    print("Choose method:")
    print("  1. Send by phone number")
    print("  2. Send by contact name")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        recipient = input("Enter phone number (e.g., +1234567890): ").strip()
    elif choice == "2":
        recipient = input("Enter contact name (e.g., John): ").strip()
    else:
        print("❌ Invalid choice")
        return
    
    if not recipient:
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
    result = send_whatsapp_message(recipient, message)
    
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
