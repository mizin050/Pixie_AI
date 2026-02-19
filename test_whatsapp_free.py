"""
Test Free WhatsApp Integration Options
"""
from src.integrations.whatsapp_free import WhatsAppFree, send_whatsapp_free

def test_free_options():
    print("="*70)
    print("  TESTING FREE WHATSAPP OPTIONS")
    print("="*70)
    print()
    
    wa = WhatsAppFree()
    
    print(f"✓ Best available method: {wa.method}")
    print()
    
    if wa.method == "pywhatkit":
        print("📱 PyWhatKit is available!")
        print("   - 100% FREE")
        print("   - Easy to use")
        print("   - 80% reliable")
        print()
        print("Usage:")
        print('  send_whatsapp_free("+1234567890", "Hello!", instant=True)')
        
    elif wa.method == "selenium":
        print("🌐 Selenium is available!")
        print("   - 100% FREE")
        print("   - Full control")
        print("   - 85% reliable")
        print()
        print("Usage:")
        print('  wa.send_message_selenium("1234567890", "Hello!")')
        
    else:
        print("⚠️  No free methods installed")
        print()
        print("Install options:")
        print("  1. PyWhatKit (Recommended):")
        print("     pip install pywhatkit")
        print()
        print("  2. Selenium (Advanced):")
        print("     pip install selenium webdriver-manager")
        print()
        print("  3. Both:")
        print("     pip install pywhatkit selenium webdriver-manager")
    
    print()
    print("="*70)
    print()
    
    # Test if user wants to send
    if wa.method != "gui":
        test = input("Want to test sending a message? (yes/no): ").strip().lower()
        
        if test == "yes":
            phone = input("Enter phone number (with country code, e.g., +1234567890): ").strip()
            message = input("Enter message: ").strip()
            
            if phone and message:
                print()
                print("📱 Sending message...")
                result = send_whatsapp_free(phone, message, instant=True)
                
                print()
                if result["success"]:
                    print("✅ MESSAGE SENT!")
                    print(f"   Method: {result['method']}")
                else:
                    print("❌ MESSAGE FAILED")
                    print(f"   Error: {result['error']}")
                    if 'install' in result:
                        print(f"   Install: {result['install']}")
    
    print()
    print("See WHATSAPP_FREE_OPTIONS.md for detailed guide")
    print()

if __name__ == "__main__":
    test_free_options()
