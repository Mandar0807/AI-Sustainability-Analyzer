import sqlite3
from pathlib import Path

# Use absolute path so it always opens the correct DB regardless of where you run it
DB_PATH = Path(__file__).parent / "history.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Fix 1: Replace NULL optimized_prompt with empty string (for compare/NLP rows)
cursor.execute("UPDATE prompt_history SET optimized_prompt = '' WHERE optimized_prompt IS NULL")
print(f"Fix 1: Fixed {cursor.rowcount} NULL optimized_prompt rows")

# Fix 2: Set analysis_type = 'single' for old rows that were saved before the column existed
cursor.execute("""
    UPDATE prompt_history
    SET analysis_type = 'single'
    WHERE analysis_type IS NULL
    AND model_key NOT IN ('nlp', 'compare')
""")
print(f"Fix 2: Fixed {cursor.rowcount} NULL analysis_type rows -> set to 'single'")

conn.commit()
print("Done! Database fixed successfully.")
conn.close()