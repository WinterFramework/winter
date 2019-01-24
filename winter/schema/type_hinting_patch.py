# TODO: Remove this file once the new drf-yasg is released
import datetime
import inspect
import typing
import uuid
from collections import OrderedDict
from decimal import Decimal

from drf_yasg import openapi
from rest_framework.settings import api_settings as rest_framework_settings

NotHandled = object()


def decimal_return_type():
    return openapi.TYPE_STRING if rest_framework_settings.COERCE_DECIMAL_TO_STRING else openapi.TYPE_NUMBER


hinting_type_info = [
    (bool, (openapi.TYPE_BOOLEAN, None)),
    (int, (openapi.TYPE_INTEGER, None)),
    (str, (openapi.TYPE_STRING, None)),
    (float, (openapi.TYPE_NUMBER, None)),
    (dict, (openapi.TYPE_OBJECT, None)),
    (Decimal, (decimal_return_type, openapi.FORMAT_DECIMAL)),
    (uuid.UUID, (openapi.TYPE_STRING, openapi.FORMAT_UUID)),
    (datetime.datetime, (openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (datetime.date, (openapi.TYPE_STRING, openapi.FORMAT_DATE)),
]


def get_origin_type(hint_class):
    origin_type = hint_class.__origin__ if hasattr(hint_class, '__origin__') else None
    return origin_type or hint_class


def is_origin_type_subclasses(hint_class, check_class):
    origin_type = get_origin_type(hint_class)
    if not inspect.isclass(origin_type):
        return False
    return issubclass(origin_type, check_class)


def inspect_union_hint_class(hint_class):
    if not typing:
        return NotHandled

    if get_origin_type(hint_class) == typing.Union:
        child_type = hint_class.__args__[0]
        return get_basic_type_info_from_hint(child_type)

    return NotHandled


def inspect_primitive_hint_class(hint_class):
    for check_class, type_format in hinting_type_info:
        if is_origin_type_subclasses(hint_class, check_class):
            swagger_type, format = type_format
            if callable(swagger_type):
                swagger_type = swagger_type()
            return OrderedDict([
                ('type', swagger_type),
                ('format', format),
            ])

    return NotHandled


def inspect_collection_hint_class(hint_class):
    if not typing:
        return NotHandled

    if is_origin_type_subclasses(hint_class, (typing.Sequence, typing.AbstractSet)):
        args = hint_class.__args__
        child_class = args[0] if args else str
        child_type_info = get_basic_type_info_from_hint(child_class)
        if not child_type_info:
            child_type_info = {'type': openapi.TYPE_STRING}
        return OrderedDict([
            ('type', openapi.TYPE_ARRAY),
            ('items', openapi.Items(**child_type_info)),
        ])

    return NotHandled


hint_class_inspectors = [
    inspect_union_hint_class,
    inspect_primitive_hint_class,
    inspect_collection_hint_class,
]


def get_basic_type_info_from_hint(hint_class):
    """Given a class (eg from a SerializerMethodField's return type hint,
    return its basic type information - ``type``, ``format``, ``pattern``,
    and any applicable min/max limit values.

    :param hint_class: the class
    :return: the extracted attributes as a dictionary, or ``None`` if the field type is not known
    :rtype: OrderedDict
    """
    for hint_class_inspector in hint_class_inspectors:
        result = hint_class_inspector(hint_class)
        if result is not NotHandled:
            return result

    return None
