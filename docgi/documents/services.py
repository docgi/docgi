from posixpath import join as urljoin

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.request import Request

from . import models
from ..workspaces.models import Workspace

User = get_user_model()
CLIENT_PUBLIC_COL_PATH = "p/c"  # Client side need implement this route
CLIENT_PUBLIC_DOC_PATH = "p/d"  # Client side need implement this route


def get_user_collections(user: User, workspace: Workspace, queryset=models.Collection.objects.all()):
    return queryset.filter(
        Q(workspace=workspace) &
        Q(
            Q(
                private=False
            ) |
            Q(
                private=True, creator=user
            )
        )
    )


def get_user_documents(user: User, workspace: Workspace, queryset=models.Document.objects.all()):
    return queryset.filter(
        Q(collection__in=get_user_collections(user, workspace)) &
        Q(
            Q(draft=False) |
            Q(draft=True, creator=user)
        )
    )


def build_public_collection_url(collection: models.Collection, request: Request):
    if collection.public is True:
        headers = request.headers
        origin = headers.get("origin", "")
        if not origin:
            return ""
        return urljoin(origin, CLIENT_PUBLIC_COL_PATH, str(collection.id))
    return ""


def build_public_document_url(document: models.Document, request: Request):
    return ""
