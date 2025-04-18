import logging

from celery import shared_task


log = logging.getLogger(__name__)


@shared_task
def test_task():
    log.info('test task running')
