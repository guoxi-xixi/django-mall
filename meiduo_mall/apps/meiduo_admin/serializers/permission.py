
#####################权限#################################
from rest_framework import serializers
from django.contrib.auth.models import Permission

class PermissionModelSerializer(serializers.ModelSerializer):
    """
    用户权限表序列化器
    """
    class Meta:
        model = Permission
        fields = '__all__'


#####################ContentType#################################
from django.contrib.auth.models import ContentType

class ContentTypeModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = ['id', 'name']


#####################组#################################
from django.contrib.auth.models import Group

class GroupModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


#####################普通管理员序列化器#################################
from apps.users.models import User

class AdminUserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'



