from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import time
from pathlib import Path
import mtranslate as mt

# Resolve project paths relative to this file, not process CWD.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
VOICE_HTML_PATH = PROJECT_ROOT / "Data" / "Voice.html"
TEMP_DIR_PATH = PROJECT_ROOT / "Frontend" / "Files"
STATUS_PATH = TEMP_DIR_PATH / "Status.data"

# Load environment variables from the .env file.
env_vars = dotenv_values(ENV_PATH)
# Get the input language setting from the environment variables.
InputLanguage = (env_vars.get("InputLanguage") or "en").strip()

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;
        let finalTranscript = "";

        function startRecognition() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                output.textContent = "Speech recognition is not supported in this browser.";
                return;
            }

            finalTranscript = "";
            recognition = new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onresult = function(event) {
                let interimTranscript = "";
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + " ";
                    } else {
                        interimTranscript += transcript;
                    }
                }
                output.textContent = (finalTranscript + interimTranscript).trim();
            };

            recognition.onend = function() {
                if (recognition) {
                    recognition.start();
                }
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.onend = null;
                recognition.stop();
            }
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
VOICE_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(VOICE_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Lazy-initialized browser instance.
driver = None


def GetDriver():
    global driver
    if driver is None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    TEMP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    with open(STATUS_PATH, "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    if not new_query:
        return ""
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # Check if the query is a question and add a question mark if necessary.
    if any(new_query.startswith(word + " ") or new_query == word for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    current_driver = GetDriver()

    # Open the HTML file in the browser.
    current_driver.get(VOICE_HTML_PATH.resolve().as_uri())
    # Start speech recognition by clicking the start button.
    current_driver.find_element(by=By.ID, value="start").click()

    last_text = ""
    last_change_time = time.time()
    start_time = time.time()
    max_wait_seconds = 20
    stable_for_seconds = 1.0

    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = current_driver.find_element(by=By.ID, value="output").text.strip()

            if Text != last_text:
                last_text = Text
                last_change_time = time.time()

            # If recognition output has been stable for a short window, treat it as complete.
            if last_text and (time.time() - last_change_time) >= stable_for_seconds:
                current_driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower() == "en" or InputLanguage.lower().startswith("en-"):
                    return QueryModifier(last_text)

                SetAssistantStatus("Translating...")
                return QueryModifier(UniversalTranslator(last_text))

        except Exception:
            pass

        # Prevent hanging forever when no speech is captured.
        if (time.time() - start_time) >= max_wait_seconds:
            try:
                current_driver.find_element(by=By.ID, value="end").click()
            except Exception:
                pass
            return ""

        time.sleep(0.15)

# Main execution block.
if __name__ == "__main__":
    try:
        while True:
            # Continuously perform speech recognition and print the recognized text.
            Text = SpeechRecognition()
            if Text:
                print(Text)
    finally:
        if driver is not None:
            driver.quit()
