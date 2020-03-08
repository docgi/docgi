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
router.register(
    r"workspace/members",
    apis.WorkspaceMemberAPI,
    basename="workspace-members"
)

urlpatterns = [
    re_path(r"workspace/$", apis.WorkspaceApi.as_view(), name="workspace-info"),
    re_path(r"stats-workspaces/$", apis.StatsWorkspaceAPI.as_view(), name="stats-workspaces"),
    re_path(r"workspaces/check/$", apis.CheckWorkspaceView.as_view(), name="check"),
    re_path(r"invitations/sends/$", apis.SendInvitationApi.as_view(), name="send-invitation"),
    re_path(r"invitations/join/$", apis.JoinInvitationApi.as_view(), name="join-invitation"),
]

urlpatterns += router.urls
