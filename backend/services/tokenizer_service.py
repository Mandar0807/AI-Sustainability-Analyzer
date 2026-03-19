from config import MODELS
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Cache tokenizers so we don't reload them every time
_tokenizer_cache = {}

def get_tokenizer(model_key: str):
    if model_key in _tokenizer_cache:
        return _tokenizer_cache[model_key]

    tokenizer_name = MODELS[model_key]["tokenizer"]
    print(f"Loading tokenizer for {model_key}: {tokenizer_name}")

    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name,
            trust_remote_code=True
        )
        _tokenizer_cache[model_key] = tokenizer
        return tokenizer
    except Exception as e:
        print(f"Warning: Could not load tokenizer for {model_key}: {e}")
        return None

def count_tokens(text: str, model_key: str) -> int:
    try:
        tokenizer = get_tokenizer(model_key)
        if tokenizer is None:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Tokenizer error for {model_key}: {e}")
        # Fallback estimate
        return len(text) // 4

def count_tokens_both(prompt: str, response: str, model_key: str) -> dict:
    prompt_tokens = count_tokens(prompt, model_key)
    response_tokens = count_tokens(response, model_key)
    return {
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": prompt_tokens + response_tokens
    }