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
