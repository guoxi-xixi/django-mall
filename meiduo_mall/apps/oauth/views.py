import json
import re

import django_redis
from django.shortcuts import render

# Create your views here.

"""
第三方登录的步骤：
1. QQ互联开发平台申请成为开发者（可以不用做）
2. QQ互联创建应用（可以不用做）
3. 按照文档开发（看文档的）

3.1 准备工作                        -----------------------------------准备好了

    # QQ登录参数
    # 我们申请的 客户端id
    QQ_CLIENT_ID = '101474184'          appid
    # 我们申请的 客户端秘钥
    QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'   appkey
    # 我们申请时添加的: 登录成功后回调的路径
    QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

3.2 放置 QQ登录的图标（目的： 让我们点击QQ图标来实现第三方登录）  ------------- 前端做好了

3.3 根据oauth2.0 来获取code 和 token                      ---------------我们要做的
    对于应用而言，需要进行两步：
    1. 获取Authorization Code；    表面是一个链接，实质是需要用户同意，然后获取code

    2. 通过Authorization Code获取Access Token

3.4 通过token换取 openid                                ----------------我们要做的
    openid是此网站上唯一对应用户身份的标识，网站可将此ID进行存储便于用户下次登录时辨识其身份，
    或将其与用户在网站上的原有账号进行绑定。

把openid 和 用户信息 进行一一对应的绑定


生成用户绑定链接 ----------》获取code   ------------》获取token ------------》获取openid --------》保存openid

"""

"""
生成用户绑定链接

前端： 当用户点击QQ登录图标的时候，前端应该发送一个axios(Ajax)请求

后端：
    请求
    业务逻辑        调用QQLoginTool 生成跳转链接
    响应            返回跳转链接 {"code":0,"qq_login_url":"http://xxx"}
    路由          GET   qq/authorization/
    步骤      
            1. 生成 QQLoginTool 实例对象
            2. 调用对象的方法生成跳转链接
            3. 返回响应

404 路由不匹配
405 方法不被允许（你没有实现请求对应的方法）
"""
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
from django.http import JsonResponse

class QQLoginURLView(View):

    def get(self, request):
        # 1.生成QQLoginTool实例对象
            # client_id=None,               appid
            # client_secret=None,           appsecret
            # redirect_uri=None,            用户同意登录之后，跳转的页面
            # state=None                    不知道什么意思，随便写。等出了问题再分析问题
        # 初始化OAuthQQ对象
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='xxxx'
        )
        # 2. 调用对象的方法生成跳转链接  获取QQ登录扫码页面，扫码后得到Authorization Code
        qq_login_url = qq.get_qq_url()
        # 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101474184&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8080%2Foauth_callback.html&state=xxxx'
        # 3. 返回响应
        return JsonResponse({'code': 0, 'msg': 'ok', 'login_url': qq_login_url})


"""
需求： 获取code，通过code换取token，再通过token换取openid

前端：
    应该获取 用户同意登录的code。把这个code发送给后端
后端：
    请求          获取code
    业务逻辑       通过code换取token，再通过token换取openid
                根据openid进行判断
                如果没有绑定过，则需要绑定
                如果绑定过，则直接登录
    响应          
    路由          GET         oauth_callback/?code=xxxxx
    步骤
        1. 获取code
        2. 通过code换取token
        3. 再通过token换取openid
        4. 根据openid进行判断
        5. 如果没有绑定过，则需要绑定
        6. 如果绑定过，则直接登录
"""
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
from apps.users.models import User

