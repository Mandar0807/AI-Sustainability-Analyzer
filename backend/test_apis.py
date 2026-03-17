import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

print("Loaded keys check:")
print("GROQ:", os.getenv("GROQ_API_KEY", "NOT FOUND")[:10])
print("COHERE:", os.getenv("COHERE_API_KEY", "NOT FOUND")[:10])
print("MISTRAL:", os.getenv("MISTRAL_API_KEY", "NOT FOUND")[:10])
print("OPENROUTER:", os.getenv("OPENROUTER_API_KEY", "NOT FOUND")[:10])
print("HF:", os.getenv("HUGGINGFACE_API_KEY", "NOT FOUND")[:10])
print()

def test_groq():
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say hello in 5 words"}]
    )
    print("✅ Groq:", response.choices[0].message.content)

def test_cohere():
    import cohere
    client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    response = client.chat(
        model="command-r-plus-08-2024",
        messages=[{"role": "user", "content": "Say hello in 5 words"}]
    )
    print("✅ Cohere:", response.message.content[0].text)

def test_mistral():
    from mistralai import Mistral
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": "Say hello in 5 words"}]
    )
    print("✅ Mistral:", response.choices[0].message.content)

def test_openrouter():
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    response = client.chat.completions.create(
        model="google/gemma-3-27b-it:free",
        messages=[{"role": "user", "content": "Say hello in 5 words"}]
    )
    print("✅ OpenRouter:", response.choices[0].message.content)

def test_huggingface():
    from huggingface_hub import InferenceClient
    client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[{"role": "user", "content": "Say hello in 5 words"}]
    )
    print("✅ HuggingFace:", response.choices[0].message.content)

if __name__ == "__main__":
    print("Testing all APIs...\n")

    try: test_groq()
    except Exception as e: print("❌ Groq failed:", e)

    try: test_cohere()
    except Exception as e: print("❌ Cohere failed:", e)

    try: test_mistral()
    except Exception as e: print("❌ Mistral failed:", e)

    try: test_openrouter()
    except Exception as e: print("❌ OpenRouter failed:", e)

    try: test_huggingface()
    except Exception as e: print("❌ HuggingFace failed:", e)