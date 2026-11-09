# Upgrading to Winter 33

`winter` is a namespace package now: the `import winter` facade is gone, use `winter.web` instead
(`@winter.web.route_get(...)`). `winter_openapi`, `winter_django`, `winter_sqlalchemy`, `winter_ddd`,
`winter.core` and `winter.data` are gone; their contents live under `winter.<package>` as described in
[architecture.md](architecture.md). A codemod rewrites a code base, preserving formatting:

```
pip install libcst
python tools/migrate_to_33.py path/to/your/project
```

`winter.web` does not depend on Django any more. What the codemod cannot do for you:

- Custom `ArgumentResolver`, `IOutputProcessor`, `ExceptionMapper` and `Interceptor` implementations receive
  `winter.web.Request` instead of `django.http.HttpRequest`: `request.query_parameters`, `request.headers`,
  `request.body`, `request.path_parameters`, `request.full_path`. API methods that declare a `HttpRequest`
  argument still get the Django request. `winter.web.throttling.reset`, `get_next_page_url` and
  `get_previous_page_url` from `winter.web.pagination.utils` take a `winter.web.Request` too.
- Raw responses: return `winter.web.Response(status_code, body=bytes, headers={...})`; returning a Django
  `HttpResponse` still works under the Django adapter.
- `winter.ddd.NotFoundException` is not mapped to HTTP 404 by the framework. Add
  `winter.web.problem(status=404)(NotFoundException)` before `winter.web.setup()`.
- Throttling storage is explicit: `winter.web.set_throttling_storage(RedisThrottlingStorage(configuration))`
  from `winter.redis.throttling`, or `InMemoryThrottlingStorage()` for a single process.
- `Request` has no `user`. Who gets throttled is decided by the identity resolver: `winter.django.setup()`
  installs one that uses the Django user, `winter.web.set_throttling_identity_resolver` replaces it.
