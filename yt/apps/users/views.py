from django.contrib.auth import get_user_model
from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .tasks import (
    send_activation_email,
    send_confirmation_email,
    send_reset_password_email,
    send_reset_username_email,
)


class CustomUserViewSet(UserViewSet):
    """
    Custom UserViewSet from Djoser.
    Added:
    - To queryset added prefetch_related('channel')
    Mails for account activation, confirmation, reset_password and reset_username will be send via Celery.
    """

    queryset = get_user_model().objects.all().prefetch_related("channel")

    def _get_mail_args(self, user):
        context = {"user_id": user.pk}
        to = [get_user_email(user)]
        return context, to

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(sender=self.__class__, user=user, request=self.request)

        if settings.SEND_ACTIVATION_EMAIL:
            context, to = self._get_mail_args(user)
            send_activation_email.apply_async(args=[context, to], ignore_result=True)

    def perform_update(self, serializer, *args, **kwargs):
        # FIXME: сделать переброс активации при смене почты через Celery в этом методе
        return super().perform_update(serializer, *args, **kwargs)

    def _serializer_validation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)
        return user

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(sender=self.__class__, user=user, request=self.request)

        if settings.SEND_CONFIRMATION_EMAIL:
            context, to = self._get_mail_args(user)
            send_confirmation_email.apply_async(args=[context, to], ignore_result=True)
        return Response({"success", "Your account successfuly activated!"}, status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        user = self._serializer_validation(request)

        if not settings.SEND_ACTIVATION_EMAIL:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user:
            context, to = self._get_mail_args(user)
            send_activation_email.apply_async(args=[context, to], ignore_result=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        user = self._serializer_validation(request)

        if user:
            context, to = self._get_mail_args(user)
            send_reset_password_email.apply_async(args=[context, to], ignore_result=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path=f"reset_{get_user_model().USERNAME_FIELD}")
    def reset_username(self, request, *args, **kwargs):
        user = self._serializer_validation(request)

        if user:
            context, to = self._get_mail_args(user)
            send_reset_username_email.apply_async(args=[context, to], ignore_result=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
