# -*- coding: utf-8 -*-

# @File    : meiduo_mall spu.py
# @Time    : 2022/7/20 17:33
# @Author  : xixi

from rest_framework import serializers
from apps.goods.models import SPU

class SPUModelSerializer(serializers.ModelSerializer):

    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        fields = '__all__'
