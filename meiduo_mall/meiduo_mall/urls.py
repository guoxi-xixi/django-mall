"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

#
# from django.http import HttpResponse
# def log(request):
#     # 导入
#     import logging
#     # 创建日志器
#     logger = logging.getLogger('django')
#     # 调用日志器的方法保存日志
#     logger.info('用户登录')
#     logger.warning('redis缓存不足')
#     logger.error('该记录不存在')
#     logger.debug('debug')
#
#
#     return HttpResponse('log')
from utils.converters import *
from django.urls import register_converter

register_converter(UsernameConverter, 'username')
register_converter(MobileConverter, 'mobile')
register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('log/', log),
    path('', include('apps.users.urls')),
    path('', include('apps.verifications.urls')),
]
