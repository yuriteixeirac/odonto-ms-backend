from rest_framework.permissions import BasePermission

from apps.accounts.enums import Cargo


class IsClinicAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.cargo == Cargo.ADMIN
        )
