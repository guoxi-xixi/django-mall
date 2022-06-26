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
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }

    def create(self, validated_data):
        # 调用父类的create
        # user = super(AdminUserModelSerializer, self).create(validated_data)
        user = super().create(validated_data)

        # 密码加密
        user.set_password(validated_data.get('password'))
        # 后台用户
        user.is_staff = True
        user.save()

        return user

    def update(self, instance, validated_data):
        # 调用父类的update
        super(AdminUserModelSerializer, self).update(instance, validated_data)

        # 密码加密
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
            instance.save()

        return instance
