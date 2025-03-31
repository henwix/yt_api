import logging

from django.contrib.auth import authenticate, get_user_model, login  # noqa
from django.db import transaction
from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from project.containers import get_container  # noqa
from rest_framework import generics, status  # noqa
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken  # noqa

from .tasks import (
    send_activation_email,
    send_confirmation_email,
    send_reset_password_email,
    send_reset_username_email,
)
from .use_cases.authorize import AuthorizeUserUseCase  # noqa

log = logging.getLogger(__name__)


# class UserLoginView(APIView):
#     def post(self, request):
#         container = get_container()
#         use_case: AuthorizeUserUseCase = container.resolve(AuthorizeUserUseCase)

#         result = use_case.execute(
#             {'username': request.data.get('username')},
#         )

#         username = request.data.get('username')
#         password = request.data.get('password')

#         user = authenticate(username=username, password=password)

#         if not user.otp_enabled:
#             refresh = RefreshToken.for_user(user)
#             access = refresh.access_token

#             return Response({'refresh': refresh, 'access': refresh}, status=201)

#         # генерируем код
#         # сейвим в кеш с почтой
#         # отправляем письмо

#         return Response({'Email sent': 'We send email, please, confirm access'}, status=200)


# class OTPVerifyView(APIView):
#     def post(self, request):
#         container = get_container()
#         service: BaseAuthService = container.resolve(BaseAuthService)

#         code = request.data.get('code')
#         email = request.data.get('email')

#         cached_code = cache.get(f"code for: {email}")

#         if cached_code == code:
#             user = User.objects.filter(email).first()

#             refresh = RefreshToken.for_user(user)
#             access = refresh.access_token

#             return Response({'refresh': refresh, 'access': refresh}, status=201)


class CustomUserViewSet(UserViewSet):
    """
    Custom UserViewSet from Djoser.
    Added:
    - To queryset added prefetch_related('channel')
    Mails for account activation, confirmation, reset_password and reset_username will be send via Celery.
    """

    queryset = get_user_model().objects.all().prefetch_related('channel')

    def _get_mail_args(self, user):
        context = {'user_id': user.pk}
        to = [get_user_email(user)]
        return context, to

    def _serializer_validation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False if self.action == 'resend_activation' else True)
        return user

    def _check_activation_email(self, user):
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context, to = self._get_mail_args(user)
            send_activation_email.apply_async(args=[context, to], queue='email-queue', ignore_result=True)

    def perform_create(self, serializer, *args, **kwargs):
        with transaction.atomic():
            user = serializer.save(*args, **kwargs)
            signals.user_registered.send(sender=self.__class__, user=user, request=self.request)
            transaction.on_commit(lambda: self._check_activation_email(user))

    def perform_update(self, serializer, *args, **kwargs):
        with transaction.atomic():
            user = serializer.save()
            signals.user_updated.send(sender=self.__class__, user=user, request=self.request)
            transaction.on_commit(lambda: self._check_activation_email(user))

    @action(['post'], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(sender=self.__class__, user=user, request=self.request)

        if settings.SEND_CONFIRMATION_EMAIL:
            context, to = self._get_mail_args(user)
            send_confirmation_email.apply_async(args=[context, to], queue='email-queue', ignore_result=True)
        return Response({'success', 'Your account successfully activated!'}, status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        user = self._serializer_validation(request)

        if not settings.SEND_ACTIVATION_EMAIL:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user:
            context, to = self._get_mail_args(user)
            send_activation_email.apply_async(args=[context, to], queue='email-queue', ignore_result=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def reset_password(self, request, *args, **kwargs):
        user = self._serializer_validation(request)

        if user:
            context, to = self._get_mail_args(user)
            send_reset_password_email.apply_async(args=[context, to], queue='email-queue', ignore_result=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False, url_path=f'reset_{get_user_model().USERNAME_FIELD}')
    def reset_username(self, request, *args, **kwargs):
        user = self._serializer_validation(request)

        if user:
            context, to = self._get_mail_args(user)
            send_reset_username_email.apply_async(args=[context, to], queue='email-queue', ignore_result=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
