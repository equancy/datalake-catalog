import json
from pkg_resources import resource_stream
from jsonschema import Draft7Validator


class SchemaValidator:
    def __init__(self, schema):
        if isinstance(schema, dict):
            self._schema = schema
        else:
            with resource_stream("datalake_catalog", f"schemas/{schema}.json") as f:
                self._schema = json.load(f)
        Draft7Validator.check_schema(self._schema)
        self._validator = Draft7Validator(self._schema)

    @property
    def schema(self):
        return self._schema

    def validate(self, data):
        self._validator.validate(data)
