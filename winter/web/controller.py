from typing import Type
import warnings


def controller(controller_class: Type) -> Type:
    warnings.warn('Do not use the decorator. It is not required and has no functionality.', DeprecationWarning)
    return controller_class
