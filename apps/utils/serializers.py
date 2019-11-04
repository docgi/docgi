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
            "`only_create_fields` or `only_update_fields` must be type of `list` or `tuple`."
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
    """
    This mixin override to_representation method of serializer class.
    Please set valid attribute 'on_represent_fields_maps' in Meta class of serializer.

    Example 'on_represent_fields_maps':
    class Meta:
        model = ...
        fields = (...,)
        on_represent_fields_maps = {
            "members": {
                "class": UserSerializer,
                "many": True,  # default is False
            }
        }
    """
    @property
    def on_represent_fields_maps(self) -> dict:
        assert hasattr(self, "Meta"), (
            f"Class {self.__class__.__name__} missing class Meta attribute."
        )
        assert hasattr(self.Meta, "on_represent_fields_maps"), (
            f"Class {self.__class__.__name__}.Meta missing on_represent_fields_maps attribute. "
            f"To use this mixin please set valid 'on_represent_fields_maps' attribute."
        )
        return self.Meta.on_represent_fields_maps

    def to_representation(self, instance):
        on_represent_fields_maps = self.on_represent_fields_maps
        for field_name in on_represent_fields_maps.keys():
            field = self.fields.pop(field_name, None)
            if field is not None:
                if on_represent_fields_maps[field_name].get("source", None) is None:
                    on_represent_fields_maps[field_name].update(
                        {"source": field.source}
                    )

        ret = super().to_representation(instance=instance)
        for field_name in on_represent_fields_maps.keys():
            Serializer = on_represent_fields_maps[field_name].get("class", None)
            assert Serializer is not None, (
                "Field 'class' attribute is None or not set. "
                "Please set valid serializer class for this field."
            )
            source = on_represent_fields_maps[field_name].get("source")
            many = on_represent_fields_maps[field_name].get("many", False)

            if source is not None:
                data = getattr(instance, source, None) or getattr(instance, field_name, None)
            else:
                data = getattr(instance, field_name, None)

            # If source data is ManyRelatedManager we need fetch all data.
            if data.__class__.__name__ == "ManyRelatedManager":
                data = data.all()

            ret[field_name] = Serializer(
                instance=data,
                many=many,
                context=self.context
            ).data

        return ret
