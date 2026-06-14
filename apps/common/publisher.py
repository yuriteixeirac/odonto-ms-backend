import json
from datetime import timedelta

from django.utils import timezone
from pika import BasicProperties

from apps.agenda.models.agendamento import Agendamento
from apps.common import rabbitmq


def publish_lembrete(agendamento: Agendamento):
    conn, channel = rabbitmq.get_channel()

    channel.queue_declare(rabbitmq.LEMBRETES_WHATSAPP_QUEUE, durable=True)
    channel.queue_declare(
        rabbitmq.LEMBRETES_WHATSAPP_QUEUE_DELAY,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": rabbitmq.LEMBRETES_WHATSAPP_QUEUE,
        },
    )

    inicio = agendamento.inicio - timedelta(hours=24)  # type: ignore
    agora = timezone.now()
    delay = int((inicio - agora).total_seconds() * 1000)

    if delay <= 0:
        routing_key = rabbitmq.LEMBRETES_WHATSAPP_QUEUE
        properties = BasicProperties(delivery_mode=2, content_type="application/json")
    else:
        routing_key = rabbitmq.LEMBRETES_WHATSAPP_QUEUE_DELAY
        properties = BasicProperties(
            delivery_mode=2, content_type="application/json", expiration=str(delay)
        )

    channel.basic_publish(
        exchange="",
        routing_key=routing_key,
        body=json.dumps(
            {
                "tipo": "lembrete_whatsapp",
                "agendamento_id": agendamento.id,
                "agendamento_inicio": agendamento.inicio.isoformat(),
            }
        ),
        properties=properties,
    )

    conn.close()
