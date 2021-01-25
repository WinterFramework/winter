from winter.web import get_instance
from winter.web import set_factory


class App:
    pass


class Controller:
    def __init__(self, app: App = None):
        self.app = app


def test_default_get_instance():
    # Act
    controller = get_instance(Controller)

    # Assert
    assert controller.app is None


def test_get_instance():
    app = App()

    def factory(cls):
        return cls(app)

    set_factory(factory)
    try:
        # Act
        controller = get_instance(Controller)

        # Assert
        assert isinstance(controller, Controller)
        assert controller.app is app
    finally:
        set_factory(None)
