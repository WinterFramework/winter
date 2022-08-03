# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
