import json

from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.enums import Cargo
from apps.accounts.models.clinica import Clinica
from apps.accounts.models.usuario import Usuario
from apps.common.redis import redis_cli


class ConviteTest(APITestCase):
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
            email="ze@test.com",
            nome="Zé",
            sobrenome="Maria",
            password="password",
            telefone="99999999999",
            clinica=self.clinica,
        )

    def tearDown(self) -> None:
        for key in redis_cli.scan_iter("convite:*"):
            redis_cli.delete(key)

    def test_criar_convite(self):
        self.client.force_authenticate(self.usuario)  # type: ignore
        response = self.client.post(
            reverse("criar_convite"), {"cargo": Cargo.CLINICO.value}, format="json"
        )

        self.assertEqual(response.status_code, 201)  # type: ignore

        convite_uuid = response.data["data"]["convite"]  # type: ignore
        convite = redis_cli.get(f"convite:{convite_uuid}")

        convite_data = json.loads(convite)  # type: ignore

        self.convite = convite_uuid

        self.assertIsNotNone(convite)
        self.assertEqual(convite_data["clinica_id"], self.clinica.id)  # type: ignore
        self.assertEqual(convite_data["cargo"], Cargo.CLINICO.value)

    def test_criar_convite_com_cargo_invalido(self):
        self.client.force_authenticate(self.usuario)  # type: ignore
        response = self.client.post(
            reverse("criar_convite"), {"cargo": "um-cargo-invalido"}, format="json"
        )

        self.assertEqual(response.status_code, 400)  # type: ignore

    def test_usuario_nao_autenticado_nao_cria_convite(self):
        response = self.client.post(
            reverse("criar_convite"), {"cargo": Cargo.AUXILIAR.value}, format="json"
        )

        self.assertEqual(response.status_code, 401)  # type: ignore

    def test_criar_usuario_com_convite(self):
        self.client.force_authenticate(self.usuario)  # type: ignore
        convite = self._criar_convite()

        response = self.client.post(
            reverse("usar_convite", kwargs={"convite_uuid": convite}),
            data={
                "email": "teste@test.com",
                "password": "teste123",
                "nome": "Teste",
                "sobrenome": "da Silva",
                "telefone": "99999999991",  # telefone diferente de quem adicionou
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)  # type: ignore

    def _criar_convite(self, cargo=Cargo.CLINICO.value):
        self.client.force_authenticate(user=self.usuario)  # type: ignore

        response = self.client.post(
            reverse("criar_convite"),
            {"cargo": cargo},
            format="json",
        )

        return response.data["data"]["convite"]  # type: ignore
