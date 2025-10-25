from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


class CustomUser(AbstractUser):
    otp_enabled = models.BooleanField(
        default=False,
        help_text=_('Controls whether email OTP verification is required for login'),
    )
    email = models.EmailField(
        unique=True,
        help_text=_("User's email address"),
    )
    password = models.CharField(max_length=128, help_text=_('User password'))
