from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.enums import Cargo
from apps.accounts.models.clinica import Clinica
from apps.accounts.models.usuario import Usuario
from apps.agenda.enums import Status
from apps.agenda.models.agendamento import Agendamento
from apps.agenda.models.paciente import Paciente
from apps.agenda.models.procedimento import Procedimento


class CalendarioTest(APITestCase):
    clinica = None
    clinico = None
    paciente = None

    def setUp(self) -> None:
        self.clinica = Clinica.objects.create(
            nome="Clínica para Testes",
            email="clinica@testes.com",
            telefone="84999999999",
            endereco={},
        )

        self.clinico = Usuario.objects.create_user(
            nome="Clínico",
            sobrenome="da Silva",
            telefone="84999999999",
            email="clinico@testes.com",
            password="teste123",
            clinica=self.clinica,
            cargo=Cargo.CLINICO,
        )

        self.paciente = Paciente.objects.create(
            nome="Yuri",
            sobrenome="Teixeira",
            cpf="73261292741",
            telefone="5599999999999",
            email="yuri@gmail.com",
            clinica=self.clinica,
        )

    def test_mes_e_ano_vazios(self):
        response = self._get_calendario()
        self.assertEqual(response.status_code, 400)

    def test_mes_invalido(self):
        response = self._get_calendario(ano=2026, mes=67)
        self.assertEqual(response.status_code, 400)

    def test_dias_vazios(self):
        response = self._get_calendario(ano=2026, mes=6)

        passou = True
        for dia in response.data["data"]["dias"]:
            for contagem in dia["contagem_por_status"].values():
                if contagem:
                    passou = False

        self.assertTrue(passou)

    from datetime import datetime, timedelta

    from django.utils import timezone

    def test_dia_com_agendamentos(self):
        procedimento = Procedimento.objects.create(
            nome="Canal",
            duracao=90,
            valor=120.0,
            clinica=self.clinica,
        )

        inicio_1 = timezone.make_aware(datetime(2026, 6, 10, 10, 0))
        fim_1 = inicio_1 + timedelta(minutes=procedimento.duracao)

        inicio_2 = timezone.make_aware(datetime(2026, 6, 10, 14, 0))
        fim_2 = inicio_2 + timedelta(minutes=procedimento.duracao)

        Agendamento.objects.create(
            inicio=inicio_1,
            fim=fim_1,
            clinico=self.clinico,
            procedimento=procedimento,
            status=Status.PENDENTE,
            paciente=self.paciente,
        )

        Agendamento.objects.create(
            inicio=inicio_2,
            fim=fim_2,
            clinico=self.clinico,
            procedimento=procedimento,
            status=Status.AGENDADO,
            paciente=self.paciente,
        )

        response = self._get_calendario(ano=2026, mes=6)

        self.assertEqual(response.status_code, 200, response.data)

        dia_10 = next(
            dia for dia in response.data["data"]["dias"] if dia["data"] == "2026-06-10"
        )

        self.assertEqual(dia_10["total"], 2)
        self.assertEqual(dia_10["contagem_por_status"][Status.PENDENTE], 1)
        self.assertEqual(dia_10["contagem_por_status"][Status.AGENDADO], 1)

    def _get_calendario(self, ano: int | None = None, mes: int | None = None):
        self.client.force_authenticate(self.clinico)
        query_params = {}
        if ano and mes:
            query_params = {"ano": ano, "mes": mes}

        return self.client.get(reverse("calendario_mensal"), data=query_params)
