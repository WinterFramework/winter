from openapi_schema_pydantic.v3.v3_0_3 import Schema

from winter_openapi.inspection import DataTypes
from winter_openapi.inspection import TypeInfo


def convert_type_info_to_openapi_schema(value: TypeInfo, *, output: bool) -> Schema:
    if value.type_ == DataTypes.ANY:
        return Schema(
            description='Can be any value - string, number, boolean, array or object.',
            nullable=value.nullable,
        )

    data = {
        'type': value.type_.value
    }
    if value.title:
        data['title'] = value.title if output else f'{value.title}Input'

    if value.description:
        data['description'] = value.description

    if value.format_ is not None:
        data['schema_format'] = value.format_.value

    if value.child is not None:
        data['items'] = convert_type_info_to_openapi_schema(value.child, output=output)

    if value.nullable:
        data['nullable'] = True

    if value.enum is not None:
        data['enum'] = value.enum

    if value.properties:
        data['properties'] = {
            key: convert_type_info_to_openapi_schema(value, output=output)
            for key, value in value.properties.items()
        }

    if output:
        required_properties = list(value.properties)
    else:
        required_properties = [
            property_name
            for property_name in value.properties
            if property_name not in value.properties_defaults
               and not value.properties[property_name].nullable
               and not value.properties[property_name].can_be_undefined
        ]

    if required_properties:
        data['required'] = required_properties

    return Schema(**data)
