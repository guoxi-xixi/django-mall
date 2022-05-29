from django.urls import path
from .views import *

urlpatterns = {
    path('payment/status/', PaymentStatusView.as_view()),

    path('payment/<order_id>/', PayUrlView.as_view()),
    # 路由相同会报错，找不到，放到顶部 - 实际开发不能定义相同
    # path('payment/status/', PaymentStatusView.as_view()),
}