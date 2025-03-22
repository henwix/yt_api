import os

import boto3
from celery import shared_task


@shared_task
def delete_channel_files_task(files):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_S3_REGION_NAME'),
    )
    try:
        response = s3_client.delete_objects(Bucket='django-henwix-bucket', Delete={'Objects': files})
        return f'Files successfully deleted: {len(response.get("Deleted", []))}'

    except Exception as e:
        return f'Failed to delete files: {e}'
