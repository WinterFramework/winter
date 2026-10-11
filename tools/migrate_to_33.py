"""
Rewrite imports of a code base from Winter 32 to Winter 33.

    pip install libcst
    python tools/migrate_to_33.py path/to/project [more paths]   # rewrites files in place
    python tools/migrate_to_33.py --check path/to/project          # only lists files that would change

What it does:
- `import winter` facade is gone (`winter` is a namespace package): `winter.route_get` becomes
  `winter.web.route_get`, `from winter import request_body` becomes `from winter.web import request_body`.
- `winter_openapi`, `winter_django`, `winter_sqlalchemy`, `winter_ddd` become `winter.openapi`, ...
- `winter.core` is split into `winter.components`, `winter.application` and `winter.json`.
- `winter.data` is split into `winter.pagination` and `winter.ddd`.
- Redis throttling configuration moves to `winter.redis.throttling`.
Formatting and comments are preserved. The old paths keep working with a DeprecationWarning until 34.0,
so running this is not urgent, except for the `import winter` facade which is gone in 33.0.
"""
import argparse
import pathlib
import sys
from typing import Iterable
from typing import List
from typing import Set
from typing import Tuple

import libcst as cst
from libcst.codemod import CodemodContext
from libcst.codemod import TransformSuccess
from libcst.codemod import transform_module
from libcst.codemod.commands.rename import RenameCommand

FACADE_NAMES = (
    'ResponseEntity', 'arguments_resolver', 'request_body', 'request_header', 'response_header', 'response_status',
    'ArgumentResolver', 'ArgumentsResolver', 'raises', 'register_output_processor_resolver', 'map_query_parameter',
    'response_headers_serializer', 'route', 'route_delete', 'route_get', 'route_patch', 'route_post', 'route_put',
)

# Most specific first: RenameCommand renames prefixes too.
RENAMES: List[Tuple[str, str]] = [
    ('winter_openapi', 'winter.openapi'),
    ('winter_django', 'winter.django'),
    ('winter_sqlalchemy', 'winter.sqlalchemy'),
    ('winter_ddd', 'winter.ddd'),
    ('winter.core.json', 'winter.json'),
    ('winter.core.utils.typing', 'winter.components.typing'),
    ('winter.core.utils.nested_types', 'winter.components.nested_types'),
    ('winter.core.utils.TypeWrapper', 'winter.components.nested_types.TypeWrapper'),
    ('winter.core.utils.has_nested_type', 'winter.components.nested_types.has_nested_type'),
    ('winter.core.utils.camel_to_human', 'winter.web.exceptions.beautify_string.camel_to_human'),
    ('winter.core.utils.PositiveInteger', 'winter.web.pagination.positive_integer.PositiveInteger'),
    ('winter.core.module_discovery', 'winter.application.module_discovery'),
    ('winter.core.injection', 'winter.application.injection'),
    ('winter.core.application', 'winter.application.application'),
    ('winter.core.get_injector', 'winter.application.get_injector'),
    ('winter.core.set_injector', 'winter.application.set_injector'),
    ('winter.core.WinterApplication', 'winter.application.WinterApplication'),
    ('winter.core', 'winter.components'),
    ('winter.data.pagination', 'winter.pagination'),
    ('winter.data.exceptions', 'winter.ddd.exceptions'),
    ('winter.data.repository', 'winter.ddd.repository'),
    ('winter.data', 'winter.ddd'),
    ('winter.web.throttling.RedisThrottlingConfiguration', 'winter.redis.throttling.RedisThrottlingConfiguration'),
    (
        'winter.web.throttling.set_redis_throttling_configuration',
        'winter.redis.throttling.set_redis_throttling_configuration',
    ),
    ('winter.web.RedisThrottlingConfiguration', 'winter.redis.throttling.RedisThrottlingConfiguration'),
    ('winter.web.set_redis_throttling_configuration', 'winter.redis.throttling.set_redis_throttling_configuration'),
] + [(f'winter.{name}', f'winter.web.{name}') for name in FACADE_NAMES]

