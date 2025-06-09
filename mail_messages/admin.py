from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_subject", "message_body")
    search_fields = ("message_subject",)
