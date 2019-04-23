from ..core import annotate


class NotNeedAuthentication:
    pass


def no_authentication(controller_class):
    return annotate(NotNeedAuthentication(), single=True)(controller_class)


def is_authentication_needed(component) -> bool:
    return component.annotations.get_one_or_none(NotNeedAuthentication) is None
