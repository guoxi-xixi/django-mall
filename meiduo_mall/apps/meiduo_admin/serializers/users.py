from rest_framework import serializers
from apps.users.models import User

class UserModelSerializer(serializers.ModelSerializer):

    # password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }
    # 重写create方法对password进行加密
    def create(self, validated_data):
        # user = User.objects.create(**validated_data)
        # user.set_password(validated_data.get('password'))
        # user.save()
        # return user

        return User.objects.create_user(**validated_data)
