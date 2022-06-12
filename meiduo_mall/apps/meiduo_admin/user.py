# 当系统的功能 不能满足我们需求的时候就要重写

def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义JWT认证成功返回数据
    """
    return {
        'token': token,
        # JWT 默认
        # 'user': UserSerializer(user, context={'request': request}).data
        'username': user.username,
        'id': user.id
    }
