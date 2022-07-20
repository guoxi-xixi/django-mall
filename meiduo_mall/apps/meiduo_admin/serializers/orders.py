from apps.orders.models import OrderInfo, OrderGoods
from rest_framework import serializers
from apps.goods.models import SKU



class SKUModelSerializer(serializers.ModelSerializer):
    """
        商品sku表序列化器
    """
    class Meta:
        model = SKU
        # fields = '__all__'
        fields = ['name', 'default_image']


class OrderGoodsModelSerializer(serializers.ModelSerializer):
    """
        订单商品序列化器
    """
    # 嵌套返回sku表数据
    sku = SKUModelSerializer()

    class Meta:
        model = OrderGoods
        # fields = '__all__'
        fields = ['count', 'price', 'sku']


class OrderModelSerializer(serializers.ModelSerializer):
    """
        订单序列化器
    """

    # 关联嵌套返回 用户表数据和订单商品表数据
    user = serializers.StringRelatedField()
    skus = OrderGoodsModelSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'

