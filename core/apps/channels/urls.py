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
    path('channel/', views.ChannelRetrieveUpdateDeleteView.as_view(), name='channel-detail'),
    path('channel/subscribers/', views.ChannelSubscribersView.as_view(), name='channel-subscribers'),
    path('channel/delete-avatar/', views.ChannelAvatarDestroy.as_view(), name='channel-avatar-destroy'),
    path('c/<slug:slug>', views.ChannelMainView.as_view(), name='channel-show'),
    path('c/<slug:slug>/about', views.ChannelAboutView.as_view(), name='channel-about'),
    path('', include(router.urls)),
]
