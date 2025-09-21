from rest_framework.permissions import BasePermission


class AuthUserPermission(BasePermission):
    # actions that do not require authentication
    SAFE_ACTIONS = ['create']

    # actions that require authentication
    AUTH_REQUIRED_ACTIONS = ['update', 'partial_update', 'retrieve', 'set_password']

    def has_permission(self, request, view):
        if view.action in self.SAFE_ACTIONS:
            return True

        if view.action in self.AUTH_REQUIRED_ACTIONS and request.user.is_authenticated:
            return True

        return False
