import punq

from core.apps.payments.providers.stripe_provider import (
    BaseStripeProvider,
    StripeProvider,
)
from core.apps.payments.services.stripe_service import (
    BaseCustomerIdValidatorService,
    BaseStripeEventValidatorService,
    BaseStripeService,
    BaseStripeSubAlreadyExistsValidatorService,
    BaseStripeSubDoesNotExistValidatorService,
    BaseStripeSubStillActiveValidatorService,
    CustomerIdValidatorService,
    StripeEventValidatorService,
    StripeService,
    StripeSubAlreadyExistsValidatorService,
    StripeSubDoesNotExistValidatorService,
    StripeSubStillActiveValidatorService,
)
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.payments.use_cases.get_stripe_sub_state import GetStripeSubStateUseCase
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase


def init_payments(container: punq.Container) -> None:
    # use cases
    container.register(CreateCheckoutSessionUseCase)
    container.register(GetStripeSubStateUseCase)
    container.register(StripeWebhookUseCase)

    # services
    container.register(BaseStripeService, StripeService)
    container.register(BaseStripeEventValidatorService, StripeEventValidatorService)
    container.register(BaseCustomerIdValidatorService, CustomerIdValidatorService)
    container.register(BaseStripeSubAlreadyExistsValidatorService, StripeSubAlreadyExistsValidatorService)
    container.register(BaseStripeSubDoesNotExistValidatorService, StripeSubDoesNotExistValidatorService)
    container.register(BaseStripeSubStillActiveValidatorService, StripeSubStillActiveValidatorService)

    # providers
    container.register(BaseStripeProvider, StripeProvider)
