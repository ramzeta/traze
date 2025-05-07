import pika, json, sqlite3, threading, os

db_path = "./data/traces.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
lock = threading.Lock()

cursor.execute('''
CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    timestamp TEXT,
    path TEXT,
    method TEXT,
    status_code INTEGER,
    body TEXT
)
''')
conn.commit()

def callback(ch, method, properties, body):
    event = json.loads(body)
    payload = event.get("payload", {})
    with lock:
        cursor.execute(
            '''INSERT INTO traces (event_id, timestamp, path, method, status_code, body)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                event.get("eventId"),
                event.get("timestamp"),
                payload.get("path"),
                payload.get("method"),
                payload.get("status_code"),
                payload.get("body")
            )
        )
        conn.commit()

def start_consumer():
    rabbit_host = os.getenv("RABBITMQ_HOST", "localhost")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue='trace_queue')
    channel.basic_consume(queue='trace_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

threading.Thread(target=start_consumer, daemon=True).start()