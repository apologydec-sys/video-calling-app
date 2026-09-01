import random
import string
import uuid

from django.conf import settings
from django.db import models


class Room(models.Model):
    code = models.CharField(max_length=12, unique=True, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Room {self.code}"

    @classmethod
    def generate_code(cls, length=6):
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choice(alphabet) for _ in range(length))
            if not cls.objects.filter(code=code).exists():
                return code

    @property
    def share_link(self):
        return f"/join/{self.code}/"


class RoomInvite(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
