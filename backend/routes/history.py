from fastapi import APIRouter, HTTPException
from models.database import get_connection

router = APIRouter()

@router.get("/history")
def get_history(limit: int = 20, offset: int = 0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM prompt_history
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return {"history": [dict(row) for row in rows]}

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