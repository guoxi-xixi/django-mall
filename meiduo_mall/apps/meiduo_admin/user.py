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


from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from rest_framework import serializers

from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class MeiduoTokenSerializer(JSONWebTokenSerializer):

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                ###############################
                # 验证只有 is_staff:True的用户可以登录后台管理系统
                if not user.is_staff:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)
                ###############################

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


######################## 重写JWT自定义序列化器 ##############################
from rest_framework_jwt.views import JSONWebTokenAPIView
class MeiduoObtainJSONWebToken(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = MeiduoTokenSerializer

meiduo_token = MeiduoObtainJSONWebToken.as_view()