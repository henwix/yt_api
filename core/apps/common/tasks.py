from logging import Logger

from celery import shared_task

from core.project.containers import get_container


@shared_task
def test_task():
    container = get_container()
    logger: Logger = container.resolve(Logger)

    logger.info('test task running')
