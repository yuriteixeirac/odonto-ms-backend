from django.core.management.base import BaseCommand

from apps.accounts.enums import Cargo
from apps.accounts.models import Clinica
from apps.accounts.models.usuario import Usuario
from apps.accounts.serializers.usuario_serializers import UsuarioInputSerializer


class Command(BaseCommand):
    help = "Cria ou consulta uma clínica e um superusuário associado a ela."

    def add_arguments(self, parser):
        parser.add_argument("--clinica", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--nome", required=True)
        parser.add_argument("--sobrenome", required=True)
        parser.add_argument("--telefone", required=True)

    def handle(self, *args, **options):
        clinica, _ = Clinica.objects.get_or_create(nome=options["clinica"])  # type: ignore

        password = input("Senha: ")

        options["clinica"] = clinica

        serializer = UsuarioInputSerializer(
            data={
                "email": options["email"],
                "nome": options["nome"],
                "sobrenome": options["sobrenome"],
                "telefone": options["telefone"],
                "clinica": clinica,
                "password": password,
            }
        )

        if not serializer.is_valid():
            self.stderr.write(
                msg=f"Falha na serialização dos dados de entrada: {serializer.errors}"
            )
            return

        usuario = Usuario.objects.create_superuser(
            **serializer.validated_data, clinica=clinica
        )

        self.stdout.write(f"Superusuário criado: {usuario.email}")
