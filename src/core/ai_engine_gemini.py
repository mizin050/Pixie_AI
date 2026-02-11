import google.generativeai as genai
from dotenv import load_dotenv
import os
import sys
import re
from PIL import Image

# Add project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.memory_simple import ChatMemorySimple
from src.utils.files import fs_tools
from src.utils.documents import process_document

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    raise ValueError("❌ GEMINI_API_KEY not found in .env. Get one from: https://aistudio.google.com/app/apikey")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize simple memory (no external dependencies)
memory = ChatMemorySimple()

SYSTEM_PROMPT = """
You are Pixie, a helpful AI assistant with vision and file system access capabilities.
Your name is Pixie. When asked about your name or identity, you should say "I'm Pixie, your AI assistant."
You have access to previous conversations and can help with files and folders.

Available file system commands (use these when user asks about files/folders):
- READ_FILE: path/to/file.txt - Read file contents
- LIST_DIR: path/to/directory - List directory contents
- SEARCH_FILES: path/to/search pattern - Search for files
- FILE_INFO: path/to/file - Get file information

When user asks to read, open, or view a file, use: READ_FILE: <path>
When user asks to list or show folder contents, use: LIST_DIR: <path>
When user asks to find or search files, use: SEARCH_FILES: <path> <pattern>

IMPORTANT - WhatsApp Desktop Instructions:
When sending WhatsApp messages, you MUST use the WhatsApp Desktop app's search box:
1. Click on the search box at the TOP of WhatsApp Desktop (not system contacts)
2. Type the contact name in WhatsApp's search box
3. Wait for WhatsApp to show search results
4. Click on the contact from WhatsApp's search results
5. Type the message in the chat input box
6. Press Enter to send

DO NOT try to access system contacts or phone contacts. Always use WhatsApp's built-in search.

Give useful and concise answers. Address the user respectfully.
When analyzing images, be descriptive and helpful.
Remember: Your name is Pixie.
"""

def get_gemini_model(multimodal=False):
    """Get the appropriate Gemini model"""
    # Use the latest flash model which supports text, images, and documents
    return genai.GenerativeModel('gemini-flash-latest')

def process_file_commands(text):
    """Process file system commands in the AI response"""
    commands_executed = []
    
    # Check for file system commands
    if "READ_FILE:" in text:
        parts = text.split("READ_FILE:")
        for part in parts[1:]:
            file_path = part.split()[0].strip()
            result = fs_tools.read_file(file_path)
            commands_executed.append(("READ_FILE", file_path, result))
    
    if "LIST_DIR:" in text:
        parts = text.split("LIST_DIR:")
        for part in parts[1:]:
            dir_path = part.split()[0].strip()
            result = fs_tools.list_directory(dir_path)
            commands_executed.append(("LIST_DIR", dir_path, result))
    
    if "SEARCH_FILES:" in text:
        parts = text.split("SEARCH_FILES:")
        for part in parts[1:]:
            tokens = part.split()
            if len(tokens) >= 2:
                search_path = tokens[0].strip()
                pattern = tokens[1].strip()
                result = fs_tools.search_files(search_path, pattern)
                commands_executed.append(("SEARCH_FILES", f"{search_path} {pattern}", result))
    
    if "FILE_INFO:" in text:
        parts = text.split("FILE_INFO:")
        for part in parts[1:]:
            file_path = part.split()[0].strip()
            result = fs_tools.get_file_info(file_path)
            commands_executed.append(("FILE_INFO", file_path, result))
    
    return commands_executed

