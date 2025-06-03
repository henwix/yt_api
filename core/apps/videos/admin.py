from django.contrib import admin

from core.apps.videos.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'status', 'author', 'video_id']
