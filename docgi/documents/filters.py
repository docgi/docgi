from django_filters import rest_framework as filters

from docgi.documents import models


class DocumentFilter(filters.FilterSet):
    class Meta:
        model = models.Document
        fields = ("collection", "draft", "own")

    own = filters.BooleanFilter(method="documented_by_me")

    def documented_by_me(self, queryset, name, value):
        return queryset.filter(creator=self.request.user)
