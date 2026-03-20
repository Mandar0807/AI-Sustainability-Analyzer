from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_service import call_llm
from services.tokenizer_service import count_tokens
from services.metrics_service import calculate_all_metrics, calculate_savings
from services.optimizer_service import optimize_prompt
from models.database import get_connection

router = APIRouter()

class AnalyzeRequest(BaseModel):
    prompt: str
    model_key: str

@router.post("/analyze")
async def analyze_prompt(request: AnalyzeRequest):
    prompt = request.prompt.strip()
    model_key = request.model_key

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if model_key not in ["groq", "cohere", "mistral", "openrouter", "huggingface"]:
        raise HTTPException(status_code=400, detail="Invalid model key")

    try:
        # ─────────────────────────────────────────
        # STEP 1: Send original prompt to LLM
        # ─────────────────────────────────────────
        print(f"\n[1] Sending original prompt to {model_key}...")
        llm_result = call_llm(model_key, prompt)
        original_response = llm_result["text"]

        # ─────────────────────────────────────────
        # STEP 2: Tokenize original prompt + response
        # ─────────────────────────────────────────
        print(f"[2] Tokenizing original prompt...")
        original_prompt_tokens = count_tokens(prompt, model_key)
        original_response_tokens = count_tokens(original_response, model_key)

        # ─────────────────────────────────────────
        # STEP 3: Calculate original metrics
        # ─────────────────────────────────────────
        print(f"[3] Calculating original metrics...")
        original_metrics = calculate_all_metrics(
            prompt_tokens=original_prompt_tokens,
            response_tokens=original_response_tokens,
            model_key=model_key
        )

        # ─────────────────────────────────────────
        # STEP 4: Optimize the prompt
        # ─────────────────────────────────────────
        print(f"[4] Optimizing prompt...")
        optimized_prompt = optimize_prompt(prompt, model_key)

        # ─────────────────────────────────────────
        # STEP 5: Send optimized prompt to LLM
        # ─────────────────────────────────────────
        print(f"[5] Sending optimized prompt to {model_key}...")
        optimized_llm_result = call_llm(model_key, optimized_prompt)
        optimized_response = optimized_llm_result["text"]

        # ─────────────────────────────────────────
        # STEP 6: Tokenize optimized prompt + response
        # ─────────────────────────────────────────
        print(f"[6] Tokenizing optimized prompt...")
        optimized_prompt_tokens = count_tokens(optimized_prompt, model_key)
        optimized_response_tokens = count_tokens(optimized_response, model_key)

        # ─────────────────────────────────────────
        # STEP 7: Calculate optimized metrics
        # ─────────────────────────────────────────
        print(f"[7] Calculating optimized metrics...")
        optimized_metrics = calculate_all_metrics(
            prompt_tokens=optimized_prompt_tokens,
            response_tokens=optimized_response_tokens,
            model_key=model_key
        )

        # ─────────────────────────────────────────
        # STEP 8: Calculate savings
        # ─────────────────────────────────────────
        print(f"[8] Calculating savings...")
        savings = calculate_savings(original_metrics, optimized_metrics)

        # ─────────────────────────────────────────
        # STEP 9: Save to SQLite database
        # ─────────────────────────────────────────
        print(f"[9] Saving to database...")
        from config import MODELS
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prompt_history (
                model_key, model_name,
                original_prompt, optimized_prompt,
                original_prompt_tokens, original_response_tokens, original_total_tokens,
                original_flops, original_energy, original_co2,
                optimized_prompt_tokens, optimized_response_tokens, optimized_total_tokens,
                optimized_flops, optimized_energy, optimized_co2,
                token_reduction, energy_reduction, co2_reduction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_key,
            MODELS[model_key]["name"],
            prompt,
            optimized_prompt,
            original_metrics["prompt_tokens"],
            original_metrics["response_tokens"],
            original_metrics["total_tokens"],
            original_metrics["flops"],
            original_metrics["energy_kwh"],
            original_metrics["co2_grams"],
            optimized_metrics["prompt_tokens"],
            optimized_metrics["response_tokens"],
            optimized_metrics["total_tokens"],
            optimized_metrics["flops"],
            optimized_metrics["energy_kwh"],
            optimized_metrics["co2_grams"],
            savings["token_reduction_pct"],
            savings["energy_reduction_pct"],
            savings["co2_reduction_pct"]
        ))
        conn.commit()
        history_id = cursor.lastrowid
        conn.close()

        # ─────────────────────────────────────────
        # STEP 10: Return full results
        # ─────────────────────────────────────────
        print(f"[10] Done! Returning results...")
        return {
            "success": True,
            "history_id": history_id,
            "model": {
                "key": model_key,
                "name": MODELS[model_key]["name"],
                "provider": MODELS[model_key]["provider"]
            },
            "original": {
                "prompt": prompt,
                "response": original_response,
                "metrics": original_metrics
            },
            "optimized": {
                "prompt": optimized_prompt,
                "response": optimized_response,
                "metrics": optimized_metrics
            },
            "savings": savings
        }

    except Exception as e:
        print(f"Error in analyze_prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))