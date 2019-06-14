from django.urls import re_path
from django.conf.urls import url
from .consumers import ChatConsumer
from .online import OnlinePresence

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/(?P<user_name>[^/]+)/$', ChatConsumer),
    re_path(r'^ws/presence/(?P<user_name>[^/]+)/$', OnlinePresence),
]
