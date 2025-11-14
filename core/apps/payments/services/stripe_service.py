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
    STRIPE_SUBSCRIPTION_TRIAL_DAYS,
)
from core.apps.payments.enums import StripeSubscriptionAllTiersEnum, StripeSubscriptionStatusesEnum
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
        if sub is not None and sub['status'] != StripeSubscriptionStatusesEnum.CANCELED:
            raise StripeSubAlreadyExistsError(customer_id=sub['customer_id'])


class BaseStripeSubDoesNotExistValidatorService(ABC):
    @abstractmethod
    def validate(self, sub: dict | None) -> None: ...


class StripeSubDoesNotExistValidatorService(BaseStripeSubDoesNotExistValidatorService):
    def validate(self, sub: dict | None) -> None:
        if sub is None or sub['status'] == StripeSubscriptionStatusesEnum.CANCELED:
            raise StripeSubDoesNotExistError()


@dataclass
class BaseStripeService(ABC):
    stripe_provider: BaseStripeProvider
    cache_service: BaseCacheService

    @abstractmethod
    def save_customer_id(self, user_id: int, customer_id: str) -> bool: ...

    @abstractmethod
    def get_customer_id(self, user_id: int) -> str | None: ...

    @abstractmethod
    def delete_customer_id(self, user_id: int) -> bool: ...

    @abstractmethod
    def save_sub_state_by_customer_id(self, customer_id: str, state: dict) -> bool: ...

    @abstractmethod
    def get_sub_state_by_customer_id(self, customer_id: str | None) -> dict | None: ...

    @abstractmethod
    def delete_sub_state_by_customer_id(self, customer_id: str) -> bool: ...

    @abstractmethod
    def extract_sub_payment_method_info(self, pm: stripe.PaymentMethod | str) -> dict | None: ...

    @abstractmethod
    def build_sub_state(self, customer_id: str, sub: stripe.Subscription) -> dict: ...

    @abstractmethod
    def create_checkout_session(
        self, customer_id: str, user_id: int, sub_tier: str, trial_days: int | None = None
    ) -> stripe.checkout.Session: ...

    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> stripe.Customer: ...

    @abstractmethod
    def get_sub_price_by_sub_tier(self, sub_tier: str) -> str: ...

    @abstractmethod
    def get_sub_tier_by_sub_price(self, sub_price: str) -> str: ...

    @abstractmethod
    def get_sub_tier_by_user(self, user: UserEntity | AnonymousUserEntity) -> str: ...

    @abstractmethod
    def get_subs_list_by_customer_id(self, customer_id: str) -> list[stripe.Subscription]: ...

    @abstractmethod
    def get_customer_portal_session_url(self, customer_id: str) -> str: ...

    @abstractmethod
    def construct_event(self, payload: bytes, signature: str) -> stripe.Event: ...

    @abstractmethod
    def get_sub_trial_days(self, sub_state: dict | None = None) -> int | None: ...


@dataclass
class StripeService(BaseStripeService):
    logger: Logger
    _STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_customer_id']
    _STRIPE_SUB_STATE_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_sub_state']
    _STRIPE_CUSTOMER_PORTAL_CACHE_KEY_PREFIX = CACHE_KEYS['stripe_customer_portal']
    _STRIPE_SUBSCRIPTION_TIER_PRICES = STRIPE_SUBSCRIPTION_TIER_PRICES
    _STRIPE_SUBSCRIPTION_TIER_PRICES_INVERTED = {v: k for k, v in _STRIPE_SUBSCRIPTION_TIER_PRICES.items()}

    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        saved = self.cache_service.set(key=customer_id_cache_key, data=customer_id)
        return saved

    def get_customer_id(self, user_id: int) -> str | None:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        return self.cache_service.get(key=customer_id_cache_key)

    def delete_customer_id(self, user_id: int) -> bool:
        customer_id_cache_key = f'{self._STRIPE_CUSTOMER_ID_CACHE_KEY_PREFIX}{user_id}'
        return self.cache_service.delete(key=customer_id_cache_key)

    def save_sub_state_by_customer_id(self, customer_id: str, state: dict) -> bool:
        sub_state_cache_key = f'{self._STRIPE_SUB_STATE_CACHE_KEY_PREFIX}{customer_id}'
        saved = self.cache_service.set(key=sub_state_cache_key, data=state)
        return saved

    def get_sub_state_by_customer_id(self, customer_id: str | None) -> dict | None:
        if customer_id is None:
            return None

        sub_state_cache_key = f'{self._STRIPE_SUB_STATE_CACHE_KEY_PREFIX}{customer_id}'
        return self.cache_service.get(key=sub_state_cache_key)

    def delete_sub_state_by_customer_id(self, customer_id: str) -> bool:
        sub_state_cache_key = f'{self._STRIPE_SUB_STATE_CACHE_KEY_PREFIX}{customer_id}'
        return self.cache_service.delete(key=sub_state_cache_key)

    def extract_sub_payment_method_info(self, pm: stripe.PaymentMethod | str) -> dict | None:
        if not pm or not isinstance(pm, stripe.PaymentMethod):
            return None

        pm_type: str | None = pm.get('type')
        pm_data: dict = pm.get(pm_type, {})

        return {
            'type': pm_type,
            'brand': pm_data.get('brand'),
            'last4': pm_data.get('last4'),
            'bank': pm_data.get('bank'),
            'bank_name': pm_data.get('bank_name'),
            'email': pm_data.get('email'),
        }

    def build_sub_state(self, customer_id: str, sub: stripe.Subscription) -> dict:
        sub_item_data = sub['items']['data'][0]
        sub_price_id = sub_item_data['price']['id']

        return {
            'subscription_id': sub['id'],
            'customer_id': customer_id,
            'status': sub['status'],
            'price_id': sub_price_id,
            'tier': self.get_sub_tier_by_sub_price(sub_price=sub_price_id),
            'current_period_start': sub_item_data['current_period_start'],
            'current_period_end': sub_item_data['current_period_end'],
            'cancel_at_period_end': sub['cancel_at_period_end'],
            'payment_method': self.extract_sub_payment_method_info(pm=sub.get('default_payment_method')),
        }

    def create_checkout_session(
        self, customer_id: str, user_id: int, sub_tier: str, trial_days: int | None = None
    ) -> stripe.checkout.Session:
        session = self.stripe_provider.create_checkout_session(
            customer_id=customer_id,
            user_id=user_id,
            sub_price=self.get_sub_price_by_sub_tier(sub_tier=sub_tier),
            trial_days=trial_days,
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

        sub_state = self.get_sub_state_by_customer_id(customer_id=self.get_customer_id(user_id=user.id))

        if not sub_state or sub_state['status'] not in [
            StripeSubscriptionStatusesEnum.ACTIVE,
            StripeSubscriptionStatusesEnum.TRIALING,
        ]:
            return StripeSubscriptionAllTiersEnum.FREE
        else:
            return sub_state['tier']

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
            self.cache_service.set(key=cache_key, data=customer_portal_url, timeout=60 * 5)

        return customer_portal_url

    def construct_event(self, payload: bytes, signature: str) -> stripe.Event:
        return self.stripe_provider.construct_event(payload=payload, signature=signature)

    def get_sub_trial_days(self, sub_state: dict | None = None) -> int | None:
        return STRIPE_SUBSCRIPTION_TRIAL_DAYS if sub_state is None else None


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
        if sub is not None and sub['status'] != StripeSubscriptionStatusesEnum.CANCELED:
            raise StripeSubStillActiveError(user_id=user.id)
