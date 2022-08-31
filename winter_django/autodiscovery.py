import winter_django
from winter.core.module_discovery import import_recursively
from winter.core.module_discovery import get_all_classes


def create_django_urls_for_package(package_name: str):
    import_recursively(package_name)
    uripatterns = []
    for class_name, cls in get_all_classes(package_name):
        uripatterns += winter_django.create_django_urls(cls)
    return uripatterns
