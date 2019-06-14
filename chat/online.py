# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.auth import login
from .models import ContactBook
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Presence

class OnlinePresence(AsyncWebsocketConsumer):
    async def connect(self):
        self.scope['user'] = self.scope['url_route']['kwargs']['user_name']

        self.room_group_name = 'online'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await database_sync_to_async(self.save_presence)()
        print(self.scope['user'] + ' is online')
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_online_status',
                'message': { 'user': self.scope['user'], 'type': 'online' }
            }
        )

    def save_presence(self):
        if Presence.objects.filter(user_id__username=self.scope['user']).count() == 0:
            Presence.objects.create(user_id=User.objects.get(username=self.scope['user']))


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_online_status',
                'message': { 'user': self.scope['user'], 'type': 'offline' }
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await database_sync_to_async(self.remove_presence)()
        print('discard')

    async def broadcast_online_status(self, event):
        message = event['message'] #json

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        
        # print('broadcast: ' + str(message) + ' is offline')

    def remove_presence(self):
        Presence.objects.filter(user_id__username=self.scope['user']).delete()