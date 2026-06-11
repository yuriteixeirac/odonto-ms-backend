from rest_framework import serializers


class CelulaCalendarioSerializer(serializers.Serializer):
    data = serializers.DateField()  # type: ignore
    total = serializers.IntegerField()
    contagem_por_status = serializers.JSONField()


class CalendarioMensalSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    mes = serializers.IntegerField()
    dias = serializers.ListField(child=CelulaCalendarioSerializer())
