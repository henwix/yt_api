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

from core.apps.common.exceptions import ServiceException
from core.apps.videos.serializers import video_serializers
from core.apps.videos.serializers.video_upload_serializers import (
    AbortUploadSerializer,
    CompleteUploadSerializer,
    GenerateUploadPartUrlSerializer,
    KeySerializer,
)
from core.apps.videos.use_cases.multipart_upload.abort_upload import AbortMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.complete_upload import CompleteUploadUseCase
from core.apps.videos.use_cases.multipart_upload.initiate_upload import InitiateMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.presigned_url_get_video import GenerateUrlForVideoRetrieveUseCase
from core.apps.videos.use_cases.multipart_upload.presigned_url_upload import GenerateUrlForUploadUseCase
from core.project.containers import get_container


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'status': {'type': 'string'},
                'filename': {'type': 'string'},
            },
            'required': ['name', 'filename'],
        },
    },
)
class InitiateMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = video_serializers.VideoSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: InitiateMultipartUploadUseCase = container.resolve(InitiateMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()

        try:
            result = use_case.execute(
                user=request.user,
                filename=request.data.get('filename'),
                validated_data=serializer.validated_data,
            )
        except ClientError as error:
            logger.error(
                "S3 client can't create multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


class GenerateUploadPartUrlView(generics.GenericAPIView):
    serializer_class = GenerateUploadPartUrlSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForUploadUseCase = container.resolve(GenerateUrlForUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=request.user,
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                part_number=serializer.validated_data.get('part_number'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        201: {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'description': 'Presigned URL for video download',
                },
            },
        },
    },
)
class GenerateDownloadVideoUrlView(generics.GenericAPIView):
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForVideoRetrieveUseCase = container.resolve(GenerateUrlForVideoRetrieveUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                key=serializer.validated_data.get('key'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video download",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


class AbortMultipartUploadView(generics.GenericAPIView):
    serializer_class = AbortUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: AbortMultipartUploadUseCase = container.resolve(AbortMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=request.user,
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't abort multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


class CompleteMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteUploadSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CompleteUploadUseCase = container.resolve(CompleteUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=request.user,
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                parts=serializer.validated_data.get('parts'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't complete multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)
