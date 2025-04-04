from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'videos'


router = DefaultRouter()
router.register('video', views.VideoViewSet, basename='video')
router.register('video-comment', views.CommentVideoAPIView, basename='video-comment')
router.register('history', views.VideoHistoryView, basename='history')
router.register('playlists', views.PlaylistAPIView, basename='playlists')

urlpatterns = [
    path('', include(router.urls)),
    path('get-upload-link/<str:filename>/', views.GeneratePresignedUrlView.as_view(), name='upload-link'),
    path('my-videos/', views.MyVideoView.as_view(), name='my-videos'),
]
