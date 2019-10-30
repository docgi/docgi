from rest_framework import viewsets

from . import serializers, models


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.all()
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(
            workspace_id=self.request.user.workspace
        )
