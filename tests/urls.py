import winter

from . import controllers

urlpatterns = [
    *winter.django.create_django_urls(controllers.SimpleController),
]
