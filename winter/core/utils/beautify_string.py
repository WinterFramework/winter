import re


def camel_to_human(value: str, separator: str = ' ', is_capitalize: bool = False) -> str:
    assert value is not None
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    result_value = pattern.sub(separator, value).lower()
    return result_value.capitalize() if is_capitalize else result_value
