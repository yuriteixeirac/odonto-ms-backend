import json

from apps import agenda
from apps.common.rabbitmq import LEMBRETES_WHATSAPP_QUEUE, get_channel


def publish_lembrete(agendamento_id: int):
    conn, channel = get_channel()

    channel.basic_publish(
        exchange="",
        routing_key=LEMBRETES_WHATSAPP_QUEUE,
        body=json.dumps(
            {"tipo": "lembrete_whatsapp", "agendamento_id": agendamento_id}
        ),
    )

    conn.close()
