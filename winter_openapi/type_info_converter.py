from openapi_pydantic.v3.v3_0_3 import Schema

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

    if value.enum is not None:
        data['enum'] = value.enum

    if value.properties:
        sorted_keys = sorted(value.properties.keys())
        data['properties'] = {
            key: convert_type_info_to_openapi_schema(value.properties[key], output=output)
            for key in sorted_keys
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

    schema = Schema(**data)

    if value.nullable:
        if value.type_.value == 'object':
            # https://stackoverflow.com/questions/40920441/how-to-specify-a-property-can-be-null-or-a-reference-with-swagger
            # Better solution, but not implemented yet https://github.com/OpenAPITools/openapi-generator/issues/9083
            schema = Schema(nullable=True, allOf=[schema])
        else:
            schema.nullable = True

    return schema
