from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to load environment variables from a .env file.
from pathlib import Path

# Resolve project paths relative to this file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
CHAT_LOG_PATH = PROJECT_ROOT / "Data" / "ChatLog.json"

# Load environment variables from the .env file.
env_vars = dotenv_values(ENV_PATH)

# Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages.
messages = []

# Define a system message that provides context to the AI chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information.
**• Do not tell time until i ask, do not talk too much, just answer the question.**•
**• Reply in only English, even if the question is in Hindi, reply in English.**•
**• Do not provide notes in the output, just answer the question and never mention your training data. **•
"""

# List of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# Attempt to load the chat log from a JSON file.
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = load(f)  # Load existing messages from the chat log.
except FileNotFoundError:
    # If the file doesn't exist, create an empty JSON file to store chat logs.
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f)

# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()  # Get the current date and time.
    day = current_date_time.strftime("%A")  # Day of the week.
    date = current_date_time.strftime("%d")  # Day of the month.
    month = current_date_time.strftime("%B")  # Full month name.
    year = current_date_time.strftime("%Y")  # Year.
    hour = current_date_time.strftime("%H")  # Hour in 24-hour format.
    minute = current_date_time.strftime("%M")  # Minute.
    second = current_date_time.strftime("%S")  # Second.
    
    # Format the information into a string.
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines)  # Join the cleaned lines back together.
    return modified_answer

# Main chatbot function to handle user queries.
def chatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    
    try:
        # Load the existing chat log from the JSON file.
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)
        
        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": f"{Query}"})
        
        # Make a request to the Groq API to get a response.
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,  # Include system instructions, real-time info, & messages
            temperature=0.7,  # Adjust response randomness (higher means more random).
            top_p=1,  # Use nucleus sampling (controls diversity).
            stream=True,  # Enable streaming response.
            stop=None  # Allow the model to determine when to stop.
        )
        
        Answer = ""  # Initialize an empty string to store the AI's response.
        
        # Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check if there's content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the answer.
        
        Answer = Answer.replace("</s>", "")  # Clean up any unwanted tokens from the response.
        
        # Append the AI's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})
        
        # Save the updated chat log to the JSON file.
        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)
        
        # Return the modified answer.
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        # Handle errors by printing the error and resetting the chat log.
        print(f"Error: {e}")
        with open(CHAT_LOG_PATH, "w") as f:
            dump([], f, indent=4)
        return "Sorry, I encountered an error. Please try again."


# Main execution
if __name__ == "__main__":
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        response = chatBot(query)
        print(f"{Assistantname}: {response}")
