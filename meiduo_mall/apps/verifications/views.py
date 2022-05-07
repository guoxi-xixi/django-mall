from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

"""
前端
    拼接 url，传给 img , img发起请求
    url=http://ip:port/image_codes/uuid/
    
后端
    请求      接收路由中的 uuid
    业务逻辑    生成图片的验证码和二进制图片，保存在redis中
    响应      返回图片二进制
    步骤：     
            # 1.接收路由中的 uuid
            # 2.生成图片验证码和图片二进制
            # 3.通过redis 保存图片验证码和图片二进制
            # 4.返回图片二进制
"""

class ImageCodeView(View):

    def get(self, request, uuid):
        # 1.接收路由中的 uuid
        # 2.生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text 是图片验证码的内容 例如:xyzz
        # image 是图片二进制
        text,image = captcha.generate_captcha()
        # 3.通过redis 保存图片验证码和图片二进制
        # 3.1 进行redis链接
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 指令操作
        # name, time, value
        redis_cli.setex(uuid, 60, text)
        # 4.返回图片二进制
        # 图片是二进制，不能使用JSON接收
        # conent_type = 响应体数据类型
        # content_type 语法： 大类/小类
        # content_type (MIME类型)
        # 图片：image/jepg, image/png, image/gig
        return HttpResponse(image,content_type='image/jpeg')