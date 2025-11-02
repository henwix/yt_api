from enum import Enum

from django.db import models


class EntityStatus(Enum):
    NOT_LOADED = 'not_loaded'


class CaptchaVersionsEnum(models.TextChoices):
    GOOGLE_V3 = 'v3'
    GOOGLE_V2_VISIBLE = 'v2_visible'
    GOOGLE_V2_INVISIBLE = 'v2_invisible'
