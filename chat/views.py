# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from chat.serializers import UserSerializer, GroupSerializer, ConversationSerializer, ContactBookSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework import status
from rest_framework.decorators import permission_classes as pc
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from pprint import pprint
from django.contrib.auth import get_user_model
from .models import Conversation, ContactBook
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
# Create your views here.

class IsCreationOrIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            if view.action == 'create':
                return True
            else:
                return False
        else:
            return True

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsCreationOrIsAuthenticated,)
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ['username']
    filter_fields = ['username']


    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            u = User.objects.create_user(**serializer.validated_data)
            return Response({ 'id': u.pk }, status=status.HTTP_201_CREATED)

        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        return Response({ 'username': user.username })


class CurrentUserDetails(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        l = []
        if request.GET.get('type') == 'user_groups':
            for g in request.user.groups.all():
                l.append({ 'group_name': g.name, 'id': g.id })
            return Response(data=l, status=status.HTTP_200_OK)
        elif request.GET.get('type') == 'user_contacts':
            cb = ContactBook.objects.filter(book_owner=request.user.id)
            for contact in cb:
                l.append({ 'id': contact.user_id.id, 'username': contact.user_id.username })
            return Response(data=l, status=status.HTTP_200_OK)
        elif request.GET.get('type') == 'self_info':
            details = { 'id': request.user.id, 'username': request.user.username }
            return Response(data=details, status=status.HTTP_200_OK)

        return Response(data=None, status=status.HTTP_400_BAD_REQUEST)



class UserExistsView(APIView):

    def post(self, request, *args, **kwargs):

        username = request.data['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(data={'message': True})
        else:
            return Response(data={'message': False})

class GroupViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


    def create(self, request):
        """
        Creates a new group and adds users to the group
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            g = Group.objects.create(**serializer.validated_data)
            for uid in request.data.get('user_ids'):
                g.user_set.add(uid)
            g.user_set.add(request.user.id)

            return Response({ 'message': True }, status=status.HTTP_201_CREATED)

        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def add_to_group(self, request, group_id):
        """
        Adds users to existing group
        """
        try:
            g = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({ 'message': False }, status=status.HTTP_400_BAD_REQUEST)

        for id in request.data.get('user_ids'):
            g.user_set.add(id)

        return Response({ 'message': True }, status=status.HTTP_201_CREATED)


class ContactBookViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = ContactBook.objects.all()
    serializer_class = ContactBookSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        count = 0
        if serializer.is_valid():
            pprint(request.data.get('user_ids'))
            for uid in request.data.get('user_ids'):
                cb_data = ContactBook.objects.filter(book_owner=User.objects.get(pk=request.user.id), user_id=User.objects.get(pk=uid)).count()
                if cb_data == 0:
                    cb = ContactBook(book_owner=User.objects.get(pk=request.user.id), user_id=User.objects.get(pk=uid))
                    cb.save()
                    count += 1

            return Response({ 'created': count }, status=status.HTTP_201_CREATED)

        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ConversationSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    queryset = Conversation.objects.all()
    lookup_field = 'message_owner'
    factory = APIRequestFactory()
    # request = factory.get('/')

    

    def post(self, request):
        chat_room = self.request.data['chat_room']

        if chat_room is not None:
            convo = Conversation.objects.filter(chat_room=chat_room).order_by('-created_at')
            page = self.paginate_queryset(convo)
            if page is not None:

                serializer_context = {
                    'request': request
                }
                serializer = self.serializer_class(many=True, instance=page, context=serializer_context)
                return self.get_paginated_response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator
        
    def paginate_queryset(self, queryset):
         if self.paginator is None:
             return None
         return self.paginator.paginate_queryset(queryset, self.request, view=self)
         
    def get_paginated_response(self, data):
         assert self.paginator is not None
         return self.paginator.get_paginated_response(data)



class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_details': { 'id': token.user_id, 'username': User.objects.get(pk=token.user_id).username }})






# channels
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })
