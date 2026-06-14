import json
from pprint import pprint

from pika.adapters.blocking_connection import BlockingChannel
from pika.amqp_object import Properties
from pika.spec import Basic

from apps.agenda.enums import Status
from apps.agenda.models.agendamento import Agendamento
from apps.common import rabbitmq
from apps.notificacoes.models import WhatsAppInstance
from apps.notificacoes.service import WhatsappService


def consume_queue(
    ch: BlockingChannel,
    method: Basic.Deliver,
    properties: Properties,
    body: bytes,
):
    try:
        payload = json.loads(body)
        pprint(payload)

        wpp_service = WhatsappService()
        agendamento = Agendamento.objects.get(pk=payload["agendamento_id"])  # type: ignore

        if agendamento.status == Status.CANCELADO:
            print("Agendamento cancelado. Lembrete descartado.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if agendamento.inicio.isoformat() != payload.get("agendamento_inicio"):
            print("Agendamento remarcado. Lembrete antigo descartado.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        instancia = WhatsAppInstance.objects.filter(  # type: ignore
            clinica=agendamento.paciente.clinica
        ).first()

        if not instancia:
            print("Instância não encontrada.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        wpp_service.enviar_mensagem(
            instancia,
            telefone=agendamento.paciente.telefone,
            mensagem=f"Você tem uma consulta ({agendamento.procedimento}) com o/a clínico(a) {agendamento.clinico} amanhã às {str(agendamento.inicio.time()).split('.')[0][:-3]}.",
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print("Mensagem enviada ao número " + agendamento.paciente.telefone)
    except Exception as e:
        print(repr(e))
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    _, channel = rabbitmq.get_channel()

    channel.queue_declare(queue=rabbitmq.LEMBRETES_WHATSAPP_QUEUE, durable=True)
    channel.queue_declare(
        queue=rabbitmq.LEMBRETES_WHATSAPP_QUEUE_DELAY,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": rabbitmq.LEMBRETES_WHATSAPP_QUEUE,
        },
    )

    channel.basic_consume(
        queue=rabbitmq.LEMBRETES_WHATSAPP_QUEUE,
        on_message_callback=consume_queue,
        auto_ack=False,
    )
    channel.start_consuming()
