# Pixie Desktop Operator - Implementation Roadmap

## Current Status

✅ Basic chat UI (WhatsApp-style)
✅ Gemini API integration
✅ Voice input/output
✅ Simple memory system
✅ System tray integration

## What We're Building Next

Transform Pixie into a full desktop AI operator with vision, control, and safety systems.

---

## Phase 1: Core Brain & Planning (Week 1)

### Goals

- Structured decision-making
- Task decomposition
- JSON schema validation
- Retry logic

### Tasks

#### 1.1 Brain Module

**File**: `src/agent/brain.py`

- [ ] Create Gemini client wrapper
- [ ] Implement structured output validation
- [ ] Add retry logic for API failures
- [ ] Create decision schema

#### 1.2 Planner Module

**File**: `src/agent/planner.py`

- [ ] Goal → Steps decomposition
- [ ] Step validation
- [ ] Re-planning logic
- [ ] Progress tracking

#### 1.3 Decision Engine

**File**: `src/agent/decision.py`

- [ ] Action selection logic
- [ ] Context building
- [ ] Confidence estimation
- [ ] Risk assessment

#### 1.4 Evaluator

**File**: `src/agent/evaluator.py`

- [ ] Success/failure detection
- [ ] Screen state comparison
- [ ] Error detection
- [ ] Completion verification

### Deliverables

- Working brain that can plan multi-step tasks
- JSON-validated decisions
- Basic retry logic
- Test suite for planning

### Testing

```python
# Test case
goal = "Open Chrome and go to gmail.com"
plan = planner.create_plan(goal)
assert len(plan.steps) >= 2
assert plan.steps[0].action == "open_app"
assert plan.steps[1].action == "navigate"
```

---

## Phase 2: Vision System (Week 2)

### Goals

- Screen capture
- Text extraction
- UI state detection
- Vision summaries

### Tasks

#### 2.1 Screen Capture

**File**: `src/vision/capture.py`

- [ ] Full screen capture (mss)
- [ ] Active window capture
- [ ] Region capture
- [ ] Multi-monitor support

#### 2.2 OCR Integration

**File**: `src/vision/ocr.py`

- [ ] Tesseract integration
- [ ] Text extraction
- [ ] Coordinate mapping
- [ ] Confidence scoring

#### 2.3 UI Detection

**File**: `src/vision/ui_detect.py`

- [ ] Error message detection
- [ ] Login prompt detection
- [ ] Button/input detection
- [ ] Loading state detection

#### 2.4 Vision Summary

**File**: `src/vision/vision_summary.py`

- [ ] Compact screen descriptions
- [ ] Relevant element extraction
- [ ] State change detection
- [ ] Gemini-optimized format

### Deliverables

- Fast screen capture (<100ms)
- Accurate OCR (>90% accuracy)
- Reliable UI state detection
- Compact vision summaries

### Testing

```python
# Test case
screen = capture_screen()
text = extract_text(screen)
state = detect_ui_state(screen)
summary = create_summary(screen)
assert len(summary) < 500  # Compact
assert "error" in state or "success" in state
```

---

## Phase 3: Control Layer (Week 3)

### Goals

- Browser automation (Playwright)
- Mouse/keyboard control
- Hybrid control logic
- Action execution

### Tasks

#### 3.1 Playwright Integration

**File**: `src/browser/playwright_ctrl.py`

- [ ] Browser launch
- [ ] Navigation
- [ ] Element interaction
- [ ] Page state extraction

#### 3.2 Mouse Control

**File**: `src/control/mouse.py`

- [ ] Click at coordinates
- [ ] Click at text
- [ ] Drag and drop
- [ ] Scroll

#### 3.3 Keyboard Control

**File**: `src/control/keyboard.py`

- [ ] Type text
- [ ] Keyboard shortcuts
- [ ] Special keys
- [ ] Clipboard operations

#### 3.4 System Control

**File**: `src/control/system.py`

- [ ] Launch applications
- [ ] Window management
- [ ] File operations
- [ ] System commands

#### 3.5 Hybrid Controller

**File**: `src/control/hybrid.py`

- [ ] Browser vs desktop detection
- [ ] Automatic fallback
- [ ] Action routing
- [ ] Error handling

### Deliverables

- Reliable browser control
- Accurate mouse/keyboard control
- Smart hybrid switching
- Comprehensive action library

### Testing

```python
# Test case
browser = launch_browser()
browser.navigate("https://google.com")
browser.type("input[name='q']", "test")
browser.click("button[name='btnK']")
assert "test" in browser.get_url()
```

---

## Phase 4: Safety Systems (Week 4)

### Goals

- Confidence scoring
- Permission system
- Risk classification
- Retry & recovery

### Tasks

#### 4.1 Confidence Scoring

**File**: `src/agent/confidence.py`

- [ ] Multi-factor scoring
- [ ] Threshold logic
- [ ] Score tracking
- [ ] Trend analysis

#### 4.2 Permission System

**File**: `src/control/permissions.py`

- [ ] Risk level classification
- [ ] Permission requests
- [ ] User approval flow
- [ ] Decision logging

