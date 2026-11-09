# Upgrading to Winter 34

A web application is composed explicitly in a `winter.web.WebApplication`, which imports every module of the
given packages and their subpackages on construction, and adapters build from it. `find_package_routes`,
`create_django_urls_from_routes`, `WinterApplication` and the `setup()` functions of `winter.web`, `winter.django`
and `winter.openapi` are gone.

```python
import service_a
import winter.django
import winter.web

app = winter.web.WebApplication(modules=[service_a], injector=injector)  # applications may share one injector
urlpatterns = winter.django.create_urls(app)
```

- `winter.django.create_urls(app, prefix='public-api/v1/')` serves an application under a path prefix, a path
  without a leading slash and with a trailing one, like the paths of routes. The routes of its requests carry the
  prefix, unlike the prefix of a Django `include`, which Winter does not see. `winter.django.route_of(request)`
  gives the route of a request, e.g. for a middleware to log `route.url_path`, `public-api/v1/orders/{order_id}/`,
  and None for a request that Winter does not serve. The `route` attribute of the view methods is gone.
- Django does not check CSRF on the views of Winter any more, as when Winter was built on DRF: CSRF matters only for
  a request authenticated by a cookie, and the application authenticates. An application authenticated by a Django
  session checks CSRF itself, in its authentication interceptor.
- An exception handler is a method marked with `@winter.web.exception_handler` whose first argument is
  annotated with the exceptions it handles; the class is created by the injector. `ExceptionHandler`,
  `exception_handlers_registry` with `add_handler` and `set_default_handler`, and the handler argument of
  `@raises` are gone: `@raises(Exc)` only declares the response for OpenAPI.

  ```python
  class FileStorageExceptionHandlers:
      @winter.web.exception_handler
      @winter.web.response_status(HTTPStatus.BAD_GATEWAY)
      def handle_download(self, exception: FileStorageDownloadException) -> ErrorDTO:
          ...
  ```

- Exception handlers belong to applications: a handler, like a `@problem` exception, handles exceptions in the
  applications whose definitions include it, in every endpoint, whether declared with `@raises` or not. An
  exception of another package belongs to the applications whose modules include its module, e.g.
  `winter.web.problem(status=404)(NotFoundException)` with `modules=[api, winter.ddd.exceptions]`.
  The handler of the nearest class in the exception's MRO handles it; two handlers of one exception class in an
  application fail on startup. A handler of the application replaces the built-in handler of the same exception
  class. An exception declared with `@raises` that only a handler of `Exception` would handle fails on startup,
  such as a `@problem` exception from a module the application does not include.
- Winter no longer answers 500 itself: an exception that no handler handles goes to the host, which logs it with its
  traceback and answers 500. Under Django, that is Django, as for any of its views: `got_request_exception` is sent,
  so Sentry sees the exception, `DEBUG` shows its page, and the test client raises it in the test. A WSGI server
  such as gunicorn does the same. A handler of `Exception` gives an application its own response instead. An
  exception raised by a handler is not handled again and goes to the host.
