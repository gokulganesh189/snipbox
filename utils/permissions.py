from rest_framework.permissions import BasePermission


class IsNormalUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_active
            and request.user.is_superuser is None
        )


class IsAdminUser(BasePermission):
    """
    An admin is a superuser active and also staff
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_superuser
            and request.user.is_active
            and request.user.is_staff
        )

class IsAdminOrModerator(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_staff
            and request.user.is_active
            and request.user.is_superuser is None
        )