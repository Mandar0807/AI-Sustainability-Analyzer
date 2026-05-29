from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import init_db
import nltk
import os

def download_nltk_data():
    nltk_dir = '/opt/render/nltk_data'
    os.makedirs(nltk_dir, exist_ok=True)
    packages = [
        'stopwords', 'punkt', 'punkt_tab',
        'wordnet', 'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng', 'omw-1.4'
    ]
    for pkg in packages:
        try:
            nltk.download(pkg, download_dir=nltk_dir, quiet=True)
        except Exception:
            pass

download_nltk_data()

from routes.analyze import router as analyze_router
from routes.history import router as history_router
from routes.nlp import router as nlp_router
from routes.compare import router as compare_router
from routes.recommend import router as recommend_router

app = FastAPI(
    title="AI Sustainability Analyzer",
    description="Analyze and optimize AI prompts for sustainability",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-sustainability-analyzer-q8lu.vercel.app",
    ],
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
app.include_router(nlp_router)
app.include_router(compare_router)
app.include_router(recommend_router)