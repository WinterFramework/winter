

def setup():
    from winter.core import get_injector
    from .injector_config import MessagingConfiguration

    injector = get_injector()
    injector.binder.install(MessagingConfiguration())

