from apps.goods.models import SKU, SKUSpecification
from rest_framework import serializers

# SKUSpecification 序列化器 -- sku规格和规格选项
class SKUSpecificationModelSerializer(serializers.ModelSerializer):
    # 默认外键只读，修改字段属性
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']

class SKUModelSerializer(serializers.ModelSerializer):
    """
    前端传递的数据形式是
    {
        caption: "12不想13香"
        category_id: 115            ~~~~~~
        cost_price: "1"
        is_launched: "true"
        market_price: "11"
        name: "13香"
        price: "1"
        specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
        spu_id: 2                   ~~~~~~~
        stock: "1"
    }

    Q1. 外键中 spu和category的数据  前端是以 category_id 和 spu_id 的形式传递的 所以我们的序列化器 要改变
        spu_id=serializers.IntegerField()
        category_id=serializers.IntegerField()

    Q2. 我们 通过 添加 spu_id 和 category_id 能接收前端的数据,
        但是并没有改变 系统自动生成的  spu和category 这2个字段必传的选项
        如何去解决呢???
        ① 改为 required=False
        ② 为了配合查询数据的展示 我们 重写 spu 和category 这2个字段

        spu=serializers.StringRelatedField()
        category=serializers.StringRelatedField()

        新的疑问!!!  默认的字段是 required=True

        StringRelatedField 本质是什么???
        本质是 获取 关联模型的 __str__ 里的数据

    Q3. 当我们的sku保存了之后, sku的最终 (规格)选项 也应该入库
        specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}] 这个没有入库!!!!

        # validated_data  其实是等于 我们序列化器 通过字段 验证的数据
        # 当前 我们在 序列化器中 并没有定义 specs 所以 validated_data 里没有 specs
        # 我们想要获取 specs 有至少2种方法
        # 1. 添加 specs 字段
        # 2. 通过 断点我们发现  self.context['request'] 可以获取 当前的请求对象.
    """
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    spu = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    specs = SKUSpecificationModelSerializer(many=True)
    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        # validated_data  其实是等于 我们序列化器 通过字段 验证的数据
        # 当前 我们在 序列化器中 并没有定义 specs 所以 validated_data 里没有 specs
        # 我们想要获取 specs 有至少2种方法
        # 1. 添加 specs 字段
        # 2. 通过 断点我们发现  self.context['request'] 可以获取 当前的请求对象.

        # 保存 sku和 sku规格.规格选项

        # 1. 把 规格和规格选项 单独获取出来
        specs = validated_data.pop('specs')
        from django.db import transaction
        with transaction.atomic():
            # 开启事务 - 事务开启点
            save_point = transaction.savepoint()
            try:
                # 2. 先保存sku数据
                sku = SKU.objects.create(**validated_data)
                # 3. 对规格和规格选项进行遍历保存
                for spec in specs:
                    # spec = {spec_id: "4", option_id: 8}
                    SKUSpecification.objects.create(sku=sku, **spec)
            except Exception as e:
                # 事务回滚点
                transaction.savepoint_rollback(save_point)
            else:
                # 提交事务
                transaction.savepoint_commit(save_point)

        return sku



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
