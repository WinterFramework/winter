import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import TypeAlias
from uuid import UUID

import winter

ArrayAlias: TypeAlias = list[int]


@winter.route('with-query-parameter')
class APIWithQueryParameters:

    @winter.map_query_parameter('string', to='mapped_string')
    @winter.route_get('/{?date,boolean,optional_boolean,optional_boolean_new_typing_style,date_time,array,array_new_typing_style,array_alias,expanded_array*,string,uid}')
    def root(
        self,
        date: datetime.date,
        date_time: datetime.datetime,
        boolean: bool,
        array: List[int],
        array_new_typing_style: list[int],
        array_alias: ArrayAlias,
        expanded_array: List[str],
        mapped_string: str,
        uid: UUID,
        optional_boolean: Optional[bool] = None,
        optional_boolean_new_typing_style: bool | None = None,
    ) -> dict[str, Any]:
        return {
            'date': date,
            'date_time': date_time,
            'boolean': boolean,
            'optional_boolean': optional_boolean,
            'optional_boolean_new_typing_style': optional_boolean_new_typing_style,
            'array': array,
            'array_new_typing_style': array_new_typing_style,
            'array_alias': array_alias,
            'expanded_array': expanded_array,
            'string': mapped_string,
            'uid': str(uid),
        }
