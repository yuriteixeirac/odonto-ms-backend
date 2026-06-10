from datetime import time, timedelta

from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.enums import Cargo
from apps.accounts.models.clinica import Clinica
from apps.accounts.models.usuario import Usuario


class ExpedienteTest(APITestCase):
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

    def test_criar_expediente(self):
        inicio = time.fromisoformat("10:00:00")
        fim = timedelta(
            hours=inicio.hour, minutes=inicio.minute, seconds=inicio.second
        ) + timedelta(hours=8)

        self.client.force_authenticate(self.admin)  # type: ignore

        response = self.client.post(
            reverse("expediente-list"),
            data={
                "dia": 2,
                "inicio": inicio,
                "fim": fim,
                "clinico": self.clinico.id,  # type: ignore
            },
        )

        self.assertEqual(response.status_code, 201)  # type: ignore

    def test_criar_expediente_com_horario_invalido(self):
        inicio = time.fromisoformat("10:00:00")
        fim = timedelta(
            hours=inicio.hour, minutes=inicio.minute, seconds=inicio.second
        ) - timedelta(hours=8)

        self.client.force_authenticate(self.admin)  # type: ignore

        response = self.client.post(
            reverse("expediente-list"),
            data={
                "dia": 2,
                "inicio": inicio,
                "fim": fim,
                "clinico": self.clinico.id,  # type: ignore
            },
        )

        self.assertEqual(response.status_code, 400)  # type: ignore

    def test_criar_expedientes_no_mesmo_dia(self):
        inicio = time.fromisoformat("10:00:00")
        fim = timedelta(
            hours=inicio.hour, minutes=inicio.minute, seconds=inicio.second
        ) + timedelta(hours=8)

        self.client.force_authenticate(self.admin)  # type: ignore

        first_response = self.client.post(
            reverse("expediente-list"),
            data={
                "dia": 3,
                "inicio": inicio,
                "fim": fim,
                "clinico": self.clinico.id,  # type: ignore
            },
        )

        second_response = self.client.post(
            reverse("expediente-list"),
            data={
                "dia": 3,
                "inicio": inicio,
                "fim": fim,
                "clinico": self.clinico.id,  # type: ignore
            },
        )

        self.assertEqual(first_response.status_code, 201)  # type: ignore
        self.assertEqual(second_response.status_code, 400)  # type: ignore
