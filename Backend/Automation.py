from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from pathlib import Path
from urllib.parse import quote_plus

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "Data"
env_vars = dotenv_values(ENV_PATH)
GroqAPIKey = (
    env_vars.get("GroqAPIKey")
    or env_vars.get("GROQ_API_KEY")
    or os.getenv("GroqAPIKey")
    or os.getenv("GROQ_API_KEY")
)
GroqModel = (
    env_vars.get("GroqModel")
    or env_vars.get("GROQ_MODEL")
    or os.getenv("GroqModel")
    or os.getenv("GROQ_MODEL")
    or "llama-3.3-70b-versatile"
)

# CSS classes for Google scraping
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOc",
           "LwkFKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {env_vars.get('Username')}, You're a content writer. You have to write content like letters."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        if client is None:
            return "Unable to generate content: missing Groq API key in .env."
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model=GroqModel,
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = str(Topic).strip()
    if Topic.lower().startswith("content "):
        Topic = Topic[8:].strip()
    if not Topic:
        return False

    ContentByAI = ContentWriterAI(Topic)
    file_path = DATA_DIR / f"{Topic.lower().replace(' ', '')}.txt"
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(str(file_path))
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYouTube(query):
    playonyt(query)
    return True

def OpenApp(AppName):
    AppName = AppName.lower()
    try:
        appopen(AppName, match_closest=True, output=True)
        return True
    except:
        def extract_links(html):
            if html is None: return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        search_query = quote_plus(f"{AppName} official website")
        url = f"https://www.google.com/search?q={search_query}"
        response = requests.get(url, headers={'User-Agent': useragent}, timeout=10)
        links = extract_links(response.text)
        if links:
            webopen(links[0])
            return True
        return False

def CloseApp(AppName):
    if "all" in AppName:
        return False
    try:
        close(AppName, match_closest=True, output=False)
        return True
    except:
        return False

def SystemAutomation(command):
    command = command.lower()
    if "unmute" in command:
        keyboard.press_and_release("volume mute")
    elif "mute" in command:
        keyboard.press_and_release("volume mute")
    elif "volume up" in command:
        keyboard.press_and_release("volume up")
    elif "volume down" in command:
        keyboard.press_and_release("volume down")
    return True

async def GoogleMaps(Topic):
    URL = f"https://www.google.com/search?q={quote_plus(Topic)}"
    headers = {'User-Agent': useragent}
    response = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for class_name in classes:
        element = soup.find(class_=class_name)
        if element:
            return element.get_text()
    return "No direct result found."

async def TranslateAndExecute(Query):
    Query = str(Query).strip()
    lower_query = Query.lower()
    if lower_query.startswith("google search "):
        GoogleSearch(Query[14:].strip())
    elif lower_query.startswith("youtube search "):
        YouTubeSearch(Query[15:].strip())
    elif lower_query.startswith("play "):
        PlayYouTube(Query[5:].strip())
    elif lower_query.startswith("open "):
        OpenApp(Query[5:].strip())
    elif lower_query.startswith("close "):
        CloseApp(Query[6:].strip())
    elif lower_query.startswith("content "):
        Content(Query)
    elif "volume" in lower_query or "mute" in lower_query:
        SystemAutomation(Query)
    else:
        result = await GoogleMaps(Query)
        print(result)

# Example Execution
if __name__ == "__main__":
    pass
