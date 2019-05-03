import datetime

import winter


@winter.controller
@winter.route('with-query-parameter')
class ControllerWithQueryParameters:

    @winter.query_parameter('date')
    @winter.query_parameter('boolean')
    @winter.query_parameter('date_time')
    @winter.route_get('/')
    def root(
            self,
            date: datetime.date,
            date_time: datetime.datetime,
            boolean: bool,
    ) -> dict:
        return {
            'date': date,
            'date_time': date_time,
            'boolean': boolean,
        }
