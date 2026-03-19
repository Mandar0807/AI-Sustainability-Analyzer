import sys
sys.path.append('.')

from services.tokenizer_service import count_tokens, count_tokens_both

test_prompt = "What is artificial intelligence? Explain in detail."
test_response = "Artificial intelligence is the simulation of human intelligence in machines."

print("Testing tokenizer service...\n")

models = ["groq", "cohere", "mistral", "openrouter", "huggingface"]

for model in models:
    print(f"Testing {model}...")
    try:
        result = count_tokens_both(test_prompt, test_response, model)
        print(f"✅ {model}")
        print(f"   Prompt tokens:   {result['prompt_tokens']}")
        print(f"   Response tokens: {result['response_tokens']}")
        print(f"   Total tokens:    {result['total_tokens']}")
    except Exception as e:
        print(f"❌ {model} failed: {e}")
    print()