from dataclasses import dataclass

from django.db import transaction
from django.db.utils import settings

from core.apps.channels.services.channels import BaseChannelService
from core.apps.common.services.encoding import BaseEncodingService
from core.apps.common.services.smtp_email import BaseEmailService
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser
from core.apps.users.services.codes import BaseCodeService
from core.apps.users.services.users import BaseUserService


@dataclass
class UserCreateUseCase:
    user_service: BaseUserService
    channel_service: BaseChannelService
    code_service: BaseCodeService
    email_service: BaseEmailService
    encoding_service: BaseEncodingService

    def execute(self, validated_data: dict) -> CustomUser | dict:
        # retrieve whether activation is required from settings
        activation_required = self.user_service.is_activation_required()

        # start transaction
        with transaction.atomic():
            # create new user by provided data
            user: CustomUser = self.user_service.create_by_data(
                data={
                    'username': validated_data.get('username'),
                    'email': validated_data.get('email'),
                    'password': validated_data.get('password'),
                    'is_active': False if activation_required else True,
                },
            )

            # check if the 'channel' dict was provided, if not, create an empty one
            validated_data.setdefault('channel', {})

            # add just created user to the 'channel' dict
            validated_data['channel']['user'] = user

            # create channel for the new user
            self.channel_service.create_by_data(data=validated_data)

        # check if the activation is required
        if activation_required:
            user_entity = user_to_entity(user)

            # generate activation code and encoded user id
            code = self.code_service.generate_user_email_code(
                user=user_entity,
                cache_prefix=settings.CACHE_KEYS.get('activate_user'),
            )
            encoded_id = self.encoding_service.base64_encode(data=user_entity.id)

            # send email with activation code
            self.email_service.send_email(
                to=[user_entity.email],
                context={
                    'username': user_entity.username,
                    'code': code,
                    'encoded_id': encoded_id,
                    'url': self.email_service.build_frontend_email_url_with_code_and_id(
                        uri=settings.EMAIL_FRONTEND_ACTIVATE_URI,
                        encoded_id=encoded_id,
                        code=code,
                    ),
                },
                subject='Activate your account',
                template=settings.EMAIL_SMTP_TEMPLATES.get('activate_user'),
            )

            # return message that the email was sent
            return {'detail': 'Activation email successfully sent'}

        # return the CustomUser instance if the activation is not required
        return user
