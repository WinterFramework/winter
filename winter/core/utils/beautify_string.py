import re

pattern = re.compile(r'(?<!^)(?=[A-Z])')


def camel_to_human(value: str, separator: str = ' ') -> str:
    return pattern.sub(separator, value).lower()
