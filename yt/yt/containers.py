from functools import lru_cache

import punq
from apps.channels.containers import initialize_channels
from apps.reports.containers import initialize_reports
from apps.videos.containers import initialize_videos


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    initialize_channels(container)
    initialize_reports(container)
    initialize_videos(container)

    return container
