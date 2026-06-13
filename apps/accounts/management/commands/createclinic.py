from getpass import getpass

from django.core.management import CommandError
from django.core.management.base import BaseCommand

from apps.accounts.enums import Cargo
from apps.accounts.models import Clinica
from apps.accounts.models.usuario import Usuario
from apps.accounts.serializers.usuario_serializers import UsuarioInputSerializer
from apps.accounts.services import CEPService
from apps.accounts.validators import validate_phone


class Command(BaseCommand):
    help = "Cria ou consulta uma clínica e um usuário administrador associado a ela."

    def add_arguments(self, parser):
        parser.add_argument("--nome", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--telefone", required=True)
        parser.add_argument("--cep", required=True)

    def handle(self, *args, **options):
        endereco = CEPService.get_endereco(options["cep"])
        telefone = options["telefone"]

        validate_phone(telefone)

        clinica, criada = Clinica.objects.get_or_create(
            nome=options["nome"],
            defaults={
                "email": options["email"],
                "telefone": options["telefone"],
                "endereco": endereco,
            },
        )

        if not criada:
            raise CommandError(f"Clínica já existente encontrada: {clinica.nome}")

        self.stdout.write(f"Clínica criada: {clinica.id}. {clinica.nome}")
