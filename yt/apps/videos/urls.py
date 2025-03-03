from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'videos'


video_router = DefaultRouter()
video_router.register("video", views.VideoViewSet, basename='video')


urlpatterns = [
    path('', include(video_router.urls)),
]