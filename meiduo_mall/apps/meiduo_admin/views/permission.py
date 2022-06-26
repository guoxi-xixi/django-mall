
# 用户
from apps.users.models import User
# 组
from django.contrib.auth.models import Group
# 权限
from django.contrib.auth.models import Permission

"""

1:1
1:n
n:m

老师和学生

老师表
学生表
老师和学生的关系表

"""

#####################权限#################################
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from apps.meiduo_admin.utils import PageNum
from apps.meiduo_admin.serializers.permission import PermissionModelSerializer

class PermissionModelViewSet(ModelViewSet):

    queryset = Permission.objects.all()

    serializer_class = PermissionModelSerializer

    pagination_class = PageNum


############ContentType 权限类型###################################
"""
所谓的权限 其实就是 对于模型的增删改查操作
我们需要确定对哪个模型 有 增删改查的权限
"""
from django.contrib.auth.models import ContentType
from rest_framework.generics import ListAPIView
from apps.meiduo_admin.serializers.permission import ContentTypeModelSerializer

class ContentTypeListAPIView(ListAPIView):

    queryset = ContentType.objects.all()

    serializer_class = ContentTypeModelSerializer


############组管理################################################
from django.contrib.auth.models import Group
from apps.meiduo_admin.serializers.permission import GroupModelSerializer

class GroupModelViewSet(ModelViewSet):

    queryset = Group.objects.all()

    serializer_class = GroupModelSerializer

    pagination_class = PageNum

###############组管理--权限列表展示###################################################

class GroupPermissionListAPIView(ListAPIView):

    queryset = Permission.objects.all()

    serializer_class = PermissionModelSerializer


###############管理员管理###################################################
from apps.users.models import User
from apps.meiduo_admin.serializers.permission import AdminUserModelSerializer

class AdminUserModelViewSet(ModelViewSet):

    queryset = User.objects.filter(is_staff=True)

    serializer_class = AdminUserModelSerializer

    pagination_class = PageNum


##############管理员管理-获取所有组#############################################
class SimpleGroupListAPIView(ListAPIView):

    queryset = Group.objects.all()

    serializer_class = GroupModelSerializer


