from dataclasses import dataclass

from django.db import transaction

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.models import CustomUser
from core.apps.users.services.users import BaseUserService


@dataclass
class UserCreateUseCase:
    user_service: BaseUserService
    channel_service: BaseChannelService

    @transaction.atomic
    def execute(self, validated_data: dict) -> CustomUser:
        # create new user by provided data
        user: CustomUser = self.user_service.create_by_data(
            data={
                'username': validated_data.get('username'),
                'email': validated_data.get('email'),
                'password': validated_data.get('password'),
            },
        )

        # check if the 'channel' dict was provided, if not, create an empty one
        validated_data.setdefault('channel', {})

        # add just created user to the 'channel' dict
        validated_data['channel']['user'] = user

        # create a channel for the new user
        self.channel_service.create_by_data(data=validated_data)

        # TODO: сделать отправку письма с активацией тут, или может быть перетащить отправку в service create_by_data

        # if settings.SEND_ACTIVATION_EMAIL:
        #     user.is_active = False
        #     user.save(update_fields=["is_active"])

        return user
