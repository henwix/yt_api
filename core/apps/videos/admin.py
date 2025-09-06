from django.contrib import admin

from core.apps.videos.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'status', 'author', 'video_id', 'upload_id', 's3_key', 'status', 'upload_status']
