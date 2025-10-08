from django.contrib import admin

from core.apps.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'text', 'author', 'created_at']
    list_editable = ['author', 'text']
