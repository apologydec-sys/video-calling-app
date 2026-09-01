import os

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Room, RoomInvite
from .serializers import CreateRoomSerializer, RoomSerializer


# ============================================================
# PAGE VIEWS
# ============================================================

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


# ============================================================
# ROOM API
# ============================================================

@api_view(["POST"])
def create_room(request):
    serializer = CreateRoomSerializer(data=request.data)

    if serializer.is_valid():
        room = Room.objects.create(
            title=serializer.validated_data.get("title") or "New Room",
            code=Room.generate_code(),
            created_by=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response(
            RoomSerializer(room).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def room_detail(request, room_code):
    room = get_object_or_404(Room, code=room_code)

    return Response(
        RoomSerializer(room).data
    )


@api_view(["GET"])
def join_room(request, room_code):
    room = get_object_or_404(Room, code=room_code)

    if request.accepted_media_type == "application/json":
        return JsonResponse(
            {
                "room_code": room.code,
                "title": room.title or "Untitled Room",
                "share_link": room.share_link,
            }
        )

    return redirect(
        "lobby_page",
        room_code=room.code,
    )


# ============================================================
# EMAIL INVITATION
# ============================================================

@api_view(["POST"])
def send_room_invite(request, room_code):
    """
    Send a video-call invitation to an email address.

    The actual email delivery is handled by Django's
    configured email backend.
    """

    # --------------------------------------------------------
    # Find room
    # --------------------------------------------------------

    room = get_object_or_404(
        Room,
        code=room_code,
    )

    # --------------------------------------------------------
    # Get email from request
    # --------------------------------------------------------

    email = (
        request.data.get("email") or ""
    ).strip()

    # --------------------------------------------------------
    # Validate email
    # --------------------------------------------------------

    if not email:
        return Response(
            {
                "email": [
                    "Email address is required."
                ]
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)

    except ValidationError:
        return Response(
            {
                "email": [
                    "Enter a valid email address."
                ]
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Create invitation
    # --------------------------------------------------------

    invite = RoomInvite.objects.create(
        room=room,
        email=email,
    )

    # --------------------------------------------------------
    # Create invitation URL
    # --------------------------------------------------------

    invite_url = request.build_absolute_uri(
        reverse(
            "accept_invite",
            args=[invite.token],
        )
    )

    # --------------------------------------------------------
    # Email information
    # --------------------------------------------------------

    room_title = (
        room.title
        or "an Akanni X call"
    )

    subject = (
        f"You are invited to join {room_title}"
    )

    message = (
        f"You have been invited to join "
        f"{room_title}.\n\n"

        f"Click the link below to join the "
        f"video call:\n\n"

        f"{invite_url}\n\n"

        f"Room code: {room.code}\n\n"

        f"See you in the call!"
    )

    # --------------------------------------------------------
    # Sender
    # --------------------------------------------------------

    from_email = os.environ.get(
        "DEFAULT_FROM_EMAIL"
    )

    if not from_email:
        return Response(
            {
                "message": (
                    "Email is not configured. "
                    "Set DEFAULT_FROM_EMAIL."
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )

    except Exception as error:
        # Delete invitation if email could not be sent
        invite.delete()

        return Response(
            {
                "message": (
                    "The invitation could not be sent."
                ),
                "error": str(error),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return Response(
        {
            "message": (
                f"Invite sent to {email}."
            ),
            "invite_url": invite_url,
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# ACCEPT INVITATION
# ============================================================

def accept_invite(request, token):
    invite = get_object_or_404(
        RoomInvite.objects.select_related("room"),
        token=token,
    )

    # Mark invitation as accepted
    if invite.accepted_at is None:
        invite.accepted_at = timezone.now()

        invite.save(
            update_fields=["accepted_at"]
        )

    # Send visitor to lobby
    return redirect(
        "lobby_page",
        room_code=invite.room.code,
    )