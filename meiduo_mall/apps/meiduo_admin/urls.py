from django.urls import path
# from rest_framework_jwt.views import obtain_jwt_token
from apps.meiduo_admin.user import meiduo_token
from apps.meiduo_admin.views import home, users

urlpatterns = {
    # 项目根urls 中配置 根路由可省略meiduo_admin
    # path('meiduo_admin/authorizations/', obtain_jwt_token),
    # path('authorizations/', obtain_jwt_token),    # 系统默认视图
    path('authorizations/', meiduo_token),  # 重写后 认证用户的视图

    # 日下单用户统计
    path('statistical/day_active/', home.DailyActiveAPIview.as_view()),
    # 日下单用户统计
    path('statistical/day_orders/', home.DailyOrderCountAPIView.as_view()),
    # 月新增用户
    path('statistical/month_increment/', home.MonthCountAPIView.as_view()),
    # 用户统计
    path('statistical/total_count/', home.UserCountAPIView.as_view()),
    # 日新增用户统计
    path('statistical/day_increment/', home.DailyUserCountAPIView.as_view()),
    # 用户 - user
    path('users/', users.UserAPIView.as_view()),
}
