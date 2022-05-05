from django.urls import path
from apps.users.views import *

urlpatterns = {
    # 判断用户是否重复
    path('usernames/<username:username>/count/', UsernameCountView.as_view())
}