import pika, json, uuid, time
from datetime import datetime
import os

def connect_to_rabbitmq(retries=5, delay=2):
    rabbit_host = os.getenv("RABBITMQ_HOST", "localhost")
    for _ in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
            channel = connection.channel()
            channel.queue_declare(queue='trace_queue')
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("⏳ Esperando RabbitMQ...")
            time.sleep(delay)
    raise Exception("❌ No se pudo conectar a RabbitMQ")

def publish_trace_event(path, method, status, body):
    try:
        connection, channel = connect_to_rabbitmq()
        event = {
            "eventId": str(uuid.uuid4()),
            "eventType": "TRACE_REQUEST",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": {
                "path": path,
                "method": method,
                "status_code": status,
                "body": body
            }
        }
        channel.basic_publish(
            exchange='',
            routing_key='trace_queue',
            body=json.dumps(event)
        )
        channel.close()
        connection.close()
    except Exception as e:
        print("❌ Error publicando evento:", e)
