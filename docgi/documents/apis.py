from django.contrib.postgres.fields import JSONField
from django.db.models import Subquery, IntegerField, OuterRef, Count, Value, Q
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce
from rest_framework import viewsets

from docgi.documents import filters, permissions
from docgi.base.apis import DocgiFlexSerializerViewSetMixin
from . import serializers, models


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.all()
    permission_classes = [
        permissions.CollectionPermission
    ]

    def get_queryset(self):
        current_user = self.request.user
        workspace_id = current_user.get_jwt_current_workspace_name()

        private_coll_qs = models.Collection.members.through.objects.filter(
            user=self.request.user,
            collection__workspace__exact=workspace_id,
        ).values_list("collection", flat=True)

        if self.action == "list":
            self.queryset = self.queryset.filter(
                parent__isnull=True
            )

        if self.action == "retrieve":
            child_collection_qs = models.Collection.objects.filter(
                parent=OuterRef("pk"), workspace_id__exact=workspace_id
            ).annotate(
                cols=RawSQL(
                    """
                    coalesce(
                        json_agg(
                            json_build_object(
                                'id', id,
                                'name', name,
                                'color', concat('#', color)
                            )
                        ),
                        '[]'::json
                    )
                    """, ()
                )
            ).values_list("cols", flat=True)

            doc_qs = models.Document.objects.filter(
                collection=OuterRef("pk")
            ).annotate(
                docs=RawSQL(
                    """
                    coalesce(
                        json_agg(json_build_object('id', id, 'title', title)),
                        '[]'::json
                    )
                    """, ()
                )
            ).values_list("docs", flat=True)

            self.queryset = self.queryset.annotate(
                child_cols=Subquery(child_collection_qs, output_field=JSONField()),
                docs=Subquery(doc_qs, output_field=JSONField())
            )

        return self.queryset.filter(
            Q(workspace_id=self.request.user.get_jwt_current_workspace_name()) &
            Q(
                Q(private=False) |
                Q(
                    Q(private=True) & Q(id__in=Subquery(private_coll_qs))
                )
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
        count_star_qs = Count(
            Subquery(
                models.UserStarDoc.objects.order_by().values("doc").filter(
                    doc=OuterRef("id")
                ),
                output_field=IntegerField()
            )
        )
        return self.queryset.filter(
            Q(collection__workspace=self.request.user.get_jwt_current_workspace_name()) &
            Q(
                Q(collection__private=False) |
                Q(collection__private=True, collection__creator=self.request.user)
            )
        ).annotate(
            star=Coalesce(count_star_qs, Value(0))
        )
