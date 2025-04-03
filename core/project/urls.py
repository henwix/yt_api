from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from core.project.settings import local

urlpatterns = [
    # other
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('auth/', include('rest_framework.urls')),
    # API v1
    path('api/v1/', include('core.api.v1.urls')),
    # documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


#  media root

if local.DEBUG:
    urlpatterns += static(local.MEDIA_URL, document_root=local.MEDIA_ROOT)
