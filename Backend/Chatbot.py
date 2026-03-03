from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from pathlib import Path
from Backend.FolderContext import get_folder_context_message

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
CHAT_LOG_PATH = PROJECT_ROOT / "Data" / "ChatLog.json"

env_vars = dotenv_values(ENV_PATH)

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)
messages = []

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}.
Follow these rules:
- Reply only in English, even if the user asks in another language.
- Do not mention training data.
- Do not provide the current time unless the user asks for it.
- Give detailed and practical answers by default.
- When useful, structure responses with sections, bullet points, and step-by-step instructions.
- If the user asks how to do something, include concrete steps and examples.
- Use clear markdown-style structure in responses (e.g., ## headings, 1. numbered steps, - bullet points).
- For explanatory answers, use this default format:
  1) ## Quick Answer
  2) ## Steps
  3) ## Tips or Common Mistakes
  4) ## Next Actions
- When providing code, always use fenced code blocks with a language tag, like ```python.
- Keep spacing clean: add a blank line between sections and before/after code blocks.
- Only keep responses very short when the user explicitly asks for brevity.
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

try:
    with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)
except FileNotFoundError:
    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
        dump([], f)


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = "Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data


def AnswerModifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)


def chatBot(query):
    try:
        with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
            messages = load(f)

        messages.append({"role": "user", "content": f"{query}"})

        folder_context = get_folder_context_message()
        context_messages = []
        if folder_context:
            context_messages.append({"role": "system", "content": folder_context})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + context_messages + [{"role": "system", "content": RealtimeInformation()}] + messages,
            temperature=0.6,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None,
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer=answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
            dump([], f, indent=4)
        return "Sorry, I encountered an error. Please try again."


if __name__ == "__main__":
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        response = chatBot(query)
        print(f"{Assistantname}: {response}")
