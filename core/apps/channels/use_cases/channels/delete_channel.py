from dataclasses import dataclass

from core.apps.channels.services.channels import BaseChannelService
from core.apps.payments.services.stripe_service import BaseStripeSubStillActiveValidatorService
from core.apps.users.entities import UserEntity


@dataclass
class DeleteChannelUseCase:
    channel_service: BaseChannelService
    validator_service: BaseStripeSubStillActiveValidatorService

    def execute(self, user: UserEntity) -> None:
        self.validator_service.validate(user=user)
        self.channel_service.delete_channel_by_user(user=user)
