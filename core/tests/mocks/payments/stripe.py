from core.apps.payments.services.stripe_service import StripeService


class DummyStripeService(StripeService):
    get_sub_tier_by_sub_price_response: str = 'pro'

    def get_sub_tier_by_sub_price(self, sub_price: str) -> str:  # noqa
        return self.get_sub_tier_by_sub_price_response
