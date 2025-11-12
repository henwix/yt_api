import pytest
from punq import Any

from core.apps.payments.exceptions import StripeCustomerIdNotStringError
from core.apps.payments.services.stripe_service import BaseCustomerIdValidatorService


def test_customer_id_validator_not_raised_with_allowed_type(
    stripe_customer_id_validator_service: BaseCustomerIdValidatorService,
):
    stripe_customer_id_validator_service.validate(customer_id='cus_218647826')


@pytest.mark.parametrize('expected_customer_id', [[], {}, 123, ()])
def test_customer_id_validator_raised_with_not_allowed_type(
    stripe_customer_id_validator_service: BaseCustomerIdValidatorService,
    expected_customer_id: Any,
):
    with pytest.raises(StripeCustomerIdNotStringError):
        stripe_customer_id_validator_service.validate(customer_id=expected_customer_id)
