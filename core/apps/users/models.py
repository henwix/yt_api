from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    otp_enabled = models.BooleanField(
        default=False,
        help_text='Controls whether email OTP verification is required for login',
    )
    email = models.EmailField(
        unique=True,
        help_text="User\'s email address",
    )
    password = models.CharField(max_length=128, help_text="User's password")
