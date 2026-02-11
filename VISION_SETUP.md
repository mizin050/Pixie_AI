# 🖼️ Vision Setup Guide - FREE Option!

## ✨ Free Vision with Ollama + LLaVA

Pixie can analyze images completely FREE using Ollama with the LLaVA vision model!

### 📥 Installation (5 minutes)

#### Step 1: Install Ollama

1. Go to https://ollama.ai
2. Download for Windows
3. Run the installer
4. Ollama will start automatically in the background

#### Step 2: Download LLaVA Model

Open Command Prompt or PowerShell and run:

```bash
ollama pull llava
```

This downloads the LLaVA vision model (~4.5GB). Wait for it to complete.

#### Step 3: Test It

```bash
ollama run llava
```

Type a message and press Enter. If it responds, you're ready!

### 🚀 Using Vision in Pixie

1. **Start Pixie** (Ollama runs automatically in background)
2. **Upload an image** using the + button
3. **Ask questions** like:
   - "What's in this image?"
   - "Describe what you see"
   - "What color is the object?"

That's it! Completely free, runs on your computer!

---

## 💰 Alternative: OpenAI (Paid)

If you prefer OpenAI's GPT-4 Vision (more accurate but costs money):

### Setup:

1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
```

3. Install: `pip install openai`

### Pricing:

- ~$0.01 per image analysis
- Requires credit card on file

---

## 🔄 How Pixie Chooses

Pixie tries vision providers in this order:

1. **Groq** (if vision models available) - Free
2. **Ollama** (LLaVA) - Free, local
3. **OpenAI** (GPT-4 Vision) - Paid, cloud

---

## 🛠️ Troubleshooting

### "Ollama not running"

- Make sure Ollama is installed
- Check if it's running: `ollama list`
- Restart Ollama: Close and reopen the Ollama app

### "Model not found"

- Run: `ollama pull llava`
- Wait for download to complete

### Slow responses

- First run is slower (loading model)
- Subsequent runs are faster
- LLaVA runs on your GPU if available

### Out of memory

- LLaVA needs ~8GB RAM
- Close other applications
- Or use smaller model: `ollama pull llava:7b`

---

## 📊 Comparison

| Feature  | Ollama (LLaVA) | OpenAI GPT-4V |
| -------- | -------------- | ------------- |
| Cost     | FREE           | ~$0.01/image  |
| Speed    | Medium         | Fast          |
| Accuracy | Good           | Excellent     |
| Privacy  | Local          | Cloud         |
| Setup    | 5 minutes      | 2 minutes     |
| Internet | Not required   | Required      |

---

## 🎯 Recommended Setup

**For most users**: Use **Ollama + LLaVA** (free!)

**For best accuracy**: Use **OpenAI** (if you don't mind paying)

**For privacy**: Use **Ollama** (everything stays on your computer)

---

## 📝 Example Usage

```
You: *uploads screenshot*
You: "What's in this image?"

Pixie: "I can see a Windows desktop with a code editor open.
The code appears to be Python, and there's a file explorer
on the left side showing a project structure..."
```

---

**Enjoy FREE vision with Pixie! 🦊👁️✨**
