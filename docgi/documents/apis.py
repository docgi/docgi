from django.db.models import Q, Prefetch
from rest_framework import viewsets

from docgi.documents import filters, permissions
from . import serializers, models
from ..base.apis import REGEX_UUID


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.all()
    permission_classes = [
        permissions.CollectionPermission
    ]
    lookup_value_regex = REGEX_UUID

    def get_queryset(self):
        current_user = self.request.user
        workspace_id = current_user.get_current_workspace_id()

        return self.queryset.filter(
            workspace_id=workspace_id,
        ).filter(
            Q(
                private=False
            ) |
            Q(
                private=True, creator=self.request.user
            )
        ).prefetch_related(
            Prefetch(
                "documents",
                queryset=models.Document.objects.select_related(
                    "creator"
                )
            )
        )


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DocumentSerializer
    queryset = models.Document.objects.select_related(
        "creator"
    ).prefetch_related(
        "contributors"
    ).all()
    filterset_class = filters.DocumentFilter
    lookup_value_regex = REGEX_UUID

    def get_queryset(self):
        return self.queryset.filter(
            Q(collection__workspace=self.request.user.get_current_workspace_id()) &
            Q(
                Q(collection__private=False) |
                Q(collection__private=True, collection__creator=self.request.user)
            )
        )
