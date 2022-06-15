"""
用户管理

    用户展示    --  获取用户信息,实现分页和搜索功能
        1. 先实现用户查询
            1.1 查询所有用户
            1.2 将对象列表转换为 满足需求的字典列表 (序列化器)
            1.3 返回响应
        2. 最后实现分页
        3. 再实现搜索功能
            es - elasticsearch
            模糊查询

            3.1 获取 keyword
            3.2 根据keywork进行 模糊查询

    新增用户    --  增加一个测试用户

"""
from rest_framework.generics import ListCreateAPIView
from apps.meiduo_admin.serializers.users import UserModelSerializer
from apps.users.models import User

# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from collections import OrderedDict
#
# class PageNum(PageNumberPagination):
#     # 1.开启分页
#     page_size = 5
#
#     # 2.设置每页记录多少条记录
#         # 2.1 开启 每页多少条记录 可以通过传递的参数传递
#         # 2.2 pagesize=xxx 每页多少条记录的 key
#     page_size_query_param = 'pagesize'
#     #
#     # # 一页最多记录
#     max_page_size = 5
#
#     def get_paginated_response(self, data):
#         # self.page.paginator.per_page    # 动态
#         # self.page_size  # 固定
#
#         return Response(
#             OrderedDict([
#                 ('count', self.page.paginator.count),       # 总共多少条记录
#                 ('lists', data),                             # 结果列表
#                 ('page', self.page.number),                 # 第几页
#                 ('pages', self.page.paginator.num_pages),   # 总共几页
#                 ('pagesize', self.page.paginator.per_page)  # 一页多少记录
#             ])
#         )

from apps.meiduo_admin.utils import PageNum

class UserAPIView(ListCreateAPIView):

    # queryset = User.objects.all()
    # 设置属性 queryset 只能设置一个查询结果集
    # 设置方法  def get_queryset(self): 可以根据  不同的业务逻辑返回不同的查询结果集
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return User.objects.filter(username__contains=keyword)

        return User.objects.all()

    serializer_class = UserModelSerializer

    pagination_class = PageNum