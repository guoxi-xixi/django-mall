# -*- coding: utf-8 -*-
"""
@Time       ：2022/11/27 15:05
@Author     ：xixi <446837204@qq.com>
@File       ：meiduo_mall brands.py
"""

from rest_framework import serializers
from apps.goods.models import Brand


class BrandsListModelSerializer(serializers.ModelSerializer):
    """
        品牌序列化器
    """

    class Meta:
        model = Brand
        fields = ['id', 'name']
