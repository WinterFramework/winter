import typing


class ConvertException(Exception):
    NON_FIELD_ERROR = 'non_field_error'
    MISSING_FIELDS_PATTERN = 'Missing fields: "{missing_fields}"'
    NOT_IN_ALLOWED_VALUES_PATTERN = 'Value not in allowed values("{allowed_values}"): "{value}"'

    _invalid_type_pattern = 'Invalid type.'
    _invalid_type_with_name_pattern = 'Invalid type. Need: "{type_name}". Got: "{value}"'
    _error_pattern_from_value_and_type_name = 'Cannot convert "{value}" to {type_name}'

    def __init__(self, errors: typing.Union[str, typing.Dict]):
        self.errors = errors

    @classmethod
    def invalid_type(cls, value: typing.Any, type_name: typing.Optional[str] = None) -> 'ConvertException':
        if type_name:
            error = cls._invalid_type_with_name_pattern.format(value=value, type_name=type_name)
        else:
            error = cls._invalid_type_pattern.format(value=value)
        errors = {
            cls.NON_FIELD_ERROR: error,
        }
        return cls(errors)

    @classmethod
    def cannot_convert(cls, value: typing.Any, type_name: str) -> 'ConvertException':
        errors = cls._error_pattern_from_value_and_type_name.format(value=value, type_name=type_name)
        return cls(errors)
