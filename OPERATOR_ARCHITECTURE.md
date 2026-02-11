# Pixie Desktop AI Operator - Production Architecture

## Vision

Transform Pixie from a chat assistant into a full desktop AI operator that can see, understand, and control your computer with human-like reasoning and safety.

## Core Principles

1. **Vision-First**: Every action is verified by seeing the screen
2. **Permission-Based**: User approves risky actions
3. **Confidence-Driven**: Self-aware of success probability
4. **Retry-Smart**: Learns from failures and adapts
5. **Human-Readable**: Clear communication, no technical spam

---

## Architecture Layers

### 1. BRAIN (Gemini API)

**Location**: `src/agent/brain.py`

**Responsibilities**:

- Send context to Gemini
- Enforce structured JSON responses
- Validate action schemas
- Handle API errors gracefully

**Input Format**:

```json
{
  "goal": "Send email to John",
  "current_step": 2,
  "screen_state": "Gmail inbox visible, 5 unread",
  "last_action": "clicked compose button",
  "last_result": "success",
  "failures": 0
}
```

**Output Format**:

```json
{
  "reasoning": "Compose button clicked, now need to enter recipient",
  "action": "type",
  "target": "To field",
  "value": "john@example.com",
  "confidence": 0.85,
  "risk_level": "LOW"
}
```

---

### 2. PLANNER (Task Decomposition)

**Location**: `src/agent/planner.py`

**Responsibilities**:

- Break goals into verifiable steps
- Store plan in task memory
- Re-plan when blocked
- Track progress

**Example Plan**:

```
Goal: "Send email to John about meeting"
Steps:
1. Open Chrome [LOW risk]
2. Navigate to gmail.com [LOW risk]
3. Click compose button [LOW risk]
4. Type recipient: john@example.com [LOW risk]
5. Type subject: Meeting [LOW risk]
6. Type body: ... [LOW risk]
7. Click send [MEDIUM risk - requires approval]
```

---

### 3. CONTROL LAYER

#### 3A. Browser Control (Playwright)

**Location**: `src/browser/playwright_ctrl.py`

**When to Use**:

- Browser is active
- DOM elements accessible
- Standard web interactions

**Capabilities**:

- Navigate URLs
- Click elements by selector
- Type into inputs
- Extract page text
- Take screenshots
- Handle iframes

**Example**:

```python
await browser.click('button[aria-label="Compose"]')
await browser.type('input[name="to"]', 'john@example.com')
```

#### 3B. Vision Control (Screen + OCR)

**Location**: `src/vision/capture.py`, `src/control/mouse.py`

**When to Use**:

- Desktop apps (not browser)
- CAPTCHAs
- Native dialogs
- Browser extensions
- Non-HTML UI

**Capabilities**:

- Capture screen regions
- OCR text extraction
- Click coordinates
- Keyboard shortcuts
- Detect UI states

**Example**:

```python
screen = capture_screen()
text = extract_text(screen)
if "Send" in text:
    click_at_text("Send")
```

---

### 4. VISION SYSTEM

#### 4A. Screen Capture

**Location**: `src/vision/capture.py`

**Tech**: `mss` (fast screen capture)

**Capabilities**:

- Full screen capture
- Active window only
- Specific region
- Multi-monitor support

#### 4B. OCR & Text Detection

**Location**: `src/vision/ocr.py`

**Tech**: `pytesseract` or `easyocr`

**Capabilities**:

- Extract all visible text
- Find text coordinates
- Detect buttons/labels
- Language support

#### 4C. UI State Detection

**Location**: `src/vision/ui_detect.py`

**Detects**:

- Error messages
- Login prompts
- Permission dialogs
- Loading states
- Success confirmations
- "Page not found"
- Network errors

**Example**:

```python
state = detect_ui_state(screen)
# Returns: {"type": "error", "message": "Connection failed", "confidence": 0.92}
```

#### 4D. Vision Summary

**Location**: `src/vision/vision_summary.py`

**Purpose**: Create compact screen descriptions for Gemini

**Example Output**:

```
Screen: Gmail inbox
Visible: 5 unread emails, compose button top-left, search bar top-right
Active: None
Errors: None
```

---

### 5. CONFIDENCE SCORING

**Location**: `src/agent/confidence.py`

**Scoring Factors**:

```python
confidence = 0.0

# Expected text found
if expected_text in screen_text:
    confidence += 0.4

# Correct app/window active
if correct_window_active():
    confidence += 0.3

# No error keywords detected
if not detect_errors(screen):
    confidence += 0.2

# Action completed quickly
if execution_time < 2.0:
    confidence += 0.1

return min(confidence, 1.0)
```

**Decision Thresholds**:

- `>= 0.85`: Auto-continue
- `0.60 - 0.84`: Cautious continue (log warning)
- `< 0.60`: Retry or ask user

---

### 6. PERMISSION SYSTEM

**Location**: `src/control/permissions.py`

**Risk Levels**:

**LOW** (auto-approve):

- Clicking
- Typing
- Browsing
- Reading files
- Taking screenshots

**MEDIUM** (requires approval):

- Downloading files
- Sending messages
- Posting online
- Installing software
- Copying files

**HIGH** (requires explicit approval + confirmation):

- Deleting files
- Running system commands
- Accessing credentials
- Modifying system settings
- Financial transactions

**Permission Flow**:

```
1. Agent requests action
2. System checks risk level
3. If MEDIUM/HIGH:
   - Pause execution
   - Show modal dialog
   - User approves/denies
   - Log decision
4. Continue or abort
```

**UI Modal**:

```
┌─────────────────────────────────┐
│  Permission Required            │
├─────────────────────────────────┤
│  Pixie wants to:                │
│  Send email to john@example.com │
│                                 │
│  Risk Level: MEDIUM             │
│                                 │
│  [Deny]  [Approve Once]  [Always]│
└─────────────────────────────────┘
```

