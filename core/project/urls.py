import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # other
    path(os.environ.get('DJANGO_ADMIN_PATH') + "/", admin.site.urls),

    # API v1 endpoints
    path('v1/', include('core.api.v1.urls')),

    # documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # prometheus metrics
    path('', include('django_prometheus.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns.extend(
        [
            path('auth/', include('rest_framework.urls')),  # add auth urls if DEBUG is True
            path('silk/', include('silk.urls', namespace='silk')),  # add silk urls if DEBUG is True
        ],
    )
