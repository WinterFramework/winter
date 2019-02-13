_response_statuses = {}
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


def get_default_response_status(func, http_method: str) -> int:
    default_response_status = _response_statuses.get(func)
    http_method = http_method.lower()
    return default_response_status or _default_http_method_statuses.get(http_method, 200)


def _set_default_response_status(func, status: int):
    _response_statuses[func] = status
