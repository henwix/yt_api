import logging
from celery import shared_task
from djoser.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def _get_user_context(context):
    user = get_user_model().objects.get(pk=context.get('user_id'))
    context["user"] = user
    return context


@shared_task
def send_activation_email(context, to):
    logger.info("Start sending activation email to %s", to[0])
    settings.EMAIL.activation(None, _get_user_context(context)).send(to)
    logger.info("Activation email successfuly sent to %s", to[0])


@shared_task
def send_confirmation_email(context, to):
    logger.info("Start sending confirmation email to %s", to[0])
    settings.EMAIL.confirmation(None, _get_user_context(context)).send(to)
    logger.info("Confirmation email successfuly sent to %s", to[0])


@shared_task
def send_reset_password_email(context, to):
    logger.info("Start sending password reset email to %s", to[0])
    settings.EMAIL.password_reset(None, _get_user_context(context)).send(to)
    logger.info("Password reset email successfuly sent to %s", to[0])


@shared_task
def send_reset_username_email(context, to):
    logger.info("Start sending username reset email to %s", to[0])
    settings.EMAIL.username_reset(None, _get_user_context(context)).send(to)
    logger.info("Username reset email successfuly sent to %s", to[0])
