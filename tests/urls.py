import winter_django

from . import controllers
from . import drf

urlpatterns = [
    *winter_django.create_django_urls(controllers.NoAuthenticationController),
    *winter_django.create_django_urls(controllers.SimpleController),
    *winter_django.create_django_urls(controllers.ControllerWithExceptions),
    *winter_django.create_django_urls(controllers.ControllerWithProblemExceptions),
    *winter_django.create_django_urls(controllers.ControllerWithMediaTypesRouting),
    *winter_django.create_django_urls(drf.ControllerWithOutputTemplate),
    *winter_django.create_django_urls(controllers.ControllerWithPathParameters),
    *winter_django.create_django_urls(controllers.ControllerWithQueryParameters),
    *winter_django.create_django_urls(controllers.ControllerWithResponseHeaders),
    *winter_django.create_django_urls(drf.ControllerWithSerializer),
    *winter_django.create_django_urls(controllers.ControllerWithThrottling),
    *winter_django.create_django_urls(controllers.ControllerWithLimits),
    *winter_django.create_django_urls(controllers.ControllerWithRequestData),
]
