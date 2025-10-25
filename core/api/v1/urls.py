from django.urls import (
    include,
    path,
)
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

app_name = 'v1'


@extend_schema(
    responses=inline_serializer(
        name='ping',
        fields={'detail': serializers.CharField(default='pong')},
    ),
    summary='Ping API',
)
@api_view(['GET'])
def ping(request):
    return Response({'detail': 'pong'})


urlpatterns = [
    path('ping/', ping, name='ping'),
    path('', include('core.api.v1.channels.urls')),
    path('', include('core.api.v1.users.urls')),
    path('', include('core.api.v1.videos.urls')),
    path('', include('core.api.v1.reports.urls')),
    path('', include('core.api.v1.posts.urls')),
    path('', include('core.api.v1.payments.urls')),
]
