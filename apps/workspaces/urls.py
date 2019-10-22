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
    path("workspace", apis.WorkspaceApi.as_view(), name="workspace-info"),
    path("workspaces/check/", apis.CheckWorkspaceView.as_view(), name="check"),
    path("invitations/sends", apis.SendInvitationApi.as_view(), name="send-invitation"),
    path("invitations/join", apis.JoinInvitationApi.as_view(), name="join-invitation"),
]

urlpatterns += router.urls
