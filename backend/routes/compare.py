import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.compare_service import run_comparison
from models.database import get_connection
from config import MODELS

router = APIRouter()

class CompareRequest(BaseModel):
    prompt: str

@router.post("/compare")
async def compare_models(request: CompareRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if len(prompt) < 3:
        raise HTTPException(status_code=400, detail="Prompt too short")

    try:
        print(f"\n[COMPARE] Running comparison for: {prompt[:50]}...")
        result = await run_comparison(prompt)

        # Save to comparison_dataset
        try:
            save_to_dataset(prompt, result)
        except Exception as e:
            print(f"Warning: Could not save to dataset: {e}")

        # Save to prompt_history
        try:
            save_to_history(prompt, result)
        except Exception as e:
            print(f"Warning: Could not save compare to history: {e}")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        print(f"Error in compare_models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def save_to_history(prompt: str, result: dict):
    """Save comparison result to unified prompt_history table."""
    conn = get_connection()
    cursor = conn.cursor()

    insights = result.get("insights", {})

    # Serialize full results as JSON string
    results_json = json.dumps(result.get("results", []))

    cursor.execute('''
        INSERT INTO prompt_history (
            analysis_type,
            model_key,
            model_name,
            original_prompt,
            optimized_prompt,
            compare_results,
            compare_winner,
            compare_winner_name,
            compare_efficiency_gap,
            compare_fastest,
            compare_fastest_name,
            compare_total_successful,
            compare_total_failed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'compare',
        'compare',
        'Cross Model Comparison',
        prompt,
        '',
        results_json,
        insights.get("most_efficient_model"),
        insights.get("most_efficient_name"),
        insights.get("efficiency_gap_percent"),
        insights.get("fastest_model"),
        insights.get("fastest_name"),
        insights.get("total_successful"),
        insights.get("total_failed")
    ))
    conn.commit()
    conn.close()
    print(f"[COMPARE] Saved to history")

def save_to_dataset(prompt: str, result: dict):
    """Save comparison result to dataset table."""
    conn = get_connection()
    cursor = conn.cursor()

    model_data = {}
    for r in result["results"]:
        model_data[r["model_key"]] = r

    def get_val(model_key, field, default=None):
        if model_key in model_data and model_data[model_key]["success"]:
            return model_data[model_key].get(field, default)
        return default

    cursor.execute('''
        INSERT INTO comparison_dataset (
            prompt_text, prompt_word_count, prompt_token_count,
            prompt_category, prompt_complexity,
            groq_tokens, groq_energy, groq_co2, groq_response_time, groq_success,
            cohere_tokens, cohere_energy, cohere_co2, cohere_response_time, cohere_success,
            mistral_tokens, mistral_energy, mistral_co2, mistral_response_time, mistral_success,
            openrouter_tokens, openrouter_energy, openrouter_co2, openrouter_response_time, openrouter_success,
            huggingface_tokens, huggingface_energy, huggingface_co2, huggingface_response_time, huggingface_success,
            most_efficient_model, least_efficient_model
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?
        )
    ''', (
        prompt, len(prompt.split()), len(prompt.split()),
        result.get("prompt_category", "general"),
        result.get("prompt_complexity", "medium"),
        get_val("groq", "total_tokens"), get_val("groq", "energy_kwh"),
        get_val("groq", "co2_grams"), get_val("groq", "response_time"),
        1 if model_data.get("groq", {}).get("success") else 0,
        get_val("cohere", "total_tokens"), get_val("cohere", "energy_kwh"),
        get_val("cohere", "co2_grams"), get_val("cohere", "response_time"),
        1 if model_data.get("cohere", {}).get("success") else 0,
        get_val("mistral", "total_tokens"), get_val("mistral", "energy_kwh"),
        get_val("mistral", "co2_grams"), get_val("mistral", "response_time"),
        1 if model_data.get("mistral", {}).get("success") else 0,
        get_val("openrouter", "total_tokens"), get_val("openrouter", "energy_kwh"),
        get_val("openrouter", "co2_grams"), get_val("openrouter", "response_time"),
        1 if model_data.get("openrouter", {}).get("success") else 0,
        get_val("huggingface", "total_tokens"), get_val("huggingface", "energy_kwh"),
        get_val("huggingface", "co2_grams"), get_val("huggingface", "response_time"),
        1 if model_data.get("huggingface", {}).get("success") else 0,
        result.get("insights", {}).get("most_efficient_model"),
        result.get("insights", {}).get("least_efficient_model")
    ))
    conn.commit()
    conn.close()