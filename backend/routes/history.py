from fastapi import APIRouter, HTTPException
from models.database import get_connection

router = APIRouter()

@router.get("/history")
def get_history(limit: int = 20, offset: int = 0, model_key: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    if model_key:
        cursor.execute('''
            SELECT * FROM prompt_history
            WHERE model_key = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (model_key, limit, offset))
    else:
        cursor.execute('''
            SELECT * FROM prompt_history
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

    rows = cursor.fetchall()

    # Get total count
    if model_key:
        cursor.execute(
            "SELECT COUNT(*) FROM prompt_history WHERE model_key = ?",
            (model_key,)
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM prompt_history")

    total = cursor.fetchone()[0]
    conn.close()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "history": [dict(row) for row in rows]
    }

@router.get("/history/{history_id}")
def get_history_item(history_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM prompt_history WHERE id = ?",
        (history_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    return dict(row)

@router.delete("/history/{history_id}")
def delete_history(history_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM prompt_history WHERE id = ?",
        (history_id,)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"success": True, "message": f"Entry {history_id} deleted"}

@router.delete("/history")
def clear_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompt_history")
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return {"success": True, "message": f"Deleted {deleted} entries"}

@router.get("/stats")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Total analyses
    cursor.execute("SELECT COUNT(*) FROM prompt_history")
    total_analyses = cursor.fetchone()[0]

    if total_analyses == 0:
        conn.close()
        return {
            "total_analyses": 0,
            "average_token_reduction": 0,
            "average_energy_reduction": 0,
            "average_co2_reduction": 0,
            "total_co2_saved_grams": 0,
            "total_energy_saved_kwh": 0,
            "total_tokens_saved": 0,
            "most_used_model": None,
            "model_usage": {}
        }

    # Averages
    cursor.execute('''
        SELECT
            AVG(token_reduction) as avg_token,
            AVG(energy_reduction) as avg_energy,
            AVG(co2_reduction) as avg_co2,
            SUM(original_co2 - optimized_co2) as total_co2_saved,
            SUM(original_energy - optimized_energy) as total_energy_saved,
            SUM(original_total_tokens - optimized_total_tokens) as total_tokens_saved
        FROM prompt_history
    ''')
    row = cursor.fetchone()

    # Model usage count
    cursor.execute('''
        SELECT model_key, model_name, COUNT(*) as usage_count
        FROM prompt_history
        GROUP BY model_key
        ORDER BY usage_count DESC
    ''')
    model_rows = cursor.fetchall()
    conn.close()

    model_usage = {
        r["model_key"]: {
            "name": r["model_name"],
            "count": r["usage_count"]
        }
        for r in model_rows
    }

    most_used = model_rows[0]["model_key"] if model_rows else None

    return {
        "total_analyses": total_analyses,
        "average_token_reduction": round(row["avg_token"] or 0, 2),
        "average_energy_reduction": round(row["avg_energy"] or 0, 2),
        "average_co2_reduction": round(row["avg_co2"] or 0, 2),
        "total_co2_saved_grams": round(row["total_co2_saved"] or 0, 8),
        "total_energy_saved_kwh": round(row["total_energy_saved"] or 0, 8),
        "total_tokens_saved": int(row["total_tokens_saved"] or 0),
        "most_used_model": most_used,
        "model_usage": model_usage
    }