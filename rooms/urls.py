from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about_me, name="about_me"),
    path("lobby/<str:room_code>/", views.lobby_page, name="lobby_page"),
    path("room/<str:room_code>/", views.room_page, name="room_page"),
    path("join/<str:room_code>/", views.join_room, name="join_room"),
    path("invite/<uuid:token>/", views.accept_invite, name="accept_invite"),
    path("api/rooms/create/", views.create_room, name="create_room"),
    path("api/rooms/<str:room_code>/", views.room_detail, name="room_detail"),
    path("api/rooms/<str:room_code>/invite/", views.send_room_invite, name="send_room_invite"),
]
