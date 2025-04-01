from typing import Any

import factory


def factory_lazy_function(value: Any, max_length: int = 20):
    return factory.LazyFunction(lambda: value()[:max_length])
