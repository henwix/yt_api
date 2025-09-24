from rest_framework.permissions import BasePermission


class AuthUserPermission(BasePermission):
    # actions that do not require authentication
    AUTH_NOT_REQUIRED_ACTIONS = [
        'create',
        'reset_password',
        'reset_password_confirm',
        'reset_username',
        'reset_username_confirm',
    ]

    # actions that require authentication
    AUTH_REQUIRED_ACTIONS = [
        'update',
        'partial_update',
        'retrieve',
        'set_password',
        'set_email',
        'set_email_confirm',
    ]

    def has_permission(self, request, view):
        if view.action in self.AUTH_NOT_REQUIRED_ACTIONS:
            return True

        if view.action in self.AUTH_REQUIRED_ACTIONS and request.user.is_authenticated:
            return True

        return False
