POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
UPDATE_ACTIONS = ("update", "partial_update")


class DocgiReadonlyFieldsMixin(object):
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


class DocgiFlexToPresentMixin(object):
    """
    This mixin override to_representation method of serializer class.
    Please set valid attribute 'flex_represent_fields' in Meta class of serializer.

    Example 'flex_represent_fields':
    class Meta:
        model = ...
        fields = (...,)
        flex_represent_fields = {
            "members": {
                "class": UserSerializer,
                "many": True,  # default is False
            }
        }
    """
    @property
    def flex_represent_fields(self) -> dict:
        assert hasattr(self, "Meta"), (
            f"Class {self.__class__.__name__} missing class Meta attribute."
        )
        assert hasattr(self.Meta, "flex_represent_fields"), (
            f"Class {self.__class__.__name__}.Meta missing flex_represent_fields attribute. "
            f"To use this mixin please set valid 'flex_represent_fields' attribute."
        )
        return self.Meta.flex_represent_fields

    def to_representation(self, instance):
        flex_represent_fields = self.flex_represent_fields
        for field_name in flex_represent_fields.keys():
            field = self.fields.pop(field_name, None)
            if field is not None:
                if flex_represent_fields[field_name].get("source", None) is None:
                    flex_represent_fields[field_name].update(
                        {"source": field.source}
                    )

        ret = super().to_representation(instance=instance)
        for field_name in flex_represent_fields.keys():
            Serializer = flex_represent_fields[field_name].get("class", None)
            assert Serializer is not None, (
                "Field 'class' attribute is None or not set. "
                "Please set valid serializer class for this field."
            )
            source = flex_represent_fields[field_name].get("source")
            many = flex_represent_fields[field_name].get("many", False)

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


class DocgiValidateIntegrityMixin(object):
    def validate_integrity(self):
        raise NotImplementedError("`validate_integrity` not implemented.")

    def create(self, validated_data):
        self.validate_integrity()
        return super().create(validated_data)
