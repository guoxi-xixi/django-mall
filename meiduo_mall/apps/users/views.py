import json

from django.contrib.auth import logout
from django.shortcuts import render

# Create your views here.


"""
需求分析： 根据页面的功能（从上到下，从左到右），哪些功能需要和后端配合完成
如何确定 哪些功能需要和后端进行交互呢？？？
        1.经验
        2.关注类似网址的相似功能

"""

"""
判断用户名是否重复的功能。

前端(了解)：     当用户输入用户名之后，失去焦点， 发送一个axios(ajax)请求

后端（思路）：
    请求:         接收用户名 
    业务逻辑：     
                    根据用户名查询数据库，如果查询结果数量等于0，说明没有注册
                    如果查询结果数量等于1，说明有注册
    响应          JSON 
                {code:0,count:0/1,errmsg:ok}
    
    路由      GET         usernames/<username>/count/        
   步骤：
        1.  接收用户名
        2.  根据用户名查询数据库
        3.  返回响应         
"""
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import re

class UsernameCountView(View):

    def get(self, request, username):
        # 1.接收用户名   一般在路由中用转换器验证
        # if not re.match('[a-zA-Z0-9_-]{5,20}', username):
        #     return JsonResponse({'code': 200, 'errmsg': '用户名不满足要求'})
        # 2.根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        # 3.返回响应
        return JsonResponse({'code':0, 'count': count, 'errmsg': 'ok'})


class MobileCountView(View):

    def get(self, request, mobile):
        # 1.获取手机号
        # 2.手机号格式验证
        # 3.查询数据库
        count = User.objects.filter(mobile=mobile).count()
        # 4.返回响应
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})

"""
我们不相信前端提交的任何数据！！！！

前端：     当用户输入 用户名，密码，确认密码，手机号，是否同意协议之后，会点击注册按钮
            前端会发送axios请求

后端：
    请求：             接收请求（JSON）。获取数据
    业务逻辑：          验证数据。数据入库
    响应：             JSON {'code':0,'errmsg':'ok'}
                     响应码 0 表示成功 400表示失败

    路由：     POST    register/

    步骤：

        1. 接收请求（POST------JSON）
        2. 获取数据
        3. 验证数据
            3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
            3.2 用户名满足规则，用户名不能重复
            3.3 密码满足规则
            3.4 确认密码和密码要一致
            3.5 手机号满足规则，手机号也不能重复
            3.6 需要同意协议
        4. 数据入库
        5. 返回响应
"""

class RegisterView(View):

    def post(self, request):
        # 1.接收请求（POST - -----JSON）
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)
        # 2. 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')
        sms_code = body_dict.get('sms_code')
        # 3. 验证数据
        #     3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数缺失，请确认'})
        #     3.2 用户名满足规则，用户名不能重复
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})
        #     3.3 密码满足规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': 'password格式有误!'})
        #     3.4 确认密码和密码要一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次输入密码不一致'})
        #     3.5 手机号满足规则，手机号也不能重复
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号不满足规则'})
        #     3.6 需要同意协议
        if allow is not True:
            return JsonResponse({'code': 400, 'errmsg': '没有勾选校验规则'})

        # 验证短信验证码
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        redis_sms_code = redis_cli.get(mobile)
        if redis_sms_code is None:
            return JsonResponse({'code': 400, 'errmsg': '验证码已过期'})
        if sms_code != redis_sms_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码错误 '})

        # 4. 数据入库
        # 方案一
        # user = User(username=username, password=password, mobile=mobile)
        # user.save()
        # 方案二
        # User.objects.create(username=username, password=password, mobile=mobile)

        # 以上方案一和二都没有对密码进行加密
        # 密码加密
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 状态保持
        # session信息: request.session['user_id']=user_id

        # Django提供 状态保持方案
        from django.contrib.auth import login
        # request, user
        # 状态保持 -- 登录用户的信息
        login(request, user)

        # 5. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

"""
如果需求是注册成功后即表示用户认证通过，那么此时可以在注册成功后实现状态保持 (注册成功即已经登录)  v
如果需求是注册成功后不表示用户认证通过，那么此时不用在注册成功后实现状态保持 (注册成功，单独登录)

实现状态保持主要有两种方式：
    在客户端存储信息使用Cookie
    在服务器端存储信息使用Session

"""

"""
登录
    
前端：
        当用户把用户名和密码输入完成之后，会点击登录按钮。这个时候前端应该发送一个axios请求
        
后端：
    请求    ：  接收数据，验证数据
    业务逻辑：   验证用户名和密码是否正确，session
    响应    ： 返回JSON数据 0 成功。 400 失败

    POST        /login/
步骤：
    1. 接收数据
    2. 验证数据
    3. 验证用户名和密码是否正确
    4. session
    5. 判断是否记住登录
    6. 返回响应
"""

class LoginView(View):

    def post(self, request):
        # 1.接收数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        # 2. 验证数据
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmgs': '参数不全'})

        # 判断是通过 username 还是 mobile 登录
        # USERNAME_FIELD 我们可以根据 修改 User. USERNAME_FIELD 字段，来影响authenticate 的查询
        # authenticate 就是根据 USERNAME_FIELD 来查询
        if re.match(r'^1[3-9]\d{9}$', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        # 验证 username 和 password 是否合法
            if not re.match(r'^[a-zA-Z_-]{5,20}$', username):
                return JsonResponse({'code': 400, 'errmsg': '用户名不满足校验规则'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '用户名或者密码格式有误!'})
        # 3. 验证用户名和密码是否正确
        # 通过模型根据用户名进行查询
        # User.objects.get(username=username)   # 不推荐

        # 方式二：
        from django.contrib.auth import authenticate
        # authenticate 传递用户名和密码
        # 如果用户名和密码正确，则返回 User信息
        # 如果用户名和密码不正确，则返回 None
        user = authenticate(username=username, password=password)
        if user is not None:
            pass
            # return JsonResponse({'code': 0, 'errmsg': 'ok', 'userInfo': user})
        else:
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码错误'})

        # 4. session
        from django.contrib.auth import login
        login(request, user)
        # 5. 判断是否记住登录
        if remembered:
            # 记住登录-- 默认2周 或者 any ，具体时间 pd定
            request.session.set_expiry(604800)    # 3600*24*7 = 604800
        else:
            # 不记住登录 -- 浏览器关闭 session关闭
            request.session.set_expiry(0)
        # 6. 返回响应
        # return JsonResponse({'code': 0, 'errmsg': 'ok'})
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 设置 cookie 首页展示用户信息
        response.set_cookie('username', username)
        return response


"""
前端：
    当用户点击退出按钮的时候，前端发送一个axios delete请求

后端：
    请求
    业务逻辑        退出
    响应      返回JSON数据
"""

class LogoutView(View):

    # def get(self, request):
    def delete(self, request):
        # 1.删除 session信息
        logout(request)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 2.删除 cookie信息，前端是根据cookie信息来判断用户是否登录的
        response.delete_cookie('username')

        return response
