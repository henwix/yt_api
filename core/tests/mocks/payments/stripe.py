from dataclasses import dataclass
from types import SimpleNamespace

from core.apps.payments.enums import StripeSubscriptionPaidTiersEnum
from core.apps.payments.providers.stripe_provider import StripeProvider
from core.apps.payments.services.stripe_service import StripeService


@dataclass
class DummyStripeService(StripeService):
    get_sub_tier_by_sub_price_response: str = StripeSubscriptionPaidTiersEnum.PRO
    get_sub_price_by_sub_tier_response: str = 'price_123456789'

    def get_sub_tier_by_sub_price(self, sub_price: str) -> str:  # noqa
        return self.get_sub_tier_by_sub_price_response

    def get_sub_price_by_sub_tier(self, sub_tier: str) -> str:
        return self.get_sub_price_by_sub_tier_response


@dataclass
class DummyStripeProvider(StripeProvider):
    expected_customer_id: str = 'cus_123456789'
    expected_customer_portal_session_url: str = 'https://example.com'
    customer_portal_session_url_call_count: int = 0

    def create_checkout_session(
        self,
        customer_id: str,
        user_id: int,
        sub_price: str,
        trial_days: int | None = None,
    ) -> dict:
        return {
            'customer_id': customer_id,
            'user_id': user_id,
            'sub_price': sub_price,
            'trial_days': trial_days,
        }

    def create_customer(self, email: str, user_id: int) -> SimpleNamespace:
        return SimpleNamespace(email=email, user_id=user_id, id=self.expected_customer_id)

    def get_subs_list(
        self,
        status: str,
        customer_id: str | None = None,
        limit: int = 10,
        expand: list | None = None,
    ) -> dict:
        return {
            'status': status,
            'customer_id': customer_id,
            'limit': limit,
            'expand': expand,
        }

    def construct_event(self, payload: bytes, signature: str) -> dict:
        return {'payload': payload, 'signature': signature}

    def get_customer_portal_session_url(self, customer_id: str) -> str:
        self.customer_portal_session_url_call_count += 1
        return self.expected_customer_portal_session_url
