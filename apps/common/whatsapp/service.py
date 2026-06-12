from apps.accounts.validators import validate_phone


class WhatsappService:
    def __init__(self, numero: str) -> None:
        validate_phone(numero)
        self.numero = numero

    def enviar_lembrete(self, remetente: str): ...
