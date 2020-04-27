from django.contrib import admin

from . import models


@admin.register(models.Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "creator")


@admin.register(models.WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ("workspace", "user", "role")


@admin.register(models.Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        "email", "workspace", "workspace_role", "activate"
    )
