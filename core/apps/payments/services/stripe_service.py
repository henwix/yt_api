from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger
from typing import Iterable

from django.db.utils import settings

import orjson
import stripe

from core.apps.common.services.cache import BaseCacheService
from core.apps.payments.exceptions import (
    StripeCustomerIdIsNotStringError,
    StripeInvalidSubPriceError,
    StripeInvalidSubTierError,
    StripeNotAllowedEventTypeError,
    StripeSubAlreadyExistsError,
)
from core.apps.payments.providers.stripe_provider import BaseStripeProvider


@dataclass
class BaseStripeEventValidatorService(ABC):
    @abstractmethod
    def validate(self, event: stripe.Event) -> None:
        ...


class StripeEventValidatorService(BaseStripeEventValidatorService):
    def validate(self, event: stripe.Event) -> None:
        allowed_events = settings.STRIPE_ALLOWED_EVENTS
        if event['type'] not in allowed_events:
            raise StripeNotAllowedEventTypeError(event_type=event['type'])


@dataclass
class BaseCustomerIdValidatorService(ABC):
    @abstractmethod
    def validate(self, customer_id: str) -> None:
        ...


class CustomerIdValidatorService(BaseCustomerIdValidatorService):
    def validate(self, customer_id: str) -> None:
        if not isinstance(customer_id, str):
            raise StripeCustomerIdIsNotStringError(customer_id=customer_id, customer_id_type=type(customer_id))


@dataclass
class BaseStripeSubValidatorService(ABC):
    @abstractmethod
    def validate(self, sub: dict) -> None:
        ...


class StripeSubValidatorService(BaseStripeSubValidatorService):
    def validate(self, sub: dict) -> None:
        if sub is not None and sub['status'] == 'active':
            raise StripeSubAlreadyExistsError(customer_id=sub['customer_id'])


@dataclass
class BaseStripeService(ABC):
    stripe_provider: BaseStripeProvider
    cache_service: BaseCacheService
    logger: Logger

    @abstractmethod
    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        ...

    @abstractmethod
    def save_sub_by_customer_id(self, customer_id: str, data: dict) -> bool:
        ...

    @abstractmethod
    def update_customer_subscription_state(self, customer_id: str, sub: stripe.Subscription) -> bool:
        ...

    @abstractmethod
    def create_checkout_session(self, customer_id: str, user_id: int, sub_tier: str) -> stripe.checkout.Session:
        ...

    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> stripe.Customer:
        ...

    @abstractmethod
    def get_sub_price_by_sub_tier(self, sub_tier: str) -> str:
        ...

    @abstractmethod
    def get_sub_tier_by_sub_price(self, sub_price: str) -> str:
        ...

    @abstractmethod
    def get_customer_id(self, user_id: int) -> str | None:
        ...

    @abstractmethod
    def get_sub_by_customer_id(self, customer_id: str | None) -> dict | None:
        ...

    @abstractmethod
    def get_subs_list_by_customer_id(self, customer_id: str) -> Iterable[stripe.Subscription]:
        ...

    @abstractmethod
    def construct_event(self, payload, signature) -> stripe.Event:
        ...


