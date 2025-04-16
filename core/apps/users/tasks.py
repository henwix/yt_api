import logging

from django.contrib.auth import get_user_model

from celery import shared_task
from djoser.conf import settings

from core.apps.common.clients.email_client import EmailClient


log = logging.getLogger(__name__)


START_LOG_FORMAT = 'Start sending %s email to %s'
SUCCESS_LOG_FORMAT = '%s email successfully sent to %s'


def _get_user_context(context):
    user = get_user_model().objects.get(pk=context.get('user_id'))
    context['user'] = user
    return context


@shared_task
def send_activation_email(context, to):
    log.info(START_LOG_FORMAT, 'activation', to[0])
    settings.EMAIL.activation(None, _get_user_context(context)).send(to)
    log.info(SUCCESS_LOG_FORMAT, 'Activation', to[0])


@shared_task
def send_confirmation_email(context, to):
    log.info(START_LOG_FORMAT, 'confirmation', to[0])
    settings.EMAIL.confirmation(None, _get_user_context(context)).send(to)
    log.info(SUCCESS_LOG_FORMAT, 'Confirmation', to[0])


@shared_task
def send_reset_password_email(context, to):
    log.info(START_LOG_FORMAT, 'password reset', to[0])
    settings.EMAIL.password_reset(None, _get_user_context(context)).send(to)
    log.info(SUCCESS_LOG_FORMAT, 'Password reset', to[0])


@shared_task
def send_reset_username_email(context, to):
    log.info(START_LOG_FORMAT, 'username reset', to[0])
    settings.EMAIL.username_reset(None, _get_user_context(context)).send(to)
    log.info(SUCCESS_LOG_FORMAT, 'Username reset', to[0])


@shared_task(bind=True, max_retries=5)
def send_otp_code_email(self, email: str, code: str):
    email_client: EmailClient = EmailClient()

    try:
        log.info('Trying to set SMTP connection and send email to %s', email)
        msg = email_client.build_smtp_email(
            to=[email],
            context={'email': email, 'code': code},
        )
        email_client.send_email(msg)
    except Exception as e:
        log.info('Error raise while SMTP connect: %s', e)
        raise self.retry(countdown=5)
    else:
        log.info('OTP email successfully sent to email: %s, code: %s', email, code)
