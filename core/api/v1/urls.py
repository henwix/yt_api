from django.urls import include, path

app_name = 'v1'

urlpatterns = [
    path('', include('core.apps.channels.urls')),
    path('', include('core.apps.users.urls')),
    path('', include('core.apps.videos.urls')),
    path('', include('core.apps.reports.urls')),
]
