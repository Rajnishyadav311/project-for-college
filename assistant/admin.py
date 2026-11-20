from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'content_preview', 'language', 'created_at')
    list_filter = ('role', 'language')

    def content_preview(self, obj):
        return obj.content[:50]
