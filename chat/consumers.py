# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.auth import login
from .models import ContactBook
from django.contrib.auth.models import User
from .models import Conversation
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.scope['user'] = self.scope['url_route']['kwargs']['user_name']
        #self.room_group_name = 'chat_%s' % self.room_name
        self.room_group_name = self.room_name

        # if self.scope['user'] == 'AnonymousUser':
           #  # save the session (if the session backend does not access the db you can use `sync_to_async`)
           #  await database_sync_to_async(self.scope["session"].save)()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print('connected' + self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('discard')

    # Receive message from WebSocket
    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        text_data_json['data']['from_user'] = str(self.scope['user'])
        message = text_data_json['data']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )
        await database_sync_to_async(self.save_convo)((str(message['message'])))

        print('received ' + str(message['message']) + ' from ws')

    def save_convo(self, message):
        if self.room_name.startswith('chat__'):
            room_name = self.room_name.replace('chat__','')
            users = room_name.split('__')

            if ContactBook.objects.filter(book_owner=User.objects.get(username=users[0]), user_id=User.objects.get(username=users[1])).count() == 0:
                ContactBook.objects.create(book_owner=User.objects.get(username=users[0]), user_id=User.objects.get(username=users[1]))

            if ContactBook.objects.filter(book_owner=User.objects.get(username=users[1]), user_id=User.objects.get(username=users[0])).count() == 0:
                ContactBook.objects.create(book_owner=User.objects.get(username=users[1]), user_id=User.objects.get(username=users[0]))

        Conversation.objects.create(chat_room=self.room_name, 
                                        message=message, 
                                        user_id=User.objects.get(username=str(self.scope['user'])))
        

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message'] #json

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        print('chat message ' + str(message))