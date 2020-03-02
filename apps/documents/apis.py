from django.db.models import Subquery, IntegerField, OuterRef, Count, Value, Q, Exists, F
from django.db.models.functions import Coalesce
from rest_framework import viewsets

from apps.documents import filters, permissions
from apps.utils.apis import DocgiFlexSerializerViewSetMixin
from . import serializers, models


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.prefetch_related("members").all()
    permission_classes = [
        permissions.CollectionPermission
    ]

    def get_queryset(self):
        doc_qs = models.Document.objects.filter(
            collection_id=OuterRef("pk")
        ).order_by().values("pk")

        collection_qs = models.Collection.objects.filter(
            workspace_id__exact=self.request.user.workspace,
        ).order_by().values("pk")

        return self.queryset.filter(
            Q(workspace_id=getattr(self.request.user, 'workspace')) &
            Q(
                Q(private=False) | Q(private=True, creator=self.request.user)
            )
        ).annotate(
            has_doc=Exists(doc_qs),
            has_collection=Exists(collection_qs)
        ).annotate(
            has_child=F("has_doc") or F("has_collection")
        )


class DocumentViewSet(DocgiFlexSerializerViewSetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.DocumentSerializer
    queryset = models.Document.objects.select_related(
        "creator"
    ).prefetch_related(
        "contributors"
    ).all()
    filterset_class = filters.DocumentFilter

    def get_queryset(self):
        count_star_qs = Count(
            Subquery(
                models.UserStarDoc.objects.order_by().values("doc").filter(
                    doc=OuterRef("id")
                ),
                output_field=IntegerField()
            )
        )
        return self.queryset.filter(
            Q(collection__workspace=getattr(self.request.user, 'workspace')) &
            Q(
                Q(collection__private=False) |
                Q(collection__private=True, collection__creator=self.request.user)
            )
        ).annotate(
            star=Coalesce(count_star_qs, Value(0))
        )
