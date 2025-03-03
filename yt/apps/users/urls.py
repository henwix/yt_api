from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'users'

# Register custom UserViewSet from Djoser
router = DefaultRouter()
router.register("users", CustomUserViewSet)

urlpatterns = [
    #  djoser user endpoints
    re_path(r'^auth/', include(router.urls)),

    #  JWT tokens endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]