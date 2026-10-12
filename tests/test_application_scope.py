"""
North-star test for docs/architecture.md, principle 2: framework behaviour is never
process-global. Two Application instances in one process must not share behavioural
registries. Marked xfail(strict=True): it turns green when the Application scope lands,
and strict forces the marker to be removed at that moment. `raises` limits the expected failure to
`Application` not existing yet or the registries still being shared; any other error is a real failure.
"""
import pytest


class _ErrorA(Exception):
    pass


@pytest.mark.xfail(
    strict=True,
    raises=(ImportError, AssertionError),
    reason='North star: behavioural registries are scoped to an Application instance',
)
def test_two_applications_do_not_share_exception_handlers():  # pragma: no cover
    from winter.application import Application
    from winter.web.exceptions.handlers import DefaultExceptionHandler
    from winter.web.exceptions.handlers import ExceptionHandler
    from winter.web.exceptions.handlers import ExceptionHandlersRegistry

    class HandlerA(ExceptionHandler):
        def handle(self, exception: Exception, **kwargs):
            return 'a'

    app_1 = Application()
    app_2 = Application()

    app_1.get(ExceptionHandlersRegistry).add_handler(_ErrorA, HandlerA)

    assert isinstance(app_1.get(ExceptionHandlersRegistry).get_handler(_ErrorA), HandlerA)
    assert isinstance(app_2.get(ExceptionHandlersRegistry).get_handler(_ErrorA), DefaultExceptionHandler)
