"""Deprecated since 33.0, removed in 34.0. See winter.components, winter.application and winter.json."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter.core', 'winter.components, winter.application and winter.json')
alias_modules(
    exact={
        'winter.core.annotation_decorator': 'winter.components.annotation_decorator',
        'winter.core.annotations': 'winter.components.annotations',
        'winter.core.component': 'winter.components.component',
        'winter.core.component_method': 'winter.components.component_method',
        'winter.core.component_method_argument': 'winter.components.component_method_argument',
        'winter.core.docstring': 'winter.components.docstring',
        'winter.core.application': 'winter.application.application',
        'winter.core.injection': 'winter.application.injection',
        'winter.core.module_discovery': 'winter.application.module_discovery',
        'winter.core.utils.typing': 'winter.components.typing',
        'winter.core.utils.nested_types': 'winter.components.nested_types',
        'winter.core.utils.beautify_string': 'winter.web.exceptions.beautify_string',
        'winter.core.utils.positive_integer': 'winter.web.pagination.positive_integer',
    },
    prefixes={
        'winter.core.json': 'winter.json',
    },
)

from winter.application import WinterApplication  # noqa: E402
from winter.application import get_injector  # noqa: E402
from winter.application import set_injector  # noqa: E402
from winter.components import ArgumentDoesNotHaveDefault  # noqa: E402
from winter.components import Component  # noqa: E402
from winter.components import ComponentMethod  # noqa: E402
from winter.components import ComponentMethodArgument  # noqa: E402
from winter.components import annotate  # noqa: E402
from winter.components import annotate_class  # noqa: E402
from winter.components import annotate_method  # noqa: E402
from winter.components import component  # noqa: E402
from winter.components import component_method  # noqa: E402
from winter.components import is_component  # noqa: E402
