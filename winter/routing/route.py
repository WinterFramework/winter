import typing

import dataclasses
import uritemplate

from ..core import ComponentMethod
from ..core import ComponentMethodArgument
from ..core import cached_property
from ..http import MediaType
from ..query_parameter import QueryParameterAnnotation


@dataclasses.dataclass(frozen=True)
class Route:
    http_method: str
    url_path: str
    method: ComponentMethod
    produces: typing.Tuple[MediaType] = None
    consumes: typing.Tuple[MediaType] = None

    @cached_property
    def _path_variables(self):
        return uritemplate.variables(self.url_path)

    def has_path_variable(self, name: str):
        return name in self._path_variables

    @cached_property
    def path_arguments(self) -> typing.List[ComponentMethodArgument]:
        path_arguments = []
        for path_variable in self._path_variables:
            argument = self.method.get_argument(path_variable)
            if argument is not None:
                path_arguments.append(argument)
        return path_arguments

    @cached_property
    def query_arguments(self) -> typing.List[typing.Tuple[ComponentMethodArgument, str]]:
        query_arguments = []

        annotations = self.method.annotations.get(QueryParameterAnnotation)

        for query_parameter_annotation in annotations:
            argument = self.method.get_argument(query_parameter_annotation.map_to)
            if argument is not None:
                query_arguments.append((argument, query_parameter_annotation.name))
        return query_arguments
