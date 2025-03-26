from rest_framework import generics, viewsets

from apps.common.pagination import CustomCursorPagination

from .permissions import IsStaffOrCreateOnly
from .repositories.reports import ORMVideoReportRepository
from .serializers import VideoReportSerializer
from .services.reports import VideoReportsService


# TODO: доделать создание репортов и валидацию на их количество от одного юзера
class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    serializer_class = VideoReportSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsStaffOrCreateOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VideoReportsService(repository=ORMVideoReportRepository())

    def get_queryset(self):
        return self.service.get_reports(self.action)
