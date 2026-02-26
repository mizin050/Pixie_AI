# Realtime Search Engine module
from googlesearch import search
from groq import Groq # Importing the Groq library to use its API.
from json import load, dump # Importing functions to read and write JSON files.
import datetime # Importing the datetime module for real time date and time information.
import os
import re
from pathlib import Path
import requests
from dotenv import dotenv_values # Importing dotenv_values to read environment variables from a .env file.
from Backend.FolderContext import get_folder_context_message

# Resolve project paths relative to this file, not the current working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
CHAT_LOG_PATH = PROJECT_ROOT / "Data" / "ChatLog.json"

# Load environment variables from the .env file.
env_vars = dotenv_values(ENV_PATH)

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username") or os.getenv("Username") or "User"
Assistantname = env_vars.get("Assistantname") or os.getenv("Assistantname") or "Assistant"
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

if not GroqAPIKey:
    raise RuntimeError(
        "Missing Groq API key. Set 'GroqAPIKey' or 'GROQ_API_KEY' in .env or environment variables."
    )

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Prefer web results when available. If web results are missing, answer from general knowledge and clearly say if a fact may have changed. ***
*** If live values are provided in system context, use them directly and do not claim data is unavailable. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.
try:
    CHAT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)
except:
    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
        dump([], f)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    try:
        Answer = f"The search results for '{query}' are:\n[start]\n"
        google_results = list(search(query, advanced=True, num_results=5))
        for i in google_results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        if not google_results:
            return (
                f"No live web results were found for '{query}'. "
                "Use your general knowledge and mention uncertainty for time-sensitive facts."
            )

        Answer += "[end]"
        return Answer
    except Exception:
        return (
            f"Live search is currently unavailable for '{query}'. "
            "Use your general knowledge and mention uncertainty for time-sensitive facts."
        )


def FinanceSnapshot(query):
    q = query.lower()
    if "apple" not in q:
        return ""

    lines = []

    # Live-ish stock quote (delayed) from Stooq.
    if "stock" in q or "share" in q or "price" in q or "aapl" in q:
        try:
            response = requests.get("https://stooq.com/q/l/?s=aapl.us&i=5", timeout=10)
            if response.ok:
                parts = response.text.strip().split(",")
                if len(parts) >= 7:
                    symbol, date, time, _open, high, low, close = parts[:7]
                    lines.append(
                        f"Apple stock snapshot: Symbol={symbol}, Date={date}, Time={time}, Last/Close={close}, High={high}, Low={low}."
                    )
        except Exception:
            pass

    # Market cap snapshot from CompaniesMarketCap page metadata.
    if "networth" in q or "net worth" in q or "market cap" in q or "valuation" in q:
        try:
            response = requests.get(
                "https://companiesmarketcap.com/apple/marketcap/",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if response.ok:
                match = re.search(
                    r"As of ([A-Za-z]+ \d{4}) Apple has a market cap of (\$[0-9.]+ [A-Za-z]+ USD)",
                    response.text,
                )
                if match:
                    as_of, market_cap = match.groups()
                    lines.append(f"Apple market cap snapshot: {market_cap} (as of {as_of}).")
        except Exception:
            pass

    if not lines:
        return ""
    return "Finance data:\n" + "\n".join(lines)

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global messages

    # Load the chat log from the JSON file.
    with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    # Build per-request context to avoid mutating shared global state.
    search_context = GoogleSearch(prompt)
    finance_context = FinanceSnapshot(prompt)
    folder_context = get_folder_context_message()
    conversation = SystemChatBot + [{"role": "system", "content": search_context}]
    if folder_context:
        conversation.append({"role": "system", "content": folder_context})
    if finance_context:
        conversation.append({"role": "system", "content": finance_context})
    recent_messages = messages[-12:]

    # Generate a response using the Groq client.
    try:
        completion = client.chat.completions.create(
            model=GroqModel,
            messages=conversation + [{"role": "system", "content": Information()}] + recent_messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )
    except Exception as e:
        return AnswerModifier(f"Model request failed: {e}")

    Answer = ""

    # Concatenate response chunks from the streaming output.
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean up the response.
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save the updated chat log back to the JSON file.
    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer=Answer)

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
