# -*- coding: utf-8 -*-
"""
@Time       ：2022/11/27 15:07
@Author     ：xixi <446837204@qq.com>
@File       ：meiduo_mall brands.py
"""
from rest_framework.generics import ListAPIView
from apps.goods.models import Brand
from apps.meiduo_admin.serializers.brands import BrandsListModelSerializer


class BrandSimpleListAPIView(ListAPIView):
    """品牌列表"""
    queryset = Brand.objects.all()

    serializer_class = BrandsListModelSerializer
