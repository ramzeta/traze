from fastapi import APIRouter
import sqlite3, threading

router = APIRouter()
conn = sqlite3.connect('./data/traces.db', check_same_thread=False)
lock = threading.Lock()

@router.get("/traces")
def get_all_traces():
    with lock:
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, timestamp, path, method, status_code, body FROM traces ORDER BY id DESC")
        return [
            {
                "event_id": r[0],
                "timestamp": r[1],
                "path": r[2],
                "method": r[3],
                "status_code": r[4],
                "body": r[5]
            } for r in cursor.fetchall()
        ]