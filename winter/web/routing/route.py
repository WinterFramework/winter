import re
from typing import List
from typing import Set

import uritemplate
from uritemplate import URITemplate
from uritemplate.variable import Operator

from winter.core import ComponentMethod
from winter.web.query_parameters import MapQueryParameterAnnotation
from winter.web.query_parameters.query_parameter import QueryParameter

_remove_query_params_regexp = re.compile(r'{\?[^}]*}')


class Route:

    def __init__(
        self,
        http_method: str,
        url_path_with_query_parameters: str,
        method: ComponentMethod,
    ):
        self._url_path_with_query_parameters = url_path_with_query_parameters
        self.method = method
        self.http_method = http_method

    @property
    def url_path(self):
        return _remove_query_params_regexp.sub('', self._url_path_with_query_parameters)

    def get_path_variables(self) -> Set[str]:
        return uritemplate.variables(self.url_path)

    def get_query_parameters(self) -> List[QueryParameter]:
        query_parameters = []
        map_query_parameters_annotations = self.method.annotations.get(MapQueryParameterAnnotation)
        map_to_by_names = {
            map_query_parameter.name: map_query_parameter.map_to
            for map_query_parameter in map_query_parameters_annotations
        }

        query_variables = (
            variable
            for variable in URITemplate(self._url_path_with_query_parameters).variables
            if variable.operator == Operator.form_style_query
        )
        for variable in query_variables:
            for variable_name, variable_params in variable.variables:
                map_to = map_to_by_names.get(variable_name, variable_name)
                query_parameter = QueryParameter(
                    name=variable_name,
                    map_to=map_to,
                    explode=variable_params['explode'],
                )
                query_parameters.append(query_parameter)
        return query_parameters
