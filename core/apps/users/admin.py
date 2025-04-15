from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username',
        'password',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
        'otp_enabled',
    ]
