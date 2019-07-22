from .. import converters


class PositiveInteger(int):

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        if self < 0:
            raise ValueError(f'PositiveInteger can not be negative: {self}')
        super().__init__()


@converters.converter(PositiveInteger)
def convert_positive_integer(value, type_):
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise converters.ConvertException.cannot_convert(value=value, type_name='PositiveInteger')
