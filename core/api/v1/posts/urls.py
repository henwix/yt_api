from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from core.api.v1.posts.views import PostAPIViewset


app_name = "posts"


router = DefaultRouter()
router.register("posts", PostAPIViewset, basename='videos')


urlpatterns = [
    path('', include(router.urls)),
]
