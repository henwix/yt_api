from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'videos'


router = DefaultRouter()
router.register("video", views.VideoViewSet, basename='video')
router.register("video-comment", views.CommentVideoAPIView, basename='video-comment')

urlpatterns = [
    path('', include(router.urls)),
]