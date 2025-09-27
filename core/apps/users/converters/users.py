from django.contrib.auth.models import AnonymousUser

from core.apps.users.entities import (
    AnonymousUserEntity,
    UserEntity,
)
from core.apps.users.models import CustomUser


def user_from_entity(user: UserEntity) -> CustomUser:
    return CustomUser(
        pk=user.id,
        email=user.email,
        username=user.username,
        otp_enabled=user.otp_enabled,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
        date_joined=user.date_joined,
    )


def user_to_entity(user: CustomUser | AnonymousUser) -> UserEntity | AnonymousUserEntity:
    if user.is_anonymous:
        return AnonymousUserEntity()

    return UserEntity(
        id=user.id,
        email=user.email,
        username=user.username,
        otp_enabled=user.otp_enabled,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
        date_joined=user.date_joined,
    )
