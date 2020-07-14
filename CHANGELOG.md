# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
