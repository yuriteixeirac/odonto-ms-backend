import os

import pika
from dotenv import load_dotenv
from pika.adapters.blocking_connection import BlockingChannel

load_dotenv()

LEMBRETES_WHATSAPP_QUEUE = "lembretes_whatsapp"


def get_rabbitmq_conn() -> pika.BlockingConnection:
    return pika.BlockingConnection(
        parameters=pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST") or "localhost",
            port=int(os.getenv("RABBITMQ_PORT") or 5672),
            credentials=pika.PlainCredentials(
                username=os.getenv("RABBITMQ_USERNAME") or "root",
                password=os.getenv("RABBITMQ_PASSWORD") or "",
            ),
        )
    )


def get_channel() -> tuple[pika.BlockingConnection, BlockingChannel]:
    conn = get_rabbitmq_conn()
    channel = conn.channel()

    channel.queue_declare(LEMBRETES_WHATSAPP_QUEUE, durable=True)

    return conn, channel
