from django.urls import path

from apps.notificacoes.views import conectar_instancia, criar_instancia, enviar_mensagem

urlpatterns = [
    path("conexao/", conectar_instancia, name="conectar_instancia"),
    path("instancia/", criar_instancia, name="criar_instancia"),
    path("mensagem/", enviar_mensagem, name="enviar_mensagem"),
]
