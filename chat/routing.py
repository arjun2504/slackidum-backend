from django.urls import re_path
from django.conf.urls import url
from chat.consumers.consumers import ChatConsumer
from chat.consumers.new_msg_consumer import NewMsgConsumer
from chat.consumers.online import OnlinePresence

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/(?P<user_name>[^/]+)/$', ChatConsumer),
    re_path(r'^ws/presence/(?P<user_name>[^/]+)/$', OnlinePresence),
    re_path(r'^ws/newmsg/(?P<user_name>[^/]+)/$', NewMsgConsumer),
]
