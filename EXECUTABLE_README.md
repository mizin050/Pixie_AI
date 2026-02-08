# Pixie AI - Executable Version

## What was built

Your Pixie AI application has been compiled into a standalone executable: **PixieAI.exe**

## Location

The executable is located in: `dist/PixieAI.exe`

## File Size

Approximately 72 MB (includes Python runtime and all dependencies)

## How to Use

1. **Run the executable**: Double-click `PixieAI.exe` in the `dist` folder
2. **System tray**: The app will start minimized in your system tray (look for the fox icon)
3. **Menu options**:
   - **Pixie UI**: Click to open/close the chat interface and fox window
   - **Mic**: Toggle voice input on/off
   - **Quit**: Exit the application

## Important Notes

- The `.env` file with your API keys is embedded in the executable
- The executable is portable - you can copy the `PixieAI.exe` file to any Windows computer
- No Python installation required on the target machine
- First launch may be slower as Windows scans the file

## Troubleshooting

If the executable doesn't start:

1. Check Windows Defender/antivirus - it may flag the exe as suspicious (false positive)
2. Run as administrator if needed
3. Make sure your `.env` file was present during build

## Rebuilding

To rebuild the executable after making changes:

```batch
build_exe.bat
```

Or manually:

```batch
pyinstaller pixie.spec --clean
```

## What's Included

- Main application (main.py)
- Chat interface (pixie_web_chat.py)
- Fox image window (fox_image.py)
- AI integration (groq_ai.py)
- Speech recognition (speech_to_text.py)
- Voice output (voice_player.py)
- All assets (fox.png, chat.html)
- Environment variables (.env)
