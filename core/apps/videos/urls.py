from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from core.apps.videos.views import (
    upload_views,
    video_views,
)


app_name = 'videos'


router = DefaultRouter()
router.register('video', video_views.VideoViewSet, basename='video')
router.register('video-comment', video_views.CommentVideoAPIView, basename='video-comment')
router.register('history', video_views.VideoHistoryView, basename='history')
router.register('playlist', video_views.PlaylistAPIView, basename='playlist')

urlpatterns = [
    path('', include(router.urls)),
    path('my-videos/', video_views.MyVideoView.as_view(), name='my-videos'),
    path('get-upload-link/<str:filename>/', upload_views.GeneratePresignedUrlView.as_view(), name='upload-link'),

    # endpoints for video multipart upload
    path('video-upload-init/', upload_views.InitiateMultipartUploadView.as_view(), name='upload-video-init'),
    path('video-upload-link/', upload_views.GenerateUploadPartUrlView.as_view(), name='upload-video-url'),
    path('video-upload-complete/', upload_views.CompleteMultipartUploadView.as_view(), name='upload-video-complete'),
    path('video-upload-abort/', upload_views.AbortMultipartUploadView.as_view(), name='upload-video-abort'),
]
