import os
from datetime import timedelta

import boto3
import django_filters
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from apps.common.pagination import CustomCursorPagination
from apps.common.permissions import IsAuthenticatedOrAdminOrReadOnly, IsAuthenticatedOrAuthorOrReadOnly

from . import serializers
from .filters import VideoFilter
from .models import Video, VideoComment, VideoLike, VideoView


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing, retrieving, creating, editing and deleting 'Video' instances.
    Supports searching by 'name', 'description', 'author__name', 'author__slug' fields.
    Returns nothing if 'search' query-param was not provided - '?search' param for listing is required.
    Example: api/v1/video?search=airplane
    """

    lookup_field = "video_id"
    lookup_url_kwarg = "video_id"
    permission_classes = [IsAuthenticatedOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = VideoFilter
    pagination_class = CustomCursorPagination
    search_fields = ["@name", "@description", "@author__name", "@author__slug"]
    ordering_fields = ["created_at", "views_count"]
    throttle_scope = "video"

    @action(url_path="like", methods=["post", "delete"], detail=True)
    def like(self, request, video_id):
        """
        API endpoint for 'likes' and 'dislikes' actions.
        'POST' and 'DELETE' methods are available for setting 'likes'/'dislikes' and removing them.

        POST: Only one field can be provided: 'is_like' - true by default and means like, but false - dislike.
        DELETE: Have no required fields.
        Related video determines by 'video_id' query-param.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/like/
        """

        channel = request.user.channel
        video = get_object_or_404(Video, video_id=video_id)

        if request.method == "POST":
            is_like = request.data.get("is_like", True)

            like, created = VideoLike.objects.get_or_create(
                channel=channel,
                video=video,
                defaults={
                    "is_like": is_like,
                },
            )

            if not created:
                like.is_like = is_like
                like.save()

            return Response({"status": "success", "is_like": is_like}, status=HTTP_200_OK)

        if request.method == "DELETE":
            deleted, _ = VideoLike.objects.filter(channel=channel, video=video).delete()

            if deleted:
                return Response({"status": "Success"}, status=HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Like not found"}, HTTP_404_NOT_FOUND)

    @action(url_path="view", methods=["post"], detail=True)
    def view(self, request, video_id):
        """
        API endpoint for adding views to videos.

        Have no required fields.
        Allows add a view if the previous one was more than 24 hours ago.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/view/
        """

        channel = getattr(request.user, "channel", None)
        video = get_object_or_404(Video, video_id=video_id)
        ip_address = request.META.get("REMOTE_ADDR")

        last_view = VideoView.objects.filter(
            channel=channel if channel else None,
            ip_address=ip_address if ip_address else None,
            video=video,
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).exists()

        if not last_view:
            VideoView.objects.create(
                channel=channel,
                video=video,
                ip_address=ip_address,
            )
            return Response({"status": "success"}, status=HTTP_201_CREATED)
        else:
            return Response({"error": "View already exists"}, status=HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        """
        Custom 'get_serializer_class' method.
        If action is list - return VideoPreviewSerializer else VideoSerializer
        """

        if self.action == "list":
            return serializers.VideoPreviewSerializer
        return serializers.VideoSerializer

    def get_queryset(self):
        """
        Custom get_queryset method.

        Add 'views_count' annotated field if action == 'list' for 'Video' preview.
        If action == 'retrieve' - add views_count and likes_count for 'Video' detail info.
        """

        if self.action == "list":
            if not self.request.query_params.get("search"):
                return []
            return (
                Video.objects.select_related("author")
                .filter(status=Video.VideoStatus.PUBLIC)
                .annotate(views_count=Count("views", distinct=True))
            )
        if self.action == "retrieve":
            return (
                Video.objects.select_related("author")
                .all()
                .annotate(
                    views_count=Count("views", distinct=True),
                    likes_count=Count("likes", filter=Q(likes__is_like=True), distinct=True),
                    comments_count=Count("comments"),
                    subs_count=Count("author__followers", distinct=True),
                )
            )
        return Video.objects.all()

    def list(self, request, *args, **kwargs):
        if not request.query_params.get("search"):
            return Response({"None": "No results found. Try different keywords or remove search filters"})
        return super().list(request, *args, **kwargs)


class CommentVideoAPIView(viewsets.ModelViewSet):
    """
    API endpoint for listing, retrieving, updating and deleting Video Comments.

    Permissions:
        GET - Everyone
        POST - Authenticated only
        DELETE/POST/PUT - Comment's author only

    Supports pagination by cursor.

    Example: /api/v1/video-comment/?v=uN9qVyjTrO6
    """

    serializer_class = serializers.VideoCommentSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsAuthenticatedOrAuthorOrReadOnly]

    def get_queryset(self):
        if self.action == "list":
            video = self.request.query_params.get("v")
            if not video:
                return []
            return VideoComment.objects.all().select_related("author", "video").filter(video__video_id=video)
        return VideoComment.objects.all().select_related("author", "video")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="v",
                description="*Required parameter to get related video's comments.",
                required=True,
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        if not request.query_params.get("v"):
            return Response({"None": "No comments found."})
        return super().list(request, *args, **kwargs)


class GeneratePresignedUrlView(APIView):
    """
    API endpoint to generate presigned URL for channel_avatar uploading to S3.
    Takes one required parameter: 'filename' to generate URL based on that name.
    Example: /api/v1/get-upload-link/17388dff.jpg/
    """

    def get(self, request, filename):
        if filename and filename[-4:] not in [".png", ".jpg"]:
            return Response({"error": "Unsupported file format"}, status=HTTP_400_BAD_REQUEST)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_S3_REGION_NAME"),
        )

        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": os.environ.get("AWS_STORAGE_BUCKET_NAME"),
                "Key": f"channel_avatars/{filename}",
            },
            ExpiresIn=120,
            HttpMethod="PUT",
        )

        return Response({"put_url": url}, status=HTTP_200_OK)
