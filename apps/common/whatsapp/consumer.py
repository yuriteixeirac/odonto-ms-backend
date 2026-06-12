import json

from pika.adapters.blocking_connection import BlockingChannel
from pika.amqp_object import Properties
from pika.frame import Method
from pika.spec import Basic

from apps.agenda.models.agendamento import Agendamento
from apps.common.rabbitmq import LEMBRETES_WHATSAPP_QUEUE, get_channel
from apps.common.whatsapp.service import WhatsappService


def consume_queue(
    ch: BlockingChannel, method: Basic.Deliver, properties: Properties, body: bytes
):
    try:
        payload = json.loads(body)

        whatsapp_service = WhatsappService("5584999999999")

        agendamento = Agendamento.objects.get(pk=payload["agendamento_id"])  # type: ignore
        whatsapp_service.enviar_lembrete(agendamento.paciente.telefone)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    conn, channel = get_channel()

    channel.basic_consume(
        queue=LEMBRETES_WHATSAPP_QUEUE, on_message_callback=consume_queue
    )
    channel.start_consuming()
