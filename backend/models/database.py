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

    # Original single model analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analysis_type TEXT DEFAULT 'single',
            model_key TEXT,
            model_name TEXT,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT DEFAULT '',
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
            co2_reduction REAL,
            nlp_original_tokens INTEGER,
            nlp_optimized_tokens INTEGER,
            nlp_tokens_saved INTEGER,
            nlp_percent_saved REAL,
            nlp_grade TEXT,
            nlp_efficiency_score INTEGER,
            nlp_issues_count INTEGER,
            nlp_rule_tokens_saved INTEGER,
            nlp_llmlingua_tokens_saved INTEGER,
            compare_results TEXT,
            compare_winner TEXT,
            compare_winner_name TEXT,
            compare_efficiency_gap REAL,
            compare_fastest TEXT,
            compare_fastest_name TEXT,
            compare_total_successful INTEGER,
            compare_total_failed INTEGER
        )
    ''')

    # Dataset table for recommendations
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

    # Add new columns to existing table if they dont exist
    new_columns = [
        ("analysis_type", "TEXT DEFAULT 'single'"),
        ("nlp_original_tokens", "INTEGER"),
        ("nlp_optimized_tokens", "INTEGER"),
        ("nlp_tokens_saved", "INTEGER"),
        ("nlp_percent_saved", "REAL"),
        ("nlp_grade", "TEXT"),
        ("nlp_efficiency_score", "INTEGER"),
        ("nlp_issues_count", "INTEGER"),
        ("nlp_rule_tokens_saved", "INTEGER"),
        ("nlp_llmlingua_tokens_saved", "INTEGER"),
        ("compare_results", "TEXT"),
        ("compare_winner", "TEXT"),
        ("compare_winner_name", "TEXT"),
        ("compare_efficiency_gap", "REAL"),
        ("compare_fastest", "TEXT"),
        ("compare_fastest_name", "TEXT"),
        ("compare_total_successful", "INTEGER"),
        ("compare_total_failed", "INTEGER"),
    ]

    for col_name, col_type in new_columns:
        try:
            cursor.execute(
                f"ALTER TABLE prompt_history ADD COLUMN {col_name} {col_type}"
            )
        except Exception:
            pass  # Column already exists

    conn.commit()
    conn.close()
    print("✅ Database initialized")

if __name__ == "__main__":
    init_db()