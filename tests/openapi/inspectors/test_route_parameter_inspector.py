import logging

from winter.openapi import PathParametersInspector
from winter.openapi import register_route_parameters_inspector
from winter.openapi.initialization import initialize


def test_add_same_inspector_write_warning_log(caplog):
    initialize()

    with caplog.at_level(logging.WARNING):
        register_route_parameters_inspector(PathParametersInspector())
    assert 'PathParametersInspector already registered' in caplog.text
