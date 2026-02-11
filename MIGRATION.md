# Migration Guide

## What Changed?

The codebase has been reorganized into a clean, modular structure. All functionality remains the same, but files have been moved and renamed.

## File Mapping

### Moved Files

| Old Location            | New Location             |
| ----------------------- | ------------------------ |
| `groq_ai.py`            | `src/core/ai_engine.py`  |
| `chat_memory_mem0.py`   | `src/core/memory.py`     |
| `pixie_web_chat.py`     | `src/ui/chat_window.py`  |
| `chat.html`             | `src/ui/chat.html`       |
| `speech_to_text.py`     | `src/utils/speech.py`    |
| `vision_handler.py`     | `src/utils/vision.py`    |
| `document_processor.py` | `src/utils/documents.py` |
| `file_tools.py`         | `src/utils/files.py`     |

### Deleted Files (Unused)

- `recognition.py` - Duplicate of speech_to_text.py
- `voice_player.py` - Unused voice output
- `chat_memory.py` - Replaced by mem0 version
- `pixie_pygame.py` - Unused pygame implementation
- `test_vision.py` - Test file
- `test_webview_api.py` - Test file
- `chat_backup.html` - Backup file
- `chat_enhanced.html` - Unused variant
- `chat_debug.html` - Debug file

## Import Changes

### Old Imports

```python
from groq_ai import get_response
from chat_memory_mem0 import ChatMemoryMem0
from pixie_web_chat import create_chat_window
from speech_to_text import record_voice
from vision_handler import analyze_images
from document_processor import process_document
from file_tools import fs_tools
```

### New Imports

```python
from src.core.ai_engine import get_response
from src.core.memory import ChatMemoryMem0
from src.ui.chat_window import create_chat_window
from src.utils.speech import record_voice
from src.utils.vision import analyze_images
from src.utils.documents import process_document
from src.utils.files import fs_tools
```

## What You Need to Do

### If You're Using the Application

**Nothing!** Just run `python main.py` as before. Everything works the same.

### If You Have Custom Code

1. **Update imports** to use the new `src.` prefix
2. **Update file paths** if you reference specific files
3. **Remove references** to deleted files

### If You're Building the Executable

The `pixie.spec` file has been updated. Just run:

```bash
pyinstaller pixie.spec --clean
```

## Benefits of New Structure

✅ **Better organization** - Code is grouped logically
✅ **Easier maintenance** - Find files quickly
✅ **No duplicates** - Removed unused code
✅ **Professional** - Industry-standard structure
✅ **Scalable** - Easy to add new features

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:

1. Make sure you're running from the project root
2. Check that `src/` folder exists with all subfolders
3. Verify `__init__.py` files are present in each folder

### Missing Files

If files are missing:

1. Check the file mapping table above
2. Look in the new `src/` folder structure
3. Deleted files were unused - functionality is preserved

### Old Scripts Not Working

If you have custom scripts:

1. Update imports to use `src.` prefix
2. Run from project root directory
3. Check Python path includes project root

## Need Help?

- Check [STRUCTURE.md](STRUCTURE.md) for full project layout
- Read [README.md](README.md) for documentation
- See [SETUP.md](SETUP.md) for installation guide

---

**Migration completed successfully!** 🎉
