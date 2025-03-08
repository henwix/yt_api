import boto3
import os

def run():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get("AWS_S3_REGION_NAME")
    )

    url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': "django-henwix-bucket", 
            'Key': "channel_avatars/2fe38985-01a5-4c30-a93b-898d1e280278-profile_image-70x70.png"
        },
        ExpiresIn=60
    )

    print(url)