import dataclasses

import winter.core
from winter_openapi.generation import get_schema_title

DTO = dataclasses.dataclass(type('DTO', (), {
    '__annotations__': {
        'id': int,
    },
}))
SecondDTO = dataclasses.dataclass(type('DTO', (), {
    '__annotations__': {
        'id': int,
    },
}))


def test_get_schema_title():
    @winter.core.component_method
    def method(dto: DTO, second_dto: SecondDTO):
        return dto, second_dto

    dto_argument = method.get_argument('dto')
    second_dto_argument = method.get_argument('second_dto')

    # Act
    dto_title = get_schema_title(dto_argument)
    second_dto_title = get_schema_title(second_dto_argument)

    # Assert
    assert dto_title == 'DTO' == get_schema_title(dto_argument)
    assert second_dto_title == 'DTO1' == get_schema_title(second_dto_argument)
