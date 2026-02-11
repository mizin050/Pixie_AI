# Project Structure

## Overview

The Pixie AI Assistant codebase has been reorganized into a clean, modular structure for better maintainability and scalability.

## Directory Layout

```
AI-Assistant-for-Computer/
│
├── main.py                      # Application entry point
│
├── src/                         # Source code
│   ├── __init__.py
│   │
│   ├── core/                    # Core AI functionality
│   │   ├── __init__.py
│   │   ├── ai_engine.py        # Main AI logic with Groq API
│   │   └── memory.py           # Chat memory with Mem0
│   │
│   ├── ui/                      # User interface
│   │   ├── __init__.py
│   │   ├── chat_window.py      # Web-based chat interface
│   │   └── chat.html           # Chat UI template
│   │
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── speech.py           # Speech-to-text
│       ├── vision.py           # Image analysis
│       ├── documents.py        # Document processing
│       └── files.py            # File system tools
│
├── fox.png                      # Application icon
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
│
├── requirements.txt             # Python dependencies
├── pixie.spec                   # PyInstaller spec file
├── build_exe.bat               # Build script
│
├── README.md                    # Main documentation
├── SETUP.md                     # Quick setup guide
├── STRUCTURE.md                 # This file
├── EXECUTABLE_README.md         # Executable build guide
├── FILE_ACCESS_GUIDE.md         # File system features
└── VISION_SETUP.md              # Vision capabilities setup
```

## Module Descriptions

### Core Modules

#### `src/core/ai_engine.py`

- Main AI interaction logic
- Groq API integration
- Model selection and management
- File command processing
- Image and document handling

#### `src/core/memory.py`

- Persistent chat history
- Mem0 integration for semantic memory
- Context retrieval
- History search functionality

### UI Modules

#### `src/ui/chat_window.py`

- Web-based chat interface using pywebview
- File upload handling
- API bridge between JavaScript and Python
- Window management

#### `src/ui/chat.html`

- Modern chat interface
- File drag-and-drop
- Message history display
- Responsive design

### Utility Modules

#### `src/utils/speech.py`

- Speech-to-text using Google Speech Recognition
- Microphone input handling
- Ambient noise adjustment

#### `src/utils/vision.py`

- Multi-provider vision support (Groq, Ollama, OpenAI)
- Image encoding and processing
- Provider fallback logic

#### `src/utils/documents.py`

- PDF reading (PyPDF2)
- Word document processing (python-docx)
- Excel file handling (pandas)
- Text file processing

#### `src/utils/files.py`

- File system operations
- Directory listing
- File search
- Security restrictions

## Entry Point

### `main.py`

- System tray integration
- Voice control loop
- UI window management
- Application lifecycle

## Configuration Files

### `.env`

```env
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=optional_key
OLLAMA_URL=http://localhost:11434
```

### `requirements.txt`

Organized by category:

- Core dependencies (groq, python-dotenv)
- UI (pywebview, pystray, Pillow)
- Speech (SpeechRecognition, PyAudio)
- Memory (mem0ai, qdrant-client)
- Vision (requests, openai)
- Documents (PyPDF2, python-docx, pandas, openpyxl)

## Import Structure

All imports use the `src.` prefix with automatic path resolution:

```python
# Each module adds project root to sys.path if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Then import normally
from src.core.ai_engine import get_response
from src.utils.speech import record_voice
```

This ensures modules work both when:

- Running from project root: `python main.py`
- Running as subprocess: `python src/ui/chat_window.py`

## Removed Files

The following unused files were removed during reorganization:

- `recognition.py` (duplicate of speech_to_text.py)
- `voice_player.py` (unused voice output)
- `chat_memory.py` (replaced by mem0 version)
- `pixie_pygame.py` (unused pygame implementation)
- `test_vision.py` (test file)
- `test_webview_api.py` (test file)
- `chat_backup.html` (backup file)
- `chat_enhanced.html` (unused variant)
- `chat_debug.html` (debug file)

## Build Artifacts

### `build/`

PyInstaller build cache (gitignored)

### `dist/`

Contains `PixieAI.exe` after building (gitignored)

### `models/`

Vosk speech models (gitignored)

### `__pycache__/`

Python bytecode cache (gitignored)

## Data Files

### `chat_history.json`

Persistent chat history (gitignored)

### `mem0_db/`

Mem0 vector database (gitignored)

## Development Workflow

1. **Make changes** to source files in `src/`
2. **Test** by running `python main.py`
3. **Check imports** are using `src.` prefix
4. **Update docs** if adding features
5. **Build executable** with `pyinstaller pixie.spec`

## Benefits of New Structure

✅ **Modular**: Clear separation of concerns
✅ **Maintainable**: Easy to find and update code
✅ **Scalable**: Simple to add new features
✅ **Clean**: No duplicate or unused code
✅ **Professional**: Industry-standard structure
✅ **Testable**: Easy to write unit tests

## Future Enhancements

Potential additions to the structure:

```
src/
├── tests/              # Unit tests
├── plugins/            # Plugin system
├── config/             # Configuration management
└── models/             # AI model management
```

---

**Last Updated**: After code reorganization and cleanup
