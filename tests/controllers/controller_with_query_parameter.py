import datetime
from typing import Optional

import winter


@winter.controller
@winter.route('with-query-parameter')
class ControllerWithQueryParameters:

    @winter.query_parameter('date')
    @winter.query_parameter('boolean')
    @winter.query_parameter('optional_boolean')
    @winter.query_parameter('date_time')
    @winter.route_get('/')
    def root(
            self,
            date: datetime.date,
            date_time: datetime.datetime,
            boolean: bool,
            optional_boolean: Optional[bool] = None,
    ) -> dict:
        return {
            'date': date,
            'date_time': date_time,
            'boolean': boolean,
            'optional_boolean': optional_boolean,
        }
