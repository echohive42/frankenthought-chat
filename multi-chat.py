import os
import asyncio
from termcolor import colored
import google.generativeai as genai
from openai import AsyncOpenAI

# Constants
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
COMMANDS = {
    "--change": "Change the current model",
    "--clear": "Clear the chat history",
    "--exit": "Exit the chat",
    "--help": "Show available commands"
}

# Model configurations
GEMINI_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 65536,
    "response_mime_type": "text/plain",
}

# Initialize clients
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-01-21",
        generation_config=GEMINI_CONFIG
    )
    print(colored("✓ Gemini initialized successfully", "green"))
except Exception as e:
    print(colored(f"✗ Error initializing Gemini: {str(e)}", "red"))
    gemini_model = None

try:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    print(colored("✓ OpenAI initialized successfully", "green"))
except Exception as e:
    print(colored(f"✗ Error initializing OpenAI: {str(e)}", "red"))
    openai_client = None

try:
    openrouter_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    print(colored("✓ OpenRouter initialized successfully", "green"))
except Exception as e:
    print(colored(f"✗ Error initializing OpenRouter: {str(e)}", "red"))
    openrouter_client = None

# Available models
MODELS = {
    1: ("Gemini", "gemini-2.0-flash-thinking-exp-01-21"),
    2: ("OpenAI", "o1"),
    3: ("DeepSeek", "deepseek/deepseek-r1"),
    4: ("Qwen", "qwen/qwq-32b-preview")
}

# Single shared chat history
chat_history = []

def print_models():
    print(colored("\nAvailable Models:", "yellow"))
    for num, (name, _) in MODELS.items():
        print(colored(f"{num}. {name}", "yellow"))
    print(colored("0. Exit", "red"))

def print_commands():
    print(colored("\nAvailable Commands:", "yellow"))
    for cmd, desc in COMMANDS.items():
        print(colored(f"{cmd}: {desc}", "yellow"))

def get_model_choice():
    while True:
        try:
            print_models()
            choice = int(input(colored("\nChoose a model (0-4): ", "cyan")))
            if choice == 0:
                print(colored("Goodbye!", "green"))
                return None
            if choice in MODELS:
                return choice
            print(colored("Invalid choice. Please try again.", "red"))
        except ValueError:
            print(colored("Please enter a valid number.", "red"))

async def send_openai_message(client, model, message):
    try:
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": message})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

async def chat_with_model(model_choice, message):
    try:
        model_name = MODELS[model_choice][0]
        model_id = MODELS[model_choice][1]
        
        print(colored(f"\nSending message to {model_name}...", "cyan"))
        
        if model_choice == 1 and gemini_model:  # Gemini
            if not hasattr(chat_with_model, 'gemini_chat'):
                chat_with_model.gemini_chat = gemini_model.start_chat(history=[])
                # Convert existing history to Gemini format and replay
                for msg in chat_history:
                    if msg["role"] == "user":
                        chat_with_model.gemini_chat.send_message(msg["content"])
            response = chat_with_model.gemini_chat.send_message(message)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response.text})
            return response.text
            
        elif model_choice == 2 and openai_client:  # OpenAI
            response = await send_openai_message(openai_client, model_id, message)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})
            return response
            
        elif model_choice in [3, 4] and openrouter_client:  # OpenRouter models
            response = await send_openai_message(openrouter_client, model_id, message)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})
            return response
            
        else:
            return "Selected model is not available."
            
    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    print_commands()
    current_model = get_model_choice()
    if current_model is None:
        return

    print(colored(f"\nChatting with {MODELS[current_model][0]}. Type --help for available commands.", "green"))
    
    while True:
        try:
            message = input(colored("\nYou: ", "cyan")).strip()
            
            if message.lower() == "--exit":
                print(colored("Goodbye!", "green"))
                break
                
            elif message.lower() == "--help":
                print_commands()
                continue
                
            elif message.lower() == "--change":
                new_model = get_model_choice()
                if new_model is None:
                    break
                current_model = new_model
                print(colored(f"\nSwitched to {MODELS[current_model][0]}", "green"))
                continue
                
            elif message.lower() == "--clear":
                chat_history.clear()
                if hasattr(chat_with_model, 'gemini_chat'):
                    delattr(chat_with_model, 'gemini_chat')
                print(colored("\nChat history cleared", "green"))
                continue
                
            if not message:
                continue
                
            response = await chat_with_model(current_model, message)
            print(colored(f"\n{MODELS[current_model][0]}: {response}", "green"))
            
        except Exception as e:
            print(colored(f"An error occurred: {str(e)}", "red"))

if __name__ == "__main__":
    asyncio.run(main())