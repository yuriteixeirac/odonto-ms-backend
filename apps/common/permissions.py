from rest_framework.permissions import BasePermission

from apps.accounts.enums import Cargo


class IsClinicaAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.cargo == Cargo.ADMIN
        )


class IsClinico(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.cargo == Cargo.CLINICO
        )


class IsRecepcionista(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.cargo == Cargo.RECEPCIONISTA
        )


class IsRecepcionistaOuAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.cargo == Cargo.RECEPCIONISTA
            or request.user.cargo == Cargo.ADMIN
        )
