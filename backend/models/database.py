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
    conn.commit()
    conn.close()
    print("✅ Database initialized")

if __name__ == "__main__":
    init_db()