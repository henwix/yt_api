from logging import Logger

from django.contrib.auth import get_user_model

import orjson
import punq
from celery import shared_task
from djoser.conf import settings

from core.apps.common.clients.email_client import EmailClient
from core.project.containers import get_container


def _get_user_context(context):
    user = get_user_model().objects.get(pk=context.get('user_id'))
    context['user'] = user
    return context


@shared_task
def send_activation_email(context, to):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)

    logger.info(
        'Start sending activation email',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )
    settings.EMAIL.activation(None, _get_user_context(context)).send(to)
    logger.info(
        'Activation email successfully sent',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )


@shared_task
def send_confirmation_email(context, to):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)

    logger.info(
        'Start sending confirmation email',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )
    settings.EMAIL.confirmation(None, _get_user_context(context)).send(to)
    logger.info(
        'Confirmation email successfully sent',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )


@shared_task
def send_reset_password_email(context, to):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)

    logger.info(
        'Start sending password reset email',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )
    settings.EMAIL.password_reset(None, _get_user_context(context)).send(to)
    logger.info(
        'Password reset email successfully sent',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )


@shared_task
def send_reset_username_email(context, to):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)

    logger.info(
        'Start sending username reset email',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )
    settings.EMAIL.username_reset(None, _get_user_context(context)).send(to)
    logger.info(
        'Username reset email successfully sent',
        extra={'log_meta': orjson.dumps({'email': to[0]}).decode()},
    )


@shared_task(bind=True, max_retries=5)
def send_otp_code_email(self, email: str, code: str):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)
    email_client: EmailClient = container.resolve(EmailClient)

    try:
        logger.info(
            'Trying to set SMTP connection and send email',
            extra={'log_meta': orjson.dumps({'email': email}).decode()},
        )
        msg = email_client.build_smtp_email(
            to=[email],
            context={'email': email, 'code': code},
        )
        email_client.send_email(msg)
    except Exception as error:
        logger.info(
            'Error raised while trying to set SMTP connection',
            extra={'log_meta': orjson.dumps({'error': str(error)}).decode()},
        )
        raise self.retry(countdown=5)
    else:
        logger.info(
            'OTP email successfully sent to email',
            extra={'log_meta': orjson.dumps({'email': email, 'code': code}).decode()},
        )
