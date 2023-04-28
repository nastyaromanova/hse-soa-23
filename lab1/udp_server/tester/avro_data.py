import avro.schema

avro_schema = avro.schema.parse('''
{
    "type": "record",
    "name": "TestData",
    "fields": [
        {"name": "number", "type": "int"},
        {"name": "float", "type": "double"},
        {"name": "bool", "type": "boolean"},
        {"name": "string", "type": "string"},
        {"name": "listNumber", "type": {"type": "array", "items": "int"}},
        {"name": "listString", "type": {"type": "array", "items": "string"}},
        {"name": "dict", "type": {"type": "map", "values": "int"}}
    ]
}
''')