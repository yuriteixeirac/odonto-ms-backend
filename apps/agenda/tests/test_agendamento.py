from datetime import time, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.enums import Cargo
from apps.accounts.models.clinica import Clinica
from apps.accounts.models.usuario import Usuario
from apps.agenda.enums import Dia, Status
from apps.agenda.models.agendamento import Agendamento
from apps.agenda.models.expediente import Expediente
from apps.agenda.models.procedimento import Procedimento


class AgendamentoTest(APITestCase):
    clinica: Clinica
    admin: Usuario
    clinico: Usuario
    recepcionista: Usuario
    procedimento: Procedimento

    def setUp(self) -> None:
        self.clinica = Clinica.objects.create(
            nome="Clínica dos Testes",
            email="clinica@test.com",
            telefone="84999999999",
            endereco={"rua": "dos Bobos"},
        )

        self.admin = Usuario.objects.create_superuser(
            email="admin@test.com",
            nome="Admin",
            sobrenome="dos Admantos",
            telefone="84999999998",
            password="test123",
            cargo=Cargo.ADMIN,
            clinica=self.clinica,
        )

        self.clinico = Usuario.objects.create_user(
            email="clinico@test.com",
            nome="Clínico",
            sobrenome="dos Clinicantos",
            telefone="84999999991",
            password="test123",
            cargo=Cargo.CLINICO,
            clinica=self.clinica,
        )

        self.recepcionista = Usuario.objects.create_user(
            email="recepcao@test.com",
            nome="Recepção",
            sobrenome="Teste",
            telefone="84999999992",
            password="test123",
            cargo=Cargo.RECEPCAO,
            clinica=self.clinica,
        )

        inicio, fim = time.fromisoformat("10:00:00"), time.fromisoformat("18:00:00")

        for dia in Dia.values:
            Expediente.objects.create(
                dia=dia,
                inicio=inicio,
                fim=fim,
                clinico=self.clinico,
            )

        self.procedimento = Procedimento.objects.create(
            nome="Canal",
            duracao=90,
            valor=120.0,
            clinica=self.clinica,
            ativo=True,
        )

    def _inicio_valido(self):
        return (timezone.now() + timedelta(days=1)).replace(
            hour=11,
            minute=0,
            second=0,
            microsecond=0,
        )

    def _payload(self, **overrides):
        payload = {
            "inicio": self._inicio_valido().isoformat(),
            "procedimento": self.procedimento.id,
            "clinico": self.clinico.id,
        }

        payload.update(overrides)
        return payload

    def test_criar_agendamento(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)

        agendamento = Agendamento.objects.first()

        self.assertIsNotNone(agendamento)
        self.assertEqual(agendamento.clinico, self.clinico)
        self.assertEqual(agendamento.procedimento, self.procedimento)
        self.assertEqual(agendamento.fim, agendamento.inicio + timedelta(minutes=90))

    def test_nao_cria_agendamento_no_passado(self):
        self.client.force_authenticate(user=self.admin)

        inicio_passado = timezone.now() - timedelta(days=1)

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(inicio=inicio_passado.isoformat()),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_nao_cria_agendamento_com_clinico_inexistente(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(clinico=999999),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_nao_cria_agendamento_com_usuario_que_nao_e_clinico(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(clinico=self.recepcionista.id),
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_nao_cria_agendamento_com_procedimento_inativo(self):
        self.client.force_authenticate(user=self.admin)

        self.procedimento.ativo = False
        self.procedimento.save()

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_nao_cria_agendamento_sem_expediente_no_dia(self):
        self.client.force_authenticate(user=self.admin)

        Expediente.objects.filter(clinico=self.clinico).delete()

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_nao_cria_agendamento_com_overlap(self):
        self.client.force_authenticate(user=self.admin)

        inicio = self._inicio_valido()

        Agendamento.objects.create(
            inicio=inicio,
            fim=inicio + timedelta(minutes=90),
            clinico=self.clinico,
            procedimento=self.procedimento,
            status=Status.AGENDADO,
        )

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(inicio=(inicio + timedelta(minutes=30)).isoformat()),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_agendamento_cancelado_nao_bloqueia_horario(self):
        self.client.force_authenticate(user=self.admin)

        inicio = self._inicio_valido()

        Agendamento.objects.create(
            inicio=inicio,
            fim=inicio + timedelta(minutes=90),
            clinico=self.clinico,
            procedimento=self.procedimento,
            status=Status.CANCELADO,
        )

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(inicio=inicio.isoformat()),
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Agendamento.objects.count(), 2)

    def test_nao_cria_agendamento_fora_do_horario_do_expediente(self):
        self.client.force_authenticate(user=self.admin)

        inicio_fora = self._inicio_valido().replace(hour=19, minute=0)

        response = self.client.post(
            reverse("agendamento-list"),
            data=self._payload(inicio=inicio_fora.isoformat()),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Agendamento.objects.count(), 0)
