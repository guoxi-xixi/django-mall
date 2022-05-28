import json

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


"""
需求：
        点击提交订单，生成订单
前端：
        会发送axiso请求。 POST   携带数据  地址id,支付方式  携带用户的session信息（cookie）

        没有必须要携带  总金额， 商品id和数量 （后端自己都可以获取到）

后端：
    请求：         接收请求，验证数据
    业务逻辑：      数据入库
    响应：         返回响应

    路由：     POST
    步骤：

        1. 接收请求     user,address_id,pay_method
        2. 验证数据
        order_id 主键（自己生成）
        支付状态由支付方式决定
        总数量，总金额，运费
        连接redis
        hash
        set
        根据商品id，查询商品信息 sku.price

        3. 数据入库     生成订单（订单基本信息表和订单商品信息表）
            3.1先保存订单基本信息

            3.2再保存订单商品信息
              连接redis
              获取hash
              获取set     v
              最好重写组织一个数据，这个数据是选中的商品信息 
              根据选中商品的id进行查询
              判断库存是否充足，
              如果充足，则库存减少，销量增加
              如果不充足，下单失败
              保存订单商品信息
        4. 返回响应


        一。接收请求     user,address_id,pay_method
        二。验证数据
        order_id 主键（自己生成）
        支付状态由支付方式决定
        总数量，总金额， = 0
        运费
        三。数据入库     生成订单（订单基本信息表和订单商品信息表）
            1.先保存订单基本信息

            2 再保存订单商品信息
              2.1 连接redis
              2.2 获取hash
              2.3 获取set   
              2.4 遍历选中商品的id，
                最好重写组织一个数据，这个数据是选中的商品信息
                {sku_id:count,sku_id:count}

              2.5 遍历 根据选中商品的id进行查询
              2.6 判断库存是否充足，
              2.7 如果不充足，下单失败
              2.8 如果充足，则库存减少，销量增加
              2.9 累加总数量和总金额
              2.10 保存订单商品信息
          3.更新订单的总金额和总数量
          4.将redis中选中的商品信息移除出去
        四。返回响应
"""
from apps.orders.models import OrderInfo,OrderGoods
from django.db import transaction   # 事务 可使用装饰器 or with


class OrderCommitView(LoginRequiredJSONMixin, View):
    """提交订单"""

    def post(self, request):
        user = request.user
        # 一。接收请求     user,address_id,pay_method
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        # 二。验证数据
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})

        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '参数异常'})

        # if pay_method not in [1,2]:   这么写是没有问题的。
        # 从代码的可读性来说很差。 不知道 1 什么意思 2 什么意思
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': '参数异常'})

        # order_id 主键（自己生成）   年月日时分秒 + 用户id（9位数字）
        from datetime import datetime
        # datetime.strftime()   可以，建议使用django timezone
        # Year month day Hour Minute Second %f 微秒
        from django.utils import timezone
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S%f')+('%09d'%user.id)

        # 支付状态由支付方式决定
        # 代码是对的。可读性差
        # if pay_method == 1: # 货到付款
        #     status=2
        # else:
        #     status=1
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = 2  # 货到付款，修改订单状态为 2
        else:
            status = 1  # 支付宝，修改订单状态为 1

        # 总数量，总金额， = 0
        total_count = 0
        from decimal import Decimal # 货币使用货币类型
        total_amount = Decimal('0') # 初始化为0，后续累加金额

        # 运费
        freight = Decimal('10.00')

        # 事务，要执行都执行，要失败都失败
        with transaction.atomic():
            # 开启事务
            point = transaction.savepoint()

            # 三。数据入库     生成订单（订单基本信息表和订单商品信息表）
            #     1.先保存订单基本信息
            order_info = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            #
            #     2 再保存订单商品信息
            #       2.1 连接redis
            redis_cli = get_redis_connection('carts')
            pipeline = redis_cli.pipeline()
            #       2.2 获取hash
            pipeline.hgetall('carts_%s'%user.id)
            #       2.3 获取set
            pipeline.smembers('selected_%s'%user.id)
            result = pipeline.execute()
            sku_id_counts = result[0]
            sku_selected = result[1]
            #       2.4 遍历选中商品的id，
            carts = {}
            #         最好重写组织一个数据，这个数据是选中的商品信息

            for sku_id in sku_selected:
                carts[int(sku_id)] = int(sku_id_counts[sku_id])
            #         {sku_id:count,sku_id:count}
            #
            #       2.5 遍历 根据选中商品的id进行查询
            for sku_id, count in carts.items():
                try:
                    sku = SKU.objects.get(id=sku_id)
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code': 400, 'errmsg': '获取商品信息失败'})
                else:
                    # 2.6 判断库存是否充足，
                    if sku.stock < count:
                        # 2.7 如果不充足，下单失败
                        transaction.savepoint_rollback(point) # 库存不足，回滚事务
                        return JsonResponse({'code': 400, 'errmsg': '库存不足'})
                    else:
                        # 2.8 如果充足，则库存减少，销量增加
                        sku.stock -= count
                        sku.sales += count
                        sku.save()
                        # 2.9 累加总数量和总金额
                        order_info.total_amount += (sku.price*count)
                        order_info.total_count += count
                        # 2.10 保存订单商品信息
                        OrderGoods.objects.create(
                            order=order_info,
                            sku=sku,
                            count=count,
                            price=sku.price
                        )

            #   3.更新订单的总金额和总数量
            order_info.total_amount += freight  # 添加运费
            order_info.save()
            # 提交点 - 执行事务
            transaction.savepoint_commit(point)

        # 4.将redis中选中的商品信息移除出去    测试，暂缓
        # pipeline.hdel('carts_%s'%user.id, *sku_selected)
        # pipeline.srem('selected_%s'%user.id, *sku_selected)
        # pipeline.execute()
        # 四。返回响应
        return JsonResponse({'code': 0, 'msg': 'ok', 'order_id': order_id})
