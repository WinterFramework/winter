from openapi_pydantic import Components as Components310
from openapi_pydantic import Contact as Contact310
from openapi_pydantic import Discriminator as Discriminator310
from openapi_pydantic import Encoding as Encoding310
from openapi_pydantic import Example as Example310
from openapi_pydantic import ExternalDocumentation as ExternalDocumentation310
from openapi_pydantic import Header as Header310
from openapi_pydantic import Info as Info310
from openapi_pydantic import License as License310
from openapi_pydantic import Link as Link310
from openapi_pydantic import MediaType as MediaType310
from openapi_pydantic import OAuthFlow as OAuthFlow310
from openapi_pydantic import OAuthFlows as OAuthFlows310
from openapi_pydantic import OpenAPI as OpenAPI310
from openapi_pydantic import Operation as Operation310
from openapi_pydantic import Parameter as Parameter310
from openapi_pydantic import PathItem as PathItem310
from openapi_pydantic import Reference as Reference310
from openapi_pydantic import RequestBody as RequestBody310
from openapi_pydantic import Response as Response310
from openapi_pydantic import Schema as Schema310
from openapi_pydantic import SecurityScheme as SecurityScheme310
from openapi_pydantic import Server as Server310
from openapi_pydantic import ServerVariable as ServerVariable310
from openapi_pydantic import Tag as Tag310
from openapi_pydantic import XML as XML310
from openapi_pydantic.v3.v3_0_3 import Components as Components303
from openapi_pydantic.v3.v3_0_3 import Contact as Contact303
from openapi_pydantic.v3.v3_0_3 import Discriminator as Discriminator303
from openapi_pydantic.v3.v3_0_3 import Encoding as Encoding303
from openapi_pydantic.v3.v3_0_3 import Example as Example303
from openapi_pydantic.v3.v3_0_3 import ExternalDocumentation as ExternalDocumentation303
from openapi_pydantic.v3.v3_0_3 import Header as Header303
from openapi_pydantic.v3.v3_0_3 import Info as Info303
from openapi_pydantic.v3.v3_0_3 import License as License303
from openapi_pydantic.v3.v3_0_3 import Link as Link303
from openapi_pydantic.v3.v3_0_3 import MediaType as MediaType303
from openapi_pydantic.v3.v3_0_3 import OAuthFlow as OAuthFlow303
from openapi_pydantic.v3.v3_0_3 import OAuthFlows as OAuthFlows303
from openapi_pydantic.v3.v3_0_3 import OpenAPI as OpenAPI303
from openapi_pydantic.v3.v3_0_3 import Operation as Operation303
from openapi_pydantic.v3.v3_0_3 import Parameter as Parameter303
from openapi_pydantic.v3.v3_0_3 import PathItem as PathItem303
from openapi_pydantic.v3.v3_0_3 import Reference as Reference303
from openapi_pydantic.v3.v3_0_3 import RequestBody as RequestBody303
from openapi_pydantic.v3.v3_0_3 import Response as Response303
from openapi_pydantic.v3.v3_0_3 import Schema as Schema303
from openapi_pydantic.v3.v3_0_3 import SecurityScheme as SecurityScheme303
from openapi_pydantic.v3.v3_0_3 import Server as Server303
from openapi_pydantic.v3.v3_0_3 import ServerVariable as ServerVariable303
from openapi_pydantic.v3.v3_0_3 import Tag as Tag303
from openapi_pydantic.v3.v3_0_3 import XML as XML303
from pydantic import Extra

from winter.data.pagination import Page
from winter.web.exceptions import RequestDataDecodeException
from winter.web.exceptions import ThrottleException
from winter.web.exceptions import UnsupportedMediaTypeException
from winter.web.pagination import PagePositionArgumentResolver
from winter.web.pagination.limits import MaximumLimitValueExceeded
from .annotations import global_exception
from .annotations import register_global_exception
from .generator import generate_openapi
from .inspection.inspection import inspect_type
from .inspection.inspection import register_type_inspector
from .inspectors import PagePositionArgumentsInspector
from .inspectors import PathParametersInspector
from .inspectors import QueryParametersInspector
from .inspectors import RouteParametersInspector
from .inspectors import get_route_parameters_inspectors
from .inspectors import inspect_page
from .inspectors import register_route_parameters_inspector
from .swagger_ui import get_swagger_ui_html
from .validators import validate_missing_raises_annotations


