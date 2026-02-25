# Pixie_AI 🦊

An intelligent AI assistant with voice interaction, real-time search, image generation, and a beautiful 3D GUI interface.

## ✨ Features

- **Voice Interaction**: Speech-to-text and text-to-speech capabilities for natural conversations
- **Real-time Search**: Access up-to-date information from the web
- **Image Generation**: Create images using AI models
- **3D GUI Interface**: Interactive fox mascot with modern UI
- **Chatbot**: Intelligent conversational AI powered by advanced language models
- **Automation**: Task automation capabilities
- **Chat History**: Persistent conversation logging

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

## 👤 Author

**mizin050**
- GitHub: [@mizin050](https://github.com/mizin050)

## 🙏 Acknowledgments

- Thanks to all contributors and users of Pixie_AI
- Built with modern AI technologies and frameworks

---

⭐ Star this repository if you find it helpful!
