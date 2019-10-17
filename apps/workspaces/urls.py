from django.urls import path, re_path
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
    path("", apis.WorkspaceApi.as_view(), name="workspace-info"),
    path("check/", apis.CheckWorkspaceView.as_view(), name="check"),
    path("send-invitations/", apis.SendInvitationApi.as_view(), name="send-invitation"),
]

urlpatterns += router.urls
