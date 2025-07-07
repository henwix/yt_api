from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Iterable

from social_django.models import UserSocialAuth

from core.apps.users.converters.users import user_from_entity
from core.apps.users.entities import UserEntity


@dataclass
class BaseOAuth2Repository(ABC):
    @abstractmethod
    def get_connected_providers(self, user: UserEntity) -> Iterable[UserSocialAuth]:
        ...


class OAuth2Repository(BaseOAuth2Repository):
    def get_connected_providers(self, user: UserEntity) -> Iterable[UserSocialAuth]:
        return UserSocialAuth.objects.filter(user=user_from_entity(user=user))
