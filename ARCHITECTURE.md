# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                 │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             │ Voice Input                    │ GUI Interaction
             │                                │
┌────────────▼────────────┐      ┌───────────▼────────────────┐
│   System Tray Icon      │      │   Web Chat Interface       │
│   (pystray)             │      │   (pywebview)              │
│                         │      │                            │
│  • Pixie UI Toggle      │      │  • Message Input           │
│  • Mic Toggle           │      │  • File Upload             │
│  • Quit                 │      │  • History Display         │
└────────────┬────────────┘      └───────────┬────────────────┘
             │                                │
             └────────────┬───────────────────┘
                          │
                ┌─────────▼──────────┐
                │     main.py        │
                │  (Entry Point)     │
                └─────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
│   src/core/    │ │  src/ui/   │ │  src/utils/    │
│                │ │            │ │                │
│ • ai_engine    │ │ • chat_    │ │ • speech       │
│ • memory       │ │   window   │ │ • vision       │
│                │ │ • chat.html│ │ • documents    │
│                │ │            │ │ • files        │
└───────┬────────┘ └─────┬──────┘ └───────┬────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
│  Groq API      │ │ Mem0 DB  │ │  File System    │
│  (AI Models)   │ │ (Qdrant) │ │  (Local Files)  │
└────────────────┘ └──────────┘ └─────────────────┘
```

## Component Interaction Flow

### Voice Input Flow

```
User speaks → Microphone → speech.py → Google Speech API
                                              ↓
                                    Transcribed Text
                                              ↓
                                        ai_engine.py
                                              ↓
                                         Groq API
                                              ↓
                                        AI Response
                                              ↓
                                    Console Output
```

### Chat Interface Flow

```
User types → chat.html → JavaScript → chat_window.py (API)
                                              ↓
                                        ai_engine.py
                                              ↓
                                    ┌─────────┴─────────┐
                                    │                   │
                            Text Message          File Upload
                                    │                   │
                                    ├───────────────────┤
                                    │                   │
                              Groq API          vision.py/documents.py
                                    │                   │
                                    └─────────┬─────────┘
                                              ↓
                                        AI Response
                                              ↓
                                    chat.html (Display)
```

### Memory Flow

```
User Message → ai_engine.py → memory.py → Mem0
                                              ↓
                                    Store in Qdrant DB
                                              ↓
                                    Retrieve Context
                                              ↓
                                    Include in Prompt
                                              ↓
                                         Groq API
```

## Module Dependencies

### Core Modules

#### ai_engine.py

**Dependencies:**

- `groq` - AI API client
- `memory.py` - Chat history
- `vision.py` - Image analysis
- `documents.py` - Document processing
- `files.py` - File system access

**Provides:**

- `get_response()` - Main AI interaction
- `reset_history()` - Clear chat
- `get_chat_history()` - Retrieve history
- `search_history()` - Search messages

#### memory.py

**Dependencies:**

- `mem0` - Memory management
- `qdrant_client` - Vector database

**Provides:**

- `ChatMemoryMem0` class
- `add_message()` - Store message
- `get_context()` - Retrieve context
- `search_history()` - Semantic search

### UI Modules

#### chat_window.py

**Dependencies:**

- `webview` - Web interface
- `ai_engine.py` - AI responses
- `files.py` - File operations
- `documents.py` - Document processing

**Provides:**

- `create_chat_window()` - Launch UI
- `ChatAPI` class - JavaScript bridge

#### chat.html

**Dependencies:**

- Modern browser (via pywebview)
- JavaScript ES6+

**Provides:**

- Message display
- File upload UI
- History management

### Utility Modules

#### speech.py

**Dependencies:**

- `speech_recognition` - STT
- `pyaudio` - Audio input

**Provides:**

- `record_voice()` - Capture and transcribe

#### vision.py

**Dependencies:**

- `groq` - Vision models
- `requests` - Ollama API
- `openai` - OpenAI Vision

**Provides:**

- `analyze_images()` - Multi-provider vision

#### documents.py

**Dependencies:**

- `PyPDF2` - PDF reading
- `python-docx` - Word docs
- `pandas` - Excel files

**Provides:**

- `process_document()` - Universal processor

#### files.py

**Dependencies:**

- `os`, `pathlib` - File operations

**Provides:**

- `FileSystemTools` class
- `read_file()`, `list_directory()`, etc.

## Data Flow

### Request Processing

```
1. Input (Voice/Text/File)
   ↓
2. Preprocessing (speech.py, documents.py)
   ↓
3. Context Retrieval (memory.py)
   ↓
4. AI Processing (ai_engine.py → Groq)
   ↓
5. Response Generation
   ↓
6. Memory Storage (memory.py)
   ↓
7. Output (Console/UI)
```

### File Upload Processing

```
1. User uploads file (chat.html)
   ↓
2. JavaScript reads file as base64
   ↓
3. Send to Python (chat_window.py)
   ↓
4. Decode and save temp file
   ↓
5. Determine file type
   ↓
6. Process accordingly:
   • Image → vision.py
   • Document → documents.py
   • Text → direct to AI
   ↓
7. Include in AI prompt
   ↓
8. Generate response
   ↓
9. Clean up temp files
```

## Security Model

### File System Access

```
FileSystemTools
    ↓
Allowed Paths Check
    ↓
    ├─ Home Directory (~)
    ├─ Current Directory (.)
    └─ Custom Paths (configurable)
        ↓
    Operation Permitted
```

### API Key Management

```
.env file (not in git)
    ↓
python-dotenv loads
    ↓
Environment variables
    ↓
Used by modules
    ↓
Never logged or exposed
```

## Performance Considerations

### Memory Management

- Chat history limited to last N messages
- Temp files cleaned after processing
- Vector DB uses on-disk storage

### API Optimization

- Model selection based on task
- Context window management
- Token limit awareness

### UI Responsiveness

- Async voice input loop
- Non-blocking UI operations
- Background process for chat window

## Scalability

### Adding New Features

**New AI Provider:**

```
1. Create provider module in src/utils/
2. Implement standard interface
3. Add to ai_engine.py fallback chain
4. Update requirements.txt
```

**New Document Type:**

```
1. Add processor to documents.py
2. Update file type detection
3. Add dependencies to requirements.txt
```

**New UI Component:**

```
1. Create module in src/ui/
2. Integrate with main.py
3. Update chat_window.py if needed
```

## Technology Stack

### Core

- **Python 3.8+** - Main language
- **Groq API** - AI inference
- **Mem0** - Memory management
- **Qdrant** - Vector database

### UI

- **pywebview** - Web interface
- **pystray** - System tray
- **Pillow** - Image handling

### Speech

- **SpeechRecognition** - STT
- **PyAudio** - Audio input

### Vision

- **Groq** - Primary vision
- **Ollama** - Local vision
- **OpenAI** - Fallback vision

### Documents

- **PyPDF2** - PDF processing
- **python-docx** - Word docs
- **pandas** - Excel files

## Deployment

### Development

```
python main.py
```

### Production (Executable)

```
pyinstaller pixie.spec
→ dist/PixieAI.exe
```

### Distribution

- Single executable file
- Embedded Python runtime
- All dependencies included
- ~70-80 MB file size

---

**Architecture designed for modularity, maintainability, and scalability.**
