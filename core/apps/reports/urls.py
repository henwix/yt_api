from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from .views import VideoReportsView


app_name = 'reports'

router = DefaultRouter()
router.register('video-reports', VideoReportsView, basename='video-reports')

urlpatterns = [
    path('', include(router.urls)),
]
