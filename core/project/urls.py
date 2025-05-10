from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from core.project.settings import prod


urlpatterns = [
    # other
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('auth/', include('rest_framework.urls')),

    # API v1
    path('api/v1/', include('core.api.v1.urls')),

    # documentation
    path('docs-schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # prometheus metrics
    path('', include('django_prometheus.urls')),
]


#  media root

if prod.DEBUG:
    urlpatterns += static(prod.MEDIA_URL, document_root=prod.MEDIA_ROOT)
