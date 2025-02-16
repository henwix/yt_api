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

urlpatterns = [
    #  djoser user endpoints
    re_path(r'^auth/', include(router.urls)),

    #  simpleJWT tokens endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # custom API
    path('channel/', views.ChannelDetailUpdateView().as_view(), name='channel-detail'),
    path('video-upload/', views.VideoUploadView().as_view(), name='video-upload')
]
