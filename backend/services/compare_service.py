import asyncio
import time
from config import MODELS
from services.metrics_service import calculate_all_metrics
from services.tokenizer_service import count_tokens
from services.nlp_service import analyze_and_optimize

def detect_prompt_category(prompt: str) -> str:
    prompt_lower = prompt.lower()
    categories = {
        "code": ["write code", "function", "program", "script",
                 "implement", "algorithm", "python", "javascript",
                 "debug", "fix the", "class ", "def "],
        "explanation": ["explain", "what is", "describe", "tell me about",
                       "how does", "what are", "define"],
        "comparison": ["difference between", "compare", " vs ",
                      "versus", "better than", "which is"],
        "creative": ["write a", "create a", "generate", "compose",
                    "story", "poem", "essay"],
        "analysis": ["analyze", "evaluate", "assess", "review",
                    "pros and cons", "advantages"],
        "factual": ["who", "when", "where", "how many",
                   "what year", "which country"]
    }
    for category, keywords in categories.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return category
    return "general"

def detect_complexity(prompt: str) -> str:
    word_count = len(prompt.split())
    if word_count <= 10:
        return "simple"
    elif word_count <= 25:
        return "medium"
    else:
        return "complex"

async def call_model_async(model_key: str, prompt: str) -> dict:
    """
    Call a single model asynchronously.
    Returns result dict with success flag.
    """
    start_time = time.time()
    try:
        loop = asyncio.get_event_loop()

        # Run the synchronous LLM call in a thread pool
        from services.llm_service import call_llm
        result = await loop.run_in_executor(
            None,
            call_llm,
            model_key,
            prompt
        )

        response_time = round(time.time() - start_time, 2)

        # Count tokens
        prompt_tokens = count_tokens(prompt, model_key)
        response_tokens = count_tokens(result["text"], model_key)

        # Calculate metrics
        metrics = calculate_all_metrics(
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            model_key=model_key
        )

        return {
            "model_key": model_key,
            "model_name": MODELS[model_key]["name"],
            "provider": MODELS[model_key]["provider"],
            "parameters": MODELS[model_key]["parameters"],
            "success": True,
            "response": result["text"],
            "response_time": response_time,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": metrics["total_tokens"],
            "flops": metrics["flops"],
            "energy_kwh": metrics["energy_kwh"],
            "co2_grams": metrics["co2_grams"],
            "error": None
        }

    except Exception as e:
        response_time = round(time.time() - start_time, 2)
        return {
            "model_key": model_key,
            "model_name": MODELS[model_key]["name"],
            "provider": MODELS[model_key]["provider"],
            "parameters": MODELS[model_key]["parameters"],
            "success": False,
            "response": None,
            "response_time": response_time,
            "prompt_tokens": None,
            "response_tokens": None,
            "total_tokens": None,
            "flops": None,
            "energy_kwh": None,
            "co2_grams": None,
            "error": str(e)[:200]
        }

def rank_results(results: list) -> list:
    """
    Rank successful results by CO2 emissions (lowest = best).
    Failed results go to end.
    """
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    # Sort successful by CO2
    successful.sort(key=lambda x: x["co2_grams"])

    # Add rank and medals
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, result in enumerate(successful):
        result["rank"] = i + 1
        result["medal"] = medals[i] if i < len(medals) else str(i + 1)

    # Failed results get no rank
    for result in failed:
        result["rank"] = None
        result["medal"] = "❌"

    return successful + failed

def calculate_insights(results: list) -> dict:
    """
    Calculate comparative insights from all model results.
    """
    successful = [r for r in results if r["success"]]

    if not successful:
        return {"error": "No models succeeded"}

    most_efficient = min(successful, key=lambda x: x["co2_grams"])
    least_efficient = max(successful, key=lambda x: x["co2_grams"])
    fastest = min(successful, key=lambda x: x["response_time"])
    most_tokens = max(successful, key=lambda x: x["total_tokens"])

    # Calculate efficiency gap
    if least_efficient["co2_grams"] > 0:
        efficiency_gap = round(
            ((least_efficient["co2_grams"] - most_efficient["co2_grams"])
             / least_efficient["co2_grams"]) * 100, 1
        )
    else:
        efficiency_gap = 0

    return {
        "most_efficient_model": most_efficient["model_key"],
        "most_efficient_name": most_efficient["model_name"],
        "least_efficient_model": least_efficient["model_key"],
        "least_efficient_name": least_efficient["model_name"],
        "fastest_model": fastest["model_key"],
        "fastest_name": fastest["model_name"],
        "most_detailed_model": most_tokens["model_key"],
        "most_detailed_name": most_tokens["model_name"],
        "efficiency_gap_percent": efficiency_gap,
        "recommendation": f"Use {most_efficient['model_name']} — saves {efficiency_gap}% CO₂ vs {least_efficient['model_name']}",
        "total_successful": len(successful),
        "total_failed": len(results) - len(successful)
    }

async def run_comparison(prompt: str) -> dict:
    """
    Main comparison function.
    Runs all 5 models simultaneously using asyncio.gather.
    """
    model_keys = list(MODELS.keys())

    # Run all models simultaneously
    tasks = [call_model_async(model_key, prompt) for model_key in model_keys]
    results = await asyncio.gather(*tasks)
    results = list(results)

    # Rank results
    ranked_results = rank_results(results)

    # Calculate insights
    insights = calculate_insights(ranked_results)

    # NLP analysis of the prompt
    try:
        nlp_analysis = analyze_and_optimize(prompt)
        prompt_grade = nlp_analysis.get("original_grade", "N/A")
        prompt_efficiency = nlp_analysis.get("original_efficiency_score", 0)
    except Exception:
        prompt_grade = "N/A"
        prompt_efficiency = 0

    # Detect prompt features
    category = detect_prompt_category(prompt)
    complexity = detect_complexity(prompt)

    return {
        "prompt": prompt,
        "prompt_category": category,
        "prompt_complexity": complexity,
        "prompt_grade": prompt_grade,
        "prompt_efficiency_score": prompt_efficiency,
        "results": ranked_results,
        "insights": insights,
        "total_models": len(model_keys)
    }