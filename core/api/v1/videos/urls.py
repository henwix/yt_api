from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from core.api.v1.videos.views import (
    video_upload_views,
    video_views,
)

app_name = 'videos'


router = DefaultRouter()
router.register('videos', video_views.VideoViewSet, basename='videos')
router.register('videos-comments', video_views.CommentVideoAPIView, basename='videos-comments')
router.register('history', video_views.VideoHistoryView, basename='history')
router.register('playlists', video_views.PlaylistAPIView, basename='playlists')

urlpatterns = [
    path(
        'videos/personal/',
        video_views.MyVideoView.as_view(),
        name='videos-personal',
    ),
    path(
        'playlists/<str:id>/videos/',
        video_views.PlaylistVideosView.as_view(),
        name='playlist-videos',
    ),
    # endpoints for video multipart upload
    path(
        'videos/upload_create/',
        video_upload_views.CreateMultipartUploadView.as_view(),
        name='videos-upload-create',
    ),
    path(
        'videos/upload_complete/',
        video_upload_views.CompleteMultipartUploadView.as_view(),
        name='videos-upload-complete',
    ),
    path(
        'videos/upload_abort/',
        video_upload_views.AbortMultipartUploadView.as_view(),
        name='videos-upload-abort',
    ),
    path(
        'videos/upload_url/',
        video_upload_views.GenerateUploadPartUrlView.as_view(),
        name='videos-upload-url',
    ),
    # endpoints for video download
    path(
        'videos/download_url/',
        video_upload_views.GenerateDownloadVideoUrlView.as_view(),
        name='videos-download-url',
    ),
    # router urls
    path('', include(router.urls)),
]
