from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

import orjson
import stripe

from core.apps.common.constants import CACHE_KEYS
from core.apps.common.services.cache import BaseCacheService
from core.apps.payments.constants import (
    STRIPE_ALLOWED_EVENTS,
    STRIPE_SUBSCRIPTION_TIER_PRICES,
)
from core.apps.payments.enums import StripeSubscriptionAllTiersEnum
from core.apps.payments.exceptions import (
    StripeCustomerIdNotStringError,
    StripeInvalidSubPriceError,
    StripeInvalidSubTierError,
    StripeNotAllowedEventTypeError,
    StripeSubAlreadyExistsError,
    StripeSubDoesNotExistError,
    StripeSubStillActiveError,
)
from core.apps.payments.providers.stripe_provider import BaseStripeProvider
from core.apps.users.entities import AnonymousUserEntity, UserEntity


class BaseStripeEventValidatorService(ABC):
    @abstractmethod
    def validate(self, event: stripe.Event) -> None: ...


class StripeEventValidatorService(BaseStripeEventValidatorService):
    def validate(self, event: stripe.Event) -> None:
        allowed_events = STRIPE_ALLOWED_EVENTS
        if event['type'] not in allowed_events:
            raise StripeNotAllowedEventTypeError(event_type=event['type'])


class BaseCustomerIdValidatorService(ABC):
    @abstractmethod
    def validate(self, customer_id: str) -> None: ...


class CustomerIdValidatorService(BaseCustomerIdValidatorService):
    def validate(self, customer_id: str) -> None:
        if not isinstance(customer_id, str):
            raise StripeCustomerIdNotStringError(customer_id=customer_id, customer_id_type=type(customer_id))


class BaseStripeSubAlreadyExistsValidatorService(ABC):
    @abstractmethod
    def validate(self, sub: dict | None) -> None: ...


class StripeSubAlreadyExistsValidatorService(BaseStripeSubAlreadyExistsValidatorService):
    def validate(self, sub: dict | None) -> None:
        if sub is not None and sub['status'] != 'canceled':
            raise StripeSubAlreadyExistsError(customer_id=sub['customer_id'])


class BaseStripeSubDoesNotExistValidatorService(ABC):
    @abstractmethod
    def validate(self, sub: dict | None) -> None: ...


class StripeSubDoesNotExistValidatorService(BaseStripeSubDoesNotExistValidatorService):
    def validate(self, sub: dict | None) -> None:
        if sub is None or sub['status'] == 'canceled':
            raise StripeSubDoesNotExistError()


@dataclass
class BaseStripeService(ABC):
    stripe_provider: BaseStripeProvider
    cache_service: BaseCacheService

    @abstractmethod
    def save_customer_id(self, user_id: int, customer_id: str) -> bool: ...

    @abstractmethod
    def save_sub_state_by_customer_id(self, customer_id: str, data: dict) -> bool: ...

    @abstractmethod
    def update_customer_sub_state(self, customer_id: str, sub: stripe.Subscription) -> bool: ...

    @abstractmethod
    def create_checkout_session(self, customer_id: str, user_id: int, sub_tier: str) -> stripe.checkout.Session: ...

    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> stripe.Customer: ...

    @abstractmethod
    def get_sub_price_by_sub_tier(self, sub_tier: str) -> str: ...

    @abstractmethod
    def get_sub_tier_by_sub_price(self, sub_price: str) -> str: ...

    @abstractmethod
    def get_sub_tier_by_user(self, user: UserEntity | AnonymousUserEntity) -> str: ...

    @abstractmethod
    def get_customer_id(self, user_id: int) -> str | None: ...

    @abstractmethod
    def delete_customer_id(self, user_id: int) -> bool: ...

    @abstractmethod
    def get_sub_state_by_customer_id(self, customer_id: str | None) -> dict | None: ...

    @abstractmethod
    def delete_sub_state_by_customer_id(self, customer_id: str) -> bool: ...

    @abstractmethod
    def get_subs_list_by_customer_id(self, customer_id: str) -> list[stripe.Subscription]: ...

    @abstractmethod
    def get_customer_portal_session_url(self, customer_id: str) -> str: ...

    @abstractmethod
    def construct_event(self, payload: bytes, signature: str) -> stripe.Event: ...


