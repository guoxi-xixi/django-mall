from django.shortcuts import render

# Create your views here.
from django.views import View

"""
需求：
    获取省份信息
前端：
    当页面加载的时候，会发送axios请求，来获取 省份信息
后端：
    请求：         不需要请求参数
    业务逻辑：       查询省份信息
    响应：         JSON

    路由：         areas/
    步骤：
        1.查询省份信息
        2.将对象转换为字典数据
        3.返回响应
"""
from apps.areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache

class AreasView(View):
    
    def get(self, request):
        # 1.查询省份信息
        # 优先从缓存中查询
        provinces_list = cache.get('provinces')
        # 缓存中数据为空，从数据库中查询，并缓存数据
        if provinces_list is None:
            provinces = Area.objects.filter(parent=None)
            # <QuerySet [<Area: 北京市>, <Area: 天津市>, <Area: 河北省>, <Area: 山西省>, <Area: 内蒙古自治区>, <Area: 辽宁省>, <Area: 吉林省>, <Area: 黑龙江省>, <Area: 上海市>, <Area: 江苏省>, <Area: 浙江省>, <Area: 安徽省>, <Area: 福建省>, <Area: 江西省>, <Area: 山东省>, <Area: 河南省>, <Area: 湖北省>, <Area: 湖南省>, <Area: 广东省>, <Area: 广西壮族自治区>, '...(remaining elements truncated)...']>
            # 2.将对象转换为字典数据
            provinces_list = []
            for province in provinces:
                provinces_list.append({
                    'id': province.id,
                    'name': province.name
                })
            # 保存缓存数据
            # cache.set(key,value,expire)
            cache.set('provinces', provinces_list, 24*3600)
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': provinces_list})

"""
需求：
    获取市、区县信息
前端：
    当页面修改省、市的时候，会发送axios请求，来获取 下一级的信息
后端：
    请求：         要传递省份id、市的id
    业务逻辑：       根据id查询信息，将查询结果集转换为字典列表
    响应：         JSON

    路由：         areas/id/
    步骤：
        1.获取省份id、市的id,查询信息
        2.将对象转换为字典数据
        3.返回响应
"""

class SubAreasView(View):

    def get(self, request, id):
        # 1.获取省份id、市的id,查询信息

        # 优先从缓存中获取
        sub_data = cache.get('city%s'%id)
        if sub_data is None:
            # 获取 目标区域（市/区）的 上一级 区域（省/市）
            # Area.objects.filter(parent_id=id)
            # Area.objects.filter(parent=id)
            parent_model = Area.objects.get(id=id)
            # 获取 目标区域（市/区）
            # related_name 关联模型的名字 设置为了subs，等同于默认的 area_set
            sub_model = parent_model.subs.all()
            # <QuerySet [<Area: 太原市>, <Area: 大同市>, <Area: 阳泉市>, <Area: 长治市>, <Area: 晋城市>, <Area: 朔州市>, <Area: 晋中市>, <Area: 运城市>, <Area: 忻州市>, <Area: 临汾市>, <Area: 吕梁市>]>
            # <QuerySet [<Area: 离石区>, <Area: 文水县>, <Area: 交城县>, <Area: 兴县>, <Area: 临县>, <Area: 柳林县>, <Area: 石楼县>, <Area: 岚县>, <Area: 方山县>, <Area: 中阳县>, <Area: 交口县>, <Area: 孝义市>, <Area: 汾阳市>]>

            # 2.将对象转换为字典数据
            sub_list = []
            for sub_model_item in sub_model:
                sub_list.append({
                    'id': sub_model_item.id,
                    'name': sub_model_item.name
                })
            # 组装数据
            sub_data = {
                'id': parent_model.id,  # 上级区域（省/市）id
                'name': parent_model.name,  # 上级区域（省/市）name
                'subs': sub_list    # 目标区域（市/区）
            }
            # 缓存数据，注意 市/区的key是动态变化的
            cache.set('city%s'%parent_model.id, sub_data, 24*3600)
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': sub_data})