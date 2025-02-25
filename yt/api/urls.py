from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
app_name = 'api'

# register custom UserViewSet from Djoser
router = DefaultRouter()
router.register("users", views.CustomUserViewSet)

video_router = DefaultRouter()
video_router.register("video", views.VideoViewSet, basename='video')

urlpatterns = [
    #  djoser user endpoints
    re_path(r'^auth/', include(router.urls)),

    #  JWT tokens endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API
    path('channel/', views.ChannelRetrieveUpdateDeleteView.as_view(), name='channel-detail'),
    path('c/<slug:slug>', views.ChannelMainView.as_view(), name='channel-show'),
    path('c/<slug:slug>/about/', views.ChannelAboutView.as_view(), name='channel-about'),
    path('', include(video_router.urls)),
]
