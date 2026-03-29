#!/usr/bin/env python3
"""JSON schema validator (subset of JSON Schema Draft 7)."""
import sys, json, re

def validate(instance, schema, path="$"):
    errors = []
    t = schema.get("type")
    if t:
        type_map = {"string": str, "number": (int,float), "integer": int, "boolean": bool, "array": list, "object": dict, "null": type(None)}
        expected = type_map.get(t)
        if expected and not isinstance(instance, expected):
            if not (t == "number" and isinstance(instance, int)):
                errors.append(f"{path}: expected {t}, got {type(instance).__name__}")
                return errors
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: too short (min {schema['minLength']})")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: too long (max {schema['maxLength']})")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: doesn't match pattern {schema['pattern']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: too many items")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    if isinstance(instance, dict):
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop in instance:
                errors.extend(validate(instance[prop], prop_schema, f"{path}.{prop}"))
        for req in schema.get("required", []):
            if req not in instance: errors.append(f"{path}: missing required '{req}'")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")
    return errors

def main():
    if len(sys.argv) < 2: print("Usage: schema_valid.py <demo|test>"); return
    if sys.argv[1] == "test":
        s = {"type": "object", "required": ["name", "age"], "properties": {"name": {"type": "string", "minLength": 1}, "age": {"type": "integer", "minimum": 0}}}
        assert validate({"name": "Alice", "age": 30}, s) == []
        errs = validate({"name": ""}, s)
        assert any("missing" in e for e in errs)
        assert any("too short" in e for e in errs)
        assert validate(42, {"type": "integer", "minimum": 0, "maximum": 100}) == []
        assert len(validate(101, {"type": "integer", "maximum": 100})) == 1
        assert validate([1,2,3], {"type": "array", "items": {"type": "integer"}}) == []
        assert len(validate([1,"x"], {"type": "array", "items": {"type": "integer"}})) == 1
        assert validate("red", {"enum": ["red","green","blue"]}) == []
        assert len(validate("yellow", {"enum": ["red","green","blue"]})) == 1
        assert validate("abc", {"type": "string", "pattern": "^[a-z]+$"}) == []
        assert len(validate("ABC", {"type": "string", "pattern": "^[a-z]+$"})) == 1
        print("All tests passed!")
    else:
        schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
        data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {"name": "test"}
        errs = validate(data, schema)
        print("Valid!" if not errs else f"Errors: {errs}")

if __name__ == "__main__": main()
