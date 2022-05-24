from django.urls import path
from apps.carts.views import *

urlpatterns = {
    path('carts/', CartsView.as_view()),
}