from django.apps import AppConfig


class ChannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.apps.channels'

    def ready(self):
        from core.apps.channels import signals  # noqa
