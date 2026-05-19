from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.nlp_service import analyze_and_optimize

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
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))