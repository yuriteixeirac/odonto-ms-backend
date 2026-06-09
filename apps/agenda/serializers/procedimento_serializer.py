from rest_framework import serializers

from apps.agenda.models.procedimento import Procedimento


class ProcedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedimento
        fields = "__all__"
