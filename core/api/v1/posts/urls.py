from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from core.api.v1.posts.views import (
    CommentPostAPIView,
    PostAPIViewset,
)

app_name = 'posts'


router = DefaultRouter()
router.register('posts', PostAPIViewset, basename='posts')
router.register('posts-comments', CommentPostAPIView, basename='posts-comments')


urlpatterns = [
    path('', include(router.urls)),
]
