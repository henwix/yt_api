from django.db import models


class VideoSearchOrderingEnum(models.TextChoices):
    """Enum class with ordering parameters for video searching."""

    CREATED_AT_ASC = 'created_at', 'Date of video creation ASC'
    CREATED_AT_DESC = '-created_at', 'Date of video creation DESC'
    VIEWS_COUNT_ASC = 'views_count', 'Total number of views ASC'
    VIEWS_COUNT_DESC = '-views_count', 'Total number of views DESC'
