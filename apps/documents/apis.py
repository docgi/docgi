from django.db.models import Subquery, IntegerField, OuterRef, Count, Value, Q
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
        return self.queryset.filter(
            Q(workspace_id=getattr(self.request.user, 'workspace')) &
            Q(
                Q(private=False) | Q(private=True, creator=self.request.user)
            )
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
        return self.queryset.filter(
            collection__workspace=getattr(self.request.user, 'workspace')
        ).annotate(
            star=Coalesce(Count(Subquery(
                models.UserStarDoc.objects.order_by().values("doc").filter(
                    doc=OuterRef("id")
                ),
                output_field=IntegerField()
            )), Value(0))
        )
