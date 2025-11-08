from core.apps.common.services.cache import BaseCacheService


def test_cache_set_and_retrieve_data(cache_service: BaseCacheService):
    """Test that the cache has been set and the data has been retrieved."""

    key = 'test_key'
    expected_data = 'test_data'

    cache_service.set(key=key, data=expected_data, timeout=10)

    assert cache_service.get(key=key) == expected_data


def test_cache_delete_data(cache_service: BaseCacheService):
    """Test that the data has been deleted from the cache."""

    key = 'test_key'
    expected_data = 'test_data'

    cache_service.set(key=key, data=expected_data, timeout=10)

    cache_service.delete(key=key)

    assert cache_service.get(key=key) is None
