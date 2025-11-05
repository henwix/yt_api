from types import SimpleNamespace

import punq
import pytest

from core.apps.payments.services.stripe_service import BaseStripeService
from core.tests.mocks.payments.stripe import DummyStripeService


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_user_id',
    argvalues=[
        ('cus_123456789', 152),
        ('cus_987654321', 946),
        ('cus_111111111', 42384),
        ('cus_218647826', 27),
    ],
)
def test_customer_id_saved_and_retrieved(
    stripe_service: BaseStripeService,
    expected_customer_id: str,
    expected_user_id: int,
):
    is_saved = stripe_service.save_customer_id(user_id=expected_user_id, customer_id=expected_customer_id)
    assert is_saved

    saved_customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert saved_customer_id == expected_customer_id


@pytest.mark.django_db
@pytest.mark.parametrize('expected_user_id', [1, 13, 146, 4265])
def test_customer_id_not_found_and_equals_none(stripe_service: BaseStripeService, expected_user_id: int):
    customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert customer_id is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_customer_id, expected_user_id',
    argvalues=[
        ('cus_123456789', 152),
        ('cus_987654321', 946),
        ('cus_111111111', 42384),
        ('cus_218647826', 27),
    ],
)
def test_customer_deleted(
    stripe_service: BaseStripeService,
    expected_customer_id: str,
    expected_user_id: int,
):
    is_saved = stripe_service.save_customer_id(user_id=expected_user_id, customer_id=expected_customer_id)
    assert is_saved

    saved_customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert saved_customer_id == expected_customer_id

    is_deleted = stripe_service.delete_customer_id(expected_user_id)
    assert is_deleted

    saved_customer_id = stripe_service.get_customer_id(user_id=expected_user_id)
    assert saved_customer_id is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_sub_id, expected_price_id, expected_customer_id',
    argvalues=[
        ('sub_123456789', 'price_123456789', 'cus_123456789'),
        ('sub_987654321', 'price_987654321', 'cus_987654321'),
        ('sub_676378562', 'price_264728978', 'cus_172846278'),
    ],
)
def test_sub_data_saved_and_retrieved(
    stripe_service: BaseStripeService,
    expected_sub_id: str,
    expected_price_id: str,
    expected_customer_id: str,
):
    sub_data = {'subscription_id': expected_sub_id, 'price_id': expected_price_id}
    is_saved = stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=sub_data)
    assert is_saved

    saved_sub_data = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert saved_sub_data == sub_data


@pytest.mark.django_db
@pytest.mark.parametrize('expected_customer_id', ['cus_123456789', 'cus_987654321', 'cus_767265726'])
def test_sub_data_not_found_and_equals_none(stripe_service: BaseStripeService, expected_customer_id: str):
    sub_data = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert sub_data is None


@pytest.mark.django_db
def test_sub_data_equals_none_without_customer_id(stripe_service: BaseStripeService):
    sub_data = stripe_service.get_sub_state_by_customer_id(customer_id=None)
    assert sub_data is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames='expected_sub_id, expected_price_id, expected_customer_id',
    argvalues=[
        ('sub_123456789', 'price_123456789', 'cus_123456789'),
        ('sub_987654321', 'price_987654321', 'cus_987654321'),
        ('sub_676378562', 'price_264728978', 'cus_172846278'),
    ],
)
def test_sub_data_deleted(
    stripe_service: BaseStripeService,
    expected_sub_id: str,
    expected_price_id: str,
    expected_customer_id: str,
):
    sub_data = {'subscription_id': expected_sub_id, 'price_id': expected_price_id}
    is_saved = stripe_service.save_sub_state_by_customer_id(customer_id=expected_customer_id, data=sub_data)
    assert is_saved

    saved_sub_data = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert saved_sub_data == sub_data

    is_deleted = stripe_service.delete_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert is_deleted

    saved_sub_data = stripe_service.get_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert saved_sub_data is None


@pytest.mark.django_db
@pytest.mark.parametrize('expected_customer_id', ['cus_123456789', 'cus_987654321', 'cus_767265726'])
def test_sub_data_not_deleted_if_not_found(stripe_service: BaseStripeService, expected_customer_id: str):
    is_deleted = stripe_service.delete_sub_state_by_customer_id(customer_id=expected_customer_id)
    assert not is_deleted


@pytest.mark.skip
def test_sub_state_updated(mock_container: punq.Container, dummy_stripe_subscription: SimpleNamespace):
    mock_container.register(BaseStripeService, DummyStripeService)
    stripe_service: BaseStripeService = mock_container.resolve(BaseStripeService)
    is_updated = stripe_service.update_customer_sub_state(customer_id='cus_123456789', sub=dummy_stripe_subscription)

    assert is_updated

    saved_sub = stripe_service.get_sub_state_by_customer_id(customer_id='cus_123456789')
    assert saved_sub['subscription_id'] == dummy_stripe_subscription.id
    assert saved_sub['customer_id'] == 'cus_123456789'
    assert saved_sub['status'] == dummy_stripe_subscription.status
    assert saved_sub['price_id'] == dummy_stripe_subscription['items']['data'][0]['price']['id']
    assert saved_sub['tier'] == 'pro'
    assert saved_sub['current_period_start'] == dummy_stripe_subscription['items']['data'][0]['current_period_start']
    assert saved_sub['current_period_start'] == dummy_stripe_subscription['items']['data'][0]['current_period_end']
    assert saved_sub['cancel_at_period_end'] == dummy_stripe_subscription.cancel_at_period_end
