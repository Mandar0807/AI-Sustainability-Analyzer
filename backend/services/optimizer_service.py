from services.llm_service import call_llm

OPTIMIZATION_INSTRUCTION = """You are a prompt optimization expert. 
Your task is to rewrite the following prompt in fewer words while preserving its complete meaning and intent.

Rules:
- Keep the same language as the original prompt
- Preserve all key information and requirements
- Remove unnecessary words, redundancy, and filler phrases
- The optimized prompt must be shorter than the original
- Return ONLY the optimized prompt, nothing else, no explanations

Original prompt:
{prompt}

Optimized prompt:"""

def optimize_prompt(prompt: str, model_key: str) -> str:
    """
    Send prompt to LLM with optimization instruction.
    Returns optimized (shorter) version of the prompt.
    """
    instruction = OPTIMIZATION_INSTRUCTION.format(prompt=prompt)

    try:
        result = call_llm(model_key, instruction)
        optimized = result["text"].strip()

        # Validate - optimized must be shorter than original
        if len(optimized) >= len(prompt):
            print(f"Warning: Optimized prompt is not shorter. Using original.")
            return prompt

        # Remove quotes if model wrapped the response in them
        if optimized.startswith('"') and optimized.endswith('"'):
            optimized = optimized[1:-1]
        if optimized.startswith("'") and optimized.endswith("'"):
            optimized = optimized[1:-1]

        return optimized

    except Exception as e:
        print(f"Optimization failed for {model_key}: {e}")
        return prompt  # Return original if optimization fails

def optimize_and_compare(prompt: str, model_key: str) -> dict:
    """
    Optimize the prompt and return both original and optimized versions
    with basic comparison stats.
    """
    optimized = optimize_prompt(prompt, model_key)

    original_words = len(prompt.split())
    optimized_words = len(optimized.split())
    original_chars = len(prompt)
    optimized_chars = len(optimized)

    word_reduction = round(
        ((original_words - optimized_words) / original_words) * 100, 2
    ) if original_words > 0 else 0

    return {
        "original_prompt": prompt,
        "optimized_prompt": optimized,
        "original_words": original_words,
        "optimized_words": optimized_words,
        "original_chars": original_chars,
        "optimized_chars": optimized_chars,
        "word_reduction_pct": word_reduction
    }