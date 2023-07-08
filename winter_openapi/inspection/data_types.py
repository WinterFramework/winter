from strenum import StrEnum


class DataTypes(StrEnum):
    OBJECT = "object"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    FILE = "file"
    ANY = 'AnyValue'
