_no_authentication_controller_classes = set()


def no_authentication(controller_class):
    _register_no_authentication_controller(controller_class)
    return controller_class


def is_authentication_needed(controller_class) -> bool:
    return controller_class not in _no_authentication_controller_classes


def _register_no_authentication_controller(controller_class):
    _no_authentication_controller_classes.add(controller_class)
