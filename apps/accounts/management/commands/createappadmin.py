from django.core.management.base import BaseCommand

from apps.accounts.enums import Cargo
from apps.accounts.models import Clinica
from apps.accounts.models.usuario import Usuario
from apps.accounts.serializers.usuario_serializers import UsuarioInputSerializer


class Command(BaseCommand):
    help = "Cria um superusuário para toda a aplicação."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--nome", required=True)
        parser.add_argument("--sobrenome", required=True)
        parser.add_argument("--telefone", required=True)

    def handle(self, *args, **options):
        password = input("Senha: ")

        serializer = UsuarioInputSerializer(
            data={
                "email": options["email"],
                "nome": options["nome"],
                "sobrenome": options["sobrenome"],
                "telefone": options["telefone"],
                "password": password,
            }
        )

        if not serializer.is_valid():
            self.stderr.write(
                msg=f"Falha na serialização dos dados de entrada: {serializer.errors}"
            )
            return

        usuario = Usuario.objects.create_superuser(**serializer.validated_data)  # type: ignore

        self.stdout.write(f"Superusuário criado: {usuario.email}")
