import winter
from winter.pagination import PagePosition
from winter.pagination import RedirectToDefaultLimitException


@winter.route('with-limits/')
class ControllerWithLimits:

    @winter.route_get('with-redirect-to-default/')
    @winter.pagination.limits(default=20, maximum=100, redirect_to_default=True)
    @winter.throws(RedirectToDefaultLimitException)  # TODO: add auto throws here
    def with_redirect_to_default(self, page_position: PagePosition):
        return {
            'limit': page_position.limit,
            'offset': page_position.offset,
        }
