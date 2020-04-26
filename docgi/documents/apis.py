from django.db.models import Subquery, IntegerField, OuterRef, Count, Value, Q
from django.db.models.functions import Coalesce
from rest_framework import viewsets

from docgi.documents import filters, permissions
from . import serializers, models


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.prefetch_related(
        "children",
        "documents"
    ).all()
    permission_classes = [
        permissions.CollectionPermission
    ]

    def get_queryset(self):
        current_user = self.request.user
        workspace_id = current_user.get_current_workspace_id()

        if self.action == "list":
            self.queryset = self.queryset.filter(
                parent__isnull=True
            )

        return self.queryset.filter(
            workspace_id=workspace_id,
            private=False
        )


class DocumentViewSet(viewsets.ModelViewSet):
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
            Q(collection__workspace=self.request.user.get_current_workspace_id()) &
            Q(
                Q(collection__private=False) |
                Q(collection__private=True, collection__creator=self.request.user)
            )
        ).annotate(
            star=Coalesce(count_star_qs, Value(0))
        )
