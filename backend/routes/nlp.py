import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.nlp_service import analyze_and_optimize
from models.database import get_connection

router = APIRouter()

class NLPRequest(BaseModel):
    prompt: str

@router.post("/nlp-optimize")
async def nlp_optimize(request: NLPRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if len(prompt) < 3:
        raise HTTPException(status_code=400, detail="Prompt too short")

    try:
        result = analyze_and_optimize(prompt)

        # Save to history
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prompt_history (
                    analysis_type,
                    model_key,
                    model_name,
                    original_prompt,
                    optimized_prompt,
                    nlp_original_tokens,
                    nlp_optimized_tokens,
                    nlp_tokens_saved,
                    nlp_percent_saved,
                    nlp_grade,
                    nlp_efficiency_score,
                    nlp_issues_count,
                    nlp_rule_tokens_saved,
                    nlp_llmlingua_tokens_saved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'nlp',
                'nlp',
                'NLP Optimizer',
                prompt,
                result.get('optimized_prompt', ''),
                result.get('original_token_count', 0),
                result.get('optimized_token_count', 0),
                result.get('total_tokens_saved', 0),
                result.get('total_percent_saved', 0),
                result.get('original_grade', ''),
                result.get('original_efficiency_score', 0),
                result.get('total_issues_found', 0),
                result.get('rule_based_tokens_saved', 0),
                result.get('llmlingua_additional_tokens_saved', 0)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not save NLP to history: {e}")

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))