import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech engine
tts_engine = None

def init_tts():
    """Initialize text-to-speech engine"""
    global tts_engine
    if tts_engine is None:
        tts_engine = pyttsx3.init()
        # Set properties
        tts_engine.setProperty('rate', 175)  # Speed of speech
        tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    return tts_engine

def speak_text(text):
    """Convert text to speech"""
    try:
        engine = init_tts()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠ TTS Error: {e}")

def record_voice(prompt="🎙 I'm listening...", timeout=None, phrase_time_limit=5):
    """
    Record voice input and convert to text using Google Speech Recognition
    
    Args:
        prompt: Message to display when listening
        timeout: Maximum time to wait for speech to start (None = no limit)
        phrase_time_limit: Maximum time for the phrase (default 5 seconds)
    
    Returns:
        str: Transcribed text or empty string if recognition fails
    """
    recognizer = sr.Recognizer()
    
    # Adjust for ambient noise
    with sr.Microphone() as source:
        print(prompt)
        
        # Adjust for ambient noise (only for 0.5 seconds to be faster)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen for audio
            audio = recognizer.listen(
                source, 
                timeout=timeout, 
                phrase_time_limit=phrase_time_limit
            )
            
            # Recognize speech using Google Speech Recognition
            print("🔄 Processing...")
            text = recognizer.recognize_google(audio)
            print(f"✓ You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱ Listening timed out")
            return ""
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")
            return ""
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""

if __name__ == "__main__":
    # Test the speech recognition
    print("Testing speech recognition...")
    result = record_voice()
    if result:
        print(f"Final result: {result}")
    else:
        print("No speech detected or error occurred")
