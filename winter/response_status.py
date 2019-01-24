from .controller import ControllerMethod

_default_statuses = {}
_default_http_method_statuses = {
    'get': 200,
    'post': 200,
    'patch': 200,
    'delete': 204,
}


def response_status(status: int):
    def wrapper(func):
        _set_default_response_status(func, status)
        return func
    return wrapper


def get_default_response_status(controller_method: ControllerMethod) -> int:
    default_response_status = _default_statuses.get(controller_method.func)
    http_method = controller_method.http_method.lower()
    return default_response_status or _default_http_method_statuses.get(http_method, 200)


def _set_default_response_status(func, status: int):
    _default_statuses[func] = status
