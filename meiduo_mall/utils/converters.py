from django.urls import converters

class UsernameConverter:

    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self, value):
        return value


class MobileConverter():

    regex = '1[345789]\d{9}'

    def to_python(self, value):
        return value


class UUIDConverter:
    """自定义路由转换器去匹配手机号"""
    # 定义UUID的正则表达式
    regex = '[\w-]+'

    def to_python(self, value):
        # to_python：将匹配结果传递到视图内部时使用
        return str(value)