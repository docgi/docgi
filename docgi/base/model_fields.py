from django.db.models import PositiveIntegerField


class ScopeIDField(PositiveIntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        c = super().get_db_prep_value(value, connection, prepared)
        import ipdb
        ipdb.set_trace()
