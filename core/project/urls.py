from django.conf import settings
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


urlpatterns = [
    # other
    path('OAsfhulBASfyAgfqWJhShsacAWF/', admin.site.urls),

    # API v1 endpoints
    path('api/v1/', include('core.api.v1.urls')),

    # documentation
    path('docs-schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # prometheus metrics
    path('', include('django_prometheus.urls')),
]


if settings.DEBUG:
    urlpatterns += path('auth/', include('rest_framework.urls'))  # add auth urls if DEBUG = True
    urlpatterns += path('silk/', include('silk.urls', namespace='silk'))  # add silk urls if DEBUG = True
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
