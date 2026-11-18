import winter.web


def web_application(*definitions, **kwargs) -> winter.web.WebApplication:
    """An application of classes and functions that a test defines in place, rather than in modules of their own."""
    app = winter.web.WebApplication(modules=[], **kwargs)
    app._definitions = definitions
    return app
