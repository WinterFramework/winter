import re
from typing import Dict
from typing import Type

import dataclasses
from rest_framework.request import Request

from winter.core import Component
from winter.core.utils import camel_to_human
from .exception_handler_generator import ExceptionHandlerGenerator
from .exception_mapper import ExceptionMapper
from .handlers import ExceptionHandler
from .handlers import exception_handlers_registry
from .problem_annotation import ProblemAnnotation


class ProblemExceptionHandlerGenerator(ExceptionHandlerGenerator):
    def generate(self, exception_class: Type[Exception], exception_mapper: ExceptionMapper) -> Type[ExceptionHandler]:
        from winter import response_status

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

        problem_annotations = {
            field.name: field.type
            for field in dataclasses.fields(ProblemAnnotation)
            if field.name != 'auto_handle'
        }
        if dataclasses.is_dataclass(exception_class):
            extended_annotations = {field.name: field.type for field in dataclasses.fields(exception_class)}
            problem_annotations.update(extended_annotations)

        return dataclasses.dataclass(type(f'{class_name}Dataclass', (), {'__annotations__': problem_annotations}))


class ProblemExceptionMapper(ExceptionMapper):
    def to_response_body(self, request: Request, exception: Exception) -> Dict:
        exception_class = exception.__class__
        component = Component.get_by_cls(exception_class)
        annotation = component.annotations.get_one(ProblemAnnotation)
        assert isinstance(annotation, ProblemAnnotation)

        problem_dict = dict(
            status=annotation.status,
            title=annotation.title or self._generate_default_title_value(exception_class),
            detail=annotation.detail or str(exception),
            type=annotation.type or self._generate_type_value(exception_class),
        )
        if dataclasses.is_dataclass(exception.__class__):
            problem_dict.update(dataclasses.asdict(exception))

        return problem_dict

    @classmethod
    def _generate_default_title_value(cls, exception_cls: Type[Exception]) -> str:
        strip_tail = cls._try_cut_exception_name_postfix(exception_cls)
        return camel_to_human(strip_tail).capitalize()

    @classmethod
    def _generate_type_value(cls, exception_cls: Type[Exception]) -> str:
        strip_tail = cls._try_cut_exception_name_postfix(exception_cls)
        return 'urn:problem-type:' + camel_to_human(strip_tail, separator='-')

    @classmethod
    def _try_cut_exception_name_postfix(cls, exception_cls: Type[Exception]) -> str:
        return re.sub('Exception$', '', exception_cls.__name__)


def generate_problem_handlers():
    mapper = ProblemExceptionMapper()
    handler_generator = ProblemExceptionHandlerGenerator()
    handled_problems: Dict[Type[Exception], ProblemAnnotation] = {
        cls: component.annotations.get_one(ProblemAnnotation)
        for cls, component in Component.get_all().items()
        if component.annotations.get_one_or_none(ProblemAnnotation)
    }
    for exception_class, problem_annotation in handled_problems.items():
        handler_class = handler_generator.generate(exception_class, mapper)
        exception_handlers_registry.add_handler(
            exception_class,
            handler_class,
            auto_handle=problem_annotation.auto_handle,
        )
