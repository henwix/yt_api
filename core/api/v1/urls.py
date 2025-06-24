from django.urls import (
    include,
    path,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


app_name = 'v1'


@api_view(['GET'])
def ping(request):
    return Response({'message': 'pong'})


urlpatterns = [
    path('ping/', ping, name='ping'),

    path('', include('core.api.v1.channels.urls')),
    path('', include('core.api.v1.users.urls')),
    path('', include('core.api.v1.videos.urls')),
    path('', include('core.api.v1.reports.urls')),
    path('', include('core.api.v1.posts.urls')),
]
