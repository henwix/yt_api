from functools import lru_cache

import punq

from core.apps.channels.containers import init_channels
from core.apps.common.containers import init_common
from core.apps.reports.containers import init_reports
from core.apps.users.containers import init_users
from core.apps.videos.containers import init_videos


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    init_channels(container)
    init_reports(container)
    init_videos(container)
    init_common(container)
    init_users(container)

    return container
