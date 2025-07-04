from django.urls import (
    include,
    path,
    re_path,
)
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.api.v1.users.views.social_auth_views import (
    GenerateSocialAuthUrlView,
    SocialAuthConnectedList,
    SocialAuthDisconnectView,
    SocialAuthVerifyView,
)
from core.api.v1.users.views.user_views import (
    CodeVerifyView,
    CustomUserViewSet,
    UserLoginView,
)


app_name = 'users'

# Register custom UserViewSet from Djoser
router = DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    #  djoser user endpoints
    re_path(r'^auth/', include(router.urls)),
    #  JWT tokens endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/login/', UserLoginView.as_view(), name='user_login'),
    path('users/verify_code/', CodeVerifyView.as_view(), name='user_verify_code'),

    # Social auth endpoints
    path(
        'oauth2/convert_code/<str:provider>/',
        SocialAuthVerifyView.as_view(),
        name='social-auth',
    ),
    path(
        'oauth2/get_url/<str:provider>/',
        GenerateSocialAuthUrlView.as_view(),
        name='social-url',
    ),
    path(
        'oauth2/disconnect/<str:provider>/',
        SocialAuthDisconnectView.as_view(),
        name='social-disconnect',
    ),
    path(
        'oauth2/connected/',
        SocialAuthConnectedList.as_view(),
        name='social-connected',
    ),
]
