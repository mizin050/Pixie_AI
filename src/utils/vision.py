import os
import sys
import base64
from dotenv import load_dotenv

# Add project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_ollama(image_paths, user_text):
    """Analyze images using Ollama with LLaVA (FREE, runs locally)"""
    try:
        import requests
        
        # Ollama API endpoint (default local)
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Try to check if Ollama is running
        try:
            requests.get(f"{ollama_url}/api/tags", timeout=2)
        except:
            return None, "Ollama not running. Install from https://ollama.ai and run: ollama pull llava"
        
        # Encode first image
        if not image_paths:
            return None, "No images provided"
        
        image_path = image_paths[0]  # Use first image
        base64_image = encode_image(image_path)
        
        # Call Ollama API
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llava",
                "prompt": user_text,
                "images": [base64_image],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from model"), None
        else:
            return None, f"Ollama error: {response.status_code}"
            
    except ImportError:
        return None, "requests library not installed. Run: pip install requests"
    except Exception as e:
        return None, f"Error with Ollama: {str(e)}"

def analyze_image_with_openai(image_paths, user_text):
    """Analyze images using OpenAI GPT-4 Vision (PAID)"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OpenAI API key not found in .env file"
        
        client = OpenAI(api_key=api_key)
        
        # Build content with images
        content = [{"type": "text", "text": user_text}]
        
        for image_path in image_paths:
            try:
                if image_path.startswith('http'):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image_path}
                    })
                else:
                    base64_image = encode_image(image_path)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content, None
        
    except ImportError:
        return None, "OpenAI library not installed. Run: pip install openai"
    except Exception as e:
        return None, f"Error with OpenAI: {str(e)}"

def analyze_images(image_paths, user_text, groq_vision_model=None):
    """
    Analyze images using available vision API
    Priority: Groq > Ollama (free) > OpenAI (paid)
    Returns: (response_text, error_message)
    """
    
    # Try Groq first if vision model available
    if groq_vision_model:
        return None, None  # Let Groq handle it
    
    # Try Ollama (FREE, local)
    print("Trying Ollama (free, local)...")
    response, error = analyze_image_with_ollama(image_paths, user_text)
    if response:
        return response, None
    
    print(f"Ollama not available: {error}")
    
    # Fallback to OpenAI (PAID)
    print("Trying OpenAI (paid)...")
    response, error = analyze_image_with_openai(image_paths, user_text)
    if response:
        return response, None
    
    # No vision available
    error_msg = """Vision not available. To enable FREE vision:

1. Install Ollama: https://ollama.ai
2. Run: ollama pull llava
3. Start Ollama (it runs in background)
4. Upload images and ask questions!

Alternative (PAID):
- Add OPENAI_API_KEY to .env file
- Install: pip install openai"""
    
    return None, error_msg

