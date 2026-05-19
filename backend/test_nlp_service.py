import sys
sys.path.append('.')

from services.nlp_service import analyze_and_optimize

test_prompts = [
    "Can you please explain to me in great detail what blockchain technology is all about and how it works?",
    "I would really like to know and understand what artificial intelligence is and how it is being used in modern technology today.",
    "Could you kindly help me understand the differences between machine learning and deep learning and also explain when we should use one over the other?",
    "What is AI?",
    "Write a Python function to implement binary search algorithm with detailed comments explaining each step"
]

print("Testing NLP Service...\n")

for i, prompt in enumerate(test_prompts):
    print(f"{'='*60}")
    print(f"Test {i+1}:")
    print(f"Original:  {prompt}")
    print(f"Words:     {len(prompt.split())}")

    result = analyze_and_optimize(prompt)

    print(f"\nIssues found: {result['total_issues_found']}")
    for issue in result['issues']:
        print(f"  [{issue['severity'].upper()}] {issue['type']}: '{issue['found']}' — {issue['suggestion']}")

    print(f"\nStage 2 (Rule-based): {result['rule_based_result']['prompt']}")
    print(f"  Saved: {result['rule_based_result']['tokens_saved']} tokens")

    print(f"\nStage 3 (LLMLingua):  {result['optimized_prompt']}")
    print(f"  Removed words: {result['removed_words']}")

    print(f"\nFinal Summary:")
    print(f"  Original tokens:  {result['original_token_count']}")
    print(f"  Optimized tokens: {result['optimized_token_count']}")
    print(f"  Total saved:      {result['total_tokens_saved']} ({result['total_percent_saved']}%)")
    print(f"  Grade:            {result['original_grade']}")
    print(f"  Time:             {result['processing_time_seconds']}s")
    print(f"  API cost:         ${result['api_cost']}")
    print()