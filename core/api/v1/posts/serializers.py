from rest_framework import serializers

from core.apps.posts.models import Post


class PostCreateInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['text']


class PostCreateOutSerializer(serializers.Serializer):
    pk = serializers.CharField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField()
