import pytest

from core.apps.payments.exceptions import StripeNotAllowedEventTypeError
from core.apps.payments.services.stripe_service import BaseStripeEventValidatorService


@pytest.mark.parametrize(
    argnames='expected_event_type',
    argvalues=[
        'checkout.session.completed',
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
        'customer.subscription.trial_will_end',
        'invoice.paid',
        'invoice.payment_failed',
        'payment_intent.payment_failed',
        'payment_intent.canceled',
    ],
)
def test_stripe_event_type_validator_not_raised_with_allowed_types(
    stripe_event_type_validator_service: BaseStripeEventValidatorService,
    expected_event_type: str,
):
    stripe_event_type_validator_service.validate(event={'type': expected_event_type})


def test_stripe_event_type_validator_raised_with_not_allowed_types(
    stripe_event_type_validator_service: BaseStripeEventValidatorService,
):
    with pytest.raises(StripeNotAllowedEventTypeError):
        stripe_event_type_validator_service.validate(event={'type': 'test.event_type'})
