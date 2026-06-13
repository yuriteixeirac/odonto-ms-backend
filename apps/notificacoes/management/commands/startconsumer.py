from django.core.management.base import BaseCommand

from apps.notificacoes.queue.consumer import start_consumer


class Command(BaseCommand):
    help = "Inicia os consumidores da fila de lembretes."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando consumidor de fila de lembretes.")
        start_consumer()
