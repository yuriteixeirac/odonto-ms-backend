from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.accounts.views import (
    ClinicaViewSet,
    UsuarioViewSet,
    criar_convite_view,
    me_view,
    usar_convite_view,
)

router = DefaultRouter()
router.register(r"clinica", ClinicaViewSet, basename="clinica")
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", me_view, name="me"),
    path("convite/<convite_uuid>/", usar_convite_view, name="usar_convite"),
    path("convite/", criar_convite_view, name="criar_convite"),
]

urlpatterns += router.urls
