from django.shortcuts import render

# Create your views here.

"""
需求：
    提交订单页面的展示
前端：
        发送一个axios请求来获取 地址信息和购物车中选中商品的信息
后端：
    请求：         必须是登录用户才可以访问
    业务逻辑：      地址信息，购物车中选中商品的信息
    响应：         JSON
    路由：
            GET     orders/settlement/
    步骤：

        1.获取用户信息
        2.地址信息
            2.1 查询用户的地址信息 [Address,Address,...]
            2.2 将对象数据转换为字典数据
        3.购物车中选中商品的信息
            3.1 连接redis
            3.2 hash        {sku_id:count,sku_id:count}
            3.3 set         [1,2]
            3.4 重新组织一个 选中的信息
            3.5 根据商品的id 查询商品的具体信息 [SKU,SKU,SKu...]
            3.6 需要将对象数据转换为字典数据
"""
import logging

from utils.views import LoginRequiredJSONMixin
from django.views import View
from apps.users.models import Address
from django_redis import get_redis_connection
from apps.goods.models import SKU
from django.http import JsonResponse

logger = logging.getLogger('django')

class OrderSettlementView(LoginRequiredJSONMixin, View):
    """结算订单"""

    def get(self, request):
        # 1.获取用户信息
        user = request.user
        # 2.地址信息
        #     2.1 查询用户的地址信息 [Address,Address,...]
        addresses = Address.objects.filter(user=user, is_deleted=False)
        #     2.2 将对象数据转换为字典数据
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        # 3.购物车中选中商品的信息
        #     3.1 连接redis
        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        #     3.2 hash        {sku_id:count,sku_id:count}
        pipeline.hgetall('carts_%s'%user.id)
        #     3.3 set         [1,2]
        pipeline.smembers('selected_%s'%user.id)

        result = pipeline.execute() # result = [hash结果，set结果]
        sku_id_count = result[0]    #{sku_id:count,sku_id:count}
        selected = result[1]    # [1,2]
        #     3.4 重新组织一个 选中的信息
        # selected_carts = {sku_id:count}
        selected_carts = {}
        for sku_id in selected:
            selected_carts[int(sku_id)] = int(sku_id_count[sku_id])
            # {sku_id:count,sku_id:count}
        #     3.5 根据商品的id 查询商品的具体信息 [SKU,SKU,SKu...]
        sku_ids = selected_carts.keys() # 获取字典所有的key 即 sku_id
        sku_list = []
        for sku_id in sku_ids:
            try:
                sku = SKU.objects.get(pk=sku_id) # pk 即 primary key 主键
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': 400, 'errmsg':'获取商品异常'})
            else:
                # 3.6 需要将对象数据转换为字典数据
                sku_list.append({
                    'id': sku.id,
                    'name': sku.name,
                    'count': int(selected_carts.get(sku_id)),
                    'default_image_url': sku.default_image.url,
                    'price': sku.price
                })

        # 运费
        from decimal import Decimal
        # Decimal -- 货币类型
        freight = Decimal('12')

        # 拼接返回的数据结构
        context = {
            'addresses': address_list,
            'skus': sku_list,
            'freight': freight, # 运费
        }

        # 返回响应
        return JsonResponse({'code': 0, 'msg': 'ok', 'context': context})
