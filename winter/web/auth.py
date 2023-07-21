from winter.core import annotate


class NotNeedAuthentication:
    pass


class CsrfExempt:
    pass


def no_authentication(api_class):
    return annotate(NotNeedAuthentication(), single=True)(api_class)


def csrf_exempt(api_method):
    return annotate(CsrfExempt(), single=True)(api_method)

