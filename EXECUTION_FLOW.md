# Pixie Execution Flow Analysis

## Current System Architecture

### 1. User Input → Operator Engine

**File:** `src/core/ai_engine_operator.py`

```
User types: "send whatsapp message to adith 'hello'"
    ↓
get_response_operator(user_text)
    ↓
Checks if it's an operator command (has action keywords)
    ↓
If YES → Create Plan
If NO → Fall back to regular chat
```

### 2. Plan Creation

**File:** `src/agent/brain.py` → `src/agent/planner.py`

```
Brain.create_plan(goal)
    ↓
Sends prompt to Gemini API with:
- System instructions
- Goal
- JSON schema for Plan
    ↓
Gemini returns JSON:
{
  "goal": "...",
  "steps": [...],
  "requires_approval": true/false,
  "risk_summary": "..."
}
    ↓
Validates against Plan schema
    ↓
Returns Plan object
```

**Current Issues:**

- ❌ Gemini sometimes sets `requires_approval=true` even for safe tasks
- ❌ Steps can be too granular (3 steps to open notepad)
- ✅ We force `requires_approval=false` if all steps are LOW risk

### 3. Approval Check

**File:** `src/core/ai_engine_operator.py`

```
plan_data = create_plan(goal)
    ↓
Check if root_access enabled → bypass approval
    ↓
Check if all steps are LOW risk → force auto-execute
    ↓
If requires_approval=false:
    → Execute immediately
Else:
    → Show approval buttons, wait for user
```

**Current Status:**

- ✅ Root access mode works
- ✅ LOW risk override works
- ✅ Approval buttons in UI work

### 4. Execution Loop

**File:** `src/core/ai_engine_operator.py` → `src/control/executor.py`

```
execute_plan()
    ↓
For each step in plan:
    1. Capture screen BEFORE action
    2. Execute action based on type:
       - open_app → system.open_app()
       - click → mouse.click() or browser.click()
       - type → keyboard.type_text()
       - press_key → keyboard.press_key()
    3. Wait 0.2s for UI to update
    4. Capture screen AFTER action
    5. Verify action succeeded using vision
    6. If confidence < 0.5 → abort
    ↓
Return execution summary
```

**Current Issues:**

- ❌ Vision verification is unreliable (low confidence)
- ❌ Threading issues with screen capture (FIXED)
- ❌ Aborts too easily on low confidence

### 5. Action Execution

**Files:** `src/control/executor.py`, `src/control/system.py`, `src/control/keyboard.py`, `src/control/mouse.py`

#### open_app Action:

```
executor._execute_open_app(action)
    ↓
system.open_app(app_name)
    ↓
1. Check if app in common_apps dict
   → If YES: Launch directly (e.g., "notepad.exe")
2. If direct launch fails:
   → Use Windows search (Win+S, type, Enter)
```

**Current Issues:**

- ❌ WhatsApp wasn't in common_apps (FIXED)
- ❌ Windows search fallback sometimes fails
- ✅ Direct launch works for common apps

#### type Action:

```
executor._execute_type(action)
    ↓
keyboard.type_text(text)
    ↓
Uses pyautogui to type character by character
```

#### click Action:

```
executor._execute_click(action)
    ↓
1. Try browser click if target specified
2. Try mouse click if coordinates specified
3. Try click_at_text if text target specified
```

## Key Problems Identified

### Problem 1: Vision Verification Too Strict

**Impact:** Actions succeed but get marked as failed due to low confidence
**Solution Options:**

1. Lower confidence threshold from 0.5 to 0.3
2. Make verification optional for certain action types
3. Use simpler verification (just check if screen changed)

### Problem 2: Plan Granularity

**Impact:** Simple tasks broken into too many steps
**Solution:** Better prompts to Gemini to use single actions (PARTIALLY FIXED)

### Problem 3: Error Recovery

**Impact:** One failed step aborts entire plan
**Solution Options:**

1. Retry failed steps
2. Continue with remaining steps
3. Ask user for guidance

### Problem 4: App Detection

**Impact:** Can't find/launch apps not in common_apps
**Solution:** Expand common_apps list, improve Windows search

## Recommended Improvements

### Priority 1: Fix Vision Verification

```python
# In executor.py, make verification less strict:
if result["confidence"] < 0.3:  # Changed from 0.5
    abort()

# Or skip verification for certain actions:
if action.type in ["open_app", "press_key"]:
    skip_verification = True
```

### Priority 2: Better Error Messages

```python
# Show user what actually happened:
"❌ Step failed: Typed 'Notepad' but couldn't verify it appeared"
# Instead of just:
"❌ Step failed: Typed: Notepad"
```

### Priority 3: Retry Logic

```python
# Retry failed steps up to 2 times:
for attempt in range(3):
    result = execute_action(step)
    if result["success"]:
        break
```

### Priority 4: Learned Tools Integration

- Save successful workflows
- Reuse them for similar tasks
- Skip planning for known tasks

## Current Success Rate

Based on testing:

- ✅ Simple apps (notepad, calculator): ~60% success
- ❌ Complex apps (WhatsApp): ~20% success
- ❌ Multi-step tasks: ~30% success

Main failure point: **Vision verification** (too strict)

## Next Steps

1. Lower confidence threshold
2. Add retry logic
3. Improve app detection
4. Better error messages
5. Test with real tasks
