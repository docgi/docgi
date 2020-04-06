from os import path

from django.conf import settings as app_settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404
from rest_framework import serializers

from docgi.auth.serializers import DocgiTokenObtainPairSerializer
from docgi.users.serializers import UserSerializer
from docgi.utils.mailer import send_mail

from . import models

User = get_user_model()
LEN_CODE = 6
URL_FRONT_END_JOIN_INVITE = "join-invite"  # Frontend must to handle this route


class CheckWorkspaceSerializer(serializers.Serializer):
    name = serializers.SlugField(required=True)


class GetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class StatsWorkspaceSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class CheckCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=LEN_CODE)


class CreateWorkspaceSerializer(serializers.Serializer):
    class InnerUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email", "username", "avatar", "need_pass")

        need_pass = serializers.SerializerMethodField()

        def get_need_pass(self, user):
            return not user.has_usable_password()

    email = serializers.EmailField(required=True, write_only=True)
    code = serializers.CharField(required=True, max_length=LEN_CODE, write_only=True)
    workspace_name = serializers.SlugField(required=True, write_only=True)

    def validate_workspace_name(self, workspace_name: str) -> str:
        workspace_name = workspace_name.lower()
        if models.Workspace.objects.filter(name__iexact=workspace_name).exists():
            raise serializers.ValidationError("Workspace with that name already exists.")
        return workspace_name

    @transaction.atomic
    def create(self, validated_data):
        user = User.get_or_create(email=validated_data["email"])
        workspace = models.Workspace.objects.create(
            name=validated_data["workspace_name"],
            creator=user
        )
        member = models.WorkspaceMember.objects.create(
            user=user,
            workspace=workspace,
            role=models.WorkspaceMember.MemberRole.ADMIN.value
        )
        return dict(
            user=user,
            workspace=workspace,
            member=member
        )

    def to_representation(self, data):
        from docgi.auth.serializers import KEY_WORKSPACE_ROLE_OBTAIN_TOKEN, KEY_WORKSPACE_NAME_OBTAIN_TOKEN

        user = data.get("user")
        workspace = data.get("workspace")
        member = data.get("member")
        ret = dict()
        ret["user"] = self.InnerUserSerializer(instance=user, context=self.context).data
        ret["token"] = str(DocgiTokenObtainPairSerializer.get_token(
            user=user,
            **{
                KEY_WORKSPACE_NAME_OBTAIN_TOKEN: workspace.name,
                KEY_WORKSPACE_ROLE_OBTAIN_TOKEN: member.role
            }
        ).access_token)
        ret["workspace"] = WorkspaceSerializer(instance=workspace, context=self.context).data
        return ret


class WorkspacePublicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workspace
        fields = ("name", "logo")


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workspace
        fields = ("name", "creator", "created", "logo")
        read_only_fields = ("creator", "name",)


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkspaceMember
        fields = ("user", "role")

    user = UserSerializer(read_only=True)


class SendInvitationSerializer(serializers.Serializer):
    class InnerInvitationSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True)
        workspace_role = serializers.ChoiceField(choices=models.WorkspaceMember.MemberRole.to_choices(),
                                                 default=models.WorkspaceMember.MemberRole.MEMBER.value)

    invitations = serializers.ListField(
        child=InnerInvitationSerializer(), required=True, allow_empty=False, allow_null=False
    )

    def _send_invite(self, instances):
        for instance in instances:
            link_join = path.join(*[app_settings.FRONT_END_HOST_NAME,
                                    instance.workspace.name,
                                    URL_FRONT_END_JOIN_INVITE,
                                    str(instance.uuid)])
            ctx = dict(
                inviter=instance.inviter.username,
                link_join=link_join,
                email=instance.email,
                workspace=instance.workspace
            )
            send_mail(subject="Invitation",
                      email=instance.email,
                      html_template_path="email/invitation/invitation.html",
                      text_template_path="email/invitation/invitation.txt",
                      context=ctx)

    def validate_invitations(self, invitations):
        for it in invitations:
            count = sum(it["email"] == _it["email"] for _it in invitations)
            if count > 1:
                raise serializers.ValidationError({"invitations": ["Contains duplicate emails."]})
        return invitations

    def create(self, validated_data):
        inviter = self.context["request"].user
        workspace = self.context["request"].user.get_current_workspace_name()
        invitations = validated_data.pop("invitations")
        result = dict()

        # We need check user who have joined to workspace,
        # if any user notify to inviter that already joined.
        emails = [it["email"] for it in invitations]
        joined = models.WorkspaceMember.objects.filter(
            user__email__in=emails, workspace__name__iexact=workspace
        ).values_list("user__email", flat=True)
        if joined:
            invitations = list(filter(lambda it: it["email"] not in joined, invitations))
            result.update(
                joined=joined
            )

        # Check email have sent invitation.
        emails = [it["email"] for it in invitations]
        invited = models.Invitation.objects.filter(
            email__in=emails,
            workspace__name__iexact=workspace,
        ).values_list("email", flat=True)
        if invited:
            invitations = list(filter(lambda it: it["email"] not in invited, invitations))
            result.update(
                invited=invited
            )

        if invitations:
            invitation_objs = [models.Invitation(
                email=it["email"],
                workspace_role=it["workspace_role"],
                workspace_id=workspace,
                inviter=inviter
            ) for it in invitations]
            instances = models.Invitation.objects.bulk_create(invitation_objs)
            self._send_invite(instances)

            result.update(
                recently_invited=[it["email"] for it in invitations]
            )
        return result

    def to_representation(self, result):
        return result


class JoinInvitationSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(write_only=True, required=True)
    workspace = serializers.SlugField(required=True)

    @transaction.atomic
    def create(self, validated_data):
        uuid = validated_data.pop("uuid")
        workspace = validated_data.pop("workspace")
        invitation = models.Invitation.objects.filter(
            uuid=uuid, activate=True, workspace_id=workspace
        ).first()
        if invitation is None:
            raise Http404()

        if invitation.is_expire():
            raise serializers.ValidationError({"uuid": ["Invitation is expired."]})

        # In case exist invitation, collect workspace id,
        # email and role and create WorkspaceMember,
        # After all mark `invitation` activate is False
        workspace_id = invitation.workspace_id
        workspace = models.Workspace.objects.get(pk=workspace_id)
        email = invitation.email
        role = invitation.workspace_role

        user = User.get_or_create(email=email)
        models.WorkspaceMember.objects.create(
            user=user, workspace_id=workspace_id, role=role
        )
        invitation.activate = False
        invitation.save()

        return dict(
            user=user,
            workspace=workspace
        )

    def to_representation(self, data):
        user = data.get("user")
        workspace = data.get("workspace")
        ret = dict(
            token=str(DocgiTokenObtainPairSerializer.get_token(
                user=user, workspace=workspace.name
            ).access_token),
            need_pass=user.has_usable_password()
        )
        return ret
