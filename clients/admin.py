from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment', 'owner')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)
    ordering = ('full_name',)
    readonly_fields = ('owner',)
    help_texts = {
        'comment': 'Введите дополнительную информацию о клиенте'
    }

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)