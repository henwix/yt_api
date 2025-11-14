import pytest

from core.apps.payments.exceptions import StripeSubStillActiveError
from core.apps.payments.services.stripe_service import BaseStripeService, BaseStripeSubStillActiveValidatorService
from core.apps.users.converters.users import user_to_entity
from core.apps.users.models import CustomUser


@pytest.mark.django_db
def test_sub_still_active_validator_not_raised_with_canceled_status(
    stripe_service: BaseStripeService,
    stripe_sub_still_active_validator_service: BaseStripeSubStillActiveValidatorService,
    user: CustomUser,
):
    stripe_service.save_customer_id(user.pk, customer_id='cus_123456789')
    stripe_service.save_sub_state_by_customer_id(customer_id='cus_123456789', state={'status': 'canceled'})
    stripe_sub_still_active_validator_service.validate(user=user_to_entity(user=user))


@pytest.mark.django_db
def test_sub_still_active_validator_not_raised_with_no_state(
    stripe_sub_still_active_validator_service: BaseStripeSubStillActiveValidatorService,
    user: CustomUser,
):
    stripe_sub_still_active_validator_service.validate(user=user_to_entity(user=user))


@pytest.mark.django_db
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
def test_sub_still_active_validator_raised_with_not_allowed_statuses(
    stripe_service: BaseStripeService,
    stripe_sub_still_active_validator_service: BaseStripeSubStillActiveValidatorService,
    user: CustomUser,
    expected_status: str,
):
    stripe_service.save_customer_id(user.pk, customer_id='cus_123456789')
    stripe_service.save_sub_state_by_customer_id(customer_id='cus_123456789', state={'status': expected_status})

    with pytest.raises(StripeSubStillActiveError):
        stripe_sub_still_active_validator_service.validate(user=user_to_entity(user=user))
