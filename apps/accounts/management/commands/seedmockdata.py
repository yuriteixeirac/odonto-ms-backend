from datetime import time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.enums import Cargo
from apps.accounts.models import Clinica, Usuario
from apps.agenda.enums import Status
from apps.agenda.models import Agendamento, Expediente, Paciente, Procedimento
from apps.notificacoes.models import WhatsAppInstance


MOCK_PASSWORD = "mock12345"
MOCK_CLINIC_NAMES = ["OdontoMS Mock Centro", "OdontoMS Mock Norte"]


def cpf_from_seed(seed: int) -> str:
    base = f"{seed:09d}"[-9:]

    first_sum = sum(int(base[index]) * (10 - index) for index in range(9))
    first_digit = (first_sum * 10) % 11
    first_digit = 0 if first_digit == 10 else first_digit

    second_base = f"{base}{first_digit}"
    second_sum = sum(int(second_base[index]) * (11 - index) for index in range(10))
    second_digit = (second_sum * 10) % 11
    second_digit = 0 if second_digit == 10 else second_digit

    return f"{base}{first_digit}{second_digit}"


def get_weekday_date(base_date, weekday: int, offset_weeks: int = 0):
    start_of_week = base_date - timedelta(days=base_date.weekday())
    return start_of_week + timedelta(days=weekday, weeks=offset_weeks)


