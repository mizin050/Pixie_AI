# Pixie AI Assistant

A voice-activated AI assistant with vision capabilities, file system access, and document processing.

## Features

- 🎙️ **Voice Control**: Hands-free interaction using speech recognition
- 👁️ **Vision**: Analyze images using Groq, Ollama (free), or OpenAI
- 📁 **File System Access**: Read, search, and manage files
- 📄 **Document Processing**: Support for PDF, Word, Excel, and text files
- 💬 **Web Chat Interface**: Modern chat UI with file upload
- 🧠 **Persistent Memory**: Conversation history with semantic search (Mem0)
- 🖥️ **System Tray**: Runs in background with easy access

## Project Structure

```
AI-Assistant-for-Computer/
├── src/
│   ├── core/
│   │   ├── ai_engine.py      # Main AI logic with Groq
│   │   └── memory.py          # Chat memory with Mem0
│   ├── ui/
│   │   ├── chat_window.py     # Web-based chat interface
│   │   └── chat.html          # Chat UI template
│   └── utils/
│       ├── speech.py          # Speech-to-text
│       ├── vision.py          # Image analysis
│       ├── documents.py       # Document processing
│       └── files.py           # File system tools
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .env.example              # Environment variables template
└── fox.png                   # App icon
```

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd AI-Assistant-for-Computer
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

4. **Optional: Install Ollama for free vision**
   - Download from https://ollama.ai
   - Run: `ollama pull llava`

## Usage

### Run the Assistant

```bash
python main.py
```

The assistant will start in the system tray. Right-click the icon to:

- **Pixie UI**: Open/close the chat window
- **Mic**: Enable/disable voice control
- **Quit**: Exit the application

### Voice Commands

- Say "Pixie UI" to open the chat interface
- Ask questions naturally
- Mention file paths to analyze images or documents

### Chat Interface

- Type messages or use voice input
- Upload images and documents
- View conversation history
- Clear history with the button

## Configuration

### Environment Variables (.env)

```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional, for OpenAI vision
OLLAMA_URL=http://localhost:11434    # Optional, for local Ollama
```

### Vision Options

1. **Groq** (Recommended): Fast, free tier available
2. **Ollama** (Free): Runs locally, requires installation
3. **OpenAI** (Paid): High quality, requires API key

## Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller pixie.spec
```

The executable will be in the `dist/` folder.

## Requirements

- Python 3.8+
- Windows (tested), Linux/Mac (should work)
- Microphone for voice input
- Internet connection for AI APIs

## Troubleshooting

### Speech Recognition Issues

- Check microphone permissions
- Ensure PyAudio is installed correctly
- Try adjusting ambient noise settings

### Vision Not Working

- Verify API keys in .env
- Check Ollama is running (if using local vision)
- Ensure image files are accessible

### Import Errors

- Make sure you're running from the project root
- Verify all dependencies are installed
- Check Python version compatibility

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
