from logging import Logger

from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import orjson
import punq
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)
from drf_spectacular.utils import extend_schema

from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    UrlSerializer,
)
from core.api.v1.common.serializers.upload_serializers import (
    BaseMultipartUploadInSerializer,
    CompleteMultipartUploadInSerializer,
    CreateMultipartUploadOutSerializer,
    GenerateMultipartUploadPartUrlInSerializer,
    KeySerializer,
    UploadUrlSerializer,
)
from core.api.v1.schema.response_examples.common import (
    deleted_response_example,
    detail_response_example,
    error_response_example,
)
from core.api.v1.schema.response_examples.files_upload import (
    multipart_upload_complete_request_example,
    multipart_upload_created_response_example,
    multipart_upload_part_url_response_example,
    s3_error_response_example,
)
from core.api.v1.videos.serializers import video_serializers
from core.apps.channels.errors import (
    ErrorCodes as ChannelsErrorCodes,
    ERRORS as CHANNELS_ERRORS,
)
from core.apps.common.errors import (
    ErrorCodes as CommonErrorCodes,
    ERRORS as COMMON_ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.errors import (
    ErrorCodes as VideosErrorCodes,
    ERRORS as VIDEOS_ERRORS,
)
from core.apps.videos.use_cases.videos_upload.abort_upload_video import AbortVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.complete_upload_video import CompleteVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.create_upload_video import CreateVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.download_video_url import GenerateUrlForVideoDownloadUseCase
from core.apps.videos.use_cases.videos_upload.upload_video_url import GenerateUrlForVideoPartUploadUseCase
from core.project.containers import get_container


@extend_schema(
    responses={
        201: CreateMultipartUploadOutSerializer,
        400: DetailOutSerializer,
        404: DetailOutSerializer,
        500: DetailOutSerializer,
        502: DetailOutSerializer,
    },
    examples=[
        multipart_upload_created_response_example(),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_FILENAME_NOT_PROVIDED]),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_FILENAME_FORMAT_ERROR]),
        error_response_example(CHANNELS_ERRORS[ChannelsErrorCodes.CHANNEL_NOT_FOUND]),
        s3_error_response_example(code=status.HTTP_500_INTERNAL_SERVER_ERROR),
        s3_error_response_example(code=status.HTTP_502_BAD_GATEWAY),
    ],
    summary='Create multipart upload',
)
class CreateMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = video_serializers.VideoCreateSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CreateVideoMultipartUploadUseCase = container.resolve(CreateVideoMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                filename=serializer.validated_data.pop('filename'),
                validated_data=serializer.validated_data,
            )

        except ClientError as error:
            logger.error(
                "S3 client can't create multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in create multipart upload",
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
        201: UploadUrlSerializer,
        400: DetailOutSerializer,
        404: DetailOutSerializer,
        500: DetailOutSerializer,
        502: DetailOutSerializer,
    },
    examples=[
        multipart_upload_part_url_response_example(),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_AUTHOR_NOT_MATCH]),
        error_response_example(CHANNELS_ERRORS[ChannelsErrorCodes.CHANNEL_NOT_FOUND]),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_NOT_FOUND_BY_UPLOAD_ID]),
        s3_error_response_example(code=status.HTTP_500_INTERNAL_SERVER_ERROR),
        s3_error_response_example(code=status.HTTP_502_BAD_GATEWAY),
    ],
    summary='Generate upload part url for video',
)
class GenerateUploadPartUrlView(generics.GenericAPIView):
    serializer_class = GenerateMultipartUploadPartUrlInSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForVideoPartUploadUseCase = container.resolve(GenerateUrlForVideoPartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                part_number=serializer.validated_data.get('part_number'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in generate presigned url for video upload",
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
        201: UrlSerializer,
        403: DetailOutSerializer,
        404: DetailOutSerializer,
        500: DetailOutSerializer,
        502: DetailOutSerializer,
    },
    examples=[
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.PRIVATE_VIDEO_PERMISSION_ERROR]),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_NOT_FOUND_BY_KEY]),
        error_response_example(COMMON_ERRORS[CommonErrorCodes.S3_FILE_WITH_KEY_NOT_EXISTS]),
        s3_error_response_example(code=status.HTTP_500_INTERNAL_SERVER_ERROR),
        s3_error_response_example(code=status.HTTP_502_BAD_GATEWAY),
    ],
    summary='Generate presigned url for video download',
)
class GenerateDownloadVideoUrlView(generics.GenericAPIView):
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForVideoDownloadUseCase = container.resolve(GenerateUrlForVideoDownloadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video download",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in generate presigned url for video download",
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
        200: DetailOutSerializer,
        400: DetailOutSerializer,
        404: DetailOutSerializer,
    },
    examples=[
        deleted_response_example(),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_AUTHOR_NOT_MATCH]),
        error_response_example(COMMON_ERRORS[CommonErrorCodes.MULTIPART_UPLOAD_EXISTS_ERROR]),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_NOT_FOUND_BY_UPLOAD_ID]),
        error_response_example(CHANNELS_ERRORS[ChannelsErrorCodes.CHANNEL_NOT_FOUND]),
    ],
    summary='Abort multipart upload',
)
class AbortMultipartUploadView(generics.GenericAPIView):
    serializer_class = BaseMultipartUploadInSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: AbortVideoMultipartUploadUseCase = container.resolve(AbortVideoMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't abort multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in abort multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: DetailOutSerializer,
        400: DetailOutSerializer,
        404: DetailOutSerializer,
        500: DetailOutSerializer,
        502: DetailOutSerializer,
    },
    examples=[
        # request
        multipart_upload_complete_request_example(),

        # response
        detail_response_example(
            name='Completed',
            value='Success',
            status_code=200,
        ),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_AUTHOR_NOT_MATCH]),
        error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_NOT_FOUND_BY_UPLOAD_ID]),
        error_response_example(CHANNELS_ERRORS[ChannelsErrorCodes.CHANNEL_NOT_FOUND]),
        s3_error_response_example(code=status.HTTP_500_INTERNAL_SERVER_ERROR),
        s3_error_response_example(code=status.HTTP_502_BAD_GATEWAY),
    ],
    summary='Complete multipart upload',
)
class CompleteMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteMultipartUploadInSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CompleteVideoMultipartUploadUseCase = container.resolve(CompleteVideoMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                parts=serializer.validated_data.get('parts'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't complete multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': error.error.get('Message')},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except BotoCoreError as error:
            logger.error(
                "BotoCoreError in complete multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)
