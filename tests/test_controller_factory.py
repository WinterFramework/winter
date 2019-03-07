from winter.controller import build_controller
from winter.controller import set_controller_factory


class App:
    pass


class Controller:

    def __init__(self, app: App = None):
        self.app = app


def test_default_controller_factory():
    # Act
    controller = build_controller(Controller)

    # Assert
    assert controller.app is None


def test_controller_factory():
    app = App()

    def controller_factory(cls):
        return cls(app)

    set_controller_factory(controller_factory)
    try:
        # Act
        controller = build_controller(Controller)

        # Assert
        assert isinstance(controller, Controller)
        assert controller.app is app
    finally:
        set_controller_factory(None)
