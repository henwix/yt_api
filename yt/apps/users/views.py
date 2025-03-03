from django.shortcuts import render
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model


class CustomUserViewSet(UserViewSet):
    """
    Customized UserViewSet from Djoser.
    prefetch_related('channel') has been added to queryset
    """

    queryset = get_user_model().objects.all().prefetch_related("channel")