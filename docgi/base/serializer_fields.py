from rest_framework.fields import Field, MinLengthValidator, MaxLengthValidator

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
UPDATE_ACTIONS = ("update", "partial_update")
COLOR_FIELD_MIN_LEN = 6
COLOR_FIELD_MAX_LEN = 7


class ColorField(Field):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            validators=[MinLengthValidator(COLOR_FIELD_MIN_LEN), MaxLengthValidator(COLOR_FIELD_MAX_LEN)],
            required=False
        )
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if len(data) == COLOR_FIELD_MAX_LEN:
            return data[1:]
        return data

    def to_representation(self, value):
        return f"#{value}"
