from logging import Logger

from rest_framework import (
    generics,
    status,
    viewsets,
)
from rest_framework.response import Response

import orjson
import punq
from drf_spectacular.utils import extend_schema

from core.api.v1.common.serializers.serializers import DetailOutSerializer
from core.api.v1.reports.serializers import VideoReportSerializer
from core.api.v1.schema.response_examples.common import (
    detail_response_example,
    error_response_example,
)
from core.apps.channels.errors import (
    ErrorCodes as ChannelsErrorCodes,
    ERRORS as CHANNELS_ERRORS,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.pagination import CustomCursorPagination
from core.apps.reports.errors import (
    ErrorCodes as ReportsErrorCodes,
    ERRORS as REPORTS_ERRORS,
)
from core.apps.reports.permissions import IsStaffOrCreateOnly
from core.apps.reports.services.reports import BaseVideoReportsService
from core.apps.reports.use_cases.create import CreateReportUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.errors import (
    ErrorCodes as VideosErrorCodes,
    ERRORS as VIDEOS_ERRORS,
)
from core.project.containers import get_container


class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    serializer_class = VideoReportSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsStaffOrCreateOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container: punq.Container = get_container()
        self.service: BaseVideoReportsService = self.container.resolve(BaseVideoReportsService)
        self.logger: Logger = self.container.resolve(Logger)

    def get_queryset(self):
        if self.action == ['list', 'retrieve']:
            return self.service.get_report_list_related()
        return self.service.get_report_list()

    @extend_schema(
        responses={
            201: DetailOutSerializer,
            400: DetailOutSerializer,
            403: DetailOutSerializer,
            404: DetailOutSerializer,
        },
        examples=[
            detail_response_example(
                name='Created',
                value='Successfully created',
                status_code=201,
            ),
            error_response_example(REPORTS_ERRORS[ReportsErrorCodes.REPORT_LIMIT]),
            error_response_example(VIDEOS_ERRORS[VideosErrorCodes.PRIVATE_VIDEO_OR_UPLOADING]),
            error_response_example(VIDEOS_ERRORS[VideosErrorCodes.VIDEO_NOT_FOUND_BY_VIDEO_ID]),
            error_response_example(CHANNELS_ERRORS[ChannelsErrorCodes.CHANNEL_NOT_FOUND]),
        ],
        summary='Create a new video report',
    )
    def create(self, request, *args, **kwargs):
        use_case: CreateReportUseCase = self.container.resolve(CreateReportUseCase)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                video_id=serializer.validated_data.get('video_slug').pk,
                reason=serializer.validated_data.get('reason'),
                description=serializer.validated_data.get('description'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
        else:
            return Response(result, status.HTTP_201_CREATED)
