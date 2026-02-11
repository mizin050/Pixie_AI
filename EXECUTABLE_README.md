# Pixie AI - Executable Version

## Building the Executable

To create a standalone executable:

```bash
pyinstaller pixie.spec --clean
```

The executable will be created in the `dist/` folder.

## What Gets Included

- Main application (main.py)
- All source code from `src/` folder:
  - Core AI engine and memory
  - UI components (chat window and HTML)
  - Utilities (speech, vision, documents, files)
- Assets (fox.png icon)
- Environment variables (.env file)
- Python runtime and all dependencies

## Running the Executable

1. **Double-click** `dist/PixieAI.exe`
2. Look for the **fox icon** in your system tray
3. **Right-click** the icon to access:
   - **Pixie UI**: Open/close chat window
   - **Mic**: Enable/disable voice control
   - **Quit**: Exit application

## Distribution

The executable is portable and can be copied to any Windows computer without requiring Python installation.

**File size**: ~70-80 MB (includes Python runtime)

## Important Notes

### API Keys

- Your `.env` file is embedded in the executable
- Make sure `.env` exists with valid API keys before building
- Don't share the executable if it contains sensitive keys

### First Launch

- Windows may scan the file (slower first start)
- Antivirus might flag it as suspicious (false positive)
- Run as administrator if needed

### Requirements on Target Machine

- Windows 10/11 (64-bit)
- No Python installation needed
- Microphone for voice input
- Internet connection for AI features

## Troubleshooting

### Executable won't start

1. Check Windows Defender/antivirus settings
2. Verify `.env` file was present during build
3. Try running as administrator
4. Check console output by running from command prompt

### Missing features

1. Rebuild with `--clean` flag
2. Verify all source files are in `src/` folder
3. Check `pixie.spec` includes all necessary files

### Large file size

- This is normal - includes Python runtime
- Use UPX compression in spec file to reduce size
- Remove unused dependencies from requirements.txt

## Updating the Spec File

Edit `pixie.spec` to customize the build:

```python
# Add data files
datas=[
    ('src', 'src'),
    ('fox.png', '.'),
    ('.env', '.'),
],

# Add hidden imports if needed
hiddenimports=[
    'src.core.ai_engine',
    'src.ui.chat_window',
    # ... other modules
],
```

## Build Script

For convenience, use the build script:

```bash
# Windows
build_exe.bat

# Or manually
pyinstaller pixie.spec --clean --noconfirm
```

## What's New in Organized Structure

The codebase is now organized into logical modules:

- `src/core/` - AI engine and memory
- `src/ui/` - User interface components
- `src/utils/` - Utility functions

This makes the code easier to maintain and extend.

---

**Note**: Always test the executable on a clean machine before distribution!
