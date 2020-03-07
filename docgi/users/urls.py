from django.urls import path
from rest_framework import routers

from . import apis, apps

app_name = apps.UsersConfig.name

router = routers.DefaultRouter()

urlpatterns = [
    path("users/me/", apis.UserMeApi.as_view(), name="user-me"),
    path("users/set-password/", apis.UserSetPasswordApi.as_view(), name="user-set-password"),
    path("users/me/change-password/", apis.UserChangePasswordApi.as_view(), name="user-change-password")
]

urlpatterns += router.urls
