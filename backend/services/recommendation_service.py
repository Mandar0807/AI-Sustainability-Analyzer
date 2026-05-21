from models.database import get_connection

def get_dataset_count() -> int:
    """Get total number of comparison entries in dataset."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM comparison_dataset")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def detect_category(prompt: str) -> str:
    """Detect prompt category using keyword matching."""
    prompt_lower = prompt.lower()
    categories = {
        "code": ["write code", "function", "program", "script",
                 "implement", "algorithm", "python", "javascript",
                 "debug", "fix", "class ", "def "],
        "explanation": ["explain", "what is", "describe",
                       "tell me about", "how does", "what are", "define"],
        "comparison": ["difference between", "compare", " vs ",
                      "versus", "better than", "which is"],
        "creative": ["write a", "create a", "generate",
                    "compose", "story", "poem", "essay"],
        "analysis": ["analyze", "evaluate", "assess",
                    "review", "pros and cons", "advantages"],
        "factual": ["who", "when", "where", "how many",
                   "what year", "which country"]
    }
    for category, keywords in categories.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return category
    return "general"

def get_complexity(prompt: str) -> str:
    """Detect prompt complexity by word count."""
    word_count = len(prompt.split())
    if word_count <= 10:
        return "simple"
    elif word_count <= 25:
        return "medium"
    return "complex"

def get_recommendation(prompt: str) -> dict:
    """
    Main recommendation function.
    
    Algorithm:
    1. Check if we have enough data (min 10 entries)
    2. Detect prompt category and complexity
    3. Find similar prompts in dataset
    4. Count which model was most efficient most often
    5. Return recommendation with confidence level
    """

    # Step 1 — Check data availability
    total_count = get_dataset_count()

    if total_count < 5:
        return {
            "available": False,
            "reason": f"Need {5 - total_count} more comparisons to enable recommendations",
            "total_analyses": total_count,
            "required": 5
        }

    # Step 2 — Analyze new prompt
    category = detect_category(prompt)
    complexity = get_complexity(prompt)
    word_count = len(prompt.split())

    # Step 3 — Find similar prompts in dataset
    conn = get_connection()
    cursor = conn.cursor()

    # Find prompts with same category
    cursor.execute('''
        SELECT
            most_efficient_model,
            groq_tokens, groq_co2, groq_success,
            cohere_tokens, cohere_co2, cohere_success,
            mistral_tokens, mistral_co2, mistral_success,
            openrouter_tokens, openrouter_co2, openrouter_success,
            huggingface_tokens, huggingface_co2, huggingface_success,
            prompt_word_count, prompt_complexity
        FROM comparison_dataset
        WHERE prompt_category = ?
        ORDER BY created_at DESC
        LIMIT 50
    ''', (category,))

    similar = cursor.fetchall()

    # If not enough similar by category, get all
    if len(similar) < 3:
        cursor.execute('''
            SELECT
                most_efficient_model,
                groq_tokens, groq_co2, groq_success,
                cohere_tokens, cohere_co2, cohere_success,
                mistral_tokens, mistral_co2, mistral_success,
                openrouter_tokens, openrouter_co2, openrouter_success,
                huggingface_tokens, huggingface_co2, huggingface_success,
                prompt_word_count, prompt_complexity
            FROM comparison_dataset
            ORDER BY created_at DESC
            LIMIT 50
        ''')
        similar = cursor.fetchall()
        used_category = "all"
    else:
        used_category = category

    conn.close()

    if not similar:
        return {
            "available": False,
            "reason": "No comparison data available yet",
            "total_analyses": total_count,
            "required": 10
        }

    # Step 4 — Count model efficiency wins
    model_wins = {
        "groq": 0,
        "cohere": 0,
        "mistral": 0,
        "openrouter": 0,
        "huggingface": 0
    }

    model_avg_co2 = {
        "groq": [],
        "cohere": [],
        "mistral": [],
        "openrouter": [],
        "huggingface": []
    }

    for row in similar:
        row = dict(row)
        winner = row.get("most_efficient_model")
        if winner and winner in model_wins:
            model_wins[winner] += 1

        # Collect CO2 averages
        for model in ["groq", "cohere", "mistral", "openrouter", "huggingface"]:
            co2_key = f"{model}_co2"
            success_key = f"{model}_success"
            if row.get(success_key) == 1 and row.get(co2_key):
                model_avg_co2[model].append(row[co2_key])

    # Step 5 — Calculate averages and find best model
    model_scores = {}
    for model in model_wins:
        avg_co2 = (
            sum(model_avg_co2[model]) / len(model_avg_co2[model])
            if model_avg_co2[model] else None
        )
        model_scores[model] = {
            "wins": model_wins[model],
            "avg_co2": avg_co2,
            "data_points": len(model_avg_co2[model])
        }

    # Find recommended model — most wins among those with data
    models_with_data = {
        k: v for k, v in model_scores.items()
        if v["data_points"] > 0
    }

    if not models_with_data:
        return {
            "available": False,
            "reason": "Insufficient model performance data",
            "total_analyses": total_count,
            "required": 10
        }

    # Primary sort: most wins. Secondary sort: lowest avg CO2
    recommended_key = max(
        models_with_data,
        key=lambda k: (
            models_with_data[k]["wins"],
            -models_with_data[k]["avg_co2"] if models_with_data[k]["avg_co2"] else 0
        )
    )

    recommended = models_with_data[recommended_key]

    # Calculate confidence
    total_similar = len(similar)
    win_ratio = recommended["wins"] / total_similar if total_similar > 0 else 0

    if win_ratio >= 0.6:
        confidence = "high"
        confidence_pct = round(win_ratio * 100)
    elif win_ratio >= 0.35:
        confidence = "medium"
        confidence_pct = round(win_ratio * 100)
    else:
        confidence = "low"
        confidence_pct = round(win_ratio * 100)

    # Model display names
    model_names = {
        "groq": "Llama 3.3 70B",
        "cohere": "Command R Plus",
        "mistral": "Mistral Small",
        "openrouter": "Gemma 3 27B",
        "huggingface": "Qwen 2.5 72B"
    }

    # Build ranked list for display
    ranked_models = sorted(
        [
            {
                "key": k,
                "name": model_names.get(k, k),
                "wins": v["wins"],
                "avg_co2": v["avg_co2"],
                "data_points": v["data_points"]
            }
            for k, v in models_with_data.items()
        ],
        key=lambda x: (x["wins"], -(x["avg_co2"] or 999)),
        reverse=True
    )

    return {
        "available": True,
        "recommended_model": recommended_key,
        "recommended_name": model_names.get(recommended_key, recommended_key),
        "confidence": confidence,
        "confidence_pct": confidence_pct,
        "wins": recommended["wins"],
        "avg_co2": recommended["avg_co2"],
        "total_similar": total_similar,
        "category_used": used_category,
        "prompt_category": category,
        "prompt_complexity": complexity,
        "total_analyses": total_count,
        "ranked_models": ranked_models,
        "reason": (
            f"For {category} prompts, {model_names.get(recommended_key)} "
            f"was most efficient in {recommended['wins']} of {total_similar} "
            f"similar analyses ({confidence_pct}% confidence)"
        )
    }