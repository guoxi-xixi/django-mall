# -*- coding: utf-8 -*-

# @File    : meiduo_mall spu.py
# @Time    : 2022/7/20 17:34
# @Author  : xixi

from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SPU
from apps.meiduo_admin.serializers.spu import SPUModelSerializer
from apps.meiduo_admin.utils import PageNum
from rest_framework.permissions import IsAdminUser


class SPUModelViewSet(ModelViewSet):

    # queryset = SPU.objects.all()

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return SPU.objects.get(name__contains=keyword)
        return SPU.objects.all()

    serializer_class = SPUModelSerializer

    pagination_class = PageNum

    permission_classes = [IsAdminUser]
