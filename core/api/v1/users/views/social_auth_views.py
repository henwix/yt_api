from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.oauth import BaseOAuth2
from social_django.utils import (
    load_backend,
    load_strategy,
)


class GenerateSocialAuthUrlView(APIView):
    def get(self, request, provider):
        redirect_uri = request.build_absolute_uri(f'/api/v1/social_auth/{provider}/')
        strategy = load_strategy(request)
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=redirect_uri)

        if not backend:
            return Response({'error': 'Invalid provider'}, status=400)

        auth_url = backend.auth_url()
        return Response({'auth_url': auth_url})


class SocialAuthView(APIView):
    def get(self, request, provider):
        # provider = request.data.get('provider')
        # code = request.data.get('code')
        # redirect_uri = request.data.get('redirect_uri')

        # if not provider or not code or not redirect_uri:
        # return Response({'error': 'Missing required parameters'}, status=400)

        strategy = load_strategy(request)
        # TODO: add Exceptions Middleware
        # TODO: read the documentation for social-auth-app-django
        backend: BaseOAuth2 = load_backend(
            strategy=strategy,
            name=provider,
            redirect_uri=reverse_lazy('v1:users:social_auth', kwargs={'provider': provider}),
        )
        user = backend.auth_complete(
            user=request.user if request.user.is_authenticated else None,
        )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        tokens = {'refresh': str(refresh), 'access': str(access)}
        print(tokens)
        return HttpResponseRedirect(
            reverse_lazy('v1:users:customuser-me'),
        )
        return Response(tokens)
