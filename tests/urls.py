import winter.django

from . import controllers

urlpatterns = [
    *winter.django.create_django_urls(controllers.NoAuthenticationController),
    *winter.django.create_django_urls(controllers.SimpleController),
    *winter.django.create_django_urls(controllers.ControllerWithExceptions),
    *winter.django.create_django_urls(controllers.ControllerWithMediaTypesRouting),
    *winter.django.create_django_urls(controllers.ControllerWithOutputTemplate),
    *winter.django.create_django_urls(controllers.ControllerWithPathParameters),
    *winter.django.create_django_urls(controllers.ControllerWithQueryParameters),
    *winter.django.create_django_urls(controllers.ControllerWithResponseHeaders),
    *winter.django.create_django_urls(controllers.ControllerWithSerializer),
    *winter.django.create_django_urls(controllers.ControllerWithThrottling),
    *winter.django.create_django_urls(controllers.ControllerWithLimits),
    *winter.django.create_django_urls(controllers.ControllerWithRequestData),
]
