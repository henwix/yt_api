from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from core.api.v1.channels.views.channel_upload_views import (
    CompleteUploadAvatarView,
    DeleteChannelAvatarView,
    GenerateDownloadAvatarUrlView,
    GenerateUploadAvatarUrlView,
)
from core.api.v1.channels.views.channel_views import (
    ChannelAboutView,
    ChannelMainView,
    ChannelRetrieveUpdateDeleteView,
    ChannelSubscribersView,
    SubscriptionAPIView,
)

app_name = 'channels'

router = DefaultRouter()
router.register('subscription', SubscriptionAPIView, basename='subscription')


urlpatterns = [
    # channel avatar urls
    path(
        'channel/avatar_upload_url/',
        GenerateUploadAvatarUrlView.as_view(),
        name='channel-avatar-upload-url',
    ),
    path(
        'channel/avatar_upload_complete/',
        CompleteUploadAvatarView.as_view(),
        name='channel-avatar-upload-complete',
    ),
    path(
        'channel/avatar_download_url/',
        GenerateDownloadAvatarUrlView.as_view(),
        name='channel-avatar-download-url',
    ),
    path(
        'channel/avatar_delete/',
        DeleteChannelAvatarView.as_view(),
        name='channel-avatar-delete',
    ),
    # personal channel urls
    path('channel/', ChannelRetrieveUpdateDeleteView.as_view(), name='channel-detail'),
    path('channel/subscribers/', ChannelSubscribersView.as_view(), name='channel-subscribers'),
    # channel urls
    path('channels/<slug:slug>', ChannelMainView.as_view(), name='channels-show'),
    path('channels/<slug:slug>/about', ChannelAboutView.as_view(), name='channels-about'),
    # router urls
    path('', include(router.urls)),
]