class StripeService(BaseStripeService):
    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        customer_id_cache_key = f'stripe:user:{user_id}'
        saved = self.cache_service.cache_data(key=customer_id_cache_key, data=customer_id)
        self.logger.info(
            'Stripe customer_id saved to cache',
            extra={'log_meta': orjson.dumps({'customer_id': customer_id, 'user_id': user_id}).decode()},
        )
        return saved

    def save_sub_by_customer_id(self, customer_id: str, data: dict) -> bool:
        sub_data_cache_key = f'stripe:customer:{customer_id}'
        saved = self.cache_service.cache_data(key=sub_data_cache_key, data=data)
        self.logger.info(
            'Stripe sub data saved by customer_id',
            extra={'log_meta': orjson.dumps({'customer_id': customer_id}).decode()},
        )
        return saved

    def update_customer_subscription_state(self, customer_id: str, sub: stripe.Subscription) -> bool:
        sub_data = {
            'subscription_id': sub.id,
            'customer_id': customer_id,
            'status': sub.status,
            'price_id': sub['items']['data'][0]['price']['id'],
            'tier': self.get_sub_tier_by_sub_price(sub_price=sub['items']['data'][0]['price']['id']),
            'current_period_start': sub['items']['data'][0]['current_period_start'],
            'current_period_end': sub['items']['data'][0]['current_period_end'],
            'cancel_at_period_end': sub.cancel_at_period_end,
            'payment_method': {
                'brand': sub.default_payment_method.card.brand,
                'last4': sub.default_payment_method.card.last4,
            } if sub.default_payment_method and isinstance(sub.default_payment_method, stripe.PaymentMethod) else None,
        }
        self.logger.info(
            'Stripe Subscription state has been updated',
            extra={'log_meta': orjson.dumps({'customer_id': customer_id, 'sub_data': sub_data}).decode()},
        )
        return self.save_sub_by_customer_id(customer_id=customer_id, data=sub_data)

    def create_checkout_session(self, customer_id: str, user_id: int, sub_tier: str) -> stripe.checkout.Session:
        session = self.stripe_provider.create_checkout_session(
            customer_id=customer_id,
            user_id=user_id,
            sub_price=self.get_sub_price_by_sub_tier(sub_tier=sub_tier),
        )
        self.logger.info(
            'Stripe session has been created',
            extra={
                'log_meta': orjson.dumps(
                    {'customer_id': customer_id, 'user_id': user_id, 'sub_tier': sub_tier},
                ).decode(),
            },
        )
        return session

    def create_customer(self, email: str, user_id: int) -> stripe.Customer:
        new_customer = self.stripe_provider.create_customer(email=email, user_id=user_id)
        self.logger.info(
            'New Stripe customer has been created',
            extra={'log_meta': orjson.dumps({'customer_id': new_customer.id, 'user_id': user_id}).decode()},
        )
        return new_customer

    def get_sub_price_by_sub_tier(self, sub_tier: str) -> str:
        sub_tiers = {
            'pro': settings.STRIPE_PRO_SUB_PRICE,
            'premium': settings.STRIPE_PREMIUM_SUB_PRICE,
        }

        if sub_tier not in sub_tiers:
            raise StripeInvalidSubTierError(sub_tier=sub_tier)

        return sub_tiers[sub_tier]

    def get_sub_tier_by_sub_price(self, sub_price: str) -> str:
        sub_prices = {
            settings.STRIPE_PRO_SUB_PRICE: 'pro',
            settings.STRIPE_PREMIUM_SUB_PRICE: 'premium',
        }

        if sub_price not in sub_prices:
            raise StripeInvalidSubPriceError(sub_price=sub_price)

        return sub_prices[sub_price]

    def get_customer_id(self, user_id: int) -> str | None:
        customer_id_cache_key = f'stripe:user:{user_id}'
        customer_id = self.cache_service.get_cached_data(key=customer_id_cache_key)
        if customer_id:
            self.logger.info(
                'Stripe customer_id retrieved from cache',
                extra={'log_meta': orjson.dumps({'customer_id': customer_id, 'user_id': user_id}).decode()},
            )
        else:
            self.logger.info(
                'Stripe customer_id not found in cache',
                extra={'log_meta': orjson.dumps({'user_id': user_id}).decode()},
            )
        return customer_id

    def get_sub_by_customer_id(self, customer_id: str | None) -> dict | None:
        if customer_id is None:
            return None

        customer_id_sub_cache_key = f'stripe:customer:{customer_id}'
        sub = self.cache_service.get_cached_data(key=customer_id_sub_cache_key)
        if sub:
            self.logger.info(
                'Stripe sub-data retrieved from cache',
                extra={'log_meta': orjson.dumps({'customer_id': customer_id}).decode()},
            )
        else:
            self.logger.info(
                'Stripe sub-data not found in cache',
                extra={'log_meta': orjson.dumps({'customer_id': customer_id}).decode()},
            )
        return sub

    def get_subs_list_by_customer_id(self, customer_id: str) -> Iterable[stripe.Subscription]:
        return self.stripe_provider.get_subs_list(
            status='all',
            customer_id=customer_id,
            limit=1,
            expand=['data.default_payment_method'],
        )

    def construct_event(self, payload, signature) -> stripe.Event:
        return self.stripe_provider.construct_event(payload=payload, signature=signature)
