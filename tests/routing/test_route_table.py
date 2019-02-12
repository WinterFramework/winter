import winter
from winter.routing import route_table, Route


@winter.controller
@winter.route('/route_tables')
class Controller1:
    @winter.route_get('/')
    def get_list(self):
        pass

    @winter.route_get('/{id}/')
    def get_detail(self):
        pass


@winter.controller
class Controller2:
    @winter.route_post('/route_tables/')
    def create(self):
        pass


def test_route_table_collects_routes():
    routes = route_table.get_routes()

    assert Route(url_path='/route_tables/', http_method='GET') in routes
    assert Route(url_path='/route_tables/', http_method='POST') in routes
    assert Route(url_path='/route_tables/{id}/', http_method='GET') in routes
