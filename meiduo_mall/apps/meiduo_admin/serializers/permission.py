
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


