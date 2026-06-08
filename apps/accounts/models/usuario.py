from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.accounts.enums import Cargo


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("E-mail deve estar preenchido.")

        email = self.normalize_email(email)

        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save()

        return usuario

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser):
    objects = UsuarioManager()

    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=13, unique=True, null=True)

    nome = models.CharField(max_length=128)
    sobrenome = models.CharField(max_length=128)
    cargo = models.CharField(max_length=13, choices=Cargo.choices)

    clinica = models.ForeignKey("Clinica", on_delete=models.CASCADE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "sobrenome", "cargo"]
