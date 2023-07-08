import inspect
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from winter.core.utils.typing import get_origin_type
from .type_info import TypeInfo

_inspectors_by_type: Dict[
    Type,
    List[Tuple[Callable, Optional[Callable]]],
] = {}


def register_type_inspector(*types_: Type, checker: Callable = None, func: Callable = None):
    if func is None:
        return lambda func: register_type_inspector(*types_, checker=checker, func=func)

    for type_ in types_:
        callables = _inspectors_by_type.setdefault(type_, [])
        callables.append((func, checker))
    return func


class InspectorNotFound(Exception):

    def __init__(self, hint_cls):
        self.hint_cls = hint_cls

    def __str__(self):
        return f'Unknown type: {self.hint_cls}'


def inspect_type(hint_class) -> TypeInfo:
    origin_type = get_origin_type(hint_class)

    types_ = origin_type.mro() if inspect.isclass(origin_type) else type(origin_type).mro()

    for type_ in types_:
        inspectors = _inspectors_by_type.get(type_, [])
        type_info = _inspect_type(hint_class, inspectors)

        if type_info is not None:
            return type_info

    raise InspectorNotFound(hint_class)


def _inspect_type(
    hint_class,
    inspectors: List[Tuple[Callable, Optional[Callable]]],
) -> Optional[TypeInfo]:
    for inspector, checker in inspectors:
        if checker is None or checker(hint_class):
            return inspector(hint_class)
