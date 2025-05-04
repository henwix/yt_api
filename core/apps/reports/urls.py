from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from .views import VideoReportsView


app_name = 'reports'

router = DefaultRouter()
router.register('videos-reports', VideoReportsView, basename='videos-reports')

urlpatterns = [
    path('', include(router.urls)),
]
