# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.auth import login
from chat.models import ContactBook
from django.contrib.auth.models import User
from chat.models import Conversation
from channels.db import database_sync_to_async

class NewMsgConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scope['user'] = self.scope['url_route']['kwargs']['user_name']
        self.room_group_name = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['from_user']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_message',
                'message': message,
            }
        )

    # Receive message from room group
    async def new_message(self, event):
        message = event['message'] #json

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

        