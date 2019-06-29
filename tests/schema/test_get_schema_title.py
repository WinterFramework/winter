import dataclasses

import winter.core
from winter.schema.generation import get_schema_title


@dataclasses.dataclass()
class DTO:
    id: int


def test_get_schema_title():
    @winter.core.component_method
    def method(dto: DTO, second_dto: DTO):
        return dto, second_dto

    dto_argument = method.get_argument('dto')
    second_dto_argument = method.get_argument('second_dto')

    # Act
    dto_title = get_schema_title(dto_argument)
    second_dto_title = get_schema_title(second_dto_argument)

    # Assert
    assert dto_title == 'DTO'
    assert second_dto_title == 'DTO2'
