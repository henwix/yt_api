from logging import Logger

import orjson
import punq
from celery import shared_task

from core.apps.common.clients.email_client import EmailClient
from core.project.containers import get_container


@shared_task(bind=True, max_retries=5)
def send_email(self, to: list[str], context: dict, subject: str, template: str):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)
    email_client: EmailClient = container.resolve(EmailClient)

    try:
        logger.info(
            'Trying to set SMTP connection and send email via Celery Task',
            extra={'log_meta': orjson.dumps({'subject': subject, 'template': template}).decode()},
        )
        msg = email_client.build_smtp_email(
            to=to,
            context=context,
            subject=subject,
            template=template,
        )
        email_client.send_email(msg)

    except Exception as error:
        logger.info(
            'Error raised while trying to set SMTP connection',
            extra={'log_meta': orjson.dumps({'detail': str(error)}).decode()},
        )
        raise self.retry(countdown=5)

    else:
        logger.info(
            'Email successfully sent via Celery Task',
            extra={'log_meta': orjson.dumps({'subject': subject, 'template': template}).decode()},
        )
