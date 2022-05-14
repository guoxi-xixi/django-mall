from itsdangerous import TimedJSONWebSignatureSerializer as Serizalizer
from meiduo_mall import settings
import logging

logger = logging.getLogger('django')

def generic_mail_verify_token(user_id):
    """生成邮箱验证链接"""
    # 1.创建实例
    s = Serizalizer(secret_key=settings.SECRET_KEY, expires_in=3600*24)
    # 2.加密
    result = s.dumps({'user_id':user_id})
    # 3.返回数据
    return result.decode()

def check_mail_verify_token(token):
    # 1.创建实例
    s = Serizalizer(secret_key=settings.SECRET_KEY, expires_in=3600*24)
    # 2.解密
    try:
        result = s.loads(token)
    except Exception as e:
        logger.error(e)
        return None
    # 3.返回数据
    # result = {'user_id':user_id}
    return result.get('user_id')