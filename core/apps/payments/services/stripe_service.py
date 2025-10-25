from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from dataclasses import dataclass
from logging import Logger

import orjson
import stripe

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.cache import BaseCacheService
from core.apps.payments.constants import (
    STRIPE_ALLOWED_EVENTS,
    STRIPE_SUBSCRIPTION_TIERS,
)
from core.apps.payments.exceptions import (
    StripeCustomerIdNotStringError,
    StripeInvalidSubPriceError,
    StripeInvalidSubTierError,
    StripeNotAllowedEventTypeError,
    StripeSubAlreadyExistsError,
)
from core.apps.payments.providers.stripe_provider import BaseStripeProvider


@dataclass
class BaseStripeEventValidatorService(ABC):
    @abstractmethod
    def validate(self, event: stripe.Event) -> None: ...


class StripeEventValidatorService(BaseStripeEventValidatorService):
    def validate(self, event: stripe.Event) -> None:
        allowed_events = STRIPE_ALLOWED_EVENTS
        if event['type'] not in allowed_events:
            raise StripeNotAllowedEventTypeError(event_type=event['type'])


@dataclass
class BaseCustomerIdValidatorService(ABC):
    @abstractmethod
    def validate(self, customer_id: str) -> None: ...


class CustomerIdValidatorService(BaseCustomerIdValidatorService):
    def validate(self, customer_id: str) -> None:
        if not isinstance(customer_id, str):
            raise StripeCustomerIdNotStringError(customer_id=customer_id, customer_id_type=type(customer_id))


@dataclass
class BaseStripeSubValidatorService(ABC):
    @abstractmethod
    def validate(self, sub: dict | None) -> None: ...


class StripeSubValidatorService(BaseStripeSubValidatorService):
    def validate(self, sub: dict | None) -> None:
        if sub is not None and sub['status'] == 'active':
            raise StripeSubAlreadyExistsError(customer_id=sub['customer_id'])


@dataclass
class BaseStripeService(ABC):
    stripe_provider: BaseStripeProvider
    cache_service: BaseCacheService
    logger: Logger

    @abstractmethod
    def save_customer_id(self, user_id: int, customer_id: str) -> bool: ...

    @abstractmethod
    def save_sub_by_customer_id(self, customer_id: str, data: dict) -> bool: ...

    @abstractmethod
    def update_customer_subscription_state(self, customer_id: str, sub: stripe.Subscription) -> bool: ...

    @abstractmethod
    def create_checkout_session(self, customer_id: str, user_id: int, sub_tier: str) -> stripe.checkout.Session: ...

    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> stripe.Customer: ...

    @abstractmethod
    def get_sub_price_by_sub_tier(self, sub_tier: str) -> str: ...

    @abstractmethod
    def get_sub_tier_by_sub_price(self, sub_price: str) -> str: ...

    @abstractmethod
    def get_customer_id(self, user_id: int) -> str | None: ...

    @abstractmethod
    def get_sub_by_customer_id(self, customer_id: str | None) -> dict | None: ...

    @abstractmethod
    def get_subs_list_by_customer_id(self, customer_id: str) -> Iterable[stripe.Subscription]: ...

    @abstractmethod
    def construct_event(self, payload: bytes, signature: str) -> stripe.Event: ...


class StripeService(BaseStripeService):
    _STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_customer_id']
    _STRIPE_SUB_DATA_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_sub_data']
    _STRIPE_SUBSCRIPTION_TIERS = STRIPE_SUBSCRIPTION_TIERS

    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        saved = self.cache_service.set(key=customer_id_cache_key, data=customer_id)
        self.logger.info(
            'Stripe customer_id saved',
            extra={'log_meta': orjson.dumps({'customer_id': customer_id, 'user_id': user_id}).decode()},
        )
        return saved

    def save_sub_by_customer_id(self, customer_id: str, data: dict) -> bool:
        sub_data_cache_key = f'{self._STRIPE_SUB_DATA_CACHE_KEY_PREFIX}{customer_id}'
        saved = self.cache_service.set(key=sub_data_cache_key, data=data)
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
            }
            if sub.default_payment_method and isinstance(sub.default_payment_method, stripe.PaymentMethod)
            else None,
        }
        self.logger.info(
            'Stripe Subscription state has been updated by customer_id',
            extra={'log_meta': orjson.dumps({'customer_id': customer_id}).decode()},
        )
        return self.save_sub_by_customer_id(customer_id=customer_id, data=sub_data)

    def create_checkout_session(self, customer_id: str, user_id: int, sub_tier: str) -> stripe.checkout.Session:
        session = self.stripe_provider.create_checkout_session(
            customer_id=customer_id,
            user_id=user_id,
            sub_price=self.get_sub_price_by_sub_tier(sub_tier=sub_tier),
        )
        self.logger.info(
            'Stripe checkout session has been created',
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
        if sub_tier not in self._STRIPE_SUBSCRIPTION_TIERS:
            raise StripeInvalidSubTierError(sub_tier=sub_tier)

        return self._STRIPE_SUBSCRIPTION_TIERS[sub_tier]

    def get_sub_tier_by_sub_price(self, sub_price: str) -> str:
        stripe_subscription_tiers_inverted = {v: k for k, v in self._STRIPE_SUBSCRIPTION_TIERS.items()}

        if sub_price not in stripe_subscription_tiers_inverted:
            raise StripeInvalidSubPriceError(sub_price=sub_price)

        return stripe_subscription_tiers_inverted[sub_price]

    def get_customer_id(self, user_id: int) -> str | None:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        customer_id = self.cache_service.get(key=customer_id_cache_key)
        if customer_id:
            self.logger.info(
                'Stripe customer_id retrieved',
                extra={'log_meta': orjson.dumps({'customer_id': customer_id, 'user_id': user_id}).decode()},
            )
        else:
            self.logger.info(
                'Stripe customer_id not found',
                extra={'log_meta': orjson.dumps({'user_id': user_id}).decode()},
            )
        return customer_id

    def get_sub_by_customer_id(self, customer_id: str | None) -> dict | None:
        if customer_id is None:
            return None

        sub_data_cache_key = f'{self._STRIPE_SUB_DATA_CACHE_KEY_PREFIX}{customer_id}'
        sub = self.cache_service.get(key=sub_data_cache_key)
        if sub:
            self.logger.info(
                'Stripe sub-data retrieved',
                extra={'log_meta': orjson.dumps({'customer_id': customer_id}).decode()},
            )
        else:
            self.logger.info(
                'Stripe sub-data not found',
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

    def construct_event(self, payload: bytes, signature: str) -> stripe.Event:
        return self.stripe_provider.construct_event(payload=payload, signature=signature)
