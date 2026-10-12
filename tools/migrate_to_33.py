"""
Rewrite imports of a code base from Winter 32 to Winter 33.

    pip install libcst
    python tools/migrate_to_33.py path/to/project [more paths]   # rewrites files in place
    python tools/migrate_to_33.py --check path/to/project          # only lists files that would change

What it does:
- `import winter` facade is gone (`winter` is a namespace package): `winter.route_get` becomes
  `winter.web.route_get`, `from winter import request_body` becomes `from winter.web import request_body`.
- `winter_openapi`, `winter_django`, `winter_sqlalchemy`, `winter_ddd` become `winter.openapi`, ...
- `winter.core` is split into `winter.components`, `winter.application`, `winter.json` and `winter.typing`.
- `winter.data` is split into `winter.pagination` and `winter.ddd`.
- Redis throttling configuration moves to `winter.redis.throttling`, `reverse` to `winter.django`.
- `set_redis_throttling_configuration(c)` becomes `set_throttling_storage(RedisThrottlingStorage(c))`.
Formatting and comments are preserved. None of the old paths exist in 33.0.
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
from libcst.codemod.visitors import AddImportsVisitor
from libcst.codemod.visitors import RemoveImportsVisitor

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
    ('winter.core.utils.typing', 'winter.typing'),
    ('winter.core.utils.nested_types', 'winter.typing'),
    ('winter.core.utils.TypeWrapper', 'winter.typing.TypeWrapper'),
    ('winter.core.utils.has_nested_type', 'winter.typing.has_nested_type'),
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
    ('winter.web.routing.reverse', 'winter.django.reverse'),
    ('winter.web.throttling.RedisThrottlingConfiguration', 'winter.redis.throttling.RedisThrottlingConfiguration'),
    ('winter.web.RedisThrottlingConfiguration', 'winter.redis.throttling.RedisThrottlingConfiguration'),
] + [(f'winter.{name}', f'winter.web.{name}') for name in FACADE_NAMES]

SUBPACKAGES = (
    'components', 'application', 'json', 'pagination', 'typing', 'web', 'ddd', 'messaging',
    'django', 'openapi', 'sqlalchemy', 'redis', 'core', 'data',
)


def _might_use(source: str, old_name: str) -> bool:
    module, _, attribute = old_name.rpartition('.')
    return old_name in source or (module in source and attribute in source)


class _TidyImports(cst.CSTTransformer):
    """
    Dedupe imports the renames produced, one import per line, and replace the bare `import winter`
    (a namespace package now) with imports of the subpackages the module actually uses. A `winter.x`
    the codemod does not know keeps the bare import, so that nothing silently disappears.
    """

    def __init__(self):
        self._emitted: Set[str] = set()
        self._used_subpackages: Set[str] = set()
        self._imported_subpackages: Set[str] = set()
        self._uses_unknown_names = False

    def visit_Module(self, node: cst.Module) -> None:
        class Collector(cst.CSTVisitor):
            def __init__(inner):
                inner.used: Set[str] = set()
                inner.imported: Set[str] = set()
                inner.unknown = False

            def visit_ImportFrom(inner, import_from: cst.ImportFrom) -> bool:
                return False  # `from winter.x import y` does not bind the name `winter`

            def visit_Attribute(inner, attribute: cst.Attribute) -> None:
                if isinstance(attribute.value, cst.Name) and attribute.value.value == 'winter':
                    if attribute.attr.value in SUBPACKAGES:
                        inner.used.add(attribute.attr.value)
                    else:
                        inner.unknown = True

            def visit_ImportAlias(inner, alias: cst.ImportAlias) -> None:
                dotted = cst.Module([]).code_for_node(alias.name)
                if dotted.startswith('winter.'):
                    inner.imported.add(dotted.split('.')[1])

        collector = Collector()
        node.visit(collector)
        self._used_subpackages = collector.used
        self._imported_subpackages = collector.imported
        self._uses_unknown_names = collector.unknown

    def leave_SimpleStatementLine(self, original: cst.SimpleStatementLine, updated: cst.SimpleStatementLine):
        if len(updated.body) != 1 or not isinstance(updated.body[0], cst.Import):
            return updated
        wanted: List[str] = []
        for alias in updated.body[0].names:
            dotted = cst.Module([]).code_for_node(alias.name)
            if dotted == 'winter' and alias.asname is None:
                wanted.extend(f'winter.{sub}' for sub in sorted(self._used_subpackages - self._imported_subpackages))
                if self._uses_unknown_names:
                    wanted.append('winter')
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


_REDIS_SETTER = 'set_redis_throttling_configuration'


class _RedisSetterCalls(cst.CSTTransformer):
    """`set_redis_throttling_configuration(c)` -> `set_throttling_storage(RedisThrottlingStorage(c))`."""

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.Call:
        func = updated.func
        is_setter = (
            (isinstance(func, cst.Name) and func.value == _REDIS_SETTER)
            or (isinstance(func, cst.Attribute) and func.attr.value == _REDIS_SETTER)
        )
        if not is_setter:
            return updated
        storage = cst.Call(func=cst.Name('RedisThrottlingStorage'), args=updated.args)
        return updated.with_changes(func=cst.Name('set_throttling_storage'), args=[cst.Arg(storage)])


def _rewrite_redis_setter(code: str) -> str:
    if _REDIS_SETTER not in code:
        return code
    context = CodemodContext()
    module = cst.parse_module(code).visit(_RedisSetterCalls())
    AddImportsVisitor.add_needed_import(context, 'winter.web', 'set_throttling_storage')
    AddImportsVisitor.add_needed_import(context, 'winter.redis.throttling', 'RedisThrottlingStorage')
    for old_module in ('winter.web', 'winter.web.throttling'):
        RemoveImportsVisitor.remove_unused_import(context, old_module, _REDIS_SETTER)
    module = AddImportsVisitor(context).transform_module(module)
    module = RemoveImportsVisitor(context).transform_module(module)
    return module.code


def migrate_source(source: str) -> str:
    code = _rewrite_redis_setter(source)
    for old_name, new_name in RENAMES:
        if not _might_use(code, old_name):
            continue
        result = transform_module(RenameCommand(CodemodContext(), old_name=old_name, new_name=new_name), code)
        if not isinstance(result, TransformSuccess):  # pragma: no cover
            raise RuntimeError(f'{old_name} -> {new_name}: {result}')
        code = result.code
    if code != source or _has_bare_winter_import(code):
        code = cst.parse_module(code).visit(_TidyImports()).code
    return code


def _has_bare_winter_import(code: str) -> bool:
    """`import winter` used to bind winter.web; as a namespace package it binds nothing, so it needs tidying."""
    return any(line.strip() == 'import winter' for line in code.splitlines())


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
