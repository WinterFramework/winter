import logging

from winter_openapi import PathParametersInspector
from winter_openapi import register_route_parameters_inspector


def test_add_same_inspector_write_warning_log(caplog):
    with caplog.at_level(logging.WARNING):
        register_route_parameters_inspector(PathParametersInspector())
    assert 'PathParametersInspector already registered' in caplog.text
