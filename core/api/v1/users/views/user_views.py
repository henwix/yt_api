from logging import Logger

from django.contrib.auth import get_user_model  # noqa
from django.db import transaction
from rest_framework import (  # noqa
    generics,
    mixins,
    status,
    viewsets,
)
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
    UUID4CodeSerializer,
)
from core.api.v1.schema.response_examples.common import (
    detail_response_example,
    error_response_example,
    jwt_response_example,
)
from core.api.v1.users.serializers.auth import (
    AuthCodeVerifyInSerializer,
    AuthInSerializer,
    EmailSerializer,
)
from core.api.v1.users.serializers.users import (
    AuthPasswordResetConfirmSerializer,
    AuthUserSerializer,
    EmailUserSerializer,
    PasswordUserSerializer,
    UpdateUserSerializer,
    UsernameResetConfirmSerializer,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.pagination import CustomPageNumberPagination
from core.apps.common.permissions.captcha import CaptchaPermission
from core.apps.users.converters.users import user_to_entity
from core.apps.users.errors import (
    ErrorCodes as UsersErrorCodes,
    ERRORS as USERS_ERRORS,
)
from core.apps.users.models import CustomUser
from core.apps.users.permissions import AuthUserPermission
from core.apps.users.tasks import (
    send_activation_email,
    send_confirmation_email,
    send_reset_password_email,
    send_reset_username_email,
)
from core.apps.users.use_cases.users.auth_authorize import AuthorizeUserUseCase
from core.apps.users.use_cases.users.auth_verify_code import VerifyCodeUseCase
from core.apps.users.use_cases.users.user_create import UserCreateUseCase
from core.apps.users.use_cases.users.user_reset_password import UserResetPasswordUseCase
from core.apps.users.use_cases.users.user_reset_password_confirm import UserResetPasswordConfirmUseCase
from core.apps.users.use_cases.users.user_reset_username import UserResetUsernameUseCase
from core.apps.users.use_cases.users.user_reset_username_confirm import UserResetUsernameConfirmUseCase
from core.apps.users.use_cases.users.user_set_email import UserSetEmailUseCase
from core.apps.users.use_cases.users.user_set_email_confirm import UserSetEmailConfirmUseCase
from core.apps.users.use_cases.users.user_set_password import UserSetPasswordUseCase
from core.project.containers import get_container  # noqa


# TODO: activation, resend_activation
# TODO: add captcha in user creation
# TODO: доку для всех endpoints
# TODO: throttling для отправки почты на все эндпоинты
class UserView(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    permission_classes = [AuthUserPermission]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.container: punq.Container = get_container()
        self.logger: Logger = self.container.resolve(Logger)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        if self.action in ['create', 'retrieve']:
            return AuthUserSerializer
        if self.action == 'set_password':
            return PasswordUserSerializer
        if self.action == 'set_email':
            return EmailUserSerializer
        if self.action == 'set_email_confirm':
            return UUID4CodeSerializer
        if self.action in ['reset_password', 'reset_username']:
            return EmailSerializer
        if self.action == 'reset_password_confirm':
            return AuthPasswordResetConfirmSerializer
        if self.action == 'reset_username_confirm':
            return UsernameResetConfirmSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserCreateUseCase = self.container.resolve(UserCreateUseCase)

        try:
            result: CustomUser = use_case.execute(validated_data=serializer.validated_data)

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(self.get_serializer(result).data, status=status.HTTP_201_CREATED)

    @action(['post'], detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserSetPasswordUseCase = self.container.resolve(UserSetPasswordUseCase)

        use_case.execute(
            user=user_to_entity(request.user),
            password=serializer.validated_data.get('password'),
        )

        return Response({'detail': 'Success'})

    @action(['post'], detail=False)
    def set_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserSetEmailUseCase = self.container.resolve(UserSetEmailUseCase)

        result = use_case.execute(
            user=user_to_entity(request.user),
            email=serializer.validated_data.get('email'),
        )

        return Response(result, status=status.HTTP_200_OK)

    @action(['post'], detail=False)
    def set_email_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserSetEmailConfirmUseCase = self.container.resolve(UserSetEmailConfirmUseCase)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                code=serializer.validated_data.get('code'),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)

    @action(['post'], detail=False)
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserResetPasswordUseCase = self.container.resolve(UserResetPasswordUseCase)

        try:
            result = use_case.execute(email=serializer.validated_data.get('email'))

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)

    @action(['post'], detail=False)
    def reset_password_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserResetPasswordConfirmUseCase = self.container.resolve(UserResetPasswordConfirmUseCase)

        try:
            result = use_case.execute(
                encoded_id=serializer.validated_data.get('uid'),
                code=serializer.validated_data.get('code'),
                new_password=serializer.validated_data.get('password'),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)

    @action(['post'], detail=False)
    def reset_username(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserResetUsernameUseCase = self.container.resolve(UserResetUsernameUseCase)

        try:
            result = use_case.execute(email=serializer.validated_data.get('email'))

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)

    @action(['post'], detail=False)
    def reset_username_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserResetUsernameConfirmUseCase = self.container.resolve(UserResetUsernameConfirmUseCase)

        try:
            result = use_case.execute(
                encoded_id=serializer.validated_data.get('uid'),
                code=serializer.validated_data.get('code'),
                new_username=serializer.validated_data.get('username'),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


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
        error_response_example(USERS_ERRORS[UsersErrorCodes.OTP_CODE_NOT_PROVIDED_OR_NOT_FOUND]),
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


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination
    queryset = get_user_model().objects.all().prefetch_related('channel')
    captcha_allowed_methods = ['create']  # permission for this view in defined in settings file

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
