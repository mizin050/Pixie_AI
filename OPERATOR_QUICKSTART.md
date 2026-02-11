# Pixie Operator Mode - Quick Start Guide

## What is Operator Mode?

Operator Mode transforms Pixie from a chat assistant into a desktop AI operator that can:

- **Plan** multi-step tasks
- **Execute** actions on your computer
- **Verify** each step with confidence scoring
- **Request approval** for risky actions

## How to Use

### 1. Start Pixie

```bash
python main.py
```

### 2. Open the UI

- Right-click the Pixie icon in system tray
- Click "Pixie UI"

### 3. Toggle Operator Mode

- Look for the **🤖 Operator** button in the top-right
- Click to switch between:
  - **🤖 Operator Mode** (task execution)
  - **💬 Chat Mode** (normal conversation)

## Try These Commands

### Simple Tasks (Low Risk - Auto-Execute)

```
Open Chrome
Open Notepad
Go to gmail.com
```

### Complex Tasks (Medium Risk - Requires Approval)

```
Send an email to john@example.com with subject "Meeting"
Download the latest report from the website
Create a new folder called "Projects"
```

### What You'll See

When you give an operator command, Pixie will:

1. **Create a Plan**

   ```
   📋 Plan Created

   Goal: Open Chrome and go to gmail.com
   Steps: 2
   Time: ~15s
   Risk: All steps are low risk

   Steps:
   🟢 1. Launch the Google Chrome browser
   🟢 2. Navigate to gmail.com

   💡 This plan will execute automatically
   ```

2. **Show Risk Assessment**
   - 🟢 **LOW** = Safe, auto-executes
   - 🟡 **MEDIUM** = Needs approval
   - 🔴 **HIGH** = Dangerous, requires explicit confirmation

3. **Request Approval (if needed)**

   ```
   ⚠️ This plan requires your approval

   ✅ Type 'approve' to execute
   ❌ Type 'cancel' to abort
   ```

## Special Commands

- `status` or `progress` - Show current plan progress
- `approve` - Approve a pending plan
- `cancel` - Cancel the current plan

## Current Capabilities (Phase 1)

✅ **Planning** - Creates detailed, step-by-step plans
✅ **Risk Assessment** - Classifies actions as LOW/MEDIUM/HIGH
✅ **Approval Flow** - Requests permission for risky actions
✅ **Progress Tracking** - Shows which steps are complete

🚧 **Coming in Phase 2-3**:

- Actual execution (browser control, mouse/keyboard)
- Vision-based verification
- Retry logic
- Screen capture

## Examples

### Example 1: Simple Browser Task

**You**: `Open Chrome and go to gmail.com`

**Pixie**:

```
📋 Plan Created

Goal: Open Chrome and go to gmail.com
Steps: 2
Time: ~15s

Steps:
🟢 1. Launch Google Chrome browser
🟢 2. Navigate to gmail.com

💡 This plan will execute automatically
```

### Example 2: Email Task (Requires Approval)

**You**: `Send an email to john@example.com about the meeting`

**Pixie**:

```
📋 Plan Created

Goal: Send an email to john@example.com about the meeting
Steps: 7
Time: ~60s

Steps:
🟢 1. Open Chrome browser
🟢 2. Navigate to Gmail
🟢 3. Click Compose button
🟢 4. Type recipient: john@example.com
🟢 5. Type subject: Meeting
🟢 6. Type body: ...
🟡 7. Click Send button

⚠️ This plan requires your approval

✅ Type 'approve' to execute
❌ Type 'cancel' to abort
```

**You**: `approve`

**Pixie**: `✅ Plan approved! (Execution will be implemented in Phase 3)`

## Tips

1. **Be Specific**: "Open Chrome and go to gmail.com" is better than "check email"
2. **Check the Plan**: Review the steps before approving
3. **Watch Risk Levels**: 🟢 = safe, 🟡 = careful, 🔴 = dangerous
4. **Use Status**: Type `status` to see progress anytime

## Troubleshooting

### "No active plan"

- You haven't given an operator command yet
- Try: `Open Notepad`

### Plan looks wrong

- Type `cancel` to abort
- Rephrase your command more clearly
- Example: Instead of "email John", try "Send an email to john@example.com"

### Mode confusion

- Check the button in top-right
- 🤖 = Operator Mode (for tasks)
- 💬 = Chat Mode (for conversation)

## What's Next?

Phase 1 (✅ Complete):

- Brain & Planning system
- Risk assessment
- Approval flow

Phase 2 (Coming Soon):

- Vision system (screen capture, OCR)
- UI state detection
- Verification

Phase 3 (Coming Soon):

- Actual execution (Playwright + mouse/keyboard)
- Retry logic
- Error recovery

---

**Ready to test?** Start Pixie and try: `Open Chrome and go to gmail.com`
