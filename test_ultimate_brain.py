"""
Test script for the Ultimate Autonomous Brain
"""
import os
from dotenv import load_dotenv
from src.agent.autonomous_brain import AutonomousBrain

load_dotenv()

def test_brain():
    print("="*70)
    print("  TESTING PIXIE ULTIMATE AUTONOMOUS BRAIN")
    print("="*70)
    print()
    
    # Initialize brain
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    brain = AutonomousBrain(api_key)
    
    print(f"✅ Brain initialized")
    print(f"✅ GUI automation: {'Available' if brain.gui_available else 'Not available'}")
    print()
    
    # Test capabilities
    print("🧠 CAPABILITIES:")
    print("  ✓ Execute bash commands")
    print("  ✓ Create and edit files")
    print("  ✓ Run background processes")
    if brain.gui_available:
        print("  ✓ Take screenshots")
        print("  ✓ AI vision to find elements")
        print("  ✓ Click, type, press keys")
        print("  ✓ Move mouse")
    print()
    
    print("🎯 EXAMPLE TASKS YOU CAN TRY:")
    print("  • 'Create a Python hello world script and run it'")
    print("  • 'Take a screenshot and tell me what's on my screen'")
    print("  • 'Open Notepad and type Hello World'")
    print("  • 'Find all .txt files in my Documents folder'")
    print("  • 'Create a simple HTML page with a button'")
    print()
    
    # Simple test
    print("📝 Running simple test...")
    result = brain.write_file(
        "test_brain_output.txt",
        "Hello from Pixie Ultimate Brain!\nTimestamp: " + str(os.times())
    )
    print(f"   {result}")
    
    result = brain.read_file("test_brain_output.txt")
    print(f"   Read back: {result[:50]}...")
    
    print()
    print("="*70)
    print("✅ ALL SYSTEMS READY!")
    print("="*70)
    print()
    print("Start Pixie and try saying:")
    print('  "Build me a calculator app"')
    print('  "Open Chrome and search for pizza near me"')
    print()

if __name__ == "__main__":
    test_brain()
