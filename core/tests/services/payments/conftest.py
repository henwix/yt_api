import punq
import pytest

from core.apps.payments.services.stripe_service import BaseStripeService


@pytest.fixture
def stripe_service(container: punq.Container) -> BaseStripeService:
    return container.resolve(BaseStripeService)


# @pytest.fixture
# def dummy_stripe_subscription() -> SimpleNamespace:
#     """Mock stripe.Subscription object using SimpleNamespace"""
#
#     return SimpleNamespace(
#         id='sub_123456789',
#         status='active',
#         cancel_at_period_end=False,
#         default_payment_method='123',
#         items={
#             'data': [
#                 {
#                     'price': {
#                         'id': 'price_123456789',
#                     },
#                     'current_period_start': 1762366397,
#                     'current_period_end': 1764958397,
#                 },
#             ],
#         },
#     )
