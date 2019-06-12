# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from chat.serializers import UserSerializer, GroupSerializer, ContactBookSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework import status
from rest_framework.decorators import permission_classes as pc
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from pprint import pprint
from django.contrib.auth import get_user_model
from .models import ContactBook
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


class CurrentUserDetails(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        l = []
        if request.GET.get('type') == 'user_groups':
            for g in request.user.groups.all():
                l.append({ 'group_name': g.name, 'id': g.id })

            return Response(data=l, status=status.HTTP_200_OK)

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
            for uids in request.data.get('user_ids'):
                cb = ContactBook(book_owner=User.objects.get(pk=request.user.id), user_id=User.objects.get(pk=uids))
                cb.save()
                count += 1

            return Response({ 'created': count }, status=status.HTTP_201_CREATED)

        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)


