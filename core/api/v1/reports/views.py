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
from core.api.v1.schema.response_examples.common import detail_response_example
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.pagination import CustomCursorPagination
from core.apps.reports.permissions import IsStaffOrCreateOnly
from core.apps.reports.services.reports import BaseVideoReportsService
from core.apps.reports.use_cases.create import CreateReportUseCase
from core.apps.users.converters.users import user_to_entity
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
            detail_response_example(
                name='Report limit error',
                value='You have reached limit of reports to this video. 3 reports by 1 user',
                status_code=400,
            ),
            detail_response_example(
                name='Private or uploading video error',
                value="You can't perform actions if the video is private or still uploading",
                status_code=403,
            ),
            detail_response_example(
                name='Video not found by "video_id" error',
                value="Video not found by video_id",
                status_code=404,
            ),
            detail_response_example(
                name='Channel not found error',
                value='Channel not found',
                status_code=404,
            ),
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
