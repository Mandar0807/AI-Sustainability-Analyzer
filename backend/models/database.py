import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "history.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Existing table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_key TEXT NOT NULL,
            model_name TEXT NOT NULL,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            original_prompt_tokens INTEGER,
            original_response_tokens INTEGER,
            original_total_tokens INTEGER,
            original_flops REAL,
            original_energy REAL,
            original_co2 REAL,
            optimized_prompt_tokens INTEGER,
            optimized_response_tokens INTEGER,
            optimized_total_tokens INTEGER,
            optimized_flops REAL,
            optimized_energy REAL,
            optimized_co2 REAL,
            token_reduction REAL,
            energy_reduction REAL,
            co2_reduction REAL
        )
    ''')

    # New dataset table for comparison + recommendation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comparison_dataset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            prompt_text TEXT NOT NULL,
            prompt_word_count INTEGER,
            prompt_token_count INTEGER,
            prompt_category TEXT,
            prompt_complexity TEXT,
            prompt_filler_ratio REAL,
            prompt_readability_score REAL,
            groq_tokens INTEGER,
            groq_energy REAL,
            groq_co2 REAL,
            groq_response_time REAL,
            groq_success INTEGER DEFAULT 0,
            cohere_tokens INTEGER,
            cohere_energy REAL,
            cohere_co2 REAL,
            cohere_response_time REAL,
            cohere_success INTEGER DEFAULT 0,
            mistral_tokens INTEGER,
            mistral_energy REAL,
            mistral_co2 REAL,
            mistral_response_time REAL,
            mistral_success INTEGER DEFAULT 0,
            openrouter_tokens INTEGER,
            openrouter_energy REAL,
            openrouter_co2 REAL,
            openrouter_response_time REAL,
            openrouter_success INTEGER DEFAULT 0,
            huggingface_tokens INTEGER,
            huggingface_energy REAL,
            huggingface_co2 REAL,
            huggingface_response_time REAL,
            huggingface_success INTEGER DEFAULT 0,
            most_efficient_model TEXT,
            least_efficient_model TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

if __name__ == "__main__":
    init_db()