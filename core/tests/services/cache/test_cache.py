import pytest

from core.apps.common.services.cache import BaseCacheService


@pytest.mark.django_db
def test_cache_set_and_retrieve_data(cache_service: BaseCacheService):
    """Test cache set and retrieve data."""
    key = 'test_key'
    expected_data = 'test_data'

    cache_service.cache_data(key=key, data=expected_data, timeout=10)

    assert cache_service.get_cached_data(key=key) == expected_data


@pytest.mark.django_db
def test_cache_delete_data(cache_service: BaseCacheService):
    """Test data deleted from cache."""
    key = 'test_key'
    expected_data = 'test_data'

    cache_service.cache_data(key=key, data=expected_data, timeout=10)

    cache_service.delete_cached_data(key=key)

    assert cache_service.get_cached_data(key=key) is None
