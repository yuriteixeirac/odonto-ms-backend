from rest_framework import serializers

from apps.accounts.serializers import ClinicaOutputSerializer
from apps.agenda.models.paciente import Paciente


class PacienteOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = "__all__"

    clinica = ClinicaOutputSerializer()


class PacienteInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = "__all__"
