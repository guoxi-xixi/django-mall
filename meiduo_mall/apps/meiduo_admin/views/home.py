
"""
日活用户

当天登录的用户的总量
2020-10-30  10:10:10
2020-10-30  15:10:10

2020-10-30  00:00:00
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from apps.users.models import User

class DailyActiveAPIview(APIView):
    """
    日活用户统计
    """
    def get(self, request):
        today = date.today()
        count = User.objects.filter(last_login__gte=today).count()
        return Response({'count': count, 'date': today})


class DailyOrderCountAPIView(APIView):
    """
    日下单用户量统计
    """
    def get(self, request):
        today = date.today()
        count = User.objects.filter(orderinfo__create_time__gte=today).count()
        return Response({'count': count, 'date': today})


"""
1. 获取今天的日期
2. 往前回退30天
3. 遍历查询数据

    例如: 10-01  到 10-2 数据
    3.1 获取区间开始的日期
    3.2 获取区间结束的日期
    3.3 查询
    3.4 把查询的数据放入列表中
"""
from datetime import timedelta

class MonthCountAPIView(APIView):
    """
    月增用户统计
    """
    def get(self, request):
        # 获取当前日期
        today = date.today()
        # 往前回退30天
        before_date = today - timedelta(days=30)
        # 创建空列表保存每天的用户量
        date_list = []

        # 遍历查询数据
        for i in range(30):
            # 获取区间开始日期 -- 循环遍历获取当天日期
            start_date = before_date + timedelta(days=i)
            # 获取区间结束的日期 -- 指定下一天日期
            end_date = start_date + timedelta(days=(i+1))
            # 查询新增用户
            count = User.objects.filter(date_joined__gte=start_date,
                                        date_joined__lt=end_date).count()
            # 查询数据插入列表中
            date_list.append({
                'count': count,
                'date': start_date
            })

        return Response(date_list)


class UserCountAPIView(APIView):
    """
    用户总量统计
    """
    def get(self, request):
        today = date.today()
        count = User.objects.all().count()
        return Response({'count': count, 'date': today})


class DailyUserCountAPIView(APIView):
    """
    日新增用户统计
    """
    def get(self, request):
        today = date.today()
        count = User.objects.filter(date_joined__gte=today).count()
        return Response({'count': count, 'date': today})

