from docgi.base.models import Choices


def get_app_config():
    result = dict()

    all_choices = Choices.__subclasses__()
    choices = dict()
    for ch in all_choices:
        ch_items = dict()

        for key, val in ch.__members__.items():
            text = " ".join(key.split("_")).title()
            value = val.value
            ch_items[text.lower()] = {
                "text": text,
                "value": value
            }

        choices[ch.__name__] = ch_items
    result.update(
        choices=choices
    )
    return result
