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
router.register('videos', video_views.VideoViewSet, basename='videos')
router.register('videos-comments', video_views.CommentVideoAPIView, basename='videos-comments')
router.register('history', video_views.VideoHistoryView, basename='history')
router.register('playlists', video_views.PlaylistAPIView, basename='playlists')

urlpatterns = [
    path('videos/personal/', video_views.MyVideoView.as_view(), name='videos-personal'),

    # endpoints for video multipart upload
    path('videos/upload/complete/', upload_views.CompleteMultipartUploadView.as_view(), name='videos-upload-complete'),
    path('videos/upload/create/', upload_views.InitiateMultipartUploadView.as_view(), name='videos-upload-create'),
    path('videos/upload/abort/', upload_views.AbortMultipartUploadView.as_view(), name='videos-upload-abort'),
    path('videos/upload/url/', upload_views.GenerateUploadPartUrlView.as_view(), name='videos-upload-url'),

    # endpoints for video download
    path('videos/download/url/', upload_views.GenerateDownloadVideoUrlView.as_view(), name='videos-download-url'),

    # router urls
    path('', include(router.urls)),
]
