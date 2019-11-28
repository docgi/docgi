from os import path

from django.conf import settings as app_settings
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import serializers

from apps.authentication.serializers import DocgiTokenObtainPairSerializer
from apps.users.serializers import UserSerializer
from apps.utils.mailer import send_mail
from . import models

User = get_user_model()
LEN_CODE = 6
URL_FRONT_END_JOIN_INVITE = "join-invite"  # Frontend must to handle this route


class CheckWorkspaceSerializer(serializers.Serializer):
    name = serializers.SlugField(required=True)


class GetCodeSerializer(serializers.Serializer):
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
        if models.Workspace.objects.filter(name__iexact=workspace_name).exists():
            raise serializers.ValidationError("Workspace with that name already exists.")
        return workspace_name

    def create(self, validated_data):
        user = User.get_or_create(email=validated_data["email"])
        workspace = models.Workspace.objects.create(
            name=validated_data["workspace_name"],
            creator=user
        )
        models.WorkspaceMember.objects.create(
            user=user,
            workspace=workspace,
            role=models.WorkspaceMember.MemberRole.ADMIN.value
        )
        return dict(
            user=user,
            workspace=workspace
        )

    def to_representation(self, data):
        user = data["user"]
        workspace = data["workspace"]
        ret = dict()
        ret["user"] = self.InnerUserSerializer(instance=user, context=self.context).data
        ret["token"] = str(DocgiTokenObtainPairSerializer.get_token(
            user=user, workspace=workspace.name
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
        fields = ("name", "creator", "created", "members", "logo")
        read_only_fields = ("creator", "name")

    members = serializers.SerializerMethodField()

    def get_members(self, workspace):
        members = workspace.members.all()
        return WorkspaceMemberSerializer(
            instance=members,
            many=True,
            context=self.context
        ).data


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkspaceMember
        fields = ("id", "user", "role")

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
                      html_template="email/invitation/invitation.html",
                      text_template="email/invitation/invitation.txt",
                      context=ctx)

    def create(self, validated_data):
        inviter = self.context["request"].user
        workspace = self.context["request"].user.workspace
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

    def create(self, validated_data):
        uuid = validated_data.pop("uuid")
        invitation = models.Invitation.objects.filter(
            uuid=uuid, activate=True
        ).first()
        if invitation is None:
            raise Http404()

        if invitation.is_expire():
            raise serializers.ValidationError("Invitation is expired.")

        # In case exist invitation, collect workspace id, email and role and create WorkspaceMember,
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
            user=UserSerializer(instance=data["user"]).data,
            token=str(DocgiTokenObtainPairSerializer.get_token(
                user=user, workspace=workspace.name
            ).access_token),
            workspace=WorkspaceSerializer(instance=workspace).data
        )
        return ret
