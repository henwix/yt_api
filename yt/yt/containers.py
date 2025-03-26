from functools import lru_cache

import punq

from yt.apps.videos.services.videos import BaseVideoService, VideoService


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


# TODO: узнать тут в целом про всё, а также, как делить initialize_container по приложениям
def _initialize_container() -> punq.Container:
    container = punq.Container()

    container.register(BaseVideoService, VideoService)

    return container
