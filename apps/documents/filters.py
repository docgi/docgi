from django_filters import rest_framework as filters

from apps.documents import models


class DocumentFilter(filters.FilterSet):
    class Meta:
        model = models.Document
        fields = ("collection",)
