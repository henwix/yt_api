from rest_framework import serializers


class KeySerializer(serializers.Serializer):
    key = serializers.CharField(max_length=256)


class FilenameSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=256)


class AbortMultipartUploadInSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=256)
    upload_id = serializers.CharField(max_length=256)


class GenerateMultipartUploadPartUrlInSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=256)
    upload_id = serializers.CharField(max_length=256)
    part_number = serializers.IntegerField(min_value=1, max_value=10000)


class CompleteMultipartUploadInSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=256)
    upload_id = serializers.CharField(max_length=256)
    parts = serializers.ListField(min_length=1, max_length=10000)


class GenerateUploadUrlOutSerializer(serializers.Serializer):
    upload_url = serializers.CharField()
    key = serializers.CharField(max_length=256)


class CreateMultipartUploadOutSerializer(serializers.Serializer):
    upload_id = serializers.CharField(max_length=256)
    key = serializers.CharField(max_length=256)
