"""
需求：
        登录的时候，将cookie数据合并到redis中
前端：

后端：
    请求：         在登录的时候，获取cookie数据
    业务逻辑：       合并到redis中
    响应：

抽象的问题 具体化（举个例子）

1. 读取cookie数据
2. 初始化一个字典 用于保存 sku_id:count
    初始化一个列表 用于保存选中的商品id
    初始化一个列表 用于保存未选中的商品id
3. 遍历cookie数据
4. 将字典数据，列表数据分别添加到redis中
5. 删除cookie数据

#######################################

redis       hash
                    1:10
                    3:10
            set
                    1

cookie
        {
            1: {count:666,selected:True},
            2: {count:999,selected:True},
            5: {count:999,selected:False},
        }

hash
1:666       1
2:999       1

 ① 当cookie数据和redis数据 有相同的商品id的时候，数量怎么办？？？ 我们以cookie为主
 ② 当cookie数据有，redis数据没有的， 全部以 cookie为主
 ③ 当redis中有的数据，cookie没有。  不动
"""
import base64
import pickle
from django_redis import get_redis_connection

def merge_cookie_to_redis(request, response):
    """登录用户合并cookies商品到redis"""
    user = request.user
    # 1. 读取cookie数据
    carts_cookies = request.COOKIES.get('carts')
    if carts_cookies is not None:
        carts = pickle.loads(base64.b64decode(carts_cookies))
        # 2. 初始化一个字典 用于保存 sku_id:count  {sku_id:count,sku_id:count,....}
        sku_id_dict = {}
        #     初始化一个列表 用于保存选中的商品id
        selected_ids = []
        #     初始化一个列表 用于保存未选中的商品id
        unselected_ids = []
        # 3. 遍历cookie数据
        """
        {
            1: {count:666,selected:True},
            2: {count:999,selected:True},
            5: {count:999,selected:False},
        }
        """
        for sku_id, sku_count_selected_dict in carts.items():
            # 1: {count:666,selected:True},
            # 字典数据
            sku_id_dict[sku_id] = sku_count_selected_dict['count']
            if sku_count_selected_dict['selected']: # true，添加到选中列表
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)
        # 4. 将字典数据，列表数据分别添加到redis中
        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()

        # 购物车商品&数量： carts_user.id:{sku_id:count,sku_id:count,....}
        # 按照pd需求实现，此处按照cookies覆盖redis数据实现
        pipeline.hmset('carts_%s'%user.id, sku_id_dict)

        # 选中商品的 sku_id: selected_id [1,3,2] -> selected_user.id:[1,2,3]
        if len(selected_ids) > 0:
            # *selected_ids  对列表数据进行解包
            pipeline.sadd('selected_%s'%user.id, *selected_ids)

        # 未选中商品的 sku_id: unselected_id [1,3,2] -> selected_user.id:[]
        if len(unselected_ids) > 0:
            pipeline.srem('selected_%s'%user.id, *unselected_ids)

        pipeline.execute()

        # 5. 删除cookie数据
        response.delete_cookie('carts')

        return response
