from enum import Enum


class Choices(Enum):
    @classmethod
    def to_choices(cls):
        # Find duplicate value, if any raise exception.
        values = cls.__members__.values()
        seen = set(values)
        if len(seen) < len(values):
            raise Exception(f"{cls.name} has duplicate values.")

        return [
            (item[1].value, item[1].name.replace("_", " ").title())
            for item in cls.__members__.items()
        ]
