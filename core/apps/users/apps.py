from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.apps.users'

    def ready(self):
        from core.apps.users import signals  # noqa
