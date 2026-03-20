from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import init_db
from routes.analyze import router as analyze_router
from routes.history import router as history_router

app = FastAPI(
    title="AI Sustainability Analyzer",
    description="Analyze and optimize AI prompts for sustainability",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "AI Sustainability Analyzer API is running"}

@app.get("/models")
def get_models():
    from config import MODELS
    return {
        "models": [
            {
                "key": key,
                "name": val["name"],
                "provider": val["provider"],
                "parameters": val["parameters"]
            }
            for key, val in MODELS.items()
        ]
    }

app.include_router(analyze_router)
app.include_router(history_router)