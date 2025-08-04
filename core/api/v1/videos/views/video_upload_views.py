from logging import Logger

from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import orjson
import punq
from botocore.exceptions import ClientError
from drf_spectacular.utils import extend_schema

from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    UrlSerializer,
)
from core.api.v1.common.serializers.upload_serializers import (
    AbortMultipartUploadInSerializer,
    CompleteMultipartUploadInSerializer,
    CreateMultipartUploadOutSerializer,
    GenerateMultipartUploadPartUrlInSerializer,
    KeySerializer,
    UploadUrlSerializer,
)
from core.api.v1.schema.response_examples.common import detail_response_example
from core.api.v1.schema.response_examples.files_upload import (
    multipart_upload_created_response_example,
    multipart_upload_part_url_response_example,
)
from core.api.v1.videos.serializers import video_serializers
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.converters.users import user_to_entity
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
    },
    examples=[
        multipart_upload_created_response_example(),
        detail_response_example(
            name='Video filename not provided error',
            value='Video filename not provided',
            status_code=400,
        ),
        detail_response_example(
            name='Unsupported video file format error',
            value='Unsupported video file format',
            status_code=400,
        ),
        detail_response_example(
            name='Channel not found error',
            value='Channel not found',
            status_code=404,
        ),
        detail_response_example(
            name='S3 error',
            value='string',
            status_code=500,
        ),
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
                {'detail': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    },
    examples=[
        multipart_upload_part_url_response_example(),
        detail_response_example(
            name='Video author does not match error',
            value='Video author does not match the current user',
            status_code=400,
        ),
        detail_response_example(
            name='Channel not found error',
            value='Channel not found',
            status_code=404,
        ),
        detail_response_example(
            name='Video not found by upload_id error',
            value='Video not found by upload_id',
            status_code=404,
        ),
        detail_response_example(
            name='S3 error',
            value='string',
            status_code=500,
        ),
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
                {'detail': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    },
    examples=[
        detail_response_example(
            name='Video permission error',
            value='You do not have permission to access this video',
            status_code=403,
        ),
        detail_response_example(
            name='Video not found by key error',
            value='Video not found by key',
            status_code=404,
        ),
        detail_response_example(
            name='File with this key does not exist in S3 error',
            value='File with this key does not exist in S3',
            status_code=404,
        ),
        detail_response_example(
            name='S3 error',
            value='string',
            status_code=500,
        ),
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
                {'detail': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        detail_response_example(
            name='Aborted',
            value='Success',
            status_code=200,
        ),
        detail_response_example(
            name='Video author does not match error',
            value='Video author does not match the current user',
            status_code=400,
        ),
        detail_response_example(
            name='Multipart upload does not exist error',
            value='Multipart upload with this key and upload_id does not exist in S3',
            status_code=404,
        ),
        detail_response_example(
            name='Video not found by upload_id error',
            value='Video not found by upload_id',
            status_code=404,
        ),
        detail_response_example(
            name='Channel not found error',
            value='Channel not found',
            status_code=404,
        ),
    ],
    summary='Abort multipart upload',
)
class AbortMultipartUploadView(generics.GenericAPIView):
    serializer_class = AbortMultipartUploadInSerializer
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
                {'detail': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'example': 'success',
                },
                'message': {
                    'type': 'string',
                    'example': 'Video upload completed successfully',
                },
            },
        },
    },
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
                {'detail': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)
