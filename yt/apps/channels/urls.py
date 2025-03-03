from django.urls import path
from . import views

app_name = 'channels'


urlpatterns = [
    path('channel/', views.ChannelRetrieveUpdateDeleteView.as_view(), name='channel-detail'),
    path('c/<slug:slug>', views.ChannelMainView.as_view(), name='channel-show'),
    path('c/<slug:slug>/about/', views.ChannelAboutView.as_view(), name='channel-about'),
]