from logging import Logger

from django.contrib.auth import get_user_model  # noqa
from django.db import transaction
from rest_framework import status  # noqa
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

import orjson
import punq
from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from drf_spectacular.utils import (
    extend_schema,
    PolymorphicProxySerializer,
)

from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    JWTOutSerializer,
)
from core.api.v1.schema.response_examples.common import (
    detail_response_example,
    error_response_example,
    jwt_response_example,
)
from core.api.v1.users.serializers.auth import (
    AuthCodeVerifyInSerializer,
    AuthInSerializer,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.pagination import CustomPageNumberPagination
from core.apps.common.permissions.captcha import CaptchaPermission
from core.apps.users.errors import (
    ErrorCodes as UsersErrorCodes,
    ERRORS as USERS_ERRORS,
)
from core.apps.users.tasks import (
    send_activation_email,
    send_confirmation_email,
    send_reset_password_email,
    send_reset_username_email,
)
from core.apps.users.use_cases.auth import (
    AuthorizeUserUseCase,
    VerifyCodeUseCase,
)
from core.project.containers import get_container  # noqa


@extend_schema(
    request=AuthInSerializer,
    responses={
        200: PolymorphicProxySerializer(
            component_name='OAuth2ConnectResponse',
            serializers=[JWTOutSerializer, DetailOutSerializer],
            resource_type_field_name=None,
        ),
        404: DetailOutSerializer,
    },
    examples=[
        jwt_response_example(),
        detail_response_example(
            name='Email sent',
            description='Sends an email with a code to verify OTP',
            value='Email successfully sent',
            status_code=200,
        ),
        error_response_example(USERS_ERRORS[UsersErrorCodes.USER_NOT_FOUND]),
    ],
    summary='Login user and get JWT tokens or send OTP code',
)
class UserLoginView(APIView):
    """Returns access and refresh tokens if user does not have OTP enabled, or
    sends an email with a code to verify OTP."""

    permission_classes = [CaptchaPermission]
    captcha_allowed_methods = ['POST']

    def post(self, request):
        container: punq.Container = get_container()
        use_case: AuthorizeUserUseCase = container.resolve(AuthorizeUserUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = AuthInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                login=serializer.validated_data.get('login'),
                password=serializer.validated_data.get('password'),
            )
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    request=AuthCodeVerifyInSerializer,
    responses={
        200: JWTOutSerializer,
        400: DetailOutSerializer,
        404: DetailOutSerializer,
    },
    examples=[
        jwt_response_example(),
        error_response_example(USERS_ERRORS[UsersErrorCodes.CODE_NOT_EQUAL]),
        error_response_example(USERS_ERRORS[UsersErrorCodes.CODE_NOT_PROVIDED]),
        error_response_example(USERS_ERRORS[UsersErrorCodes.USER_NOT_FOUND]),
    ],
    summary='Verify OTP code and get JWT tokens',
)
class CodeVerifyView(APIView):
    def post(self, request):
        container: punq.Container = get_container()
        use_case: VerifyCodeUseCase = container.resolve(VerifyCodeUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = AuthCodeVerifyInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                email=serializer.validated_data.get('email'),
                code=serializer.validated_data.get('code'),
            )
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


# TODO: refactor
class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination
    queryset = get_user_model().objects.all().prefetch_related('channel')
    captcha_allowed_methods = ['create']

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
        return Response({'detail': 'Your account successfully activated!'}, status=status.HTTP_200_OK)

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
