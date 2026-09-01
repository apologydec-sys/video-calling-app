import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class SignalingConsumer(WebsocketConsumer):
    def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"].get("room_code")
        self.room_group_name = f"room_{self.room_code}"
        self.user_name = f"Guest-{self.channel_name[:5]}"

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

        self.send(text_data=json.dumps({
            "type": "system",
            "message": f"Connected to room {self.room_code}",
            "room_code": self.room_code,
            "user_name": self.user_name,
        }))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "relay_message",
                "sender_channel": self.channel_name,
                "payload": {
                    "type": "presence",
                    "user_name": self.user_name,
                    "status": "joined",
                },
            },
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "relay_message",
                "sender_channel": self.channel_name,
                "payload": {
                    "type": "presence",
                    "user_name": self.user_name,
                    "status": "left",
                },
            },
        )
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        message_type = payload.get("type")

        if payload.get("user_name"):
            self.user_name = payload["user_name"]

        if message_type in {"offer", "answer", "ice-candidate", "join", "leave", "chat", "presence"}:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "relay_message",
                    "sender_channel": self.channel_name,
                    "payload": payload,
                },
            )
        else:
            self.send(text_data=json.dumps({"type": "error", "message": "Unsupported message type"}))

    def relay_message(self, event):
        payload = event["payload"]
        sender_channel = event["sender_channel"]

        if sender_channel == self.channel_name:
            return

        self.send(text_data=json.dumps(payload))
