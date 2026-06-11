from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.agenda.views import AgendamentoViewSet, ExpedienteViewSet, ProcedimentoViewSet
from apps.agenda.views.calendario_views import calendario_mensal_view

router = DefaultRouter()
router.register(r"procedimento", ProcedimentoViewSet, basename="procedimento")
router.register(r"expediente", ExpedienteViewSet, basename="expediente")
router.register(r"agendamento", AgendamentoViewSet, basename="agendamento")

urlpatterns = [path("calendario/", calendario_mensal_view, name="calendario_mensal")]
urlpatterns += router.urls
