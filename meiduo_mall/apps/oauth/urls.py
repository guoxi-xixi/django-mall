from django.urls import path
from apps.oauth.views import *

urlpatterns = {
    path('qq/authorization/', QQLoginURLView.as_view()),
    path('oauth_callback/', OauthQQView.as_view()),
}