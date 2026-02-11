# Send WhatsApp Message with Pixie

## ✅ CORRECT Way - Using WhatsApp Desktop Search

Pixie now knows to use WhatsApp Desktop's built-in search box (at the top of the app), NOT system contacts!

### How It Works:

1. **Clicks WhatsApp search box** (at top of WhatsApp Desktop)
2. **Types contact name** in WhatsApp's search
3. **Waits for results** from WhatsApp
4. **Clicks the contact** from WhatsApp's search results
5. **Types your message** in the chat
6. **Presses Enter** to send

### Example Commands:

**Simple message**:

```
send whatsapp message to John saying hello
```

**Detailed message**:

```
open whatsapp, search for John, and send "Hey! How are you?"
```

**Step-by-step**:

```
1. Click on WhatsApp Desktop
2. Search for contact "John"
3. Type "Hello from Pixie!"
4. Press Enter to send
```

## How Pixie Will Execute:

1. **Find WhatsApp** - Uses vision to locate the app
2. **Click search** - Finds and clicks the search box
3. **Type contact name** - Types the person's name
4. **Select contact** - Clicks on the contact
5. **Type message** - Types your message
6. **Send** - Presses Enter

## Try It Now:

### Option 1: Use Pixie UI

1. Start Pixie: `python main.py`
2. Open UI from system tray
3. Switch to 🤖 Operator mode
4. Type: `send whatsapp message to [contact name] saying [your message]`

### Option 2: Quick Test Script

Create a test file:

```python
# test_whatsapp.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.ai_engine_operator import get_response_operator

# Example: Send message
command = "open whatsapp, search for John, and send 'Hello!'"
response = get_response_operator(command)
print(response)
```

Run it:

```bash
python test_whatsapp.py
```

## What Pixie Will Do:

```
📋 Plan Created

Goal: send whatsapp message to John saying hello
Steps: 5
Time: ~20s
Risk: MEDIUM (requires approval)

Steps:
🟢 1. Focus WhatsApp Desktop window
🟢 2. Click search box
🟢 3. Type "John"
🟢 4. Click on John's contact
🟡 5. Type and send message "hello"

⚠️ This plan requires your approval

✅ Type 'approve' to execute
❌ Type 'cancel' to abort
```

Then type `approve` and watch it work!

## Tips:

1. **Make sure WhatsApp Desktop is open** before running
2. **Use exact contact names** as they appear in WhatsApp
3. **Keep messages simple** for better reliability
4. **Approve the plan** before it sends (safety!)

## Example Full Command:

In Pixie UI (Operator mode):

```
send whatsapp message to Mom saying "I'll be home at 6pm"
```

Pixie will:

1. Create a plan
2. Ask for approval (MEDIUM risk - sending message)
3. Execute when you type "approve"
4. Verify each step with vision
5. Report success!

## Safety:

- ✅ Requires approval before sending
- ✅ Shows you the exact message before sending
- ✅ Verifies each step with vision
- ✅ You can cancel anytime

---

**Ready to try?** Start Pixie and give it a command! 🦊📱
