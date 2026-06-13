from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.accounts.enums import Cargo
from apps.accounts.validators import validate_phone


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("E-mail deve estar preenchido.")

        email = self.normalize_email(email)

        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)

        usuario.full_clean()
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("cargo", Cargo.ADMIN)

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser):
    objects = UsuarioManager()

    email = models.EmailField(unique=True)
    telefone = models.CharField(
        max_length=13, unique=True, null=True, validators=[validate_phone]
    )

    nome = models.CharField(max_length=128)
    sobrenome = models.CharField(max_length=128)
    cargo = models.CharField(
        max_length=13, choices=Cargo.choices, default=Cargo.CLINICO
    )

    clinica = models.ForeignKey(
        "Clinica", on_delete=models.CASCADE, null=True, blank=True
    )

    is_staff = models.BooleanField(default=False)  # type: ignore
    is_superuser = models.BooleanField(default=False)  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "sobrenome", "telefone", "cargo"]
