from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = {
    # 项目根urls 中配置 根路由可省略meiduo_admin
    # path('meiduo_admin/authorizations/', obtain_jwt_token),
    path('authorizations/', obtain_jwt_token),
}