import json

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
from django.contrib.auth import logout

class LogoutView(View):

    # def get(self, request):
    def delete(self, request):
        # 1.删除 session信息
        logout(request)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 2.删除 cookie信息，前端是根据cookie信息来判断用户是否登录的
        response.delete_cookie('username')

        return response


"""
LoginRequiredMixin 未登录的用户 会返回 重定向。重定向并不是JSON数据

我们需要是  返回JSON数据
"""
from utils.views import LoginRequiredJSONMixin

class CenterView(LoginRequiredJSONMixin, View):

    def get(self, request):
        # request.user 就是已经登录的用户信息
        # request.user 就是来源于中间件 'django.contrib.auth.middleware.AuthenticationMiddleware',
        # 系统会进行判断 如果是登录用户，则获取登录用户的 模型实例数据
        # 若不是登录用户，则 request.user = AnonymousUser() 匿名用户
        info_data = {
            'username': request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': info_data})


"""
需求：     1.保存邮箱地址  2.发送一封激活邮件  3. 用户激活邮件

前端：
    当用户输入邮箱之后，点击保存。这个时候会发送axios请求。
    
后端：
    请求           接收请求，获取数据
    业务逻辑        保存邮箱地址  发送一封激活邮件
    响应           JSON  code=0
    
    路由          PUT     
    步骤
        1. 接收请求
        2. 获取数据
        3. 保存邮箱地址
        4. 发送一封激活邮件
        5. 返回响应
        

需求（要实现什么功能） --> 思路（ 请求。业务逻辑。响应） --> 步骤  --> 代码实现
1. 设置邮件服务器

    我们设置 163邮箱服务器
    相当于 我们开启了 让163帮助我们发送邮件。同时设置了 一些信息（特别是授权码）

2.  设置邮件发送的配置信息
    #  让django的哪个类来发送邮件
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # 邮件服务器的主机和端口号
    EMAIL_HOST = 'smtp.163.com'
    EMAIL_PORT = 25
    
    # 使用我的 163服务器 和 授权码
    #发送邮件的邮箱
    EMAIL_HOST_USER = 'qi_rui_hua@163.com'
    #在邮箱中设置的客户端授权密码
    EMAIL_HOST_PASSWORD = '123456abc'
    
3. 调用  send_mail 方法
"""

class EmailView(View):

    def put(self, request):
        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取数据
        email = data.get('email')
        # 验证数据
        if email is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400, 'errmsg': '参数异常'})
        # 3. 保存邮箱地址
        user = request.user
        user.email = email
        user.save()
        # 4. 发送一封激活邮件
        """
        from django.core.mail import send_mail
        # subject,          邮件主题
        subject = '美多商城激活邮件'
        # message,          邮件内容
        message = '激活 <a herf="http://meiduo.site:8080.site">激活</a>'
        # from_email,       发件人
        from_email = '美多商城<qi_rui_hua@163.com>'
        # recipient_list,   收件人列表
        # recipient_list = ['qwedsa55630666@163.com']
        recipient_list = [email]
        # html_message=None html格式的邮件内容

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list
        )
        """
        # 异步实现发送邮件

        # subject,          邮件主题
        subject = '美多商城激活邮件'
        # message,          邮件内容
        message = '激活 <a herf="http://meiduo.site:8080.site">激活</a>'
        # from_email,       发件人
        from_email = '美多商城<qi_rui_hua@163.com>'
        # recipient_list,   收件人列表
        recipient_list = [user.email]
        # html_message=None html格式的邮件内容

        # 生成加密的token
        from apps.users.utils import generic_mail_verify_token
        token = generic_mail_verify_token(request.user.id)
        # 生成 verify_url
        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s"%token
        # 组装html_message
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(
            subject=subject,
            message="",
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )


        # 5. 返回响应
        return JsonResponse({'code': 0, 'msg': 'ok'})


"""
需求（知道我们要干什么？？？）：
    激活用户的邮件
前端(用户干了什么，传递了什么参数)：
        用户会点击那个激活连接。那个激活连接携带了token
后端：
    请求：         接收请求，获取参数，验证参数
    业务逻辑：       user_id, 根据用户id查询数据，修改数据
    响应：         返回响应JSON
    
    路由：         PUT     emails/verification/  说明： token并没有在body里
    步骤：
        
        1. 接收请求
        2. 获取参数
        3. 验证参数
        4. 获取user_id
        5. 根据用户id查询数据
        6. 修改数据
        7. 返回响应JSON
"""

class EmailVerifyView(View):

    def put(self, request):
        # 1. 接收请求
        # 2. 获取参数
        token = request.GET.get('token')
        # 3. 验证参数
        if token is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})

        # 4. 获取user_id
        from apps.users.utils import check_mail_verify_token
        user_id = check_mail_verify_token(token)
        if user_id is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})

        # 5. 根据用户id查询数据
        # user = request.user   # 不能使用当前登录用户绑定，而应该用返回user_id的用户绑定
        user = User.objects.get(id=user_id)
        # 6. 修改数据
        user.email_active = True
        user.save()
        # 7. 返回响应JSON
        return JsonResponse({'code': 0, 'msg': 'ok'})