import pytest

from core.apps.payments.exceptions import StripeSubAlreadyExistsError
from core.apps.payments.services.stripe_service import BaseStripeSubAlreadyExistsValidatorService


def test_already_exists_validator_not_raised_with_canceled_status(
    stripe_sub_already_exists_validator_service: BaseStripeSubAlreadyExistsValidatorService,
):
    stripe_sub_already_exists_validator_service.validate(sub={'status': 'canceled'})


def test_already_exists_validator_not_raised_with_no_state(
    stripe_sub_already_exists_validator_service: BaseStripeSubAlreadyExistsValidatorService,
):
    stripe_sub_already_exists_validator_service.validate(sub=None)


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
def test_already_exists_validator_raised_with_not_allowed_statuses(
    stripe_sub_already_exists_validator_service: BaseStripeSubAlreadyExistsValidatorService,
    expected_status: str,
):
    with pytest.raises(StripeSubAlreadyExistsError):
        stripe_sub_already_exists_validator_service.validate(sub={'status': expected_status, 'customer_id': 'cus_123'})
