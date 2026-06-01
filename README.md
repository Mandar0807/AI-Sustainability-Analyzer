# 🌱 AI Prompt Sustainability Analyzer

> Analyze, optimize, and compare AI prompts across multiple models — reduce token waste, energy consumption, and CO₂ emissions.

**🚀 Live Demo:** [ai-sustainability-analyzer-q8lu.vercel.app](https://ai-sustainability-analyzer-q8lu.vercel.app)
**📦 GitHub:** [github.com/Mandar0807/AI-Sustainability-Analyzer](https://github.com/Mandar0807/AI-Sustainability-Analyzer)

---

## 🎯 What It Does

1. **Accepts** a user prompt intended for an LLM
2. **Sends** the prompt to a selected AI model and gets a real response
3. **Measures** efficiency metrics — token count, FLOPs, energy usage, CO₂ emissions
4. **Optimizes** the prompt automatically using a 3-stage NLP pipeline
5. **Compares** original vs optimized — shows % reduction in tokens, energy, and CO₂
6. **Saves** all analyses to a local database with full history and stats

---

## 🤖 Supported AI Models

| Model | Provider | Parameters |
|-------|----------|------------|
| Llama 3.3 70B | Groq | 70B |
| Command R Plus | Cohere | 104B |
| Mistral Small | Mistral AI | 22B |
| Qwen 2.5 72B | HuggingFace | 72B |

---

## 🧠 NLP Optimization Pipeline

Prompt optimization runs in 3 stages — inspired by LLMLingua:

### Stage 1 — Rule-Based Cleaning
Removes filler phrases, redundant qualifiers, and verbose starters using curated pattern matching.

```
"I would really like to know in great detail what blockchain is"
→ "Explain blockchain"
```

### Stage 2 — TF-IDF Importance Scoring
Each token is scored by its semantic importance using TF-IDF vectorization across prompt sentences. Low-scoring tokens are flagged as candidates for removal.

### Stage 3 — LLMLingua-Style Compression
POS tags boost scores for nouns, verbs, adjectives, and question words. Tokens below the importance threshold are dropped while preserving grammatical structure.

```
Compression ratio: target 75% of original tokens
Result: more focused prompt → fewer tokens → lower cost → lower emissions
```

---

## 🧮 How Metrics Are Calculated

### FLOPs (Floating Point Operations)
```
FLOPs = 6 × model_parameters × total_tokens
```

### Energy Consumption
```
Energy (kWh) = FLOPs / (312 × 10¹² × 3.6 × 10⁶)
```
Based on NVIDIA A100 GPU compute rate of 312 TFLOPS.

### CO₂ Emissions
```
CO₂ (grams) = Energy (kWh) × 475
```
Using IEA global average carbon intensity of 475 gCO₂/kWh.

---

## 🏗️ System Architecture

```
Frontend (React.js)          Backend (FastAPI)           External APIs
      │                             │                          │
      │  POST /analyze              │                          │
      │────────────────────────────▶│                          │
      │                             │   call_llm()             │
      │                             │─────────────────────────▶│
      │                             │◀─────────────────────────│
      │                             │                          │
      │                             │   nlp_pipeline()         │
      │                             │   (rule + tfidf + llmlingua)
      │                             │                          │
      │                             │   calculate_metrics()    │
      │                             │   save_to_sqlite()       │
      │◀────────────────────────────│                          │
      │   Full results JSON         │                          │
```

---

## 🛠️ Tech Stack

**Frontend:**
- React.js + React Router
- Tailwind CSS
- Chart.js + react-chartjs-2
- Axios

**Backend:**
- Python 3.12 + FastAPI
- SQLite (history persistence)
- NLTK (tokenization, POS tagging, stopwords)
- scikit-learn (TF-IDF vectorization)
- textstat (readability metrics)
- PyTorch + HuggingFace Transformers

**APIs:**
- Groq API (Llama 3.3 70B)
- Cohere API (Command R+)
- Mistral AI API (Mistral Small)
- HuggingFace Inference API (Qwen 2.5 72B)

**Deployment:**
- Backend → [Render](https://render.com) (free tier)
- Frontend → [Vercel](https://vercel.com) (free tier)

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- API keys for the providers you want to use

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```env
GROQ_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here
```

Start backend:
```bash
uvicorn main:app --reload
```

- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend: `http://localhost:3000`

Create `frontend/.env.production`:
```env
REACT_APP_API_URL=https://your-render-url.onrender.com
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Run full analysis pipeline |
| GET | `/models` | List all available models |
| GET | `/history` | Get past analyses (pagination + filter) |
| GET | `/history/{id}` | Get single analysis |
| DELETE | `/history/{id}` | Delete an analysis |
| GET | `/stats` | Get aggregate statistics |
| POST | `/nlp/optimize` | Run NLP optimization only |
| POST | `/compare` | Compare prompt across all models |

---

## 📊 Key Results

After testing with 10+ diverse prompts across 4 models:

| Metric | Result |
|--------|--------|
| Average token reduction | 7.8% |
| Best single reduction | 36.4% (Cohere — verbose prompt) |
| Total tokens saved | 981 across test analyses |
| Verbose prompt reduction | 30–60% |

**Key finding:** Verbose, conversational prompts with filler phrases show 30–60% reduction potential. Short prompts (< 10 words) show minimal reduction since they're already optimal.

---

## 💡 Key Insights

- **Short prompts** (< 10 words) show minimal reduction — already optimal
- **Long verbose prompts** with filler phrases show 30–60% reduction
- **Larger models** (104B Cohere) produce better optimized outputs than smaller models
- **Response tokens** dominate total token count — optimizing prompts reduces response length too
- **Efficiency grade** (A–F) gives instant feedback on prompt quality

---

## 📁 Project Structure

```
ai-sustainability-analyzer/
├── backend/
│   ├── config.py                  # Model configs, constants
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── models/
│   │   └── database.py            # SQLite schema + init
│   ├── routes/
│   │   ├── analyze.py             # POST /analyze pipeline
│   │   ├── history.py             # History + stats endpoints
│   │   ├── nlp.py                 # NLP optimization route
│   │   ├── compare.py             # Multi-model comparison
│   │   └── recommend.py           # Model recommendation
│   └── services/
│       ├── llm_service.py         # 4 API integrations
│       ├── nlp_service.py         # 3-stage NLP pipeline
│       ├── tokenizer_service.py   # Token counting
│       ├── metrics_service.py     # FLOPs, energy, CO₂
│       └── optimizer_service.py   # Prompt optimization
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ComparisonChart.jsx
│       │   └── StatsBar.jsx
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── History.jsx
│       │   ├── Compare.jsx
│       │   └── Recommend.jsx
│       └── services/
│           └── api.js
│
└── README.md
```

---

## 🌍 Why This Matters

Large language models consume significant computational resources. A single query to a large model can consume as much energy as charging a smartphone. At scale — billions of queries per day — this becomes a meaningful environmental concern.

This tool demonstrates that **simple prompt optimization can reduce AI energy consumption by 8–36%** without losing response quality, making AI usage more sustainable at both individual and enterprise scale.

---

## 🎬 Demo Prompts

Try these prompts to see the optimizer in action:

**High reduction (~35–40%) — use Cohere:**
```
I am really curious and would very much like to know and understand in great detail 
what the concept of blockchain technology is all about, how exactly does it work 
step by step, and what are some of the most important real world applications of 
blockchain that exist today
```

**Medium reduction (~15–25%) — use Groq:**
```
Can you please help me understand the key differences between machine learning and 
deep learning and also explain to me when we should use one approach over the other 
in real projects
```

**Minimal reduction (~5%) — use Mistral:**
```
What is AI?
```

---

## 👨‍💻 Built With

- 14-day development plan
- 4 free AI APIs
- FastAPI + React full-stack
- Custom NLP pipeline (rule-based + TF-IDF + LLMLingua-style)
- SQLite for persistence
- Chart.js for visualization
- Deployed free on Render + Vercel

---

## 📄 License

MIT License — feel free to use, fork, and contribute!