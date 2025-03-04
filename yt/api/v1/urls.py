from django.urls import path, include

app_name = 'v1'

urlpatterns = [
    path('', include('apps.channels.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.videos.urls')),
]
