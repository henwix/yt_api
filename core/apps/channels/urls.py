from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'channels'

router = DefaultRouter()
router.register('subscription', views.SubscriptionAPIView, basename='subscription')


urlpatterns = [
    # channel avatar urls
    path('channel/avatar/delete/', views.DeleteChannelAvatarView.as_view(), name='channel-avatar-delete'),
    path('channel/avatar/upload/url/', views.GenerateUploadAvatarUrlView.as_view(), name='channel-avatar-upload-url'),

    # channel urls
    path('channel/', views.ChannelRetrieveUpdateDeleteView.as_view(), name='channel-detail'),
    path('channel/<slug:slug>', views.ChannelMainView.as_view(), name='channels-show'),
    path('channel/<slug:slug>/about', views.ChannelAboutView.as_view(), name='channels-about'),

    # channel subscribers urls
    path('channel/subscribers/', views.ChannelSubscribersView.as_view(), name='channel-subscribers'),

    # router urls
    path('', include(router.urls)),
]
