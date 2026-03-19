import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Carbon intensity (IEA global average gCO2/kWh)
CARBON_INTENSITY = 475

# GPU compute rate (A100 GPU FLOPS)
GPU_COMPUTE_RATE = 312e12

# Model configurations
MODELS = {
    "groq": {
        "name": "Llama 3.3 70B",
        "model_id": "llama-3.3-70b-versatile",
        "provider": "Groq",
        "parameters": 70e9,
        "tokenizer": "NousResearch/Meta-Llama-3-8B"  # Open version, same tokenizer
    },
    "cohere": {
        "name": "Command R Plus",
        "model_id": "command-r-plus-08-2024",
        "provider": "Cohere",
        "parameters": 104e9,
        "tokenizer": "mistralai/Mistral-7B-v0.1"  # Similar tokenizer as fallback
    },
    "mistral": {
        "name": "Mistral Small",
        "model_id": "mistral-small-latest",
        "provider": "Mistral AI",
        "parameters": 22e9,
        "tokenizer": "mistralai/Mistral-7B-v0.1"
    },
    "openrouter": {
        "name": "Gemma 3 27B",
        "model_id": "google/gemma-3-27b-it:free",
        "provider": "OpenRouter",
        "parameters": 27e9,
        "tokenizer": "Qwen/Qwen2.5-72B-Instruct"  # Similar BPE tokenizer
    },
    "huggingface": {
        "name": "Qwen 2.5 72B",
        "model_id": "Qwen/Qwen2.5-72B-Instruct",
        "provider": "HuggingFace",
        "parameters": 72e9,
        "tokenizer": "Qwen/Qwen2.5-72B-Instruct"
    }
}