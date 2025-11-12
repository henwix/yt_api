import pytest

from core.apps.payments.exceptions import StripeSubDoesNotExistError
from core.apps.payments.services.stripe_service import BaseStripeSubDoesNotExistValidatorService


@pytest.mark.parametrize(
    argnames='expected_status',
    argvalues=[
        'active',
        'trialing',
        'incomplete',
        'incomplete_expired',
        'past_due',
        'unpaid',
        'paused',
    ],
)
def test_does_not_exist_validator_not_raised_with_allowed_statuses(
    stripe_sub_does_not_exist_validator_service: BaseStripeSubDoesNotExistValidatorService,
    expected_status: str,
):
    stripe_sub_does_not_exist_validator_service.validate(sub={'status': expected_status})


def test_does_not_exist_validator_raised_with_no_state(
    stripe_sub_does_not_exist_validator_service: BaseStripeSubDoesNotExistValidatorService,
):
    with pytest.raises(StripeSubDoesNotExistError):
        stripe_sub_does_not_exist_validator_service.validate(sub=None)


def test_does_not_exist_validator_raised_with_canceled_status(
    stripe_sub_does_not_exist_validator_service: BaseStripeSubDoesNotExistValidatorService,
):
    with pytest.raises(StripeSubDoesNotExistError):
        stripe_sub_does_not_exist_validator_service.validate(sub={'status': 'canceled'})
