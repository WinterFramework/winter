import datetime
from typing import Any

from typing import Dict
from typing import List
from typing import Optional

import winter


@winter.controller
@winter.route('with-query-parameter')
class ControllerWithQueryParameters:

    @winter.map_query_parameter('string', to='mapped_string')
    @winter.route_get('/{?date,boolean,optional_boolean,date_time,array,expanded_array*,string}')
    def root(
        self,
        date: datetime.date,
        date_time: datetime.datetime,
        boolean: bool,
        array: List[int],
        expanded_array: List[str],
        mapped_string: str,
        optional_boolean: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return {
            'date': date,
            'date_time': date_time,
            'boolean': boolean,
            'optional_boolean': optional_boolean,
            'array': array,
            'expanded_array': expanded_array,
            'string': mapped_string,
        }
