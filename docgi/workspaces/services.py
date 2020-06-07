from django.contrib.auth import get_user_model
from django.db.models import Q

from . import models, serializers

User = get_user_model()


def get_stat_data(user, context):
    from docgi.users.serializers import UserInfoSerializer
    from docgi.documents import services as documents_services
    from docgi.documents.serializers import SimpleDocsInfoSerializer, CollectionSerializer

    user_data = UserInfoSerializer(
        instance=user,
        context=context
    ).data
    workspace_data = serializers.WorkspaceSerializer(
        instance=user.current_workspace,
        context=context
    ).data

    workspace_members = models.WorkspaceMember.objects.filter(
        workspace=user.current_workspace
    ).select_related(
        "user"
    )
    members_data = serializers.WorkspaceMemberSerializer(
        context=context,
        many=True,
        instance=workspace_members
    ).data

    collections = documents_services.get_user_collections(
        user=user,
        workspace=user.current_workspace
    ).select_related(
        "creator"
    )
    collection_data = CollectionSerializer(instance=collections, many=True, context=context).data

    documents = documents_services.get_user_documents(user=user, workspace=user.current_workspace).select_related(
        "creator",
        "last_update_by"
    ).prefetch_related(
        "contributors"
    )
    documents_data = SimpleDocsInfoSerializer(
        instance=documents,
        many=True,
        context=context
    ).data

    data = dict(
        user=user_data,
        workspace=workspace_data,
        members=members_data,
        documents=documents_data,
        collections=collection_data
    )

    return data
