from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.core import exceptions
import django.contrib.auth.password_validation as validators
from .models import Conversation, ContactBook

class GroupSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedRelatedField(view_name='api:user-detail',
    #                                           source='username')
    name = serializers.CharField(required=False)

    class Meta:
        model = Group
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):

    # def update(self, validated_data):

    #     user = User.objects.filter(username = validate_data['username']).first()
    #     user.set_password(validated_data['password'])
    #     user.save()

    #     return user

    groups = GroupSerializer(required=False, many=True)

    def validate(self, data):
         user = User(**data)

         password = data.get('password')

         errors = dict() 
         try:
             validators.validate_password(password=password, user=User)

         except exceptions.ValidationError as e:
             errors['password'] = list(e.messages)

         if errors:
             raise serializers.ValidationError(errors)

         return super(UserSerializer, self).validate(data)

    class Meta:
        model = User
        extra_kwargs = {
            'password': { 'write_only': True }
        }
        fields = ('username', 'id', 'password', 'groups')


class ContactBookSerializer(serializers.HyperlinkedModelSerializer):
    users = UserSerializer(required=False, many=True)

    class Meta:
        model = ContactBook
        extra_kwargs = {
            'user_id': { 'required': False },
            'book_owner': { 'required': False }
        }
        fields = ('users', 'user_id', 'book_owner', 'id', 'created_at', 'updated_at')

class ConversationSerializer(serializers.ModelSerializer):


    # users = serializers.CharField(source="message_owner.password", write_only=True)
    user_id = UserSerializer(many=False, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    # updated_at = serializers.DateField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Conversation
        fields = ('id', 'message', 'user_id', 'is_read', 'chat_room', 'created_at')
