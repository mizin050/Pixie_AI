# 📚 Learned Tools - Pixie Gets Smarter!

## What Are Learned Tools?

When Pixie successfully completes a task, it **saves the workflow** as a "learned tool" that can be reused later. This makes repeated tasks **much faster**!

---

## How It Works

### First Time (Learning):

1. You: `send whatsapp message to John saying hello`
2. Pixie: Creates plan, executes, verifies (takes ~15s)
3. ✅ Success! Pixie saves this as a learned tool
4. 📚 Stored: "send_whatsapp_message_john_saying_hello"

### Next Time (Using Learned Tool):

1. You: `send whatsapp message to John saying hi again`
2. Pixie: "I know how to do this!" (uses learned tool)
3. ⚡ Executes faster (~10s) - no planning needed!
4. 📈 Updates success rate

---

## Benefits

### Speed Improvements:

- **First time**: ~15-20s (planning + execution)
- **Second time**: ~10-12s (just execution)
- **Third time**: ~8-10s (optimized execution)

### Reliability:

- Tracks success rate for each tool
- Only saves workflows with >70% confidence
- Updates based on repeated use

### Intelligence:

- Finds similar tools for related tasks
- Learns your patterns
- Gets better over time

---

## What Gets Saved

For each successful workflow:

```json
{
  "goal": "send whatsapp message to John",
  "steps": [
    { "action": "Click WhatsApp search", "confidence": 0.85 },
    { "action": "Type John", "confidence": 0.9 },
    { "action": "Click contact", "confidence": 0.8 },
    { "action": "Type message", "confidence": 0.95 },
    { "action": "Press Enter", "confidence": 0.9 }
  ],
  "execution_time": 12.5,
  "confidence": 0.88,
  "use_count": 3,
  "success_rate": 1.0
}
```

---

## Commands

### View Learned Tools:

```
tools
```

or

```
show tools
```

### Example Output:

```
📚 Learned Tools (5 total)

• send whatsapp message to John
  Used: 5 times | Success: 100% | Time: ~12s

• open notepad and type hello
  Used: 3 times | Success: 100% | Time: ~5s

• open chrome and go to gmail.com
  Used: 2 times | Success: 100% | Time: ~10s
```

---

## Examples

### Example 1: WhatsApp Messages

**First time**:

```
You: send whatsapp message to Mom saying I'll be late
Pixie: [Creates plan, executes] ✅ Success! (15s)
      📚 Saved as learned tool
```

**Second time**:

```
You: send whatsapp message to Mom saying I'm on my way
Pixie: [Uses learned tool] ⚡ Done! (10s)
      📚 Updated tool (used 2 times)
```

**Speed improvement**: 33% faster!

### Example 2: Opening Apps

**First time**:

```
You: open notepad and type hello world
Pixie: [Plans and executes] ✅ Success! (8s)
      📚 Saved as learned tool
```

**Second time**:

```
You: open notepad and type testing
Pixie: [Uses learned tool] ⚡ Done! (5s)
```

**Speed improvement**: 38% faster!

---

## Smart Matching

Pixie can find similar tools even if the command isn't exact:

**Learned**: `send whatsapp message to John saying hello`

**Will match**:

- `send whatsapp to John` (similar keywords)
- `message John on whatsapp` (same intent)
- `whatsapp John hello` (key words match)

**Won't match**:

- `send email to John` (different app)
- `call John` (different action)

---

## Storage

Learned tools are saved in:

```
AI-Assistant-for-Computer/learned_tools.json
```

You can:

- ✅ View the file to see what's learned
- ✅ Edit it manually if needed
- ✅ Delete it to start fresh
- ✅ Back it up to save your learning

---

## Statistics

After using Pixie for a while:

```
📊 Your Learned Tools Stats:

Total tools: 15
Total uses: 47
Average success rate: 94%
Time saved: ~3.5 minutes

Most used:
1. send whatsapp message (12 times)
2. open notepad (8 times)
3. open chrome (7 times)
```

---

## Tips

### 1. Be Consistent

Use similar phrasing for the same tasks:

- ✅ Good: "send whatsapp to John"
- ✅ Good: "send whatsapp to John" (again)
- ❌ Less optimal: "message John via whatsapp"

### 2. Let It Learn

The more you use Pixie, the smarter it gets:

- First use: Learning
- 2-3 uses: Optimizing
- 4+ uses: Mastered!

### 3. Check Your Tools

Periodically type `tools` to see what Pixie has learned

### 4. High Success Rate

Only workflows with >70% confidence are saved as tools

---

## Future Enhancements

Coming soon:

- 🔄 Tool sharing (export/import)
- 🎯 Tool categories
- 📈 Performance analytics
- 🤖 Auto-optimization
- 🔗 Tool chaining (combine multiple tools)

---

## How This Makes Pixie Faster

### Without Learned Tools:

```
Command → Plan (3s) → Execute (12s) → Verify (2s) = 17s
```

### With Learned Tools:

```
Command → Use Tool (0s) → Execute (10s) → Verify (1s) = 11s
```

**Result**: 35% faster on average!

---

## Real-World Impact

**Scenario**: Send 10 WhatsApp messages

**Without learning**:

- 10 × 15s = 150 seconds (2.5 minutes)

**With learning**:

- First: 15s (learning)
- Next 9: 9 × 10s = 90s
- **Total**: 105 seconds (1.75 minutes)

**Time saved**: 45 seconds (30% faster)

---

**Pixie learns from every success and gets faster over time!** 🚀📚

Try it: Do the same task twice and watch Pixie get smarter! 🦊
