from typing import override

from rest_framework import serializers

from apps.accounts.models.clinica import Clinica
from apps.accounts.validators import PhoneValidator


class ClinicaOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = "__all__"


class ClinicaInputSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=128)
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=13, validators=[PhoneValidator()])
    cep = serializers.CharField(max_length=9)

    @override
    def save(self, endereco: dict[str, str], **extra_fields):  # type: ignore
        del self.validated_data["cep"]  # type: ignore
        return Clinica.objects.create(endereco=endereco, **self.validated_data)  # type: ignore
