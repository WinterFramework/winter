# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [30.0.0] - 2025-02-27
- Dropped support of Python earlier than 3.11
- Dropped support of Django earlier than 4.2
- Dropped support of SQLAlchemy earlier than 1.4
- Added support of Python 3.13
- Reviewed new typing-related things since Python 3.8:
    - Added support of `Union[A, B]` → `A | B`
    - Added support of `List[T]` → `list[T]`, `Dict[K, V]` → `dict[K, V]`, etc.
    - Reviewed `Never` and `NoReturn` types - they are only for forever-looping functions, no sense to add their support
    - Reviewed `Self` return type support - not suitable for endpoints, they do not return classes
    - Added test for `TypeAlias` 
    - Reviewed `TypeGuard` - not suitable for endpoints
    - Reviewed `LiteralString` - not suitable for endpoints, they usually return strings
    - Reviewed `Concatenate` - not suitable for endpoints
    - Added test for `TypedDict`
- Added tests of new typing features for event system 

## [29.0.2] - 2025-02-07
- Add support of UnionType in OpenAPI schema

## [29.0.1] - 2024-12-12
- Make httpx version specification less restrictive

## [29.0.0] - 2024-12-12
- Downgrade manifested openapi version to 3.0.3

## [28.0.0] - 2024-11-05
- Update to openapi-pydantic 0.5.0

## [26.0.1] - 2024-08-15
- Remove unexpected openapi attributes from path and query parameters

## [26.0.0] - 2024-08-12
- Do not ignore unexpected openapi attributes anymore

## [25.0.2] - 2024-08-01
- Fix openapi schema sharing for Page types

## [25.0.1] - 2024-07-28
- Fix openapi schema sharing between optional and non-optional types

## [25.0.0] - 2024-07-26
- Schemas extracted to OpenAPI components, are always referenced
- Better nullable handling in OpenAPI schemas

## [24.0.1] - 2024-07-23
- Added support of Python 3.12
- Replaced openapi-schema-pydantic with openapi-pydantic

## [24.0.0] - 2024-07-09
- Get rid of Configurer

## [23.0.0] - 2024-07-08
- Bump dateutils and typing-extensions versions, drop Python 3.7 support

## [22.2.0] - 2024-07-06
- Add `add_url_segment_as_tag` boolean parameter to generate_openapi function to disable adding url segment as tag in OpenAPI

## [22.1.1] - 2024-06-17
### Bugfixes
- Add OpenAPI inspector for `@winter.web.query_parameters` case

## [22.1.0] - 2024-06-13
### Added

- Add `@winter.web.query_parameters` decorator to inject query parameters into a single method argument

## [22.0.0] - 2024-05-07
### Changed

- Delete `winter_ddd.global_domain_event_dispatcher`
- It's now application responsibility to configure `DomainEventDispatcher`
- For convenience there are a number of methods in `DomainEventDispatcher` class to add handlers
- It's not a final form as it requires a lot of manual effort and configuration, so more changes to come

## [21.0.0] - 2024-04-22
### Changed

- Add `EventPublisher.emit_many` method to emit multiple events at once
- Refactor `EventDispatcher` to dispatch events as a list or as a single event depending on handler argument type

## [20.0.1] - 2024-04-02
### Bugfixes
- get_previous_page_url and get_next_page_url fixed

## [20.0.0] - 2024-04-01
### Bugfixes
- Vulnerability fix: remove the X-Forwarded-Host/X-Host header values from next/previous page links in Page response

## [19.0.6] - 2023-09-26
### Bugfixes
- Generated OpenAPI JSON file now have no differences if generation is called multiple times

## [19.0.0] - 2023-07-21
### Changed
- DRF request and response are replaced with Django HttpRequest and HttpResponse
- Default Authorization and CSRF protection are removed from the framework
- Always encode decimals as strings despite COERCE_DECIMAL_TO_STRING setting
- Removed: JSONRenderer, create_django_urls_for_package, create_django_urls, @no_authentication, @csrf_exempt
- Removed djangorestframework from dependencies

## [18.0.0] - 2023-06-25
### Changed
- OpenAPI updated to version 3.0.3

### Deprecation
- DRF serializers are not supported anymore, use dataclasses instead. Classes and annotations deleted: PageSerializer, BodyWithContext, @input_serializer, @output_serializer
- drf_yasg deleted from dependencies

## [17.0.5] - 2023-06-15
### Bugfixes
- Fixed missing `collectionFormat` field in a OpenAPI schema for query array parameters

## [17.0.3] - 2023-06-02
### Added
- Add winter.core.json.Undefined class to represent absence of value in JSON object

## [17.0.2] - 2023-05-31
### Bugfixes
- @winter.web.csrf_exempt: fixed bug with csrf_exempt decorator for old views

## [17.0.0] - 2023-05-18
### Changed
- winter.core.module_discovery functions are now generators, package is no longer optional

## [16.0.2] - 2023-01-25
### Added
- @winter.web.csrf_exempt: this decorator marks api class as being exempt from the protection ensured by the middleware

## [16.0.1] - 2023-04-12
### Bugfixes
- Fixed specification of optional properties in OpenAPI schema for models, which used as input parameters

## [16.0.0] - 2023-04-04
### Changed
- Duplicate model names for different models don't appear in OpenAPI schema anymore - `PageMeta` renamed to `PageMetaOf{PageName}`, models in input parameters now have the suffix `Input`  

## [15.2.2] - 2023-02-23
### Added
- winter_django.create_django_urls_from_routes: function that returns a list of django urls by the list of Routes 

## [15.2.1] - 2023-02-16
### Changed
- winter.messaging: set frozen=true for Event class

## [15.2.0] - 2023-02-15
### Added
- winter.web.throttling: function allows to reset the accumulated throttling state for a specific user and scope

