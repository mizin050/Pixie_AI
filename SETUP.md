# Quick Setup Guide

## Prerequisites

- Python 3.8 or higher
- Microphone (for voice input)
- Internet connection

## Step-by-Step Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users**: If PyAudio installation fails, download the wheel file:

- Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Download the appropriate `.whl` file for your Python version
- Install: `pip install PyAudio‑0.2.11‑cp3XX‑cp3XX‑win_amd64.whl`

### 2. Get Groq API Key

1. Visit https://console.groq.com
2. Sign up for a free account
3. Generate an API key
4. Copy the key

### 3. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your API key
# GROQ_API_KEY=your_actual_key_here
```

### 4. Run the Assistant

```bash
python main.py
```

The assistant will appear in your system tray!

## Optional: Enable Free Vision

### Using Ollama (Recommended - Free & Local)

1. **Install Ollama**
   - Windows/Mac: Download from https://ollama.ai
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`

2. **Download Vision Model**

   ```bash
   ollama pull llava
   ```

3. **Start Ollama** (usually starts automatically)
   ```bash
   ollama serve
   ```

Now you can upload images in the chat!

### Using OpenAI (Paid)

1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

## Usage

### System Tray Menu

Right-click the Pixie icon in your system tray:

- **Pixie UI**: Open/close chat window
- **Mic**: Enable/disable voice control
- **Quit**: Exit application

### Voice Control

1. Click "Mic" in system tray
2. Speak naturally when you see "🎙 I'm listening..."
3. Say "Pixie UI" to open the chat window

### Chat Interface

- Type messages or click the mic button
- Upload files by clicking the 📎 button
- Drag and drop images/documents
- View history and clear when needed

## Troubleshooting

### "GROQ_API_KEY not found"

- Make sure `.env` file exists in the project root
- Check that the key is correctly formatted (no quotes needed)
- Restart the application after editing `.env`

### Microphone not working

- Check system microphone permissions
- Test microphone in other applications
- Try adjusting `phrase_time_limit` in `src/utils/speech.py`

### Import errors

- Ensure you're in the project root directory
- Verify all dependencies installed: `pip list`
- Try reinstalling: `pip install -r requirements.txt --force-reinstall`

### Chat window not opening

- Check console for error messages
- Verify `src/ui/chat.html` exists
- Try running directly: `python src/ui/chat_window.py`

## Next Steps

- Read [FILE_ACCESS_GUIDE.md](FILE_ACCESS_GUIDE.md) for file system features
- Read [VISION_SETUP.md](VISION_SETUP.md) for vision capabilities
- Check [README.md](README.md) for full documentation

## Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all prerequisites are met
3. Try the troubleshooting steps above
4. Open an issue on GitHub with error details
