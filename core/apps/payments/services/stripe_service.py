from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from logging import Logger

from django.db.utils import settings

import orjson
from stripe import Customer

from core.apps.common.services.cache import BaseCacheService
from core.apps.payments.providers.stripe_provider import BaseStripeProvider


@dataclass
class BaseStripeService(ABC):
    stripe_provider: BaseStripeProvider
    cache_service: BaseCacheService
    logger: Logger

    @abstractmethod
    def create_customer(self, email: str, user_id: int) -> Customer:
        ...

    @abstractmethod
    def get_customer_id(self, user_id: int) -> str | None:
        ...

    @abstractmethod
    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        ...

    @abstractmethod
    def get_api_key(self) -> str:
        ...


class StripeService(BaseStripeService):
    def create_customer(self, email: str, user_id: int) -> Customer:
        new_customer = self.stripe_provider.create_customer(email=email, user_id=user_id)
        self.logger.info(
            'New Stripe customer has been created',
            extra={'log_meta': orjson.dumps({'customer_id': new_customer.id, 'user_id': user_id}).decode()},
        )
        return new_customer

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

    def save_customer_id(self, user_id: int, customer_id: str) -> bool:
        customer_id_cache_key = f'stripe:user:{user_id}'
        saved = self.cache_service.cache_data(key=customer_id_cache_key, data=customer_id)
        self.logger.info(
            'Stripe customer_id saved to cache',
            extra={'log_meta': orjson.dumps({'customer_id': customer_id, 'user_id': user_id}).decode()},
        )
        return saved

    def get_api_key(self) -> str:
        return settings.STRIPE_SECRET_KEY
