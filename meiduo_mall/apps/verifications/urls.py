from django.urls import path
from apps.verifications.views import *

urlpatterns = {
    # 图形验证码
    path('image_codes/<uuid:uuid>/', ImageCodeView.as_view()),
    path('sms_codes/<mobile:mobile>/', SmsCodeView.as_view())
}