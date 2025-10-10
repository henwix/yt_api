from logging import Logger

from rest_framework import (
    generics,
    permissions,
    status,
)
from rest_framework.response import Response

import orjson
import punq
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)

from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    UrlSerializer,
)
from core.api.v1.common.serializers.upload_serializers import (
    FilenameSerializer,
    GenerateUploadUrlOutSerializer,
    KeySerializer,
)
from core.api.v1.schema.response_examples.common import (
    build_example_response_from_error,
    deleted_response_example,
    detail_response_example,
)
from core.api.v1.schema.response_examples.files_upload import s3_error_response_example
from core.apps.channels.exceptions.channels import (
    AvatarDoesNotExistsError,
    ChannelNotFoundError,
)
from core.apps.channels.exceptions.upload import AvatarFilenameFormatError
from core.apps.channels.use_cases.avatar_upload.complete_upload_avatar import CompleteUploadAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.delete_avatar import DeleteChannelAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.download_avatar_url import GenerateUrlForAvatarDownloadUseCase
from core.apps.channels.use_cases.avatar_upload.upload_avatar_url import GenerateUploadAvatarUrlUseCase
from core.apps.common.exceptions.exceptions import (
    S3FileWithKeyNotExistsError,
    ServiceException,
)
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


@extend_schema(
    responses={
        201: OpenApiResponse(response=GenerateUploadUrlOutSerializer, description='Upload URL has been generated'),
        400: OpenApiResponse(response=DetailOutSerializer, description='Filename wrong format'),
        500: OpenApiResponse(response=DetailOutSerializer, description='S3 500 error'),
        502: OpenApiResponse(response=DetailOutSerializer, description='S3 502 error'),
    },
    examples=[
        OpenApiExample(
            name='Filename',
            value={'filename': 'avatar.png'},
            request_only=True,
        ),
        build_example_response_from_error(error=AvatarFilenameFormatError),
        s3_error_response_example(code=status.HTTP_500_INTERNAL_SERVER_ERROR),
        s3_error_response_example(code=status.HTTP_502_BAD_GATEWAY),
    ],
    summary='Generate presigned url to upload avatar file in S3',
)
class GenerateUploadAvatarUrlView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FilenameSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUploadAvatarUrlUseCase = container.resolve(GenerateUploadAvatarUrlUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(filename=serializer.validated_data.get('filename'))

        except ClientError as error:
            logger.error(
                "S3 client can't generate upload avatar url",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in generate upload avatar url",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        201: OpenApiResponse(response=UrlSerializer, description='Download URL has been generated'),
        404: OpenApiResponse(response=DetailOutSerializer, description='File does not exists in S3'),
        500: OpenApiResponse(response=DetailOutSerializer, description='S3 500 error'),
        502: OpenApiResponse(response=DetailOutSerializer, description='S3 502 error'),
    },
    examples=[
        build_example_response_from_error(error=S3FileWithKeyNotExistsError),
        s3_error_response_example(code=status.HTTP_500_INTERNAL_SERVER_ERROR),
        s3_error_response_example(code=status.HTTP_502_BAD_GATEWAY),
    ],
    summary='Generate presigned url to download avatar file from S3',
)
class GenerateDownloadAvatarUrlView(generics.GenericAPIView):
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForAvatarDownloadUseCase = container.resolve(GenerateUrlForAvatarDownloadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                key=serializer.validated_data.get('key'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for avatar download",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in generate presigned url for avatar download",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        200: OpenApiResponse(response=DetailOutSerializer, description='Avatar has been deleted'),
        404: OpenApiResponse(
            response=DetailOutSerializer,
            description='Channel was not found or avatar does not exists',
        ),
    },
    examples=[
        deleted_response_example(),
        build_example_response_from_error(error=ChannelNotFoundError),
        build_example_response_from_error(error=AvatarDoesNotExistsError),
    ],
    summary='Delete channel avatar',
)
class DeleteChannelAvatarView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        container: punq.Container = get_container()
        use_case: DeleteChannelAvatarUseCase = container.resolve(DeleteChannelAvatarUseCase)
        logger: Logger = container.resolve(Logger)

        try:
            result = use_case.execute(user=user_to_entity(request.user))

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: OpenApiResponse(response=DetailOutSerializer, description='Avatar uploading has been completed'),
        404: OpenApiResponse(
            response=DetailOutSerializer,
            description='Channel was not found or file does not exists in S3',
        ),
    },
    examples=[
        detail_response_example(
            name='Completed',
            value='Success',
            status_code=200,
        ),
        build_example_response_from_error(error=ChannelNotFoundError),
        build_example_response_from_error(error=S3FileWithKeyNotExistsError),
    ],
    summary='Complete avatar file uploading',
)
class CompleteUploadAvatarView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CompleteUploadAvatarUseCase = container.resolve(CompleteUploadAvatarUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                key=serializer.validated_data.get('key'),
                user=user_to_entity(request.user),
            )

        except ServiceException as error:
            logger.error(
                error.message,
                extra={'log_meta': orjson.dumps(error).decode()},
            )
            raise

        return Response(result, status=status.HTTP_200_OK)
