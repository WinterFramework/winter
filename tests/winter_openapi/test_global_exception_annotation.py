from winter.core import Component
from winter_openapi.annotations import GlobalExceptionAnnotation
from winter_openapi.annotations import global_exception
from winter_openapi.annotations import register_global_exception


def test_global_exception_decorator_declarative_way():
    @global_exception
    class GlobalException(Exception):
        pass

    component = Component.get_by_cls(GlobalException)
    assert component is not None
    assert component.annotations.get(GlobalExceptionAnnotation) == [GlobalExceptionAnnotation(GlobalException)]


def test_global_exception_decorator_imperative_way():
    class GlobalException(Exception):
        pass

    register_global_exception(GlobalException)

    component = Component.get_by_cls(GlobalException)
    assert component is not None
    assert component.annotations.get(GlobalExceptionAnnotation) == [GlobalExceptionAnnotation(GlobalException)]
