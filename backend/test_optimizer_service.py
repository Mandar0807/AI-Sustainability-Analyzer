import sys
sys.path.append('.')

from services.optimizer_service import optimize_and_compare

test_prompts = [
    "Can you please explain to me in great detail what the concept of blockchain technology is all about, including how it works and what are some of its real world applications?",
    "I would really like to know and understand what artificial intelligence is and how it is being used in modern technology today.",
    "Could you kindly help me understand the differences between machine learning and deep learning and also explain when we should use one over the other?"
]

models = ["groq", "cohere", "mistral", "huggingface"]

print("Testing optimizer service...\n")

for model in models:
    print(f"\n{'='*60}")
    print(f"Model: {model}")
    print(f"{'='*60}")
    for i, prompt in enumerate(test_prompts):
        print(f"\nPrompt {i+1}:")
        try:
            result = optimize_and_compare(prompt, model)
            print(f"  Original  ({result['original_words']} words): {result['original_prompt']}")
            print(f"  Optimized ({result['optimized_words']} words): {result['optimized_prompt']}")
            print(f"  Word reduction: {result['word_reduction_pct']}%")
        except Exception as e:
            print(f"  ❌ Failed: {e}")