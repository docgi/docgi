REGEX_UUID = r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"


class DocgiFlexSerializerViewSetMixin(object):
    """
    Get suitable for class base on view action.
    This mixin is for use with ModelViewSet.
    """
    action_serializer_maps = {}

    def get_serializer_class(self):
        try:
            return self.action_serializer_maps[self.action]
        except (KeyError, AttributeError):
            pass
        return self.serializer_class
