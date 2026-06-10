from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.enums import Cargo
from apps.accounts.models.clinica import Clinica
from apps.accounts.models.usuario import Usuario


class ProcedimentoTest(APITestCase):
    admin = None
    clinico = None
    clinica = None

    def setUp(self) -> None:
        self.clinica = Clinica.objects.create(
            nome="Clínica dos Bobos",
            telefone="76767676767",
            email="clinica@teste.com",
            endereco={"mock": "mock"},
        )

        self.admin = Usuario.objects.create_superuser(
            email="admin@teste.com",
            nome="Admin",
            sobrenome="da Silva",
            telefone="99999999991",
            cargo=Cargo.ADMIN,
            password="teste123",
            clinica=self.clinica,
        )

        self.clinico = Usuario.objects.create_user(
            email="clinico@teste.com",
            nome="Clínico",
            sobrenome="da Silva",
            telefone="99999999999",
            cargo=Cargo.CLINICO,
            password="teste123",
            clinica=self.clinica,
        )

    def test_criar_procedimento(self):
        self.client.force_authenticate(self.admin)  # type: ignore

        response = self.client.post(
            reverse("procedimento-list"),
            data={"nome": "Canal", "duracao": 90, "valor": 120.0},
        )

        self.assertEqual(response.status_code, 201)  # type: ignore

    def test_criar_procedimento_com_tempo_menor_que_um(self):
        self.client.force_authenticate(self.admin)  # type: ignore

        response = self.client.post(
            reverse("procedimento-list"),
            data={"nome": "Limpeza", "duracao": -67, "valor": 120.0},
        )

        self.assertNotEqual(response.status_code, 201)  # type: ignore

    def test_criar_procedimento_com_valor_menor_ou_igual_a_zero(self):
        self.client.force_authenticate(self.admin)  # type: ignore

        response = self.client.post(
            reverse("procedimento-list"),
            data={"nome": "Manutenção", "duracao": 90, "valor": -120.0},
        )

        self.assertNotEqual(response.status_code, 201)  # type: ignore
