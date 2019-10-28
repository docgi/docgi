POST = "POST"
PUT = "PUT"
PATCH = "PATCH"


class OnCreateOrUpdateOnlyFieldSerializerMixin(object):
    def get_extra_kwargs(self):
        method = self.context["request"].method
        read_only_fields = getattr(self.Meta, "read_only_fields", [])

        if method == PUT or method == PATCH:
            extra_read_only_fields = getattr(self.Meta, "only_on_create_fields", None)
        elif method == POST:
            extra_read_only_fields = getattr(self.Meta, "only_on_update_fields", None)
        else:
            extra_read_only_fields = None

        if extra_read_only_fields is not None:
            assert isinstance(extra_read_only_fields, (list, tuple)), (
                "`extra_read_only_fields` must be type of `list` or `tuple`."
            )
            assert isinstance(read_only_fields, (list, tuple)), (
                "`read_only_fields` must be type of `list` or `tuple`."
            )
            read_only_fields = list(set(list(read_only_fields) + list(extra_read_only_fields)))

        setattr(self.Meta, "read_only_fields", read_only_fields)
        return super().get_extra_kwargs()
