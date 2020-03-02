from rest_framework.fields import Field, MinLengthValidator, MaxLengthValidator

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
UPDATE_ACTIONS = ("update", "partial_update")


class ColorField(Field):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            validators=[MinLengthValidator(6), MaxLengthValidator(6)],
            required=False
        )
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return f"#{value}"
