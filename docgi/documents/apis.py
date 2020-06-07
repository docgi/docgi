from django.db.models import Q, Prefetch
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny

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
        )


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DocumentSerializer
    queryset = models.Document.objects.select_related(
        "creator",
        "last_update_by"
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


class DocumentImageViewSet(CreateModelMixin,
                           viewsets.GenericViewSet):
    parser_classes = [
        MultiPartParser
    ]
    serializer_class = serializers.DocumentImageSerializer


class RecentlyUpdateDocumentAPI(ListModelMixin,
                                viewsets.GenericViewSet):
    pagination_class = None
    serializer_class = serializers.SimpleDocsInfoSerializer
    queryset = models.Document.objects.select_related(
        "creator",
        "last_update_by"
    ).prefetch_related(
        "contributors"
    ).all()

    def get_queryset(self):
        return self.queryset.filter(
            Q(collection__workspace=self.request.user.get_current_workspace_id()) &
            Q(
                Q(collection__private=False) |
                Q(collection__private=True, collection__creator=self.request.user)
            ) &
            Q(
                draft=False
            )
        ).order_by(
            "-modified"
        )[:10]


class PublicCollectionAPI(RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = models.Collection.objects.filter(
        public=True
    ).select_related(
        "workspace"
    ).prefetch_related(
        Prefetch(
            "documents",
            queryset=models.Document.objects.select_related(
                "creator",
                "last_update_by"
            )
        )
    )
    serializer_class = serializers.PublicCollectionSerializer
    permission_classes = [AllowAny]
    lookup_value_regex = REGEX_UUID
