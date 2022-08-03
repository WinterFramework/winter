import winter_django

from . import api
from . import drf

urlpatterns = [
    *winter_django.create_django_urls(api.APIWithNoAuthentication),
    *winter_django.create_django_urls(api.SimpleAPI),
    *winter_django.create_django_urls(api.APIWithExceptions),
    *winter_django.create_django_urls(api.APIWithProblemExceptions),
    *winter_django.create_django_urls(api.APIWithMediaTypesRouting),
    *winter_django.create_django_urls(drf.APIWithOutputTemplate),
    *winter_django.create_django_urls(api.APIWithPathParameters),
    *winter_django.create_django_urls(api.APIWithQueryParameters),
    *winter_django.create_django_urls(api.APIWithResponseHeaders),
    *winter_django.create_django_urls(drf.APIWithSerializer),
    *winter_django.create_django_urls(api.APIWithThrottling),
    *winter_django.create_django_urls(api.APIWithLimits),
    *winter_django.create_django_urls(api.APIWithRequestData),
]
