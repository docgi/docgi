from inspect import isclass

from django.utils.module_loading import import_string
from rest_framework.serializers import Serializer

UPDATE_ACTION = "update"
PARTIAL_UPDATE_ACTION = "partial_update"
CREATE_ACTION = "create"

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"


class DocgiSerializerUtilMixin(object):
    def is_update_method(self):
        method = self.context["request"].method
        return method in [PUT, PATCH]

    def is_post_method(self):
        method = self.context["request"].method
        return method == POST

    def get_request(self):
        return self.context["request"]

    def get_view(self):
        return self.context["view"]

    @property
    def cur_user(self):
        return self.context["request"].user


def is_subclass(cls, baseclass):
    if isclass(cls):
        return issubclass(cls, baseclass)
    return False


class DocgiExtraReadOnlyField(object):
    def get_extra_read_only_fields(self):
        method = self.context["request"].method

        if method == PUT or method == PATCH:
            extra_read_only_fields = getattr(self.Meta, "create_only_fields", [])
        elif method == POST:
            extra_read_only_fields = getattr(self.Meta, "update_only_fields", [])
        else:
            extra_read_only_fields = []

        assert isinstance(extra_read_only_fields, (list, tuple)), (
            "`only_create_fields` or `only_update_fields` must be type of `list` or `tuple`."
        )
        return extra_read_only_fields

    def get_fields(self):
        """
        In this function use some trick, auto set Meta.ref_name = None
        for force yasg generated all schema for each method.
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
                "presenter": UserSerializer,
                "many": True,  # default is False
                "source": None
            }
        }
    """

    @property
    def flex_represent_fields(self) -> dict:
        if hasattr(self, "Meta") and hasattr(self.Meta, "flex_represent_fields"):
            assert isinstance(self.Meta.flex_represent_fields, dict), (
                "`flex_represent_fields` must be dict"
            )
            return self.Meta.flex_represent_fields
        return {}

    def to_representation(self, instance):
        context = self.context
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
            presenter = flex_represent_fields[field_name].get("presenter", None)

            assert presenter is not None, (
                "`presenter` is not set or None. "
                "Please set valid `presenter` attribute. "
                "Types support is callable, serializer class or import path of serializer"
            )

            # If it is string that maybe import path of Serializer class, we try to import.
            if isinstance(presenter, str):
                presenter = import_string(presenter)

            is_callable = callable(presenter)
            is_serializer_class = is_subclass(presenter, Serializer)
            if not is_callable and not is_serializer_class:
                raise AttributeError(
                    f"Type of `presenter` not support, expected `callable`, `Serializer` got {presenter.__class__}"
                )

            source = flex_represent_fields.get(field_name).get("source", None)
            many = flex_represent_fields.get(field_name).get("many", False)
            if source is not None:
                data = getattr(instance, source, None) or getattr(instance, field_name, None)
            else:
                data = getattr(instance, field_name, None)

            # If source data is ManyRelatedManager we need fetch all data.
            if data.__class__.__name__ == "ManyRelatedManager":
                data = data.all()
                many = True

            presented_data = None
            if is_serializer_class:
                presented_data = presenter(
                    instance=data,
                    many=many,
                    context=context
                ).data
            elif is_callable:
                if many:
                    presented_data = [presenter(it) for it in data]
                else:
                    presented_data = presenter(data)
            else:
                pass

            ret[field_name] = presented_data

        return ret
