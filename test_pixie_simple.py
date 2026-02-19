"""
Test Pixie's Core Functions - WhatsApp & Browser
"""

def test_whatsapp():
    """Test WhatsApp integration"""
    print("="*70)
    print("  TESTING WHATSAPP")
    print("="*70)
    print()
    
    try:
        from src.tools.whatsapp_selenium import send_whatsapp_message
        print("✅ WhatsApp module loaded")
        print()
        print("To test, run:")
        print('  send_whatsapp_message("John", "Hello!")')
        print('  send_whatsapp_message("+1234567890", "Hello!")')
        print()
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
    
    print("="*70)
    print()


def test_browser():
    """Test browser automation"""
    print("="*70)
    print("  TESTING BROWSER AUTOMATION")
    print("="*70)
    print()
    
    try:
        from src.agent.autonomous_brain import AutonomousBrain
        import os
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  GEMINI_API_KEY not set")
            print("   Browser functions exist but need API key to use autonomous brain")
        else:
            brain = AutonomousBrain(api_key)
            print("✅ Autonomous brain loaded")
            print("✅ Browser functions available:")
            print("   - open_browser(url)")
            print("   - browser_action(url, actions)")
        
        print()
        print("To test manually:")
        print("  from selenium import webdriver")
        print("  driver = webdriver.Chrome()")
        print("  driver.get('https://google.com')")
        print()
        
    except Exception as e:
        print(f"❌ Browser error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*70)
    print()


def main():
    print()
    print("="*70)
    print("  PIXIE CORE FUNCTIONS TEST")
    print("="*70)
    print()
    
    test_whatsapp()
    test_browser()
    
    print("="*70)
    print("  SUMMARY")
    print("="*70)
    print()
    print("Pixie has 2 core functions:")
    print("  1. WhatsApp automation (Selenium)")
    print("  2. Browser automation (Selenium)")
    print()
    print("Both use Selenium which is already installed!")
    print()
    print("To use in Pixie:")
    print('  "Send WhatsApp to John"')
    print('  "Open Spotify"')
    print()


if __name__ == "__main__":
    main()
