import winter
from winter.pagination import PagePosition


@winter.route('with-limits/')
class ControllerWithLimits:

    @winter.route_get('')
    @winter.pagination.limits(default=20, maximum=100, redirect_to_default=True)
    def method(self, page_position: PagePosition):
        return {
            'limit': page_position.limit,
            'offset': page_position.offset,
        }
