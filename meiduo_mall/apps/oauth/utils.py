from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall import settings
import logging

logger = logging.getLogger('django')

# 加密
def generic_openid(openid, expire_time):

    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=expire_time)
    access_token = s.dumps({'openid': openid})
    # 将bytes类型数据转化为str
    return access_token.decode()

# 解密
def check_access_token(token, expire_time):

    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=expire_time)
    try:
        result = s.loads(token)
    except Exception as e:
        logger.info('check_access_token error%s' %e)
    else:
        return result.get('openid')