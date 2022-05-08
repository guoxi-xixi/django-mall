from django.http import HttpResponse, JsonResponse
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


"""
1.注册
我们提供免费开发测试，【免费开发测试前，请先 注册 成为平台用户】。

2.绑定测试号
免费开发测试需要在"控制台—管理—号码管理—测试号码"绑定 测试号码 。

3.开发测试
开发测试过程请参考 短信业务接口 及 Demo示例 / sdk参考（新版）示例。Java环境安装请参考"新版sdk"。

4.免费开发测试注意事项
    4.1.免费开发测试需要使用到"控制台首页"，开发者主账户相关信息，如主账号、应用ID等。
    
    4.2.免费开发测试使用的模板ID为1，具体内容：【云通讯】您的验证码是{1}，请于{2}分钟内正确输入。其中{1}和{2}为短信模板参数。
    
    4.3.测试成功后，即可申请短信模板并 正式使用 。
"""

"""
前端：
    当用户输入完手机号，图片验证码之后，前端发送一个axios请求
    sms_codes/18310820644/?image_code=knse&image_code_id=b7ef98bb-161b-437a-9af7-f434bb050643
    
后端
    请求：     接收请求，获取请求参数(路由包含手机号，用户的图片验证码和UUID)
    业务逻辑：   验证参数，验证图片验证码，生成短信验证码，保存短线验证码，发送短信验证码
    响应：     返回响应    {'code': 0, '': 'ok'}
    
    路由      GET sms_codes/18310820644/?image_code=knse&image_code_id=b7ef98bb-161b-437a-9af7-f434bb050643
    
    步骤：
        1.获取请求参数
        2.验证参数
        3.验证图片验证码
        4.生成短线验证码
        5.保存短信验证码
        6.发送短信验证码
        7.返回响应
        
需求 --》 思路 --》 步骤 --》 代码

debug 模式 就是调试模式
debug + 断点配合使用 这个我们看到程序执行的过程

添加断点 在函数体的第一行添加！！！！！
"""

class SmsCodeView(View):

    def get(self, request, mobile):
        # 1.获取请求参数
        img_code = request.GET.get('image_code')    # srt 'EBOC'
        uuid = request.GET.get('image_code_id')
        # 2.验证参数
        if not all([mobile, img_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 3.验证图片验证码
        # 3.1 连接redis
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 获取redis数据
        redis_image_code = redis_cli.get(uuid)  # b'EBOC'
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})
        # 3.3 对比
        # if redis_image_code != img_code:    # redis_image_code数据类型是byte，img_code是str
        if redis_image_code.decode().lower() != img_code.lower():    # 都把数据类型转为str，小写
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})
        # 获取短信发送flag
        sms_send_flag = redis_cli.get('sms_send_flag_%s'%mobile)
        if sms_send_flag is not None:
            return JsonResponse({'code': 400, 'errmsg': '请不要频繁发送短信'})
        # 4.生成短线验证码
        from random import randint
        sms_code = '%06d'%randint(0,999999)
        """
        频繁调用redis链接，性能较差
        
        # 5.保存短信验证码
        redis_cli.setex(mobile, 180, sms_code)
        # 6.发送短信验证码
        from libs.yuntongxun.sms import CCP
        CCP().send_template_sms(mobile, [sms_code, 3], 1)
        # 保存短信发送flag
        redis_cli.setex('sms_send_flag_%s'%mobile, 60, 1)
        """
        # 使用 pipeline 降低 redis 链接请求，降低tcp链接次数
        # 创建redis管道
        pipeline = redis_cli.pipeline()
        # 5.保存短信验证码 -- redis请求添加到请求队列
        pipeline.setex(mobile, 180, sms_code)
        # 保存短信发送flag -- redis请求添加到请求队列
        pipeline.setex('sms_send_flag_%s' % mobile, 60, 1)
        # 执行pipeline 请求
        pipeline.execute()

        # 6.发送短信验证码
        from libs.yuntongxun.sms import CCP
        CCP().send_template_sms(mobile, [sms_code, 3], 1)

        # 7.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})