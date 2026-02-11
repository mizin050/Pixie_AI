from groq import Groq
from dotenv import load_dotenv
import os
import sys
import base64
import json
import re

# Add project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.memory import ChatMemoryMem0
from src.utils.files import fs_tools
from src.utils.vision import analyze_images
from src.utils.documents import process_document

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=GROQ_API_KEY)
memory = ChatMemoryMem0()

SYSTEM_PROMPT = """
You are Pixie, a helpful AI assistant with vision and file system access capabilities.
You have access to previous conversations and can help with files and folders.

Available file system commands (use these when user asks about files/folders):
- READ_FILE: path/to/file.txt - Read file contents
- LIST_DIR: path/to/directory - List directory contents
- SEARCH_FILES: path/to/search pattern - Search for files
- FILE_INFO: path/to/file - Get file information

When user asks to read, open, or view a file, use: READ_FILE: <path>
When user asks to list or show folder contents, use: LIST_DIR: <path>
When user asks to find or search files, use: SEARCH_FILES: <path> <pattern>

Give useful and concise answers. Address the user respectfully.
When analyzing images, be descriptive and helpful.
"""

def get_best_model(vision_required=False):
    model_list = client.models.list()

    available = [m.id for m in model_list.data]
    print("Available Groq Models:\n", available)

    if vision_required:
        # Priority for vision models
        vision_priority = [
            "llama-3.2-90b-vision-preview",
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision",
            "llama-3.2-11b-vision",
            "llama-3.2-vision"
        ]
        
        for name in vision_priority:
            for model_id in available:
                if 'vision' in model_id.lower() and name.split('-')[0] in model_id.lower():
                    print(f"\n✔ Selected vision model: {model_id}\n")
                    return model_id
        
        # If no vision model found, return None
        print("⚠ No vision models available")
        return None
    
    # Priority for text models
    priority = [
        "llama-3.3-70b",
        "llama-3.2-90b",
        "llama-3.2-70b",
        "llama-3.1-8b",
        "mixtral-8x7b",
        "gemma2-9b-it"
    ]

    for name in priority:
        for model_id in available:
            if name in model_id.lower():
                print(f"\n✔ Selected model: {model_id}\n")
                return model_id

    return available[0]

BEST_MODEL = get_best_model()
VISION_MODEL = get_best_model(vision_required=True)

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

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_response(user_text, context_length=10, image_paths=None, document_paths=None):
    """Get AI response with persistent memory, images, and document analysis"""
    
    # Check if user_text contains file paths to images
    if not image_paths and not document_paths:
        # Look for file paths in the message
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
    
    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + context
    
    # If images are provided, use vision model
    if image_paths and len(image_paths) > 0:
        model_to_use = VISION_MODEL
        
        # Check if vision model is available
        if model_to_use is None:
            # Try OpenAI vision as fallback
            vision_response, vision_error = analyze_images(image_paths, user_text, None)
            
            if vision_response:
                memory.add_message("assistant", vision_response)
                return vision_response
            else:
                error_msg = f"Vision capabilities not available. {vision_error}\n\nTo enable vision:\n1. Add OPENAI_API_KEY to .env file\n2. Install OpenAI: pip install openai\n3. Or wait for Groq vision models to become available"
                memory.add_message("assistant", error_msg)
                return error_msg
        
        # Build content with images for Groq
        content = [{"type": "text", "text": user_text}]
        
        for image_path in image_paths:
            try:
                # Check if it's a URL or local file
                if image_path.startswith('http'):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image_path}
                    })
                else:
                    # Encode local image
                    base64_image = encode_image(image_path)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
        
        # Replace last message with multimodal content
        if len(messages) > 0 and messages[-1]["role"] == "user":
            messages[-1]["content"] = content
    else:
        model_to_use = BEST_MODEL

    try:
        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            max_tokens=500
        )

        text = response.choices[0].message.content.strip()
        
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
                    items = result['items'][:20]  # Show first 20 items
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
        error_msg = f"Error getting response: {e}"
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
