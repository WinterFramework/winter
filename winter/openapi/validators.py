from typing import Iterable
from typing import Set
from typing import Type


from winter.application import Application
from winter.openapi.annotations import GlobalExceptionAnnotation


def validate_missing_raises_annotations(app: Application):
    """Every @problem exception of the application is declared with @raises by one of its API methods or is global."""
    from winter.web.exceptions.problem_annotation import ProblemAnnotation
    from winter.web.exceptions.raises import ExceptionAnnotation
    from winter.components import Component

    all_problem_exception: Set[Type[Exception]] = set()
    global_exceptions: Set[Type[Exception]] = set()
    declared_raises_exceptions: Set[Type[Exception]] = set()
    components = Component.get_all()
    for cls in app.definitions:
        component = components.get(cls)
        if component is None:
            continue
        if component.annotations.get_one_or_none(ProblemAnnotation):
            all_problem_exception.add(cls)
        if component.annotations.get_one_or_none(GlobalExceptionAnnotation):
            global_exceptions.add(cls)
        for method_component in component.methods:
            exception_annotations: Iterable[ExceptionAnnotation] = method_component.annotations.get(ExceptionAnnotation)
            for exception_annotation in exception_annotations:
                declared_raises_exceptions.add(exception_annotation.exception_cls)

    not_global_exceptions = all_problem_exception - global_exceptions
    missing_exceptions = not_global_exceptions - declared_raises_exceptions
    if missing_exceptions:
        message = ', '.join(exc.__name__ for exc in sorted(missing_exceptions, key=lambda ex: ex.__name__))
        raise AssertionError('You are missing declaration for next exceptions: ' + message)
