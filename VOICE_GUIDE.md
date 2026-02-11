# Voice Interaction Guide

## How It Works

Pixie now has smart voice responses:

### Voice Input → Voice Output

When you talk to Pixie using the microphone:

- 🎤 You speak
- 🤖 Pixie responds with **voice** (text-to-speech)

### Text Input → Text Output

When you type in the chat UI:

- ⌨️ You type
- 💬 Pixie responds with **text only** (no voice)

## Using Voice Mode

1. **Enable Microphone**
   - Right-click the Pixie icon in system tray
   - Click "Mic" to turn it on
   - Speak your question

2. **Pixie Listens**
   - Wait for "🎙 I'm listening..."
   - Speak clearly within 5 seconds

3. **Pixie Responds**
   - You'll hear the response spoken back
   - Response also appears in console

## Using Text Mode

1. **Open UI**
   - Right-click Pixie icon
   - Click "Pixie UI"
   - Or say "Pixie UI" when mic is on

2. **Type Your Message**
   - Type in the chat box
   - Press Enter or click send button

3. **Read Response**
   - Response appears as text
   - No voice output in text mode

## Voice Commands

Special commands you can say:

- **"Pixie UI"** - Opens the chat window
- Any other question - Gets a spoken response

## Adjusting Voice Settings

The voice speed and volume can be adjusted in `src/utils/speech.py`:

```python
tts_engine.setProperty('rate', 175)    # Speed (default: 175)
tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
```

## Troubleshooting

### Voice not working

- Check your speakers are on
- Verify Windows audio is working
- Try restarting Pixie

### Voice too fast/slow

- Edit `src/utils/speech.py`
- Change the `rate` value (100-300)
- Lower = slower, Higher = faster

### Voice too quiet/loud

- Edit `src/utils/speech.py`
- Change the `volume` value (0.0-1.0)
- 0.0 = silent, 1.0 = maximum
