from rest_framework import serializers


class KeySerializer(serializers.Serializer):
    key = serializers.CharField(max_length=256, help_text='Key associated with the file')


class FilenameSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=256, help_text='File name to upload')


class UploadUrlSerializer(serializers.Serializer):
    upload_url = serializers.CharField(help_text='URL to upload file')


class BaseMultipartUploadInSerializer(KeySerializer, serializers.Serializer):
    upload_id = serializers.CharField(max_length=256, help_text='ID of a multipart upload_id')


class GenerateMultipartUploadPartUrlInSerializer(BaseMultipartUploadInSerializer, serializers.Serializer):
    part_number = serializers.IntegerField(
        min_value=1,
        max_value=10000,
        help_text='Part number associated with a multipart upload',
    )


class CompleteMultipartUploadInSerializer(BaseMultipartUploadInSerializer, serializers.Serializer):
    parts = serializers.ListField(
        min_length=1,
        max_length=10000,
        help_text='List of upload parts associated with a multipart upload',
    )


class GenerateUploadUrlOutSerializer(UploadUrlSerializer, KeySerializer):
    pass


class CreateMultipartUploadOutSerializer(BaseMultipartUploadInSerializer):
    pass
