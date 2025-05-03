from django.apps import AppConfig


class VideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.apps.videos'

    def ready(self):
        pass
