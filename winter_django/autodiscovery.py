import winter_django

from winter.core import ModuleDiscovery


def create_django_urls_for_package(package_name: str):
    ModuleDiscovery().import_recursively(package_name)
    uripatterns = []
    for class_name, cls in ModuleDiscovery().get_all_classes(package_name):
        uripatterns += winter_django.create_django_urls(cls)
    return uripatterns
