# Pixie_AI 🦊

An intelligent AI assistant with voice interaction, real-time search, image generation, gesture control, research capabilities, Telegram integration, and a beautiful 3D GUI interface.

## ✨ Core Features

### 🎤 Voice & Speech

- **Speech-to-Text**: Real-time voice recognition using Groq Whisper
- **Text-to-Speech**: Natural voice responses with Edge TTS
- **Voice Commands**: Hands-free control of all features
- **Multi-language Support**: Automatic translation capabilities

### 🤖 AI Intelligence

- **Conversational AI**: Context-aware chatbot powered by Llama 3.3 70B
- **Decision Engine**: Smart intent classification (general/realtime/automation)
- **Real-time Search**: Live web search with Google integration
- **Context Awareness**: Folder context and conversation history tracking
- **Chat History**: Persistent conversation logging with JSON storage

### 🖼️ Image Generation

- **AI Image Creation**: Generate images using Hugging Face models (FLUX, Stable Diffusion)
- **Diagram Support**: Create flowcharts, charts, infographics, and technical diagrams
- **Batch Generation**: Create multiple variations simultaneously
- **Auto-optimization**: Enhanced prompts for better quality

### 🖐️ Gesture Control

- **Hand Tracking**: MediaPipe-powered gesture recognition
- **Window Switching**: Palm swipe left/right to switch windows (Alt+Tab)
- **Tab Navigation**: Two-finger swipe to switch browser tabs (Ctrl+Tab)
- **Scroll Control**: Palm up/down for page scrolling
- **Pinch Zoom**: Zoom in/out with pinch gesture (Ctrl+Scroll)
- **Minimize All**: Hold closed fist to minimize all windows (Win+M)

### 📚 Research Tool

- **Deep Research**: Generate comprehensive research reports on any topic
- **Multi-source Aggregation**: Combines Google, arXiv, IEEE, Crossref sources
- **Academic Papers**: Automatic paper discovery and citation
- **Tutorial Videos**: YouTube tutorial link collection
- **Custom Length**: Specify pages (1-500) or lines (20-20000)
- **DOCX Export**: Professional formatted reports with citations

### 📱 Telegram Integration

- **Remote Control**: Control Pixie from anywhere via Telegram bot
- **File Sharing**: Send/receive files, folders, screenshots
- **Voice Messages**: Send voice replies to Telegram
- **File Browser**: Interactive file system browser with filters
- **Folder Zipping**: Automatic compression and sending of folders
- **Location Sharing**: Send GPS coordinates
- **Contact Sharing**: Share contact information
- **Polls**: Create and send polls
- **Media Albums**: Send multiple photos/videos as albums

### ⚙️ Automation & System Control

- **App Control**: Open/close applications by voice
- **Web Navigation**: Open websites and search Google/YouTube
- **Content Generation**: AI-powered writing (emails, code, documents)
- **System Commands**: Volume control, mute/unmute
- **File Operations**: Create, move, and manage files
- **Folder Context**: Load entire folders into AI context for code assistance

## 🏗️ Architecture

```
Pixie_AI/
├── Backend/           # Core AI services
│   ├── Model.py              # AI model integration
│   ├── Chatbot.py            # Conversational AI logic
│   ├── SpeechToText.py       # Voice input processing
│   ├── TextToSpeech.py       # Voice output generation
│   ├── ImageGeneration.py    # AI image creation
│   ├── RealtimeSearchEngine.py # Web search integration
│   └── Automation.py         # Task automation
├── Frontend/          # User interface
│   ├── GUI.py                # Main GUI application
│   ├── Graphics/             # 3D models and assets
│   └── Files/                # UI state management
├── Data/              # Application data
│   └── ChatLog.json          # Conversation history
└── Main.py            # Application entry point
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:

```bash
git clone https://github.com/mizin050/Pixie_AI.git
cd Pixie_AI
```

2. Create and activate virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r Requirements.txt
```

4. Configure environment variables:
   Create a `.env` file in the root directory with your API keys:

```
# Add your API keys here
```

### Running the Application

```bash
python Main.py
```

## 🎮 Usage

1. Launch the application using `python Main.py`
2. Interact with Pixie through the GUI interface
3. Use voice commands or text input
4. Ask questions, generate images, or automate tasks

## 🛠️ Technologies

- **Python**: Core programming language
- **AI/ML Models**: Language and image generation
- **3D Graphics**: Interactive UI with GLB models
- **Speech Processing**: Voice recognition and synthesis
- **Web Search**: Real-time information retrieval

## 📝 Features in Detail

### Voice Interaction

Pixie can listen to your voice commands and respond with natural speech, making interactions feel more human-like.

### Real-time Search

Get current information from the web without leaving the conversation.

### Image Generation

Create custom images by describing what you want to see.

### Automation

Automate repetitive tasks and workflows with simple commands.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).


## 🙏 Acknowledgments

- Thanks to all contributors and users of Pixie_AI
- Built with modern AI technologies and frameworks

---

⭐ Star this repository if you find it helpful!
