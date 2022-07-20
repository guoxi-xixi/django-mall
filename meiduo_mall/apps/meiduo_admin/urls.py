from django.urls import path
# from rest_framework_jwt.views import obtain_jwt_token
from apps.meiduo_admin.user import meiduo_token
from apps.meiduo_admin.views import home, users, images, skus, permission, orders

urlpatterns = [
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
    # 用户管理 - user
    path('users/', users.UserAPIView.as_view()),
    # 图片管理 - skuid
    path('skus/simple/', images.ImageSKUListAPIView.as_view()),
    # SKU - 三级分类
    path('skus/categories/', skus.GoodsCategoryListAPIView.as_view()),
    # SKU - SPU信息展示
    path('goods/simple/', skus.SPUListAPIView.as_view()),
    # SKU - specs
    path('goods/<spu_id>/specs/', skus.SPUSpecAPIView.as_view()),
    # ContentType
    path('permission/content_types/', permission.ContentTypeListAPIView.as_view()),
    # permission/simple/ - 组管理权限列表
    path('permission/simple/', permission.GroupPermissionListAPIView.as_view()),
    # permission/groups/simple/ - 管理员管理 组管理列表
    path('permission/groups/simple/', permission.SimpleGroupListAPIView.as_view()),
    # # orders - 订单管理
    # path('orders/', orders.OrderListAPIView.as_view()),
    # path('orders/<pk>/', orders.OrderGoodsRetrieveUpdateAPIView.as_view()),
    # order 状态的修改
    # path('orders/<order_id>/status/', orders.OrderStatusRetrieveUpdateAPIView.as_view()),
]

# 视图集 viewset 路由
from rest_framework.routers import DefaultRouter
# 创建路由实例
router = DefaultRouter()
# 注册路由
# 注册图片管理路由
router.register('skus/images', images.ImageModelViewSet, basename='images')

# 注册sku路由
router.register('skus', skus.SKUModelViewSet, basename='skus')

# 注册 permission 路由
router.register('permission/perms', permission.PermissionModelViewSet, basename='perms')

# 注册 group 路由
router.register('permission/groups', permission.GroupModelViewSet, basename='groups')

# 注册 admins 路由
router.register('permission/admins', permission.AdminUserModelViewSet, basename='admins')
# 注册 orders 路由
router.register('orders', orders.OrderModelViewSet, basename='orders')

# 将router生成的路由追加到urlpatterns中
urlpatterns += router.urls

print(urlpatterns)
