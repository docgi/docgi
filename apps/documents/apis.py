from django.db.models import Subquery, IntegerField, OuterRef, Count
from rest_framework import viewsets

from apps.utils.apis import DocgiFlexSerializerViewSetMixin
from . import serializers, models


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.prefetch_related("members").all()
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(
            workspace_id=self.request.user.workspace
        )


class DocumentViewSet(DocgiFlexSerializerViewSetMixin, viewsets.ModelViewSet):
    action_serializer_maps = {
        "list": serializers.ListDocumentSerializer
    }
    serializer_class = serializers.DocumentSerializer
    queryset = models.Document.objects.select_related("creator").all()

    def get_queryset(self):
        return self.queryset.filter(
            collection__workspace=self.request.user.workspace,
            collection=self.kwargs.get("collection")
        ).annotate(
            star=Count(Subquery(
                models.UserStarDoc.objects.order_by().values("doc").filter(
                    doc=OuterRef("id")
                ),
                output_field=IntegerField()
            ))
        )