---

### 7. MEMORY SYSTEM

#### 7A. Short-Term Memory

**Location**: `src/memory/short_term.py`

**Stores**:

- Current goal
- Current step
- Last 5 observations
- Active window
- Recent failures

**Lifetime**: Current task only

#### 7B. Task Memory

**Location**: `src/memory/task_memory.py`

**Stores**:

```json
{
  "task_id": "uuid",
  "goal": "Send email to John",
  "status": "in_progress",
  "steps": [
    {
      "step": 1,
      "action": "open_chrome",
      "result": "success",
      "confidence": 0.95,
      "timestamp": "2025-01-01T10:00:00"
    }
  ],
  "retries": 2,
  "failures": ["step 3: compose button not found"]
}
```

#### 7C. Long-Term Memory

**Location**: `src/memory/long_term.json`

**Stores**:

- User preferences
- Common patterns
- Learned shortcuts
- Frequent contacts
- App locations

---

### 8. MAIN AGENT LOOP

**Location**: `main.py`

**Flow**:

```python
while task_active:
    # 1. Get current state
    screen = capture_screen()
    screen_summary = summarize_screen(screen)

    # 2. Decide next action
    context = build_context(goal, step, screen_summary, memory)
    decision = brain.decide(context)

    # 3. Check permissions
    if decision.risk_level in ["MEDIUM", "HIGH"]:
        approved = request_permission(decision)
        if not approved:
            abort_task()
            break

    # 4. Execute action
    result = execute_action(decision)

    # 5. Observe result
    new_screen = capture_screen()
    success = evaluate_success(decision, new_screen)
    confidence = calculate_confidence(decision, new_screen, success)

    # 6. Update memory
    memory.add_step(decision, result, confidence)

    # 7. Decide next step
    if success and confidence > 0.85:
        move_to_next_step()
    elif retries < 3:
        retry_with_adjustment()
    else:
        replan_or_escalate()
```

---

### 9. UI DESIGN (WhatsApp Style)

**Tech Stack**: PySide6 (Qt for Python)

**Layout**:

```
┌─────────────────────────────────┐
│ 🦊 Pixie                    ⚙️  │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────┐   │
│  │ Opening Chrome...       │   │
│  └─────────────────────────┘   │
│                                 │
│              ┌────────────────┐ │
│              │ Send email to  │ │
│              │ john@example   │ │
│              └────────────────┘ │
│                                 │
│  ┌─────────────────────────┐   │
│  │ ✓ Email sent            │   │
│  │ Confidence: 95%         │   │
│  └─────────────────────────┘   │
│                                 │
├─────────────────────────────────┤
│ 💬 Type a command...        🎤 │
└─────────────────────────────────┘
```

**Message Types**:

1. **User messages** (right, orange bubble)
2. **Agent status** (left, white bubble)
3. **Action confirmations** (left, green bubble)
4. **Permission requests** (center, yellow modal)
5. **Errors** (left, red bubble)

**Features**:

- Smooth animations
- Typing indicators
- Confidence badges
- Action history
- Screenshot attachments
- Voice input button

---

### 10. IMPLEMENTATION PHASES

#### Phase 1: Core Brain (Week 1)

- [ ] Gemini API integration
- [ ] JSON schema validation
- [ ] Basic planner
- [ ] Simple decision logic

#### Phase 2: Vision System (Week 2)

- [ ] Screen capture
- [ ] OCR integration
- [ ] UI state detection
- [ ] Vision summaries

#### Phase 3: Control Layer (Week 3)

- [ ] Playwright browser control
- [ ] Mouse/keyboard control
- [ ] Hybrid decision logic
- [ ] Action execution

#### Phase 4: Safety Systems (Week 4)

- [ ] Confidence scoring
- [ ] Permission system
- [ ] Risk classification
- [ ] Retry logic

#### Phase 5: Memory & Learning (Week 5)

- [ ] Short-term memory
- [ ] Task memory
- [ ] Long-term preferences
- [ ] Pattern learning

#### Phase 6: UI Polish (Week 6)

- [ ] WhatsApp-style chat
- [ ] Permission modals
- [ ] Status indicators
- [ ] Voice integration

---

## Success Metrics

### Reliability

- Task completion rate: >85%
- Average retries per task: <2
- False positive rate: <5%

### Safety

- Unauthorized actions: 0
- User intervention rate: <10%
- Permission approval rate: >90%

### Performance

- Average task time: <30s
- Screen capture latency: <100ms
- Decision latency: <2s

### User Experience

- User satisfaction: >4.5/5
- Daily active usage: >3 tasks/day
- Feature adoption: >80%

---

## Comparison to OpenAI Operator

| Feature              | Pixie   | OpenAI Operator |
| -------------------- | ------- | --------------- |
| Vision-based control | ✅      | ✅              |
| Browser automation   | ✅      | ✅              |
| Desktop app control  | ✅      | ✅              |
| Permission system    | ✅      | ✅              |
| Confidence scoring   | ✅      | ✅              |
| Retry logic          | ✅      | ✅              |
| Local-first          | ✅      | ❌              |
| Open source          | ✅      | ❌              |
| Custom prompts       | ✅      | ❌              |
| Offline mode         | Partial | ❌              |

**Pixie Advantages**:

- Fully local control
- Customizable prompts
- Open source
- No cloud dependency (except Gemini API)
- Full transparency

**Operator Advantages**:

- Massive training data
- Proprietary vision models
- Cloud infrastructure
- Professional support

---

## Next Steps

1. Review this architecture
2. Approve implementation phases
3. Start with Phase 1 (Core Brain)
4. Iterate based on testing

This is your production blueprint. Let's build it.
