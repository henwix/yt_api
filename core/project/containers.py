from functools import lru_cache

import punq

from core.apps.channels.containers import initialize_channels
from core.apps.common.services.cache import BaseCacheService, CacheService
from core.apps.reports.containers import initialize_reports
from core.apps.videos.containers import initialize_videos


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    initialize_channels(container)
    initialize_reports(container)
    initialize_videos(container)

    container.register(BaseCacheService, CacheService)

    return container