class Command(BaseCommand):
    help = "Popula o banco com dados mock completos para testar o OdontoMS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove dados mock criados por este comando antes de recriar.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_mock_data()

        centro = self._upsert_clinica(
            nome="OdontoMS Mock Centro",
            email="centro@odontoms.local",
            telefone="84999990001",
            endereco={
                "estado": "RN",
                "cidade": "Natal",
                "bairro": "Tirol",
                "rua": "Avenida Prudente de Morais",
            },
        )
        norte = self._upsert_clinica(
            nome="OdontoMS Mock Norte",
            email="norte@odontoms.local",
            telefone="84999990002",
            endereco={
                "estado": "RN",
                "cidade": "Natal",
                "bairro": "Zona Norte",
                "rua": "Avenida João Medeiros Filho",
            },
        )
        self._remove_mock_whatsapp([centro, norte])

        app_admin = self._upsert_user(
            email="app.admin@odontoms.local",
            nome="Admin",
            sobrenome="Aplicação",
            telefone="84999990100",
            cargo=Cargo.ADMIN,
            clinica=None,
            is_staff=True,
            is_superuser=True,
        )

        centro_users = {
            "admin": self._upsert_user(
                email="admin.centro@odontoms.local",
                nome="Carla",
                sobrenome="Menezes",
                telefone="84999990101",
                cargo=Cargo.ADMIN,
                clinica=centro,
                is_staff=True,
                is_superuser=True,
            ),
            "recepcionista": self._upsert_user(
                email="recepcao.centro@odontoms.local",
                nome="Marina",
                sobrenome="Lopes",
                telefone="84999990102",
                cargo=Cargo.RECEPCIONISTA,
                clinica=centro,
            ),
            "clinico_ana": self._upsert_user(
                email="ana.clinico@odontoms.local",
                nome="Ana",
                sobrenome="Bezerra",
                telefone="84999990103",
                cargo=Cargo.CLINICO,
                clinica=centro,
            ),
            "clinico_bruno": self._upsert_user(
                email="bruno.clinico@odontoms.local",
                nome="Bruno",
                sobrenome="Costa",
                telefone="84999990104",
                cargo=Cargo.CLINICO,
                clinica=centro,
            ),
            "auxiliar": self._upsert_user(
                email="auxiliar.centro@odontoms.local",
                nome="Igor",
                sobrenome="Silva",
                telefone="84999990105",
                cargo=Cargo.AUXILIAR,
                clinica=centro,
            ),
        }

        norte_users = {
            "admin": self._upsert_user(
                email="admin.norte@odontoms.local",
                nome="Rafael",
                sobrenome="Almeida",
                telefone="84999990201",
                cargo=Cargo.ADMIN,
                clinica=norte,
                is_staff=True,
                is_superuser=True,
            ),
            "recepcionista": self._upsert_user(
                email="recepcao.norte@odontoms.local",
                nome="Bianca",
                sobrenome="Rocha",
                telefone="84999990202",
                cargo=Cargo.RECEPCIONISTA,
                clinica=norte,
            ),
            "clinico": self._upsert_user(
                email="diego.clinico@odontoms.local",
                nome="Diego",
                sobrenome="Nunes",
                telefone="84999990203",
                cargo=Cargo.CLINICO,
                clinica=norte,
            ),
        }

        centro_procedimentos = self._seed_procedimentos(centro)
        norte_procedimentos = self._seed_procedimentos(norte)

        centro_pacientes = self._seed_pacientes(
            centro,
            start_seed=100100001,
            telefone_prefix="84999991",
            names=[
                ("Yuri", "Teixeira", "yuri.paciente@odontoms.local"),
                ("Helena", "Barros", "helena.paciente@odontoms.local"),
                ("Mateus", "Fernandes", "mateus.paciente@odontoms.local"),
                ("Laura", "Nascimento", "laura.paciente@odontoms.local"),
                ("Pedro", "Oliveira", "pedro.paciente@odontoms.local"),
                ("Sofia", "Martins", "sofia.paciente@odontoms.local"),
            ],
        )
        norte_pacientes = self._seed_pacientes(
            norte,
            start_seed=200200001,
            telefone_prefix="84999992",
            names=[
                ("João", "Medeiros", "joao.paciente@odontoms.local"),
                ("Clara", "Dantas", "clara.paciente@odontoms.local"),
                ("Renata", "Freire", "renata.paciente@odontoms.local"),
            ],
        )

        self._seed_expedientes([centro_users["clinico_ana"], centro_users["clinico_bruno"]])
        self._seed_expedientes([norte_users["clinico"]])

        self._seed_agendamentos(
            clinicos=[centro_users["clinico_ana"], centro_users["clinico_bruno"]],
            pacientes=centro_pacientes,
            procedimentos=centro_procedimentos,
        )
        self._seed_agendamentos(
            clinicos=[norte_users["clinico"]],
            pacientes=norte_pacientes,
            procedimentos=norte_procedimentos,
        )

        self.stdout.write(self.style.SUCCESS("Dados mock criados/atualizados com sucesso."))
        self.stdout.write("Credenciais principais:")
        for email in [
            app_admin.email,
            centro_users["admin"].email,
            centro_users["recepcionista"].email,
            centro_users["clinico_ana"].email,
            centro_users["clinico_bruno"].email,
            norte_users["admin"].email,
            norte_users["recepcionista"].email,
            norte_users["clinico"].email,
        ]:
            self.stdout.write(f"- {email} / {MOCK_PASSWORD}")

    def _reset_mock_data(self):
        mock_clinics = Clinica.objects.filter(nome__in=MOCK_CLINIC_NAMES)
        mock_users = Usuario.objects.filter(email__endswith="@odontoms.local")

        Agendamento.objects.filter(clinico__in=mock_users).delete()
        Expediente.objects.filter(clinico__in=mock_users).delete()
        Procedimento.objects.filter(clinica__in=mock_clinics).delete()
        Paciente.objects.filter(clinica__in=mock_clinics).delete()
        WhatsAppInstance.objects.filter(clinica__in=mock_clinics).delete()
        mock_users.delete()
        mock_clinics.delete()

    def _upsert_clinica(self, *, nome, email, telefone, endereco):
        clinica, _ = Clinica.objects.update_or_create(
            nome=nome,
            defaults={"email": email, "telefone": telefone, "endereco": endereco},
        )
        return clinica

    def _upsert_user(
        self,
        *,
        email,
        nome,
        sobrenome,
        telefone,
        cargo,
        clinica,
        is_staff=False,
        is_superuser=False,
    ):
        user = Usuario.objects.filter(email=email).first()

        if not user:
            user = Usuario.objects.create_user(
                email=email,
                password=MOCK_PASSWORD,
                nome=nome,
                sobrenome=sobrenome,
                telefone=telefone,
                cargo=cargo,
                clinica=clinica,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )
            return user

        user.nome = nome
        user.sobrenome = sobrenome
        user.telefone = telefone
        user.cargo = cargo
        user.clinica = clinica
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(MOCK_PASSWORD)
        user.save()
        return user

    def _seed_procedimentos(self, clinica):
        data = [
            ("Avaliação inicial", Decimal("80.00"), 30, True),
            ("Limpeza odontológica", Decimal("180.00"), 60, True),
            ("Restauração", Decimal("260.00"), 75, True),
            ("Tratamento de canal", Decimal("850.00"), 120, True),
            ("Clareamento", Decimal("700.00"), 90, True),
            ("Procedimento inativo", Decimal("120.00"), 45, False),
        ]
        procedimentos = []

        for nome, valor, duracao, ativo in data:
            procedimento, _ = Procedimento.objects.update_or_create(
                nome=nome,
                clinica=clinica,
                defaults={"valor": valor, "duracao": duracao, "ativo": ativo},
            )
            procedimentos.append(procedimento)

        return procedimentos

    def _seed_pacientes(self, clinica, *, start_seed, telefone_prefix, names):
        pacientes = []

        for index, (nome, sobrenome, email) in enumerate(names):
            paciente, _ = Paciente.objects.update_or_create(
                cpf=cpf_from_seed(start_seed + index),
                defaults={
                    "nome": nome,
                    "sobrenome": sobrenome,
                    "telefone": f"{telefone_prefix}{index + 1:03d}",
                    "email": email,
                    "clinica": clinica,
                },
            )
            pacientes.append(paciente)

        return pacientes

    def _seed_expedientes(self, clinicos):
        for clinico in clinicos:
            for dia in range(5):
                Expediente.objects.update_or_create(
                    clinico=clinico,
                    dia=dia,
                    ativo=True,
                    defaults={"inicio": time(8, 0), "fim": time(18, 0)},
                )

            Expediente.objects.update_or_create(
                clinico=clinico,
                dia=5,
                ativo=True,
                defaults={"inicio": time(8, 0), "fim": time(12, 0)},
            )

    def _seed_agendamentos(self, *, clinicos, pacientes, procedimentos):
        active_procedures = [procedimento for procedimento in procedimentos if procedimento.ativo]
        base_date = timezone.localdate()
        appointment_data = [
            (0, 0, 9, 0, Status.AGENDADO, "MOCK: retorno de avaliação."),
            (0, 1, 11, 0, Status.PENDENTE, "MOCK: confirmar documentação."),
            (1, 2, 14, 0, Status.CONCLUIDO, "MOCK: procedimento finalizado."),
            (2, 3, 10, 0, Status.CANCELADO, "MOCK: paciente solicitou remarcação."),
            (3, 4, 15, 30, Status.AGENDADO, "MOCK: preferência por WhatsApp."),
            (4, 5, 8, 30, Status.PENDENTE, "MOCK: primeira consulta."),
            (0, 2, 16, 0, Status.AGENDADO, "MOCK: encaixe da semana seguinte."),
            (1, 0, 9, 30, Status.PENDENTE, "MOCK: revisão preventiva."),
        ]

        for index, (weekday, patient_index, hour, minute, status, observacoes) in enumerate(
            appointment_data
        ):
            clinico = clinicos[index % len(clinicos)]
            paciente = pacientes[patient_index % len(pacientes)]
            procedimento = active_procedures[index % len(active_procedures)]
            appointment_date = get_weekday_date(base_date, weekday, offset_weeks=index // 6)
            inicio = timezone.make_aware(
                timezone.datetime.combine(appointment_date, time(hour, minute))
            )
            fim = inicio + timedelta(minutes=procedimento.duracao)

            Agendamento.objects.update_or_create(
                clinico=clinico,
                paciente=paciente,
                inicio=inicio,
                defaults={
                    "fim": fim,
                    "status": status,
                    "observacoes": observacoes,
                    "procedimento": procedimento,
                },
            )

    def _remove_mock_whatsapp(self, clinicas):
        WhatsAppInstance.objects.filter(clinica__in=clinicas, nome__startswith="mock-").delete()