class OauthQQView(View):

    def get(self, request):
        # 1. 获取code
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        # 2. 通过code换取token
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='xxxx'
        )
        token = qq.get_access_token(code)
        # 3. 再通过token换取openid
        openid = qq.get_open_id(token)
        # 4. 根据openid进行判断
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        # except Exception as e:
        except OAuthQQUser.DoesNotExist:
            # 5. 如果没有绑定过，则需要绑定
            """
            封装的思想

                所谓的封装的思想其实就是把 一些实现了特定功能的代码 封装成一个函数（方法）

            封装的目的

                解耦   --- 当需求发生改变的时候，对代码的修改影响比较小

            封装的步骤
                1.把要封装的代码 定义到一个函数（方法）中
                2.优化封装的代码
                3.验证封装的代码
            """
            # 对返回给前端对 openid 加密
            from apps.oauth.utils import generic_openid
            access_token = generic_openid(openid, 3600)

            response = JsonResponse({'code': 400, 'errmsg': '未绑定', 'access_token': access_token})
            return response
        else:
            # 6. 如果绑定过，则直接登录
            # 6.1 设置session
            login(request, qquser.user)
            # 6.2 设置cookie
            response = JsonResponse({'code': 0, 'msg': 'ok'})
            response.set_cookie('username', qquser.user.username)

            # 合并未登录购物车商品
            from apps.carts.utils import merge_cookie_to_redis
            response = merge_cookie_to_redis(request, response)

            return response

    def post(self, request):
        """注册/绑定用户"""
        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取请求参数  openid
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')
        # 验证接收的数据
        if not all([mobile, password, sms_code, access_token]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的手机号'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '请输入8-20位的密码'})
        # 校验短信验证码
        redis_cli = django_redis.get_redis_connection('code')
        sms_code_server = redis_cli.get(mobile)
        if sms_code_server is None:
            return JsonResponse({'code': 400, 'errmsg': '验证码已过期'})
        if sms_code.lower() != sms_code_server.decode().lower():     # redis_image_code数据类型是byte，img_code是str
            return JsonResponse({'code': 400, 'errmsg': '输入验证码有误'})
        # 添加对 access-token 解密
        from apps.oauth.utils import check_access_token
        openid = check_access_token(access_token, 3600)
        if openid is None:
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        # 3. 根据手机号进行用户信息的查询
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号不存在
            # 5. 查询到用户手机号没有注册。我们就创建一个user信息。然后再绑定
            user = User.objects.create_user(username=mobile, mobile=mobile,password=password)
        else:
            # 手机号存在
            # 4. 查询到用户手机号已经注册了。判断密码是否正确。密码正确就可以直接保存（绑定） 用户和openid信息
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '账号或密码有误'})
        OAuthQQUser.objects.create(user=user, openid=openid)

        # 6. 完成状态保持
        login(request, user)
        # 7. 返回响应
        response = JsonResponse({'code': 0, 'msg': 'ok'})
        response.set_cookie('username', user.username)

        # 合并未登录购物车商品
        from apps.carts.utils import merge_cookie_to_redis
        response = merge_cookie_to_redis(request, response)

        return response

"""
需求： 绑定账号信息
    
    QQ(openid) 和 美多的账号信息

前端：
        当用户输入 手机号，密码，短信验证码之后就发送axios请求。请求需要携带 mobile,password,sms_code,access_token(openid)
后端：
    
    请求：         接收请求，获取请求参数
    业务逻辑：       绑定，完成状态保持
    响应：         返回code=0 跳转到首页
    路由：          POST   oauth_callback/
    步骤：
        
            1. 接收请求
            2. 获取请求参数  openid
            3. 根据手机号进行用户信息的查询
            4. 查询到用户手机号已经注册了。判断密码是否正确。密码正确就可以直接保存（绑定） 用户和openid信息
            5. 查询到用户手机号没有注册。我们就创建一个user信息。然后再绑定
            6. 完成状态保持
            7. 返回响应
"""

##########itsdangerous的基本使用##############################################
# itsdangerous就是为了数据加密

# 加密
"""
1.导入 itsdangerous类
2.创建实例对象
3.加密数据
"""
# 1.导入 itsdangerous类
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# TimedSerializer 这个类 不仅可以对数据进行加密，还是可以对数据设置一个时效
# 2.创建实例对象
# sercret_key,     密钥
# max_age          数据过期时间（s）
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

# 3.加密数据
token = s.dumps({'openid':'1234567890'})
# b'eyJhbGciOiJIUzUxMiIsImlhdCI6MTY1MjM3NTM0MCwiZXhwIjoxNjUyMzc4OTQwfQ.eyJvcGVuaWQiOiIxMjM0NTY3ODkwIn0.vA0QAWkxUTPtgPGO8CRQJ1mXeGETgW7sNEICpgkf5iawZglPtuybknMrknzRXQ74I7ensjEsG7wjHZ-cTqqU5Q'

#############################
# 解密数据
# 1. 导入 itsdangerous 类
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 2. 创建类对实例对象
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
# 3. 解密数据
s.loads(token)
# {'openid': '1234567890'}