from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from yt import settings


urlpatterns = [
    # other
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('auth/', include('rest_framework.urls')),

    # API v1
    path('api/v1/', include('api.v1.urls')),

    # documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


#  media root

if settings.DEBUG:  
    urlpatterns += static(
	    settings.MEDIA_URL,
	    document_root=settings.MEDIA_ROOT
	)