import punq

from core.apps.payments.providers.stripe_provider import (
    BaseStripeProvider,
    StripeProvider,
)
from core.apps.payments.services.stripe_service import (
    BaseStripeService,
    StripeService,
)
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase


def init_payments(container: punq.Container) -> None:
    # use cases
    container.register(CreateCheckoutSessionUseCase)

    # services
    container.register(BaseStripeService, StripeService)

    # providers
    container.register(BaseStripeProvider, StripeProvider)
