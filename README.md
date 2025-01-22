# Multi-Model Chat System

This repository contains two different implementations of a multi-model chat system that leverages various AI models for enhanced conversational capabilities.

## Files

### 1. multi-chat.py

A chat system that allows users to switch between different AI models during conversation:

- Supports Gemini, OpenAI (O1), DeepSeek, and Qwen models
- Maintains conversation history across model switches
- Features command-line interface with colored output
- Commands:
  - `--change`: Switch to a different model
  - `--clear`: Clear chat history
  - `--exit`: Exit the chat
  - `--help`: Show available commands

### 2. frankenthought-chat.py

An advanced implementation that runs all reasoning models in parallel and synthesizes their responses:

- Parallel execution of:
  1. Google's Gemini (gemini-2.0-flash-thinking-exp-01-21)
  2. OpenAI's O1 model
  3. DeepSeek's R1 model (via OpenRouter)
  4. Qwen's 32B Preview model (via OpenRouter)
- Uses OpenAI's O1 model again for final synthesis of all responses
- Maintains a detailed chat log in JSON format
- Features:
  - Parallel processing of model responses
  - Response synthesis combining insights from all models
  - Detailed logging of all responses and final synthesis
  - Commands:

    - `--clear`: Clear chat history
    - `--exit`: Exit the chat
    - `--help`: Show available commands

## 🎥 Watch How It's Built!

**[Watch the complete build process on Patreon](https://www.patreon.com/posts/how-to-build-o1-112197565?utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=postshare_creator&utm_content=join_link)**
See exactly how this  was created step by step, with detailed explanations and insights into the development process at my 1000x Cursor Course


## ❤️ Join my AI community & Get 400+ AI Projects

This is one of 400+ fascinating projects in my collection! [Support me on Patreon](https://www.patreon.com/c/echohive42/membership) to get:

- 🎯 Access to 400+ AI projects (and growing daily!)
  - Including advanced projects like [2 Agent Real-time voice template with turn taking](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 Full source code & detailed explanations
- 📚 1000x Cursor Course
- 🎓 Live coding sessions & AMAs
- 💬 1-on-1 consultations (higher tiers)
- 🎁 Exclusive discounts on AI tools & platforms (up to $180 value)

## Setup

1. Set up environment variables:

```bash
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running multi-chat.py

```bash
python multi-chat.py
```

- Select a model using numbers 1-4
- Chat normally
- Use `--change` to switch models
- Previous chat history is maintained when switching models

### Running frankenthought-chat.py

```bash
python frankenthought-chat.py
```

- Type your message
- See responses from all models (anonymized as Model 1-4)
- Get a synthesized response combining insights from all models
- All interactions are logged in `chat_responses.json`

## Features

### Common Features

- Colored terminal output for better readability
- Error handling and graceful degradation
- UTF-8 encoding for all file operations
- Async API calls for better performance

### multi-chat.py Specific

- Model switching while maintaining context
- Individual model conversations
- Chat history persistence across model changes

### frankenthought-chat.py Specific

- Parallel model execution of 4 different models
- Two-stage process:
  1. Get parallel responses from all models
  2. Use O1 to synthesize a final response
- Comprehensive JSON logging
- Anonymous model responses (Model 1, Model 2, etc.)
- Detailed chat history with timestamps

## Chat Log Format (frankenthought-chat.py)

```json
{
  "timestamp": "ISO-8601 timestamp",
  "user_message": "User's input",
  "model_responses": {
    "Model 1": "Response from first model",
    "Model 2": "Response from second model",
    "Model 3": "Response from third model",
    "Model 4": "Response from fourth model"
  },
  "final_response": "Synthesized response"
}
```

## Error Handling

- Graceful handling of API failures
- Informative error messages
- Continued operation if some models are unavailable
- Safe file operations with proper error catching

## Dependencies

- google-generativeai
- openai
- termcolor
- httpx

## Notes

- API keys must be set as environment variables
- Models may have different response times
- JSON log file grows with usage - consider periodic cleanup
- All models maintain conversation context
- O1 is used twice in frankenthought-chat.py:
  1. As one of the parallel responders
  2. As the final synthesizer of all responses
