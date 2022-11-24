# -*- coding: utf-8 -*-

# @File    : meiduo_mall spu.py
# @Time    : 2022/7/20 17:33
# @Author  : xixi

from rest_framework import serializers
from apps.goods.models import SPU, Brand


class SPUModelSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        fields = '__all__'


class BrandsModelSerializer(serializers.ModelSerializer):
    """
        品牌序列化器
    """
    name = serializers.CharField()

    class Meta:
        model = Brand
        fields = ['id', 'name']
