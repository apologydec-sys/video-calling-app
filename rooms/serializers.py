from rest_framework import serializers

from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    share_link = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = ["id", "code", "title", "created_by", "created_at", "share_link"]
        read_only_fields = ["id", "code", "created_at", "share_link"]


class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["title"]
