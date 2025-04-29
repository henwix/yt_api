from rest_framework import serializers


class AbortUploadSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=256)
    upload_id = serializers.CharField(max_length=256)


class GenerateUploadPartUrlSerializer(AbortUploadSerializer):
    part_number = serializers.IntegerField(min_value=1, max_value=10000)


class CompleteUploadSerializer(AbortUploadSerializer):
    parts = serializers.ListField(min_length=1, max_length=10000)
