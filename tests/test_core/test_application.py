import gc

import winter.core


def test_autodiscover():
    gc.collect()

    @winter.core.component
    class SimpleComponent:
        pass

    winter_app = winter.core.WinterApplication()

    winter_app.autodiscover()

    assert list(winter_app.components) == [SimpleComponent]


def test_autodiscover_with_pre_add():
    gc.collect()

    @winter.core.component
    class SimpleComponent:
        pass

    winter_app = winter.core.WinterApplication()
    winter_app.add_component(SimpleComponent)
    winter_app.autodiscover()

    assert list(winter_app.components) == [SimpleComponent]
