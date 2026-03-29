#!/usr/bin/env python3
"""schema_valid - JSON schema validator (subset of JSON Schema Draft 7)."""
import sys, re

def validate(data, schema):
    errors = []
    _validate(data, schema, "", errors)
    return errors

def _validate(data, schema, path, errors):
    if "type" in schema:
        expected = schema["type"]
        type_map = {"string": str, "number": (int, float), "integer": int,
                     "boolean": bool, "array": list, "object": dict, "null": type(None)}
        if expected in type_map:
            t = type_map[expected]
            if expected == "integer" and isinstance(data, bool):
                errors.append(f"{path}: expected integer, got boolean")
            elif not isinstance(data, t):
                errors.append(f"{path}: expected {expected}, got {type(data).__name__}")
                return
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: {data} not in {schema['enum']}")
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{path}: too short")
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(f"{path}: too long")
        if "pattern" in schema and not re.search(schema["pattern"], data):
            errors.append(f"{path}: doesn't match pattern")
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: above maximum")
    if isinstance(data, list):
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(f"{path}: too many items")
        if "items" in schema:
            for i, item in enumerate(data):
                _validate(item, schema["items"], f"{path}[{i}]", errors)
    if isinstance(data, dict):
        if "required" in schema:
            for req in schema["required"]:
                if req not in data:
                    errors.append(f"{path}: missing required '{req}'")
        if "properties" in schema:
            for key, prop_schema in schema["properties"].items():
                if key in data:
                    _validate(data[key], prop_schema, f"{path}.{key}", errors)

def test():
    schema = {
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "pattern": "@"},
            "tags": {"type": "array", "items": {"type": "string"}}
        }
    }
    assert validate({"name": "Alice", "age": 30}, schema) == []
    errs = validate({"name": "", "age": -1}, schema)
    assert len(errs) == 2
    errs2 = validate({"age": 30}, schema)
    assert any("missing required" in e for e in errs2)
    errs3 = validate({"name": "Bob", "age": 25, "email": "invalid"}, schema)
    assert any("pattern" in e for e in errs3)
    errs4 = validate({"name": "X", "age": 20, "tags": [1, 2]}, schema)
    assert len(errs4) == 2  # two non-string items
    print("OK: schema_valid")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: schema_valid.py test")