SUBPACKAGES = (
    'components', 'application', 'json', 'pagination', 'web', 'ddd', 'messaging',
    'django', 'openapi', 'sqlalchemy', 'redis', 'core', 'data',
)


def _might_use(source: str, old_name: str) -> bool:
    module, _, attribute = old_name.rpartition('.')
    return old_name in source or (module in source and attribute in source)


class _TidyImports(cst.CSTTransformer):
    """
    Dedupe imports the renames produced, one import per line, and replace the bare `import winter`
    (a namespace package now) with imports of the subpackages the module actually uses.
    """

    def __init__(self):
        self._emitted: Set[str] = set()
        self._used_subpackages: Set[str] = set()
        self._imported_subpackages: Set[str] = set()

    def visit_Module(self, node: cst.Module) -> None:
        class Collector(cst.CSTVisitor):
            def __init__(inner):
                inner.used: Set[str] = set()
                inner.imported: Set[str] = set()

            def visit_ImportFrom(inner, import_from: cst.ImportFrom) -> bool:
                return False  # `from winter.x import y` does not bind the name `winter`

            def visit_Attribute(inner, attribute: cst.Attribute) -> None:
                if isinstance(attribute.value, cst.Name) and attribute.value.value == 'winter':
                    if attribute.attr.value in SUBPACKAGES:
                        inner.used.add(attribute.attr.value)

            def visit_ImportAlias(inner, alias: cst.ImportAlias) -> None:
                dotted = cst.Module([]).code_for_node(alias.name)
                if dotted.startswith('winter.'):
                    inner.imported.add(dotted.split('.')[1])

        collector = Collector()
        node.visit(collector)
        self._used_subpackages = collector.used
        self._imported_subpackages = collector.imported

    def leave_SimpleStatementLine(self, original: cst.SimpleStatementLine, updated: cst.SimpleStatementLine):
        if len(updated.body) != 1 or not isinstance(updated.body[0], cst.Import):
            return updated
        wanted: List[str] = []
        for alias in updated.body[0].names:
            dotted = cst.Module([]).code_for_node(alias.name)
            if dotted == 'winter' and alias.asname is None:
                wanted.extend(
                    f'winter.{sub}' for sub in sorted(self._used_subpackages - self._imported_subpackages)
                )
            elif alias.asname is None:
                wanted.append(dotted)
            else:
                wanted.append(f'{dotted} as {cst.Module([]).code_for_node(alias.asname.name)}')
        lines = []
        for dotted in wanted:
            if dotted in self._emitted:
                continue
            self._emitted.add(dotted)
            line = cst.parse_statement(f'import {dotted}')
            if not lines:
                line = line.with_changes(leading_lines=updated.leading_lines)
            lines.append(line)
        if not lines:
            return cst.RemoveFromParent()
        return cst.FlattenSentinel(lines)


def migrate_source(source: str) -> str:
    code = source
    for old_name, new_name in RENAMES:
        if not _might_use(code, old_name):
            continue
        result = transform_module(RenameCommand(CodemodContext(), old_name=old_name, new_name=new_name), code)
        if not isinstance(result, TransformSuccess):
            raise RuntimeError(f'{old_name} -> {new_name}: {result}')
        code = result.code
    if code != source:
        code = cst.parse_module(code).visit(_TidyImports()).code
    return code


def python_files(paths: Iterable[str]) -> Iterable[pathlib.Path]:
    for raw in paths:
        path = pathlib.Path(raw)
        yield from ([path] if path.is_file() else sorted(path.rglob('*.py')))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--check', action='store_true', help='do not write, exit 1 if something would change')
    args = parser.parse_args(argv)

    changed = []
    for path in python_files(args.paths):
        source = path.read_text()
        if 'winter' not in source:
            continue
        migrated = migrate_source(source)
        if migrated != source:
            changed.append(path)
            if not args.check:
                path.write_text(migrated)
    for path in changed:
        print(path)
    return 1 if (args.check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
