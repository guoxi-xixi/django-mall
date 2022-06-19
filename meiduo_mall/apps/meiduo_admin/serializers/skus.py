from apps.goods.models import SKU
from rest_framework import serializers

class SKUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = '__all__'


##########三级分类数据序列化器############################################
from apps.goods.models import GoodsCategory

class GoodsCategoryModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']
