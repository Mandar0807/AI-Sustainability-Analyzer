import sys
sys.path.append('.')

from services.llm_service import call_llm

test_prompt = "What is artificial intelligence? Answer in 2 sentences."

models = ["groq", "cohere", "mistral", "openrouter", "huggingface"]

for model in models:
    print(f"\nTesting {model}...")
    try:
        result = call_llm(model, test_prompt)
        print(f"✅ {model}")
        print(f"   Response: {result['text'][:80]}...")
        print(f"   Tokens - Prompt: {result['prompt_tokens']}, Response: {result['response_tokens']}, Total: {result['total_tokens']}")
    except Exception as e:
        print(f"❌ {model} failed: {e}")