#### 4.3 Risk Classifier

**File**: `src/agent/risk_classifier.py`

- [ ] Action risk assessment
- [ ] Context-aware scoring
- [ ] User preference learning
- [ ] Override system

#### 4.4 Retry Logic

**File**: `src/agent/retry.py`

- [ ] Failure detection
- [ ] Retry strategies
- [ ] Backoff logic
- [ ] Escalation rules

### Deliverables

- Accurate confidence scores
- Working permission system
- Risk-aware execution
- Smart retry logic

### Testing

```python
# Test case
action = {"type": "delete_file", "path": "important.txt"}
risk = classify_risk(action)
assert risk == "HIGH"
approved = request_permission(action)
if approved:
    execute_action(action)
```

---

## Phase 5: Memory & Learning (Week 5)

### Goals

- Short-term task memory
- Long-term preferences
- Pattern learning
- Context retention

### Tasks

#### 5.1 Short-Term Memory

**File**: `src/memory/short_term.py`

- [ ] Current task state
- [ ] Recent observations
- [ ] Active context
- [ ] Failure tracking

#### 5.2 Task Memory

**File**: `src/memory/task_memory.py`

- [ ] Step history
- [ ] Retry counts
- [ ] Success patterns
- [ ] Failure analysis

#### 5.3 Long-Term Memory

**File**: `src/memory/long_term.py`

- [ ] User preferences
- [ ] Common patterns
- [ ] Learned shortcuts
- [ ] App locations

#### 5.4 Context Builder

**File**: `src/memory/context.py`

- [ ] Relevant history extraction
- [ ] Context prioritization
- [ ] Token optimization
- [ ] Memory pruning

### Deliverables

- Fast memory access
- Persistent preferences
- Pattern recognition
- Optimized context

### Testing

```python
# Test case
memory.add_preference("email_client", "gmail")
memory.add_pattern("send_email", ["open_gmail", "compose", "send"])
context = memory.build_context("send email")
assert "gmail" in context
```

---

## Phase 6: UI Polish (Week 6)

### Goals

- WhatsApp-style chat refinement
- Permission modals
- Status indicators
- Voice integration polish

### Tasks

#### 6.1 Chat UI Enhancement

**File**: `src/ui/chat_view.py`

- [ ] Smooth animations
- [ ] Typing indicators
- [ ] Confidence badges
- [ ] Screenshot attachments

#### 6.2 Permission Modals

**File**: `src/ui/permissions_modal.py`

- [ ] Modal dialogs
- [ ] Risk visualization
- [ ] Approval buttons
- [ ] History view

#### 6.3 Status System

**File**: `src/ui/status.py`

- [ ] Task progress
- [ ] Step indicators
- [ ] Error notifications
- [ ] Success confirmations

#### 6.4 Voice Polish

**File**: `src/ui/voice_ui.py`

- [ ] Voice activity indicator
- [ ] Waveform visualization
- [ ] Voice settings
- [ ] TTS controls

### Deliverables

- Polished chat interface
- Intuitive permission system
- Clear status feedback
- Enhanced voice experience

### Testing

- User testing with 5+ users
- UI responsiveness <16ms
- Animation smoothness 60fps
- Accessibility compliance

---

## Dependencies to Install

```bash
# Phase 1
pip install google-generativeai pydantic

# Phase 2
pip install mss pytesseract easyocr pillow

# Phase 3
pip install playwright pyautogui keyboard

# Phase 4
# (uses existing dependencies)

# Phase 5
# (uses existing dependencies)

# Phase 6
pip install PySide6
```

---

## Success Criteria

### Phase 1

- [ ] Can plan 5-step tasks
- [ ] JSON validation 100% accurate
- [ ] Retry logic works

### Phase 2

- [ ] Screen capture <100ms
- [ ] OCR accuracy >90%
- [ ] UI detection >85% accurate

### Phase 3

- [ ] Browser control 100% reliable
- [ ] Mouse/keyboard <50ms latency
- [ ] Hybrid switching works

### Phase 4

- [ ] Confidence scores accurate
- [ ] Permission system blocks risky actions
- [ ] Retry success rate >70%

### Phase 5

- [ ] Memory access <10ms
- [ ] Pattern recognition works
- [ ] Context stays under token limit

### Phase 6

- [ ] UI feels native
- [ ] Animations smooth
- [ ] User satisfaction >4.5/5

---

## Timeline

| Phase     | Duration    | Start  | End    |
| --------- | ----------- | ------ | ------ |
| Phase 1   | 1 week      | Week 1 | Week 1 |
| Phase 2   | 1 week      | Week 2 | Week 2 |
| Phase 3   | 1 week      | Week 3 | Week 3 |
| Phase 4   | 1 week      | Week 4 | Week 4 |
| Phase 5   | 1 week      | Week 5 | Week 5 |
| Phase 6   | 1 week      | Week 6 | Week 6 |
| **Total** | **6 weeks** |        |        |

---

## Ready to Start?

Say "start phase 1" and I'll begin implementing the core brain and planning system.
