from winter.core import annotate


class NotNeedAuthentication:
    pass


class CsrfExempt:
    pass


def no_authentication(api_class):
    return annotate(NotNeedAuthentication(), single=True)(api_class)


def csrf_exempt(api_class):
    return annotate(CsrfExempt(), single=True)(api_class)


def is_authentication_needed(component) -> bool:
    return component.annotations.get_one_or_none(NotNeedAuthentication) is None


def is_csrf_needed(component) -> bool:
    return component.annotations.get_one_or_none(CsrfExempt) is None
