from logging import Logger

from django.contrib.auth import get_user_model  # noqa
from rest_framework import (  # noqa
    mixins,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    PolymorphicProxySerializer,
)

from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    JWTOutSerializer,
    UUID4CodeSerializer,
)
from core.api.v1.schema.response_examples.common import (
    build_example_response_from_error,
    confirmation_email_sent_response_example,
    detail_response_example,
    jwt_response_example,
)
from core.api.v1.schema.response_examples.users import (
    user_activation_email_sent_response_example,
    user_created_response_example,
    user_email_updated_response_example,
)
from core.api.v1.users.serializers.auth import (
    AuthCodeVerifyInSerializer,
    AuthInSerializer,
    EmailSerializer,
)
from core.api.v1.users.serializers.users import (
    EmailUserSerializer,
    EmailUserUpdatedSerializer,
    PasswordResetConfirmSerializer,
    PasswordUserSerializer,
    UIDAndCodeConfirmSerializer,
    UpdateUserSerializer,
    UsernameResetConfirmSerializer,
    UserSerializer,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.permissions.captcha import CaptchaPermission
from core.apps.users.converters.users import user_to_entity
from core.apps.users.exceptions.codes import (
    OtpCodeNotEqualError,
    OtpCodeNotFoundError,
    SetEmailCodeNotProvidedOrNotFoundError,
    SetEmailUserNotEqualError,
    UserEmailCodeNotEqualError,
    UserEmailCodeNotFoundError,
)
from core.apps.users.exceptions.users import (
    InvalidUIDValueError,
    UserActivationNotAllowedError,
    UserAlreadyActivatedError,
    UserNotFoundError,
    UserWithThisDataAlreadyExistsError,
)
from core.apps.users.models import CustomUser
from core.apps.users.permissions import AuthUserPermission
from core.apps.users.use_cases.users.auth_authorize import AuthorizeUserUseCase
from core.apps.users.use_cases.users.auth_verify_code import VerifyCodeUseCase
from core.apps.users.use_cases.users.user_activation import UserActivationUseCase
from core.apps.users.use_cases.users.user_create import UserCreateUseCase
from core.apps.users.use_cases.users.user_resend_activation import UserResendActivationUseCase
from core.apps.users.use_cases.users.user_reset_password import UserResetPasswordUseCase
from core.apps.users.use_cases.users.user_reset_password_confirm import UserResetPasswordConfirmUseCase
from core.apps.users.use_cases.users.user_reset_username import UserResetUsernameUseCase
from core.apps.users.use_cases.users.user_reset_username_confirm import UserResetUsernameConfirmUseCase
from core.apps.users.use_cases.users.user_set_email import UserSetEmailUseCase
from core.apps.users.use_cases.users.user_set_email_confirm import UserSetEmailConfirmUseCase
from core.apps.users.use_cases.users.user_set_password import UserSetPasswordUseCase
from core.project.containers import get_container  # noqa


# TODO: доку для всех endpoints
# TODO: throttling для отправки почты на все эндпоинты
class UserView(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    permission_classes = [CaptchaPermission, AuthUserPermission]
    captcha_allowed_methods = ['create']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.container: punq.Container = get_container()
        self.logger: Logger = self.container.resolve(Logger)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ['create', 'retrieve']:
            return UserSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        if self.action == 'set_password':
            return PasswordUserSerializer
        if self.action == 'set_email':
            return EmailUserSerializer
        if self.action == 'set_email_confirm':
            return UUID4CodeSerializer
        if self.action in ['reset_password', 'reset_username', 'resend_activation']:
            return EmailSerializer
        if self.action == 'reset_password_confirm':
            return PasswordResetConfirmSerializer
        if self.action == 'reset_username_confirm':
            return UsernameResetConfirmSerializer
        if self.action == 'activation':
            return UIDAndCodeConfirmSerializer

    @extend_schema(summary='Update user data')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary='Update user data')
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary='Retrieve user data')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # TODO: update docs examples using 'build_example_response_from_error' if it's not a circular import
    @extend_schema(
        request=UserSerializer,
        responses={
            201: OpenApiResponse(
                response=PolymorphicProxySerializer(
                    component_name='UserCreatedResponse',
                    serializers=[UserSerializer, DetailOutSerializer],
                    resource_type_field_name=None,
                ),
                description='Successfull user creation',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='User with this data already exists',
            ),
        },
        examples=[
            user_created_response_example(),
            user_activation_email_sent_response_example(status_code=201),
            build_example_response_from_error(error=UserWithThisDataAlreadyExistsError),
        ],
        summary='Create new user and channel',
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserCreateUseCase = self.container.resolve(UserCreateUseCase)

        try:
            result: CustomUser | dict = use_case.execute(validated_data=serializer.validated_data)

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(
            data=self.get_serializer(result).data if isinstance(result, CustomUser) else result,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Successfull password update',
            ),
        },
        examples=[
            detail_response_example(
                name='Password updated',
                value='Success',
                status_code=200,
                description='Returns that response if the password has been updated successfully',
            ),
        ],
        summary='Update user password',
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation email has been successfully sent',
            ),
        },
        examples=[
            confirmation_email_sent_response_example(),
        ],
        summary='Send confirmation email with code to update user email',
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=EmailUserUpdatedSerializer,
                description='Successfull email update',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation code does not match or the email address is already taken by another user',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation code is not found or was not provided',
            ),
        },
        examples=[
            user_email_updated_response_example(),
            build_example_response_from_error(error=SetEmailCodeNotProvidedOrNotFoundError),
            build_example_response_from_error(error=SetEmailUserNotEqualError),
            build_example_response_from_error(error=UserWithThisDataAlreadyExistsError),
        ],
        summary='Validate confirmation code and update user email',
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation email has been successfully sent',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='User is not found',
            ),
        },
        examples=[
            confirmation_email_sent_response_example(),
            build_example_response_from_error(error=UserNotFoundError),
        ],
        summary='Send confirmation email with code to reset user password',
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Password has been reset',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation code does not match or the provided UID value is not valid',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation code or user was not found',
            ),
        },
        examples=[
            detail_response_example(
                name='Password has been reset',
                value='Success',
                status_code=200,
            ),
            build_example_response_from_error(error=UserNotFoundError),
            build_example_response_from_error(error=InvalidUIDValueError),
            build_example_response_from_error(error=UserEmailCodeNotFoundError),
            build_example_response_from_error(error=UserEmailCodeNotEqualError),
        ],
        summary='Validate confirmation code and reset user password',
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation email has been successfully sent',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='User is not found',
            ),
        },
        examples=[
            confirmation_email_sent_response_example(),
            build_example_response_from_error(error=UserNotFoundError),
        ],
        summary='Send confirmation email with code to reset user username',
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Username has been reset',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation code does not match or the provided UID value is not valid',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Confirmation code or user was not found',
            ),
        },
        examples=[
            detail_response_example(
                name='Username has been reset',
                value='Success',
                status_code=200,
            ),
            build_example_response_from_error(error=UserNotFoundError),
            build_example_response_from_error(error=InvalidUIDValueError),
            build_example_response_from_error(error=UserEmailCodeNotFoundError),
            build_example_response_from_error(error=UserEmailCodeNotEqualError),
        ],
        summary='Validate confirmation code and reset user username',
    )
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
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='User has been activated',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Bad request error',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Activation code or user was not found',
            ),
        },
        examples=[
            detail_response_example(
                name='User activated',
                value='Success',
                status_code=200,
            ),
            build_example_response_from_error(error=UserNotFoundError),
            build_example_response_from_error(error=InvalidUIDValueError),
            build_example_response_from_error(error=UserActivationNotAllowedError),
            build_example_response_from_error(error=UserAlreadyActivatedError),
            build_example_response_from_error(error=UserEmailCodeNotFoundError),
            build_example_response_from_error(error=UserEmailCodeNotEqualError),

        ],
        summary='Validate activation code and activate user',
    )
    @action(['post'], detail=False)
    def activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserActivationUseCase = self.container.resolve(UserActivationUseCase)

        try:
            result = use_case.execute(
                encoded_id=serializer.validated_data.get('uid'),
                code=serializer.validated_data.get('code'),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Activation email has been successfully sent',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='User activation is not allowed or the user is already activated',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='User is not found',
            ),
        },
        examples=[
            user_activation_email_sent_response_example(status_code=200),
            build_example_response_from_error(error=UserActivationNotAllowedError),
            build_example_response_from_error(error=UserNotFoundError),
            build_example_response_from_error(error=UserAlreadyActivatedError),
        ],
        summary='Resend activation email',
    )
    @action(['post'], detail=False)
    def resend_activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case: UserResendActivationUseCase = self.container.resolve(UserResendActivationUseCase)

        try:
            result = use_case.execute(email=serializer.validated_data.get('email'))

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    request=AuthInSerializer,
    responses={
        200: OpenApiResponse(
            response=PolymorphicProxySerializer(
                component_name='OAuth2ConnectResponse',
                serializers=[JWTOutSerializer, DetailOutSerializer],
                resource_type_field_name=None,
            ),
            description='JWT tokens are generated or the confirmation email has been sent',
        ),
        404: OpenApiResponse(
            response=DetailOutSerializer,
            description='User is not found',
        ),
    },
    examples=[
        jwt_response_example(),
        detail_response_example(
            name='Email sent',
            description='Sends an email with a code to verify OTP',
            value='Email successfully sent',
            status_code=200,
        ),
        build_example_response_from_error(UserNotFoundError),
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
        200: OpenApiResponse(
            response=JWTOutSerializer,
            description='JWT tokens are generated',
        ),
        400: OpenApiResponse(
            response=DetailOutSerializer,
            description='Otp code does not match',
        ),
        404: OpenApiResponse(
            response=DetailOutSerializer,
            description='Otp code or user was not found',
        ),
    },
    examples=[
        jwt_response_example(),
        build_example_response_from_error(OtpCodeNotEqualError),
        build_example_response_from_error(OtpCodeNotFoundError),
        build_example_response_from_error(UserNotFoundError),

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
