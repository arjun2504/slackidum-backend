from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.core import exceptions
import django.contrib.auth.password_validation as validators

class GroupSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedRelatedField(view_name='api:user-detail',
    #                                           source='username')
    name = serializers.CharField(required=False)

    class Meta:
        model = Group
        fields = ['id', 'name']

class UserSerializer(serializers.HyperlinkedModelSerializer):

    # def update(self, validated_data):

    #     user = User.objects.filter(username = validate_data['username']).first()
    #     user.set_password(validated_data['password'])
    #     user.save()

    #     return user

    groups = GroupSerializer(many=True)

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