- Arguments come from the request or from the injector of the application, see [Values from the
  injector](../README.md#values-from-the-injector). Custom argument resolvers are gone: `ArgumentResolver`,
  `ArgumentsResolver`, `arguments_resolver`, `RequestBodyArgumentResolver`, `ResponseHeaderArgumentResolver`,
  `winter.web.pagination.PagePositionArgumentResolver` and `winter.django.HttpRequestArgumentResolver`. A resolver of a
  type becomes a provider of that type marked `@winter.web.request_scope`. An argument of an API method, an interceptor
  or an exception handler that is neither mapped from the request nor bound in the injector fails on startup instead of
  on the first request.
- Winter needs `injector` 0.21 or later. Each request has an injector of its own, a child of the injector of the
  application, and older versions create a `@singleton` class without a binding anew in every child injector, that
  is in every request.
- An argument named `response_headers` of an exception handler no longer receives the headers of the response:
  declare a `ResponseHeader[T]` with `@winter.web.response_header`, as in an API method.
- A response header is a `str`, an `int` or a `datetime`, the types HTTP has a format for: `ResponseHeader[T]` of
  another type fails with `TypeError` on import, so a UUID or an enum is set as a `str` (`str(uid)`, `status.value`).
  `set` checks the value against `T`. A `datetime` goes as an HTTP-date in GMT in every header, not as ISO 8601, and
  needs a time zone. `response_headers_serializer` and `ResponseHeaderSerializer` are gone.
- Interceptors belong to applications: `WebApplication(..., interceptors=[AuthorizationInterceptor, AuditInterceptor])`
  lists their classes in the order they run. The injector of each request creates them, so their dependencies go
  to `__init__`. `interceptor_registry` and `InterceptorRegistry` are gone. An argument named `method` of
  `pre_handle` no longer receives the API method: declare `route: winter.web.Route` and read `route.method`.
- Output processors are gone: `register_output_processor_resolver`, `IOutputProcessor`, `IOutputProcessorResolver`,
  `register_output_processor` and `winter.django.output_template`. An API method returns data, encoded as JSON
  (`@winter.json.json_encoder` adds the encoder of a type), or a `winter.web.Response`, e.g. a rendered template:
  `Response(HTTPStatus.OK, render_to_string('report.html', context).encode(), {'content-type': 'text/html'})`.
- The `meta` of a `Page` has no `previous` and `next` links any more, and `winter.web.pagination.utils` with
  `get_previous_page_url` and `get_next_page_url` is gone. A subclass of `Page` adds them where clients need them,
  see [Extending Page class](../README.md#extending-page-class).
- `winter.application.set_injector` and `get_injector` are gone: nothing in Winter takes the injector from a global.
  The request pipeline takes it from the application, and `winter.messaging`, `winter.ddd` and `winter.sqlalchemy`
  from the injector that creates their objects. `DomainEventDispatcher` takes the injector that creates the handlers:
  `DomainEventDispatcher(injector)`, or let the injector create it. Code that called `get_injector()` declares an
  `injector: Injector` argument of its `@inject` constructor instead.
- Throttling counts in the storage that the injector of the application binds,
  e.g. `binder.bind(ThrottlingStorage, to=RedisThrottlingStorage(configuration))`; an application with `@throttling`
  and no storage fails on startup. The Django adapter throttles by the Django user, by the client address otherwise.
  `set_throttling_storage` and `set_throttling_identity_resolver` are gone.
- `winter.web.throttling.reset(request, scope)` is gone: an API method with `@throttling` declares a
  `throttle: winter.web.Throttle` argument, and `throttle.reset()` forgets what the scope has counted for the sender:
  for the identity that the request was counted for, even if the method has logged the user in since.
- `register_native_response_type` is gone: an adapter passes the response types of its framework to `handle_request`.
  An API method may still return a Django response.
- OpenAPI: `generate_openapi(app, title=..., version=...)` returns the spec. It fails unless every `@problem` exception
  of the application is declared with `@raises` by one of its API methods or is a `@global_exception`, since Python does
  not declare the exceptions of a function; `allow_missing_raises_annotation` is gone. An exception declared with
  `@raises` and without a handler fails it, as it fails `create_urls`. The `validate` argument is gone: the spec is
  built of validated models, so validating it again could not fail. An API method of the application serves it, with the
  route and the annotations the application needs, such as its own authentication ones.
  `winter.openapi.swagger_ui_response(spec_url=...)` replaces `get_swagger_ui_html` and returns the page of Swagger UI.
  `serve_spec` and `serve_swagger_ui` are gone. The `servers` of the spec are relative to where the routes are served,
  so an application served under a prefix adds it:

  ```python
  @functools.cache
  def _spec() -> dict:
      spec = winter.openapi.generate_openapi(app, title='Public API', version='1')
      return {**spec, 'servers': [{'url': '/public-api' + server['url']} for server in spec['servers']]}

  class DocsAPI:
      @winter.web.route_get('openapi.json')
      def spec(self) -> dict:
          return _spec()  # generated on the first request

      @winter.web.route_get('docs/')
      def ui(self) -> winter.web.Response:
          return winter.openapi.swagger_ui_response(spec_url='/public-api/openapi.json')
  ```

- OpenAPI: `@winter.openapi.type_inspector(Answer)` replaces `register_type_inspector` and is a decorator only; it
  also describes the subclasses of the type. `register_global_exception` is gone: `@winter.openapi.global_exception`
  remains. The parameters of a route come from its path, query and `PagePosition` arguments only:
  `register_route_parameters_inspector`, `get_route_parameters_inspectors` and `winter.openapi.initialization` are
  gone, and the inspectors and `inspect_page` are no longer exported. A parameter that no argument stands for, such
  as a header read by a request-scoped provider, is added to the spec that `generate_openapi` returns.
- Decorators name what they declare: `@winter.json.register_encoder` is `@winter.json.json_encoder`, like
  `@winter.json.json_decoder`, and `@winter.web.register_url_regexp` is `@winter.web.url_regexp`.
- `@winter.web.query_parameters`: a missing parameter takes the default of its field, or None for an `Optional`
  field, and the request fails with 400 for a missing required parameter or a value that does not decode, as for a
  query parameter of an argument. It was a 500.
- A path parameter is decoded as a query parameter is: a `date` or an `IntEnum` in the path works, and a value of a
  wrong form is a 400 instead of a 500. A class of a path parameter that was created by calling it with the string
  needs a `@winter.json.json_decoder`, as in a query parameter.
- Event handlers are found in modules, as by `WebApplication`: `add_handlers_from_modules([myproject])` of
  `DomainEventDispatcher` replaces `add_handlers_from_package('myproject')`, and of `EventSubscriptionRegistry`
  replaces `autodiscover('myproject')`. `winter.application.module_discovery.get_all_classes` is gone.
- `EventDispatcher` is imported from `winter.messaging`: the module `winter.messaging.event_dispacher` is gone.
