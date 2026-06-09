from typing import override

from rest_framework import serializers

from apps.accounts.models.usuario import Usuario


class UsuarioInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["email", "password", "nome", "sobrenome", "telefone"]

    @override
    def save(self, **kwargs):
        return Usuario.objects.create_user(**self.validated_data, **kwargs)  # type: ignore


class UsuarioOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["email", "nome", "sobrenome", "telefone"]
