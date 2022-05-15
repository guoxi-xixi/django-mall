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
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        # 表名
        db_table = 'tb_user'
        verbose_name = '用户管理'   # admin管理界面中显示中文
        # erbose_name表示单数形式的显示，verbose_name_plural表示复数形式的显示
        verbose_name_plural = verbose_name


from utils.models import BaseModel

class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    # Address模型类中的外键指向areas/models里面的Area 。指明外键时，可以使用应用名.模型类名来定义

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
        # ordering表示在进行Address查询时，默认使用的排序方式
        # ordering = ['-update_time']: 根据更新的时间倒叙