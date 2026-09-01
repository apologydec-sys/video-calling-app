from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "created_by", "created_at"]
    search_fields = ["code", "title"]
