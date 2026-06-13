import os
import unicodedata

import requests
from dotenv import load_dotenv
from rest_framework import status

from apps.notificacoes.exceptions import (
    InstanciaWhatsAppJaExiste,
    InstanciaWhatsAppNaoEncontrada,
)
from apps.notificacoes.models import WhatsAppInstance

load_dotenv()


class WhatsappService:
    api = os.getenv("EVOLUTION_API_URL")
    api_key = os.getenv("EVOLUTION_API_KEY")

    def criar_instancia(self, clinica) -> WhatsAppInstance:
        response = requests.post(
            f"{self.api}/instance/create/",
            json={
                "instanceName": self.__normalizar_nome(clinica.nome),
                "integration": "WHATSAPP-BAILEYS",
                "number": clinica.telefone,
            },
            headers={"apiKey": self.api_key},  # type: ignore
            timeout=10,
        )

        if response.status_code == status.HTTP_403_FORBIDDEN:
            raise InstanciaWhatsAppJaExiste("Instância com esse nome já existe.")

        instance_data = response.json().get("instance")

        instance = WhatsAppInstance.objects.create(  # type: ignore
            nome=instance_data.get("instanceName"),
            instancia_id=instance_data.get("instanceId"),
            clinica=clinica,
        )

        return instance

    def get_conexao(self, instance) -> str:
        """Retorna uma string codificada em base64
        representando a imagem do QR Code para conexão"""
        response = requests.get(
            f"{self.api}/instance/connect/{instance.nome}",
            headers={"apiKey": self.api_key},  # type: ignore
            timeout=10,
        )

        if response.status_code == 404:
            raise InstanciaWhatsAppNaoEncontrada("Instância não foi encontrada.")

        body = response.json()
        return body.get("base64")

    def enviar_mensagem(self, instance, telefone: str, mensagem: str):
        response = requests.post(
            f"{self.api}/message/sendText/{instance.nome}",
            json={"number": telefone, "text": mensagem},
            headers={"apiKey": self.api_key},  # type: ignore
            timeout=10,
        )

        response.raise_for_status()

    def __normalizar_nome(self, nome: str) -> str:
        nome = "".join(  # removendo acentos
            char
            for char in unicodedata.normalize("NFKD", nome)
            if not unicodedata.combining(char)
        )
        nome = nome.replace(" ", "-")  # removendo espaços
        nome = nome.lower()  # letras minusculas

        return nome