## [15.0.1] - 2023-02-03
### Added
- winter.web.find_package_routes: function that returns a list of routes by the package name 

## [15.0.0] - 2023-02-01
### Changed
- winter.messaging: EventBus interface segregated and renamed to EventPublisher
### Bugfixes
- Fixed generation of the default parameter for `order_by` OpenAPI descriptions

## [14.1.0] - 2022-12-15
### Added
- Long (multi-line) description from operation method docstring is included in the OpenAPI Operation description
- Docstrings for dataclasses and their attributes are converted to corresponding OpenAPI descriptions

## [14.0.0] - 2022-12-13
### Removed
- Python 3.6 is no longer supported
### Added
- Sequence added to json decoder

## [13.0.2] - 2022-11-23
### Bugfixes
- Fixed but with dependency

## [13.0.1] - 2022-11-23
### Bugfixes
- Fixed but with dependency

## [13.0.0] - 2022-11-23
### Added
- winter.messaging: EventBus interface added, SimpleEventBus implemented

## [12.0.0]
### Changed
- Adjust response body to comply with RFC7807 when request data decoding fails

## [11.0.0]
### Added
- get_all_subclasses function in module_discovery module
### Changed
- Refactor ModuleDiscovery to functions

## [10.0.1]
- Register ThrottleException as a global to simplify projects without throttling
- Add Swagger UI which do not rely on drf_yasg and static file server: winter_openapi.get_swagger_ui_html

## [10.0.0]

- Delete @winter.web.controller
- Delete get_component function in favor of direct Component.get_by_cls
- Rename register_controller_method_inspector to register_route_parameters_inspector
- Rename MethodArgumentsInspector to RouteParametersInspector

## [9.6.4] - 2022-08-01
### Added 
- winter_openapi: add support of StrEnum: now StrEnum will be recognized as Enum, not as simple string

## [9.6.3] - 2022-07-15
### Added 
- winter_sqlalchemy add sort method: extract sort method from paginate to apply only order_by

## [9.6.2] - 2022-07-08

winter_openapi: add more information about nested type to Page type title,
for example Page[NestedType] -> PageOfNestedType

## [9.6.1] - 2022-07-04

Return 400 Bad Request instead of 500 if UUID request parameter has a newline character in the end

## [9.6.0] - 2022-06-22

Return 400 Bad Request instead of 500 if UUID request parameter is malformed

## [9.5.6] - 2022-06-16

Fix cyclic imports caused by DRF importing external renderer classes during import

## [9.5.5] - 2022-06-13

Generate titles for dataclass-generated openapi schemas

## [9.5.4] - 2022-06-11

Fix bug in winter_openapi: nested required dataclass fields weren't marked as required.

## [9.5.3] - 2022-06-08

Fix bug in winter_openapi: required dataclass fields weren't marked as required.

## [9.4.1] - 2021-09-16

Change build system to poetry

## [9.4.0] - 2021-06-28

Update sqlalchemy to 1.4.0+

## [9.3.0] - 2021-06-21

### New features
- winter.core.ModuleDiscovery is added
- winter_django.autodiscovery.create_django_urls_for_package(package_name) is added

## [9.2.0] - 2021-06-01

### Bugfixes
- get_injector() is called lazily

## [9.1.0] - 2021-06-01

### Bugfixes
- global_domain_event_dispatcher now lazily loads injector which could be empty if importing too early

## [9.0.0] - 2021-03-31

### New features
- CRUDRepository now supports custom implementation extensions
### Changed
- set_factory changed to set_injector
- DomainEventDispatcher.set_handler_factory is deleted

## [8.2.0] - 2021-01-27

### New features
- optional method argument added to interceptors

## [8.0.0] - 2021-01-25

### New features
- winter.web now supports interceptors
- winter.web now supports configurers
### Changed
- winter.web.set_controller_factory renamed to winter.web.set_factory

## [7.0.0] - 2020-12-08

### New features
- winter_openapi add annotation @winter_openapi.global_exception
- winter_openapi add validation check for missing exceptions
### Changed
- winter.web rename annotation @winter.throws → @winter.raises
- winter.web remove argument for problem annotation `auto_handle` and define default as True


## [5.0.0] - 2020-10-25

### New features
- winter.web now supports problem annotation and handling exceptions accordingly with RFC7807  
### Changed
- Setting winter requires an explicit call to setup functions

## [4.1.1] - 2020-10-06

### Fixed
- Fix building a django url pattern for methods with multiple parameters in url_path

## [4.1.0] - 2020-07-15

### New features
- winter.web now supports Page-inherited classes. Extra fields are put to meta during serialization.

## [4.0.0] - 2020-07-14

### Changed
- process_domain_events replaced with global_domain_event_dispatcher.dispatch
- Add support for Union[Event1, Event2, ...] and List[Union[Event1, Event2, ...]] domain event handlers

## [3.0.0] - 2020-06-30

### Changed
- winter.pagination classes (Page, PagePosition, Order, Sort, SortDirection) moved to winter.data.pagination
- winter.json_encoder things (e.g. register_encoder) moved to winter.core.json
- winter.json_renderer.JSONRenderer moved to winter.django.drf.renderers.JSONRenderer
- winter.converters moved to winter.core.json.decoder
- argument_resolver, controller, output_processor are now part of winter.web. Import paths are preserved.
- winter.routing moved to winter.web.routing
- winter.exceptions moved to winter.web.exceptions
- PositiveInteger moved to winter.code.utils
- Move type_utils to winter.core.utils.typing
- Extract winter.schema to winter_openapi (winter_openapi.setup should be called manually now)
- Extract winter.drf and winter.django to winter_django (JSONRenderer moved to winter_django.renderers.JSONRenderer)
