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


#######################SPU数据##############################
from apps.goods.models import SPU

class SPUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPU
        fields = ['id', 'name']


##########SPU 规格和规格选项的序列化器############################################
from apps.goods.models import SPUSpecification, SpecificationOption

# 规格选项 序列化器
class OptionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']

# SPU 规格序列化器
class SpecsModelSerializer(serializers.ModelSerializer):
    # 创建 子模版数据
    options = OptionModelSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'options']
