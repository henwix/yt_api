from rest_framework import (
    generics,
    viewsets,
)

from core.apps.common.pagination import CustomCursorPagination
from core.project.containers import get_container

from .permissions import IsStaffOrCreateOnly
from .serializers import VideoReportSerializer
from .services.reports import BaseVideoReportsService


# TODO: доделать создание репортов и валидацию на их количество от одного юзера
class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    serializer_class = VideoReportSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsStaffOrCreateOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseVideoReportsService = container.resolve(BaseVideoReportsService)

    def get_queryset(self):
        if self.action == ['list', 'retrieve']:
            return self.service.get_report_list_related()
        return self.service.get_report_list()
