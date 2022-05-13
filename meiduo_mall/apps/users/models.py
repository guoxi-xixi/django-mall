from django.db import models

# Create your models here.

# 1.自己定义模型
# 需要自己实现密码加密和登录密码验证
# class User(models.Model):
#     name = models.CharField(max_length=20, unique=True)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=11,unique=True)

# 2.django自带 用户模型，继承重写
# django自带 用户模型，有密码加密和密码验证
# from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    """ User模型 - User表 """
    # 新值django自带user模型没有mobile字段
    mobile = models.CharField(max_length=11,unique=True)
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        # 表名
        db_table = 'tb_user'
        verbose_name = '用户管理'   # admin管理界面中显示中文
        # erbose_name表示单数形式的显示，verbose_name_plural表示复数形式的显示
        verbose_name_plural = verbose_name