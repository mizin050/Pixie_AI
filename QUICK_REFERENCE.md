# Quick Reference Guide

## 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the application
python main.py
```

## 📁 Project Structure

```
AI-Assistant-for-Computer/
├── main.py              # Entry point
├── src/
│   ├── core/           # AI engine & memory
│   ├── ui/             # Chat interface
│   └── utils/          # Helper functions
├── fox.png             # App icon
├── .env                # API keys (create from .env.example)
└── requirements.txt    # Dependencies
```

## 🎯 Key Files

| File                     | Purpose                              |
| ------------------------ | ------------------------------------ |
| `main.py`                | Application entry point, system tray |
| `src/core/ai_engine.py`  | Main AI logic, Groq integration      |
| `src/core/memory.py`     | Chat history with Mem0               |
| `src/ui/chat_window.py`  | Web chat interface                   |
| `src/utils/speech.py`    | Voice input                          |
| `src/utils/vision.py`    | Image analysis                       |
| `src/utils/documents.py` | Document processing                  |
| `src/utils/files.py`     | File system access                   |

## 💻 Common Commands

### Running

```bash
python main.py                    # Start application
python src/ui/chat_window.py     # Test chat UI only
```

### Building

```bash
pyinstaller pixie.spec --clean   # Build executable
```

### Development

```bash
pip install -r requirements.txt  # Install dependencies
pip list                         # Check installed packages
```

## 🔧 Configuration

### Environment Variables (.env)

```env
GROQ_API_KEY=your_key_here           # Required
OPENAI_API_KEY=your_key_here         # Optional
OLLAMA_URL=http://localhost:11434    # Optional
```

### Allowed File Paths (src/utils/files.py)

```python
fs_tools = FileSystemTools(allowed_paths=[
    os.path.expanduser("~"),  # Home directory
    os.getcwd(),              # Current directory
])
```

## 🎤 Voice Commands

| Command           | Action             |
| ----------------- | ------------------ |
| "Pixie UI"        | Open chat window   |
| Any question      | Get AI response    |
| File path mention | Analyze file/image |

## 🖱️ System Tray Menu

| Option   | Description                  |
| -------- | ---------------------------- |
| Pixie UI | Toggle chat window           |
| Mic      | Enable/disable voice control |
| Quit     | Exit application             |

## 📝 Import Patterns

```python
# Core
from src.core.ai_engine import get_response, reset_history
from src.core.memory import ChatMemoryMem0

# UI
from src.ui.chat_window import create_chat_window

# Utils
from src.utils.speech import record_voice
from src.utils.vision import analyze_images
from src.utils.documents import process_document
from src.utils.files import fs_tools
```

## 🔍 Troubleshooting

### Import Errors

```bash
# Make sure you're in project root
cd AI-Assistant-for-Computer
python main.py
```

### Missing Dependencies

```bash
pip install -r requirements.txt --force-reinstall
```

### API Key Issues

```bash
# Check .env file exists
ls .env

# Verify key is set (Windows)
type .env

# Restart after editing .env
```

### Microphone Not Working

- Check system permissions
- Test in other apps
- Verify PyAudio installed

## 📚 Documentation

| File                   | Content            |
| ---------------------- | ------------------ |
| `README.md`            | Main documentation |
| `SETUP.md`             | Installation guide |
| `STRUCTURE.md`         | Project layout     |
| `ARCHITECTURE.md`      | System design      |
| `MIGRATION.md`         | Upgrade guide      |
| `CHANGELOG.md`         | Version history    |
| `FILE_ACCESS_GUIDE.md` | File features      |
| `VISION_SETUP.md`      | Vision setup       |
| `EXECUTABLE_README.md` | Build guide        |

## 🛠️ Development Workflow

1. **Make changes** to files in `src/`
2. **Test** with `python main.py`
3. **Check imports** use `src.` prefix
4. **Update docs** if needed
5. **Build** with `pyinstaller pixie.spec`

## 🎨 Adding Features

### New AI Provider

1. Create file in `src/utils/`
2. Implement standard interface
3. Add to `ai_engine.py`
4. Update `requirements.txt`

### New Document Type

1. Add processor to `documents.py`
2. Update file type detection
3. Add dependencies

### New UI Component

1. Create in `src/ui/`
2. Integrate with `main.py`
3. Update imports

## 📊 Key Functions

### AI Engine

```python
get_response(text, context_length=10, image_paths=None, document_paths=None)
reset_history()
get_chat_history()
search_history(query)
```

### Memory

```python
memory.add_message(role, content, metadata=None)
memory.get_context(max_messages=10)
memory.clear_history()
memory.search_history(query)
```

### Speech

```python
record_voice(prompt="🎙 I'm listening...", timeout=None, phrase_time_limit=5)
```

### Vision

```python
analyze_images(image_paths, user_text, groq_vision_model=None)
```

### Documents

```python
process_document(file_path)
```

### Files

```python
fs_tools.read_file(file_path, max_size_mb=10)
fs_tools.list_directory(dir_path, recursive=False)
fs_tools.search_files(search_path, pattern)
fs_tools.get_file_info(file_path)
```

## 🔗 Useful Links

- **Groq Console**: https://console.groq.com
- **Ollama**: https://ollama.ai
- **OpenAI**: https://platform.openai.com
- **PyAudio Wheels**: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

## 💡 Tips

- Run from project root directory
- Keep `.env` file secure
- Use Ollama for free vision
- Check console for errors
- Clear history if responses are slow
- Build with `--clean` for fresh executable

## ⚡ Quick Fixes

### "Module not found"

```bash
pip install -r requirements.txt
```

### "API key not found"

```bash
# Create .env file
cp .env.example .env
# Add your key
```

### "Microphone timeout"

```python
# Increase timeout in src/utils/speech.py
record_voice(timeout=10, phrase_time_limit=10)
```

### "Vision not working"

```bash
# Install Ollama
# Download model
ollama pull llava
```

---

**Keep this guide handy for quick reference!** 📖