@dataclass
class StripeService(BaseStripeService):
    logger: Logger
    _STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_customer_id']
    _STRIPE_SUB_DATA_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_sub_data']
    _STRIPE_CUSTOMER_PORTAL_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_customer_portal']
    _STRIPE_SUBSCRIPTION_TIER_PRICES = STRIPE_SUBSCRIPTION_TIER_PRICES
    _STRIPE_SUBSCRIPTION_TIER_PRICES_INVERTED = {v: k for k, v in _STRIPE_SUBSCRIPTION_TIER_PRICES.items()}

    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        saved = self.cache_service.set(key=customer_id_cache_key, data=customer_id)
        return saved

    def save_sub_state_by_customer_id(self, customer_id: str, data: dict) -> bool:
        sub_data_cache_key = f'{self._STRIPE_SUB_DATA_CACHE_KEY_PREFIX}{customer_id}'
        saved = self.cache_service.set(key=sub_data_cache_key, data=data)
        return saved

    def update_customer_sub_state(self, customer_id: str, sub: stripe.Subscription) -> bool:
        sub_data = {
            'subscription_id': sub.id,
            'customer_id': customer_id,
            'status': sub.status,
            'price_id': sub['items']['data'][0]['price']['id'],
            'tier': self.get_sub_tier_by_sub_price(sub_price=sub['items']['data'][0]['price']['id']),
            # TODO: check if I can use just 'sub.current_period_start' and 'sub.current_period_end'
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
        return self.save_sub_state_by_customer_id(customer_id=customer_id, data=sub_data)

    def create_checkout_session(self, customer_id: str, user_id: int, sub_tier: str) -> stripe.checkout.Session:
        session = self.stripe_provider.create_checkout_session(
            customer_id=customer_id,
            user_id=user_id,
            sub_price=self.get_sub_price_by_sub_tier(sub_tier=sub_tier),
            trial_days=7,
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
        if sub_tier not in self._STRIPE_SUBSCRIPTION_TIER_PRICES:
            raise StripeInvalidSubTierError(sub_tier=sub_tier)
        return self._STRIPE_SUBSCRIPTION_TIER_PRICES[sub_tier]

    def get_sub_tier_by_sub_price(self, sub_price: str) -> str:
        if sub_price not in self._STRIPE_SUBSCRIPTION_TIER_PRICES_INVERTED:
            raise StripeInvalidSubPriceError(sub_price=sub_price)
        return self._STRIPE_SUBSCRIPTION_TIER_PRICES_INVERTED[sub_price]

    def get_sub_tier_by_user(self, user: UserEntity | AnonymousUserEntity) -> str:
        if user.is_anonymous:
            return StripeSubscriptionAllTiersEnum.FREE

        sub_data = self.get_sub_state_by_customer_id(customer_id=self.get_customer_id(user_id=user.id))

        if not sub_data or sub_data['status'] not in ['active', 'trialing']:
            return StripeSubscriptionAllTiersEnum.FREE
        else:
            return sub_data['tier']

    def get_customer_id(self, user_id: int) -> str | None:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        return self.cache_service.get(key=customer_id_cache_key)

    def delete_customer_id(self, user_id: int) -> bool:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        return self.cache_service.delete(key=customer_id_cache_key)

    def get_sub_state_by_customer_id(self, customer_id: str | None) -> dict | None:
        if customer_id is None:
            return None

        sub_data_cache_key = f'{self._STRIPE_SUB_DATA_CACHE_KEY_PREFIX}{customer_id}'
        return self.cache_service.get(key=sub_data_cache_key)

    def delete_sub_state_by_customer_id(self, customer_id: str) -> bool:
        sub_data_cache_key = f'{self._STRIPE_SUB_DATA_CACHE_KEY_PREFIX}{customer_id}'
        return self.cache_service.delete(key=sub_data_cache_key)

    def get_subs_list_by_customer_id(self, customer_id: str) -> list[stripe.Subscription]:
        return self.stripe_provider.get_subs_list(
            status='all',
            customer_id=customer_id,
            limit=1,
            expand=['data.default_payment_method'],
        )

    def get_customer_portal_session_url(self, customer_id: str) -> str:
        cache_key = f'{self._STRIPE_CUSTOMER_PORTAL_CACHE_KEY_PREFIX}{customer_id}'
        customer_portal_url = self.cache_service.get(key=cache_key)

        if customer_portal_url is None:
            customer_portal_url = self.stripe_provider.get_customer_portal_session_url(customer_id=customer_id)
            self.cache_service.set(key=cache_key, data=customer_portal_url, timeout=60 * 10)

        return customer_portal_url

    def construct_event(self, payload: bytes, signature: str) -> stripe.Event:
        return self.stripe_provider.construct_event(payload=payload, signature=signature)


class BaseStripeSubStillActiveValidatorService(ABC):
    @abstractmethod
    def validate(self, user: UserEntity): ...


@dataclass
class StripeSubStillActiveValidatorService(BaseStripeSubStillActiveValidatorService):
    stripe_service: BaseStripeService

    def validate(self, user: UserEntity) -> None:
        sub = self.stripe_service.get_sub_state_by_customer_id(
            customer_id=self.stripe_service.get_customer_id(user_id=user.id)
        )
        if sub is not None and sub['status'] != 'canceled':
            raise StripeSubStillActiveError(user_id=user.id)
