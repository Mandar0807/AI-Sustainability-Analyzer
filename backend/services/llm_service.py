import time
from config import (
    GROQ_API_KEY, COHERE_API_KEY, MISTRAL_API_KEY,
    OPENROUTER_API_KEY, HUGGINGFACE_API_KEY, MODELS
)

def call_groq(prompt: str) -> dict:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=MODELS["groq"]["model_id"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {
        "text": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "response_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

def call_cohere(prompt: str) -> dict:
    import cohere
    client = cohere.ClientV2(api_key=COHERE_API_KEY)
    response = client.chat(
        model=MODELS["cohere"]["model_id"],
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.message.content[0].text
    prompt_tokens = response.usage.tokens.input_tokens
    response_tokens = response.usage.tokens.output_tokens
    return {
        "text": text,
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": prompt_tokens + response_tokens
    }

def call_mistral(prompt: str) -> dict:
    from mistralai import Mistral
    client = Mistral(api_key=MISTRAL_API_KEY)
    response = client.chat.complete(
        model=MODELS["mistral"]["model_id"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {
        "text": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "response_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

def call_openrouter(prompt: str) -> dict:
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )

    fallback_models = [
        "google/gemma-3-27b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
    ]

    last_error = None
    for model_id in fallback_models:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            return {
                "text": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "response_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        except Exception as e:
            print(f"   OpenRouter model {model_id} failed, trying next...")
            last_error = e
            time.sleep(2)

    raise Exception(f"All OpenRouter models failed. Last error: {last_error}")

def call_huggingface(prompt: str) -> dict:
    from huggingface_hub import InferenceClient
    client = InferenceClient(token=HUGGINGFACE_API_KEY)
    response = client.chat.completions.create(
        model=MODELS["huggingface"]["model_id"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {
        "text": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "response_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

def call_llm(model_key: str, prompt: str) -> dict:
    dispatchers = {
        "groq": call_groq,
        "cohere": call_cohere,
        "mistral": call_mistral,
        "openrouter": call_openrouter,
        "huggingface": call_huggingface
    }
    if model_key not in dispatchers:
        raise ValueError(f"Unknown model key: {model_key}")
    return dispatchers[model_key](prompt)