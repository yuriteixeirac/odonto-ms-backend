from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("agenda/", include("apps.agenda.urls")),
    path("notificacoes/", include("apps.notificacoes.urls")),
    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
