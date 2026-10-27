import dataclasses
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from typing import Dict
from typing import Type

from .beautify_string import camel_to_human
from winter.web import ResponseHeader
from .exception_handler_generator import ExceptionHandlerGenerator
from .exception_mapper import ExceptionMapper
from .handlers import exception_handler
from .problem_handling_info import ProblemHandlingInfo
from .. import MediaType
from ..request import Request
from ..response_header_annotation import response_header


class ProblemExceptionHandlerGenerator(ExceptionHandlerGenerator):
    def __init__(self, exception_mapper: ExceptionMapper):
        self._exception_mapper = exception_mapper

    def generate(self, exception_class: Type[Exception], handling_info: ProblemHandlingInfo) -> Type:
        from ..response_status_annotation import response_status

        return_type_class = self._build_exception_dataclass(exception_class)
        exception_mapper = self._exception_mapper

        @exception_handler
        @response_status(handling_info.status)
        @response_header('Content-Type', 'content_type_header')
        def handle(
            self,
            exception: exception_class,
            request: Request,
            content_type_header: ResponseHeader[str],
            **kwargs,
        ) -> return_type_class:
            content_type_header.set(str(MediaType.APPLICATION_PROBLEM_JSON))
            return exception_mapper.to_response_body(request, exception, handling_info)

        handler_class_name = exception_class.__name__ + 'Handler'
        return type(handler_class_name, (), {'handle': handle})

    def _build_exception_dataclass(self, exception_class: Type[Exception]) -> Type:
        class_name = exception_class.__name__

        fields = {
            'status': int,
            'title': str,
            'detail': str,
            'type': str,
        }
        if is_dataclass(exception_class):
            extensions = {field.name: field.type for field in dataclasses.fields(exception_class)}
            fields.update(extensions)

        return dataclass(type(class_name, (), {'__annotations__': fields}))


class ProblemExceptionMapper(ExceptionMapper):
    def to_response_body(self, request: Request, exception: Exception, handling_info: ProblemHandlingInfo) -> Dict:
        exception_class = exception.__class__

        problem_dict = dict(
            status=handling_info.status,
            title=handling_info.title or self._generate_default_title_value(exception_class),
            detail=handling_info.detail or str(exception),
            type=handling_info.type or self._generate_type_value(exception_class),
        )
        if is_dataclass(exception.__class__):
            problem_dict.update(asdict(exception))

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
