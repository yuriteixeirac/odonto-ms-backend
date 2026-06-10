from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.agenda.views import AgendamentoViewSet, ExpedienteViewSet, ProcedimentoViewSet

router = DefaultRouter()
router.register(r"procedimento", ProcedimentoViewSet, basename="procedimento")
router.register(r"expediente", ExpedienteViewSet, basename="expediente")
router.register(r"agendamento", AgendamentoViewSet, basename="agendamento")

urlpatterns = []
urlpatterns += router.urls