def setup(allow_missing_raises_annotation: bool = False):
    __ignore_extra_openapi_pydantic_303()
    __ignore_extra_openapi_pydantic_310()
    register_global_exception(MaximumLimitValueExceeded)
    register_global_exception(ThrottleException)
    register_global_exception(RequestDataDecodeException)
    register_global_exception(UnsupportedMediaTypeException)
    register_type_inspector(Page, func=inspect_page)
    register_route_parameters_inspector(PathParametersInspector())
    register_route_parameters_inspector(QueryParametersInspector())
    register_route_parameters_inspector(PagePositionArgumentsInspector(PagePositionArgumentResolver()))
    if not allow_missing_raises_annotation:  # pragma: no cover
        validate_missing_raises_annotations()


def __ignore_extra_openapi_pydantic_303():
    XML303.Config.extra = Extra.ignore
    Components303.Config.extra = Extra.ignore
    Contact303.Config.extra = Extra.ignore
    Discriminator303.Config.extra = Extra.ignore
    Encoding303.Config.extra = Extra.ignore
    Example303.Config.extra = Extra.ignore
    ExternalDocumentation303.Config.extra = Extra.ignore
    Header303.Config.extra = Extra.ignore
    Info303.Config.extra = Extra.ignore
    License303.Config.extra = Extra.ignore
    Link303.Config.extra = Extra.ignore
    MediaType303.Config.extra = Extra.ignore
    OAuthFlow303.Config.extra = Extra.ignore
    OAuthFlows303.Config.extra = Extra.ignore
    OpenAPI303.Config.extra = Extra.ignore
    Operation303.Config.extra = Extra.ignore
    Parameter303.Config.extra = Extra.ignore
    PathItem303.Config.extra = Extra.ignore
    Reference303.Config.extra = Extra.ignore
    RequestBody303.Config.extra = Extra.ignore
    Response303.Config.extra = Extra.ignore
    Schema303.Config.extra = Extra.ignore
    SecurityScheme303.Config.extra = Extra.ignore
    Server303.Config.extra = Extra.ignore
    ServerVariable303.Config.extra = Extra.ignore
    Tag303.Config.extra = Extra.ignore


def __ignore_extra_openapi_pydantic_310():
    XML310.Config.extra = Extra.ignore
    Components310.Config.extra = Extra.ignore
    Contact310.Config.extra = Extra.ignore
    Discriminator310.Config.extra = Extra.ignore
    Encoding310.Config.extra = Extra.ignore
    Example310.Config.extra = Extra.ignore
    ExternalDocumentation310.Config.extra = Extra.ignore
    Header310.Config.extra = Extra.ignore
    Info310.Config.extra = Extra.ignore
    License310.Config.extra = Extra.ignore
    Link310.Config.extra = Extra.ignore
    MediaType310.Config.extra = Extra.ignore
    OAuthFlow310.Config.extra = Extra.ignore
    OAuthFlows310.Config.extra = Extra.ignore
    OpenAPI310.Config.extra = Extra.ignore
    Operation310.Config.extra = Extra.ignore
    Parameter310.Config.extra = Extra.ignore
    PathItem310.Config.extra = Extra.ignore
    Reference310.Config.extra = Extra.ignore
    RequestBody310.Config.extra = Extra.ignore
    Response310.Config.extra = Extra.ignore
    Schema310.Config.extra = Extra.ignore
    SecurityScheme310.Config.extra = Extra.ignore
    Server310.Config.extra = Extra.ignore
    ServerVariable310.Config.extra = Extra.ignore
    Tag310.Config.extra = Extra.ignore
