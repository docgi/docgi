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
router.register(
    r"workspace/members",
    apis.WorkspaceMemberAPI,
    basename="workspace-members"
)

urlpatterns = [
    path("workspace/", apis.WorkspaceApi.as_view(), name="workspace-info"),
    path("app-configs/", apis.AppConfigsApi.as_view(), name="app-configs"),
    path("stats-workspace/", apis.StatsWorkspaceAPI.as_view(), name="stats-workspaces"),
    path("workspaces/check/", apis.CheckWorkspaceView.as_view(), name="check"),
    path("invitations/sends/", apis.SendInvitationApi.as_view(), name="send-invitation"),
    path("invitations/join/", apis.JoinInvitationApi.as_view(), name="join-invitation"),
    path("invitations/check/", apis.CheckInvitationApi.as_view(), name="check-invitation"),
]

urlpatterns += router.urls
