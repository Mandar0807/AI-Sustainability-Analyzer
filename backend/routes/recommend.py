from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.recommendation_service import get_recommendation

router = APIRouter()

class RecommendRequest(BaseModel):
    prompt: str

@router.post("/recommend")
async def recommend_model(request: RecommendRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        result = get_recommendation(prompt)
        return {
            "success": True,
            "recommendation": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset/count")
async def get_dataset_count():
    from services.recommendation_service import get_dataset_count
    count = get_dataset_count()
    return {
        "count": count,
        "recommendation_available": count >= 5
    }