from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Room, RoomInvite
from .serializers import CreateRoomSerializer, RoomSerializer


def landing(request):
    return render(request, "landing.html")


def about_me(request):
    return render(request, "about.html")


def lobby_page(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    return render(request, "lobby.html", {"room": room})


def room_page(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    return render(request, "room.html", {"room": room})


@api_view(["POST"])
def create_room(request):
    serializer = CreateRoomSerializer(data=request.data)
    if serializer.is_valid():
        room = Room.objects.create(
            title=serializer.validated_data.get("title") or "New Room",
            code=Room.generate_code(),
            created_by=request.user if request.user.is_authenticated else None,
        )
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def room_detail(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    return Response(RoomSerializer(room).data)


@api_view(["GET"])
def join_room(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    if request.accepted_media_type == "application/json":
        return JsonResponse({"room_code": room.code, "title": room.title or "Untitled Room", "share_link": room.share_link})
    return redirect("lobby_page", room_code=room.code)


@api_view(["POST"])
def send_room_invite(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    email = (request.data.get("email") or "").strip()
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email

    try:
        validate_email(email)
    except ValidationError:
        return Response({"email": ["Enter a valid email address."]}, status=status.HTTP_400_BAD_REQUEST)

    invite = RoomInvite.objects.create(room=room, email=email)
    invite_url = request.build_absolute_uri(reverse("accept_invite", args=[invite.token]))
    send_mail(
        subject=f"You are invited to join {room.title or 'an Akanni X call'}",
        message=(
            f"You have been invited to join {room.title or 'an Akanni X call'}.\n\n"
            f"Accept the invitation and enter the call here:\n{invite_url}\n\n"
            f"Room code: {room.code}"
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )
    return Response({"message": f"Invite sent to {email}."}, status=status.HTTP_201_CREATED)


def accept_invite(request, token):
    invite = get_object_or_404(RoomInvite.objects.select_related("room"), token=token)
    if invite.accepted_at is None:
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["accepted_at"])
    return redirect("lobby_page", room_code=invite.room.code)
