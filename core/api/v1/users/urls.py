from django.urls import (
    include,
    path,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.api.v1.users.views.oauth2_views import (
    OAuth2ConnectedProvidersView,
    OAuth2ConnectView,
    OAuth2DisconnectView,
    OAuth2GenerateURLView,
)
from core.api.v1.users.views.user_views import (
    CodeVerifyView,
    UserLoginView,
    UserView,
)
from core.apps.users.routers import CustomUserRouter


app_name = 'users'


user_router = CustomUserRouter()
user_router.register(r'users', UserView, basename='user')

urlpatterns = [
    # Users endpoints
    path('auth/', include(user_router.urls)),

    # JWT tokens endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Login endpoints
    path('auth/login/', UserLoginView.as_view(), name='user_login'),
    path('auth/verify_code/', CodeVerifyView.as_view(), name='user_verify_code'),

    # Social auth endpoints
    path(
        'oauth2/convert_code/<str:provider>/',
        OAuth2ConnectView.as_view(),
        name='oauth2-connect',
    ),
    path(
        'oauth2/get_url/<str:provider>/',
        OAuth2GenerateURLView.as_view(),
        name='oauth2-url',
    ),
    path(
        'oauth2/disconnect/<str:provider>/',
        OAuth2DisconnectView.as_view(),
        name='oauth2-disconnect',
    ),
    path(
        'oauth2/connected/',
        OAuth2ConnectedProvidersView.as_view(),
        name='oauth2-connected',
    ),
]
