from rest_framework.viewsets import ModelViewSet

from apps.agenda.models.paciente import Paciente
from apps.agenda.serializers.paciente_serializer import PacienteSerializer


class PacienteViewSet(ModelViewSet):
    serializer_class = PacienteSerializer
    queyset = Paciente.objects.all()
