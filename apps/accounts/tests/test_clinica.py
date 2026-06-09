from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.models.clinica import Clinica
from apps.accounts.models.usuario import Usuario


class ClinicaTest(APITestCase):
    usuario = None
    clinica = None

    def setUp(self) -> None:
        self.clinica = Clinica(
            nome="Clínica dos Teste",
            telefone="99999999999",
            email="clinica@teste.com",
            endereco={
                "estado": "RN",
                "cidade": "Natal",
                "rua": "dos Bobos",
                "bairro": "Black Point",
            },
        )
        self.clinica.full_clean()
        self.clinica.save()

        self.usuario = Usuario.objects.create_superuser(
            email="teste@teste.com",
            password="teste123",
            nome="Teste",
            sobrenome="da Silva",
            telefone="99999999999",
            clinica=self.clinica,
        )

    def test_criar_clinica(self):
        self.client.force_authenticate(self.usuario)  # type: ignore
        response = self.client.post(
            reverse("clinica-list"),
            data={
                "nome": "Clínica de Teste",
                "cep": "70150-903",
                "telefone": "99999999999",
                "email": "testilson@teste.com",
            },
        )

        self.assertEqual(response.status_code, 201)  # type: ignore
