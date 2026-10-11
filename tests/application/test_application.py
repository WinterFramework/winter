import winter.application
import winter.components


def test_autodiscover():

    @winter.components.component
    class SimpleComponent:
        pass

    winter_app = winter.application.WinterApplication()

    winter_app.autodiscover()

    assert SimpleComponent in winter_app.components


def test_autodiscover_with_pre_add():

    class SimpleComponent:
        pass

    winter_app = winter.application.WinterApplication()
    winter_app.add_component(SimpleComponent)
    winter_app.autodiscover()

    assert SimpleComponent in winter_app.components
