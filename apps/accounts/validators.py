import re

from django.core.exceptions import ValidationError


class PhoneValidator:
    pattern = re.compile(r"(\+?\d{2})?\s?\d{2}\s?9?\s?\d{4}[\-\s]?\d{4}")

    def __call__(self, phone: str) -> None:
        if self.pattern.fullmatch(phone) is None:
            raise ValidationError("Telefone não entra no padrão esperado.")
