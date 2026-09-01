import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("rooms", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="RoomInvite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254)),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("room", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invites", to="rooms.room")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]