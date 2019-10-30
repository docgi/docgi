from django.db.models.query import QuerySet

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
UPDATE_ACTIONS = ("update", "partial_update")


class DocgiModelSerializerMixin(object):
    def get_extra_read_only_fields(self):
        method = self.context["request"].method

        if method == PUT or method == PATCH:
            extra_read_only_fields = getattr(self.Meta, "only_create_fields", [])
        elif method == POST:
            extra_read_only_fields = getattr(self.Meta, "only_update_fields", [])
        else:
            extra_read_only_fields = []

        assert isinstance(extra_read_only_fields, (list, tuple)), (
            "`only_on_create_fields` or `only_on_update_fields` must be type of `list` or `tuple`."
        )
        return extra_read_only_fields

    def get_fields(self):
        """
        In this function use some trick, auto set Meta.ref_name = None
        for force yasg generated all serializer for each method.
        Docs: https://drf-yasg.readthedocs.io/en/stable/custom_spec.html#serializer-meta-nested-class
        """
        fields = super().get_fields()
        extra_read_only_fields = self.get_extra_read_only_fields()
        setattr(self.Meta, "ref_name", None)  # Magic happen here

        for field_name in extra_read_only_fields:
            field = fields.pop(field_name)
            setattr(field, "read_only", True)  # And here
            fields.update({field_name: field})

        return fields


class DocgiFlexToPresentSerializerMixin(object):
    @property
    def on_represent_fields_maps(self) -> dict:
        return self.Meta.on_represent_fields_maps

    def to_representation(self, instance):
        for field_name in self.on_represent_fields_maps.keys():
            self.fields.pop(field_name, None)

        ret = super().to_representation(instance=instance)

        for field_name in self.on_represent_fields_maps.keys():
            data = getattr(instance, field_name, None)
            if data.__class__.__name__ == "ManyRelatedManager":
                data = data.all()
            ret[field_name] = self.on_represent_fields_maps[field_name]["class"](
                instance=data,
                many=self.on_represent_fields_maps[field_name]["many"],
                context=self.context
            ).data

        return ret
