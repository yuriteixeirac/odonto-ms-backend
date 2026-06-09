import re

from django.core.exceptions import ValidationError

phone_pattern = re.compile(r"(\+?\d{2})?\s?\d{2}\s?9?\s?\d{4}[\-\s]?\d{4}")


def validate_phone(phone: str) -> None:
    if phone_pattern.fullmatch(phone.strip()) is None:
        raise ValidationError("Telefone não entra no padrão esperado.")
