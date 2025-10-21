import punq

from core.apps.payments.providers.stripe_provider import (
    BaseStripeProvider,
    StripeProvider,
)
from core.apps.payments.services.stripe_service import (
    BaseCustomerIdValidatorService,
    BaseStripeEventValidatorService,
    BaseStripeService,
    BaseStripeSubValidatorService,
    CustomerIdValidatorService,
    StripeEventValidatorService,
    StripeService,
    StripeSubValidatorService,
)
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase


def init_payments(container: punq.Container) -> None:
    # use cases
    container.register(CreateCheckoutSessionUseCase)
    container.register(StripeWebhookUseCase)

    # services
    container.register(BaseStripeService, StripeService)
    container.register(BaseStripeEventValidatorService, StripeEventValidatorService)
    container.register(BaseCustomerIdValidatorService, CustomerIdValidatorService)
    container.register(BaseStripeSubValidatorService, StripeSubValidatorService)

    # providers
    container.register(BaseStripeProvider, StripeProvider)