def get_response(user_text, context_length=10, image_paths=None, document_paths=None):
    """Get AI response with persistent memory, images, and document analysis using Gemini"""
    
    # Check if user_text contains file paths
    if not image_paths and not document_paths:
        path_pattern = r'[A-Za-z]:\\[^<>:"|?*\n]+\.\w+'
        found_paths = re.findall(path_pattern, user_text, re.IGNORECASE)
        
        if found_paths:
            image_paths = []
            document_paths = []
            
            for path in found_paths:
                if os.path.exists(path):
                    ext = os.path.splitext(path)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico']:
                        image_paths.append(path)
                        print(f"📷 Detected image path: {path}")
                    else:
                        document_paths.append(path)
                        print(f"📄 Detected document path: {path}")
    
    # Process documents and add their content to the message
    document_content = ""
    if document_paths:
        for doc_path in document_paths:
            doc_info = process_document(doc_path)
            if doc_info['type'] == 'image':
                # It's actually an image, move it to image_paths
                if not image_paths:
                    image_paths = []
                image_paths.append(doc_info['path'])
            else:
                # Add document content to context
                doc_name = os.path.basename(doc_path)
                document_content += f"\n\n📄 Content of {doc_name} ({doc_info['format']}):\n```\n{doc_info['content'][:5000]}\n```\n"
    
    # Combine user text with document content
    full_message = user_text
    if document_content:
        full_message += document_content
    
    # Add user message to memory
    memory.add_message("user", full_message)
    
    # Get conversation context
    context = memory.get_context(max_messages=context_length)
    
    # Build conversation history for Gemini
    history = []
    for msg in context[:-1]:  # Exclude the last message (current user message)
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    
    try:
        # Determine if we need multimodal model
        multimodal = bool(image_paths and len(image_paths) > 0)
        model = get_gemini_model(multimodal=multimodal)
        
        # Add system instruction to the model
        model_with_system = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            system_instruction=SYSTEM_PROMPT
        )
        
        # Start chat with history
        chat = model_with_system.start_chat(history=history)
        
        # Prepare the message content
        if multimodal:
            # Build multimodal content with images
            content_parts = [full_message]
            
            for image_path in image_paths:
                try:
                    if os.path.exists(image_path):
                        img = Image.open(image_path)
                        content_parts.append(img)
                        print(f"✓ Added image: {image_path}")
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
            
            response = chat.send_message(content_parts)
        else:
            # Text-only message
            response = chat.send_message(full_message)
        
        text = response.text.strip()
        
        # Process any file system commands in the response
        file_commands = process_file_commands(text)
        
        # If file commands were executed, append results to response
        if file_commands:
            text += "\n\n📁 File System Results:\n"
            for cmd_type, cmd_arg, result in file_commands:
                if "error" in result:
                    text += f"\n❌ {cmd_type} {cmd_arg}: {result['error']}"
                elif cmd_type == "READ_FILE" and result.get("success"):
                    content_preview = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
                    text += f"\n✓ {cmd_type} {cmd_arg}:\n```\n{content_preview}\n```"
                elif cmd_type == "LIST_DIR" and result.get("success"):
                    items = result['items'][:20]
                    text += f"\n✓ {cmd_type} {cmd_arg} ({result['count']} items):\n"
                    for item in items:
                        icon = "📁" if item['type'] == 'directory' else "📄"
                        size = f" ({item['size']} bytes)" if 'size' in item else ""
                        text += f"{icon} {item['name']}{size}\n"
                elif cmd_type == "SEARCH_FILES" and result.get("success"):
                    text += f"\n✓ {cmd_type} {cmd_arg}: Found {result['count']} files\n"
                    for item in result['results'][:10]:
                        text += f"📄 {item['path']}\n"
                elif cmd_type == "FILE_INFO" and result.get("success"):
                    text += f"\n✓ {cmd_type} {cmd_arg}:\n"
                    text += f"  Size: {result['size']} bytes\n"
                    text += f"  Type: {'Directory' if result['is_directory'] else 'File'}\n"
                    text += f"  Extension: {result.get('extension', 'N/A')}\n"
        
        # Add assistant response to memory
        memory.add_message("assistant", text)
        
        return text
        
    except Exception as e:
        error_msg = f"Error getting response from Gemini: {e}"
        print(error_msg)
        return error_msg


def reset_history():
    """Clear chat history"""
    memory.clear_history()

def get_chat_history():
    """Get all chat history"""
    return memory.get_all_messages()

def search_history(query):
    """Search through chat history"""
    return memory.search_history(query)
