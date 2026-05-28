import time
from config import (
    GROQ_API_KEY, COHERE_API_KEY, MISTRAL_API_KEY,
    CEREBRAS_API_KEY, HUGGINGFACE_API_KEY, MODELS
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

    for attempt in range(2):  # Try twice (once, then retry after wait)
        try:
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
        except Exception as e:
            err_str = str(e)
            # 429 rate limit — wait and retry once
            if "429" in err_str or "capacity exceeded" in err_str.lower() or "rate" in err_str.lower():
                if attempt == 0:
                    print(f"   Mistral rate limit hit. Waiting 15s before retry...")
                    time.sleep(15)
                    continue
                raise Exception(
                    "Mistral API rate limit exceeded (429). "
                    "Free tier has limited requests. Please wait 1-2 minutes and try again."
                )
            raise  # Re-raise other errors as-is

def call_openrouter(prompt: str) -> dict:
    from openai import OpenAI

    client = OpenAI(
        base_url="https://api.cerebras.ai/v1",
        api_key=CEREBRAS_API_KEY
    )

    response = client.chat.completions.create(
        model=MODELS["openrouter"]["model_id"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )

    return {
        "text": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "response_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

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