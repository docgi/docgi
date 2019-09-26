from django.urls import path
from rest_framework import routers

from . import apps, apis


app_name = apps.WorkspacesConfig.name


urlpatterns = [
    path("check/", apis.CheckWorkspaceView.as_view(), name="check")
]
