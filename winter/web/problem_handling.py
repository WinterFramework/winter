import re
from typing import Dict
from typing import Type

import dataclasses
from rest_framework.request import Request

from winter import response_status
from winter.core import Component
from .exceptions import ExceptionHandler
from .exceptions import ExceptionHandlerGenerator
from .exceptions import ExceptionMapper
from .problem_annotation import ProblemAnnotation
from ..core.utils import camel_to_human


class DefaultExceptionHandlerGenerator(ExceptionHandlerGenerator):
    def generate(self, exception_class: Type[Exception], exception_mapper: ExceptionMapper) -> Type[ExceptionHandler]:
        component = Component.get_by_cls(exception_class)
        annotation = component.annotations.get_one(ProblemAnnotation)
        assert isinstance(annotation, ProblemAnnotation)

        return_type_class = self._build_exception_dataclass(exception_class)

        @response_status(annotation.status)
        def handle_method(self, request: Request, exception: exception_class, **kwargs) -> return_type_class:
            return exception_mapper.to_response_body(request, exception)

        handler_class_name = exception_class.__name__ + 'Handler'
        handler_class = type(handler_class_name, (ExceptionHandler,), {'handle': handle_method})
        return handler_class

    def _build_exception_dataclass(self, exception_class: Type[Exception]) -> Type:
        class_name = exception_class.__name__

        problem_annotations = {field.name: field.type for field in dataclasses.fields(ProblemAnnotation)}
        if dataclasses.is_dataclass(exception_class):
            extended_annotations = {field.name: field.type for field in dataclasses.fields(exception_class)}
            problem_annotations += extended_annotations

        return dataclasses.dataclass(type(f'{class_name}Dataclass', (), {'__annotations__': problem_annotations}))


class ProblemExceptionMapper(ExceptionMapper):
    def to_response_body(self, request: Request, exception: Exception) -> Dict:
        def generate_default_title_value(exception_cls: Type[Exception]) -> str:
            strip_tail = _try_cut_exception_name_postfix(exception_cls)
            return camel_to_human(strip_tail, is_capitalize=True)

        def generate_type_value(exception_cls: Type[Exception]) -> str:
            strip_tail = _try_cut_exception_name_postfix(exception_cls)
            return 'urn:problem-type:' + camel_to_human(strip_tail, separator='-')

        def _try_cut_exception_name_postfix(exception_cls: Type[Exception]) -> str:
            return re.sub('Exception$', '', exception_cls.__name__)

        exception_class = exception.__class__
        component = Component.get_by_cls(exception_class)
        annotation = component.annotations.get_one(ProblemAnnotation)
        assert isinstance(annotation, ProblemAnnotation)

        problem_dict = dict(
            status=annotation.status,
            title=annotation.title or generate_default_title_value(exception_class),
            detail=annotation.detail or str(exception),
            type=annotation.type or generate_type_value(exception_class),
        )
        if dataclasses.is_dataclass(exception.__class__):
            fields = dataclasses.fields(exception_class)
            for field in fields:
                field_value = getattr(exception, field.name)
                problem_dict[field.name] = field_value

        return problem_dict
