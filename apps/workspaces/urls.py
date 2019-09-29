from django.urls import path
from rest_framework import routers

from . import apps, apis


app_name = apps.WorkspacesConfig.name

router = routers.DefaultRouter()
router.register(
    "create-workspace",
    apis.CreateWorkspaceApi,
    basename="create-workspace"
)

urlpatterns = [
    path("check/", apis.CheckWorkspaceView.as_view(), name="check"),
]

urlpatterns += router.urls
