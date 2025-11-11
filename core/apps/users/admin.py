from django.contrib import admin

from core.apps.users.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username',
        'password',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
        'otp_enabled',
    ]
