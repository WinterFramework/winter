from strenum import StrEnum


class DataFormat(StrEnum):
    DATE = "date"
    DATETIME = "date-time"
    PASSWORD = "password"
    BINARY = "binary"
    BASE64 = "bytes"
    FLOAT = "float"
    DOUBLE = "double"
    INT32 = "int32"
    INT64 = "int64"

    # defined in JSON-schema
    EMAIL = "email"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    URI = "uri"
    UUID = "uuid"
    SLUG = "slug"
    DECIMAL = "decimal"
