from django.urls import path
from apps.orders.views import *

urlpatterns = {
    path('orders/settlement/', OrderSettlementView.as_view()),
}