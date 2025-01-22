import os
import json
import asyncio
from datetime import datetime
from termcolor import colored
import google.generativeai as genai
from openai import AsyncOpenAI

# Constants
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHAT_LOG_FILE = "chat_responses.json"
COMMANDS = {
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
    "gemini": "gemini-2.0-flash-thinking-exp-01-21",
    "o1": "o1",
    "deepseek": "deepseek/deepseek-r1",
    "qwen": "qwen/qwq-32b-preview"
}

# Single shared chat history
chat_history = []

def print_commands():
    print(colored("\nAvailable Commands:", "yellow"))
    for cmd, desc in COMMANDS.items():
        print(colored(f"{cmd}: {desc}", "yellow"))

def load_chat_log():
    try:
        if os.path.exists(CHAT_LOG_FILE):
            with open(CHAT_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(colored(f"Error loading chat log: {str(e)}", "red"))
        return []

def save_chat_log(chat_log):
    try:
        with open(CHAT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_log, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(colored(f"Error saving chat log: {str(e)}", "red"))

async def get_gemini_response(message):
    try:
        if not gemini_model:
            return "Gemini model not available"
        
        if not hasattr(get_gemini_response, 'chat'):
            get_gemini_response.chat = gemini_model.start_chat(history=[])
            for msg in chat_history:
                if msg["role"] == "user":
                    get_gemini_response.chat.send_message(msg["content"])
                    
        print(colored("Waiting for Gemini response...", "cyan"))
        response = get_gemini_response.chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

async def get_openai_response(client, model, message):
    try:
        if not client:
            return f"{model} client not available"
            
        print(colored(f"Waiting for {model} response...", "cyan"))
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": message})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"{model} Error: {str(e)}"

async def synthesize_responses(user_message, responses):
    try:
        if not openai_client:
            return "Cannot synthesize: OpenAI O1 not available"
            
        synthesis_prompt = f"""As an AI synthesizer, analyze these AI responses to the user's message and create a comprehensive, accurate response that combines the best insights from all sources.

User's Message: {user_message}

Responses from different AI models:
Model 1: {responses['gemini']}
Model 2: {responses['deepseek']}
Model 3: {responses['qwen']}
Model 4: {responses['o1']}

Create a well-structured response that:
1. Combines the unique insights from each model
2. Resolves any contradictions between the responses
3. Provides the most accurate and helpful information
4. Maintains a natural, conversational tone

"""

        messages = [
            {"role": "system", "content": "You are an expert AI response synthesizer."},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        print(colored("Synthesizing final response with O1...", "cyan"))
        response = await openai_client.chat.completions.create(
            model=MODELS["o1"],
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Synthesis Error: {str(e)}"

async def process_message(message):
    # Get responses from all models in parallel
    responses = {}
    tasks = [
        asyncio.create_task(get_gemini_response(message)),
        asyncio.create_task(get_openai_response(openrouter_client, MODELS["deepseek"], message)),
        asyncio.create_task(get_openai_response(openrouter_client, MODELS["qwen"], message)),
        asyncio.create_task(get_openai_response(openai_client, MODELS["o1"], message))
    ]
    
    results = await asyncio.gather(*tasks)
    
    responses = {
        "gemini": results[0],
        "deepseek": results[1],
        "qwen": results[2],
        "o1": results[3]
    }
    
    # Print individual responses
    print("\nIndividual model responses:")
    model_names = list(responses.keys())
    for i, response in enumerate(responses.values(), 1):
        print(colored(f"\nModel {i}:", "yellow"))
        print(colored(response, "white"))
    
    # Get final synthesized response
    final_response = await synthesize_responses(message, responses)
    
    # Save to chat history
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": final_response})
    
    # Save to log file
    chat_log = load_chat_log()
    chat_log.append({
        "timestamp": datetime.now().isoformat(),
        "user_message": message,
        "model_responses": {f"Model {i}": resp for i, resp in enumerate(responses.values(), 1)},
        "final_response": final_response
    })
    save_chat_log(chat_log)
    
    return final_response

async def main():
    print_commands()
    print(colored("\nFrankenthought Chat - Multiple AI Models with O1 Synthesis", "green"))
    print(colored("Type your message or use commands (--help to see commands)", "cyan"))
    
    while True:
        try:
            message = input(colored("\nYou: ", "cyan")).strip()
            
            if message.lower() == "--exit":
                print(colored("Goodbye!", "green"))
                break
                
            elif message.lower() == "--help":
                print_commands()
                continue
                
            elif message.lower() == "--clear":
                chat_history.clear()
                if hasattr(get_gemini_response, 'chat'):
                    delattr(get_gemini_response, 'chat')
                print(colored("\nChat history cleared", "green"))
                continue
                
            if not message:
                continue
                
            final_response = await process_message(message)
            print(colored("\nFINAL SYNTHESIZED RESPONSE:", "green"))
            print(colored(final_response, "green"))
            
        except Exception as e:
            print(colored(f"An error occurred: {str(e)}", "red"))

if __name__ == "__main__":
    asyncio.run(main()) 