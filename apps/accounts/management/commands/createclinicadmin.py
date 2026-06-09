from django.core.management.base import BaseCommand

from apps.accounts.enums import Cargo
from apps.accounts.models import Clinica
from apps.accounts.models.usuario import Usuario


class Command(BaseCommand):
    help = "Cria uma clínica e um superusuário associado a ela."

    def add_arguments(self, parser):
        parser.add_argument("--clinica", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--nome", required=True)
        parser.add_argument("--sobrenome", required=True)

    def handle(self, *args, **options):
        clinica, _ = Clinica.objects.get_or_create(nome=options["clinica"])  # type: ignore

        password = input("Senha: ")

        user = Usuario.objects.create_superuser(
            email=options["email"],
            password=password,
            clinica=clinica,
            cargo=Cargo.ADMIN,
        )

        self.stdout.write(f"Superusuário criado: {user.email}")
