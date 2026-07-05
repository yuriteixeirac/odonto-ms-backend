import os
import unicodedata

import requests
from dotenv import load_dotenv
from rest_framework import status

from apps.notificacoes.exceptions import (
    EvolutionAPINaoConfigurada,
    EvolutionAPIException,
    EvolutionAPIRespostaInvalida,
    InstanciaWhatsAppNaoEncontrada,
)
from apps.notificacoes.models import WhatsAppInstance

load_dotenv()


class WhatsappService:
    def __init__(self):
        self.api = (os.getenv("EVOLUTION_API_URL") or "").rstrip("/")
        self.api_key = os.getenv("EVOLUTION_API_KEY") or ""

    def criar_instancia(self, clinica) -> WhatsAppInstance:
        self.__validar_configuracao()
        instance_name = self.__normalizar_nome(clinica.nome)
        response = self.__post(
            "/instance/create",
            json={
                "instanceName": instance_name,
                "integration": "WHATSAPP-BAILEYS",
                "number": clinica.telefone,
            },
        )

        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_409_CONFLICT]:
            return self.__salvar_instancia_existente(clinica, instance_name)

        if not response.ok:
            raise EvolutionAPIException(self.__erro_response(response))

        try:
            body = response.json()
        except ValueError as exc:
            raise EvolutionAPIRespostaInvalida(
                "Evolution API não retornou os dados da instância criada."
            ) from exc

        if not isinstance(body, dict):
            raise EvolutionAPIRespostaInvalida(
                "Evolution API retornou os dados da instância em formato inválido."
            )

        instance_data = body.get("instance") or {}
        instance_name = instance_data.get("instanceName") or instance_name
        instance_id = instance_data.get("instanceId") or instance_data.get("id") or ""

        instance, _ = WhatsAppInstance.objects.update_or_create(  # type: ignore
            clinica=clinica,
            defaults={
                "nome": instance_name,
                "instancia_id": instance_id,
                "ativo": True,
            },
        )

        return instance

    def get_conexao(self, instance) -> str:
        """Retorna uma string codificada em base64
        representando a imagem do QR Code para conexão"""
        self.__validar_configuracao()
        response = self.__get(f"/instance/connect/{instance.nome}")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise InstanciaWhatsAppNaoEncontrada("Instância não foi encontrada.")

        if not response.ok:
            raise EvolutionAPIException(self.__erro_response(response))

        try:
            body = response.json()
        except ValueError as exc:
            raise EvolutionAPIRespostaInvalida(
                "Evolution API não retornou uma resposta JSON válida para conexão."
            ) from exc

        if not isinstance(body, dict):
            raise EvolutionAPIRespostaInvalida(
                "Evolution API retornou o QR Code em formato inválido."
            )
        qr_code = body.get("base64") or body.get("qrcode") or body.get("qr")

        if not qr_code:
            raise EvolutionAPIRespostaInvalida(
                "Evolution API não retornou um QR Code em base64."
            )

        return self.__normalizar_qr_code(qr_code)

    def enviar_mensagem(self, instance, telefone: str, mensagem: str):
        self.__validar_configuracao()
        response = self.__post(
            f"/message/sendText/{instance.nome}",
            json={"number": telefone, "text": mensagem},
        )

        if not response.ok:
            raise EvolutionAPIException(self.__erro_response(response))

    def __salvar_instancia_existente(self, clinica, instance_name: str):
        instance, _ = WhatsAppInstance.objects.update_or_create(  # type: ignore
            clinica=clinica,
            defaults={
                "nome": instance_name,
                "instancia_id": instance_name,
                "ativo": True,
            },
        )

        return instance

    def __get(self, path: str):
        try:
            return requests.get(
                f"{self.api}{path}",
                headers={"apiKey": self.api_key},
                timeout=10,
            )
        except requests.RequestException as exc:
            raise EvolutionAPIException(
                "Não foi possível conectar à Evolution API."
            ) from exc

    def __post(self, path: str, *, json: dict | None = None):
        try:
            return requests.post(
                f"{self.api}{path}",
                json=json,
                headers={"apiKey": self.api_key},
                timeout=10,
            )
        except requests.RequestException as exc:
            raise EvolutionAPIException(
                "Não foi possível conectar à Evolution API."
            ) from exc

    def __validar_configuracao(self):
        if not self.api or not self.api_key:
            raise EvolutionAPINaoConfigurada(
                "EVOLUTION_API_URL e EVOLUTION_API_KEY devem estar configuradas no .env."
            )

    def __erro_response(self, response):
        try:
            body = response.json()
        except ValueError:
            return response.text or "Evolution API retornou uma resposta inválida."

        if isinstance(body, dict):
            for key in ["message", "error"]:
                value = body.get(key)
                if isinstance(value, str):
                    return value

            nested_response = body.get("response")
            if isinstance(nested_response, dict):
                nested_message = nested_response.get("message")
                if isinstance(nested_message, str):
                    return nested_message

        return "Evolution API recusou a operação."

    def __normalizar_qr_code(self, qr_code: str):
        qr_code = qr_code.strip()

        if qr_code.startswith("data:image"):
            return qr_code

        return f"data:image/png;base64,{qr_code}"

    def __normalizar_nome(self, nome: str) -> str:
        nome = "".join(  # removendo acentos
            char
            for char in unicodedata.normalize("NFKD", nome)
            if not unicodedata.combining(char)
        )
        nome = nome.replace(" ", "-")  # removendo espaços
        nome = nome.lower()  # letras minusculas

        return nome
