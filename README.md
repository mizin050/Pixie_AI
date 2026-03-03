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
├── Backend/                    # Core AI services
│   ├── Model.py                   # Decision-making model (Cohere)
│   ├── Chatbot.py                 # Conversational AI (Groq Llama)
│   ├── SpeechToText.py            # Voice input (Groq Whisper)
│   ├── TextToSpeech.py            # Voice output (Edge TTS)
│   ├── ImageGeneration.py         # AI image creation (Hugging Face)
│   ├── RealtimeSearchEngine.py    # Web search integration
│   ├── Automation.py              # Task automation engine
│   ├── GestureControl.py          # Hand gesture recognition
│   ├── ResearchTool.py            # Research report generator
│   ├── TelegramBridge.py          # Telegram bot integration
│   └── FolderContext.py           # Folder context manager
├── Frontend/                   # User interface
│   ├── GUI.py                     # Main PyQt5 GUI
│   ├── Graphics/                  # 3D models and assets
│   └── Files/                     # UI state management
├── Data/                       # Application data
│   ├── ChatLog.json               # Conversation history
│   └── FolderContext.json         # Active folder state
├── pixieuiii/                  # 3D chat interface
│   └── chat_3d.html               # WebGL 3D fox model
└── Main.py                     # Application entry point
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Webcam (for gesture control)
- Microphone (for voice input)
- Speaker (for voice output)

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
   Create a `.env` file in the root directory:

```env
# Required API Keys
GroqAPIKey=your_groq_api_key
CohereAPIKey=your_cohere_api_key
HuggingFaceAPIKey=your_huggingface_api_key

# Optional: Telegram Integration
TelegramBotToken=your_telegram_bot_token
TelegramChatID=your_chat_id
TelegramAllowedChatID=your_allowed_chat_id

# User Configuration
Username=YourName
Assistantname=Pixie

# Optional: Model Configuration
GroqModel=llama-3.3-70b-versatile
HuggingFaceModel=black-forest-labs/FLUX.1-schnell
AssistantVoice=en-US-AriaNeural
```

### Running the Application

```bash
python Main.py
```

## 🎮 Usage Guide

### Voice Commands

**General Conversation:**

- "Hello Pixie, how are you?"
- "Tell me about quantum computing"
- "What's the weather like today?"

**Automation:**

- "Open Chrome and Facebook"
- "Close Notepad"
- "Play Afsanay by YS"
- "Volume up / Volume down / Mute"

**Search:**

- "Google search Python tutorials"
- "YouTube search machine learning"
- "Who is Elon Musk?" (realtime search)

**Image Generation:**

- "Generate image of a sunset over mountains"
- "Create a flowchart for user authentication"
- "Make an infographic about AI"

**Research:**

- "Research artificial intelligence in healthcare in 10 pages"
- "Deep research on quantum computing in 500 lines"
- "Make research report on blockchain technology"

**Folder Context:**

- "Use folder C:\Projects\MyApp"
- "Work with folder Desktop"
- "Clear folder context"

### Telegram Commands

Send these commands to your Telegram bot:

**Basic:**

- `/start` - Link your chat with Pixie
- `telegram help` - Show all commands
- `telegram send Hello!` - Send text message

**File Operations:**

- `telegram file C:\path\to\file.pdf` - Send file
- `telegram folder C:\Projects` - Zip and send folder
- `telegram screenshot` - Send current screen

**Advanced:**

- `telegram voice Hello from Pixie!` - Send voice message
- `telegram location 40.7128,-74.0060` - Send location
- `telegram contact +1234567890|John|Doe` - Send contact
- `telegram poll What's your favorite?|Option A|Option B` - Create poll
- `telegram album C:\pic1.jpg|C:\pic2.jpg` - Send photo album

### Gesture Control

**Available Gestures:**

- **Pinch (thumb + index)**: Zoom in/out (Ctrl+Scroll)
- **Open Palm Swipe Left/Right**: Switch windows (Alt+Tab)
- **Two Fingers Swipe Left/Right**: Switch browser tabs (Ctrl+Tab)
- **Open Palm Up/Down**: Scroll page
- **Closed Fist (hold 0.8s)**: Minimize all windows (Win+M)

**Tips:**

- Keep hand clearly visible to camera
- Use deliberate, smooth movements
- Press 'q' in camera window to exit gesture mode

## 🛠️ Technologies

- **Python 3.8+**: Core programming language
- **Groq API**: LLM (Llama 3.3 70B) and Speech-to-Text (Whisper)
- **Cohere API**: Decision-making and intent classification
- **Hugging Face**: Image generation (FLUX, Stable Diffusion)
- **Edge TTS**: Text-to-speech synthesis
- **MediaPipe**: Hand gesture recognition
- **PyQt5**: GUI framework
- **OpenCV**: Computer vision for gesture control
- **BeautifulSoup**: Web scraping
- **Google Search API**: Real-time information retrieval
- **Telegram Bot API**: Remote control and notifications
- **python-docx**: Research report generation

## 📝 Module Details

### Voice Interaction

Real-time speech recognition and natural voice responses create seamless human-like conversations.

### Gesture Control

Control your computer hands-free using intuitive hand gestures detected by your webcam.

### Research Tool

Generate comprehensive, citation-backed research reports by aggregating information from academic papers, web sources, and tutorial videos.

### Telegram Integration

Access Pixie remotely from your phone, send files, browse your computer's file system, and receive voice replies.

### Folder Context

Load entire project folders into Pixie's context for intelligent code assistance and project-aware responses.

### Image Generation

Create images, diagrams, flowcharts, and infographics using state-of-the-art AI models.

### Real-time Search

Get up-to-date information from the web, including live stock prices, news, and current events.

### Automation

Automate repetitive tasks like opening applications, controlling system volume, and generating content.

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
