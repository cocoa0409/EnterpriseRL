"""Validate the agent-visible contract of instantiated hidden task tools.

This gate deliberately checks the docstring as a public runtime schema, not merely
that the Python function can execute.  Every argument must be documented exactly
once and classified as id, fixed-format, enum, or verbatim.  The class-specific
contract must be complete enough that an agent can form an unambiguous call.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_task_tools.py \
      env/<scenario>/tasks/<difficulty> [--task N]
"""

import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import select_task_paths, split_task_flag


CLASS_MARKERS = {
    "id": ("Id class —", "ID class —"),
    "fixed_format": ("Fixed-format class —",),
    "enum": ("Enum class —",),
    "verbatim": ("Verbatim class —",),
}
VERBATIM_SUFFIX = " (verbatim)."


def fail(errors, where, message):
    errors.append(f"{where}: {message}")


def is_tool_function(fn):
    for decorator in fn.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Name) and target.id == "tool":
            return True
        if isinstance(target, ast.Attribute) and target.attr == "tool":
            return True
    return False


def function_parameters(fn):
    args = list(fn.args.posonlyargs) + list(fn.args.args) + list(fn.args.kwonlyargs)
    return [arg.arg for arg in args if arg.arg not in {"ctx", "context"}]


def parse_sections(doc):
    """Return summary, argument descriptions, return description, and duplicates."""
    lines = doc.splitlines()
    args_index = next((i for i, line in enumerate(lines) if line.strip() == "Args:"), None)
    returns_index = next((i for i, line in enumerate(lines) if line.strip() == "Returns:"), None)
    if args_index is None:
        return doc.strip(), {}, "", []

    summary = "\n".join(lines[:args_index]).strip()
    args_end = returns_index if returns_index is not None and returns_index > args_index else len(lines)
    descriptions = {}
    duplicates = []
    current = None
    for raw in lines[args_index + 1:args_end]:
        if not raw.strip():
            continue
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", raw)
        if match:
            current = match.group(1)
            if current in descriptions:
                duplicates.append(current)
            descriptions[current] = match.group(2).strip()
        elif current:
            descriptions[current] = f"{descriptions[current]} {raw.strip()}".strip()

    returns = ""
    if returns_index is not None:
        returns = " ".join(line.strip() for line in lines[returns_index + 1:] if line.strip())
    return summary, descriptions, returns, duplicates


def source_parameter(expr, parameters):
    names = {node.id for node in ast.walk(expr) if isinstance(node, ast.Name)} & set(parameters)
    return next(iter(names)) if len(names) == 1 else None


def schema_expectations(fn, db_schema, parameters):
    """Map function arguments to DB field schemas through ctx CRUD keyword values."""
    out = {name: [] for name in parameters}
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if not (isinstance(node.func.value, ast.Name) and node.func.value.id == "ctx"):
            continue
        if node.func.attr not in {"create", "update", "delete"} or not node.args:
            continue
        if not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
            continue
        table = db_schema.get(node.args[0].value) or {}
        for keyword in node.keywords:
            if not keyword.arg or keyword.arg not in table:
                continue
            param = source_parameter(keyword.value, parameters)
            if param:
                out[param].append(table[keyword.arg])
    return out


def annotation_name(fn, parameter):
    for arg in list(fn.args.posonlyargs) + list(fn.args.args) + list(fn.args.kwonlyargs):
        if arg.arg == parameter:
            if isinstance(arg.annotation, ast.Name):
                return arg.annotation.id
            if isinstance(arg.annotation, ast.Constant):
                return str(arg.annotation.value)
    return ""


def expected_class(fn, parameter, schemas):
    schema_types = {spec.get("type") for spec in schemas if isinstance(spec, dict) and spec.get("type")}
    if len(schema_types) == 1:
        return next(iter(schema_types))
    annotation = annotation_name(fn, parameter)
    if annotation in {"float", "int"}:
        return "fixed_format"
    if annotation == "bool":
        return "enum"
    return None


def declared_class(description):
    found = []
    for kind, markers in CLASS_MARKERS.items():
        if any(marker in description for marker in markers):
            found.append(kind)
    return found


def enum_values(schemas):
    sets = []
    for spec in schemas:
        if isinstance(spec, dict) and spec.get("type") == "enum" and isinstance(spec.get("values"), list):
            sets.append(tuple(str(value).lower() if isinstance(value, bool) else str(value)
                              for value in spec["values"]))
    if not sets:
        return ()
    return sets[0] if all(values == sets[0] for values in sets) else ()


def validate_fixed(errors, where, description, schemas, annotation):
    formats = {str(spec.get("format")) for spec in schemas
               if isinstance(spec, dict) and spec.get("type") == "fixed_format" and spec.get("format")}
    for fmt in sorted(formats):
        decimal = re.search(r"(\d+)\s*decimal places?", fmt)
        if decimal and not re.search(
                rf"(?:{decimal.group(1)}\s*decimal places?|to\s*{decimal.group(1)}\s*decimal places?)",
                description, re.I):
            fail(errors, where, f"must state the schema's {decimal.group(1)}-decimal precision")
        if "integer" in fmt.lower() and "integer" not in description.lower():
            fail(errors, where, "must state that the value is an integer")
        date_fmt = next((token for token in ("YYYY-MM-DD HH:MM:SS", "YYYY-MM-DD HH:MM", "YYYY-MM-DD", "YYYY-MM")
                         if token in fmt), None)
        if date_fmt and date_fmt not in description:
            fail(errors, where, f"must state date/time format {date_fmt}")
        if not date_fmt:
            unit = re.sub(r"(?:,?\s*\d+\s*decimal places?|,?\s*integer)$", "", fmt, flags=re.I).strip()
            unit = re.sub(r"^(?:amount|count|quantity)\b", "", unit, flags=re.I).strip(" ,")
            if unit and unit not in description:
                fail(errors, where, f"must state schema unit {unit!r}")
    if not formats and annotation == "float" and not re.search(
            r"(?:\d+\s*decimal places?|to\s*\d+\s*decimal places?|precision)", description, re.I):
        fail(errors, where, "fixed-format float without a mapped schema field must still state precision")
    if not formats and annotation == "int" and "integer" not in description.lower():
        fail(errors, where, "fixed-format integer without a mapped schema field must state integer precision")
    if annotation in {"float", "int"} and not re.search(
            r"\bunits?\b|\bdimensionless\b|\bpercent(?:age)?\b|\bratios?\b", description, re.I):
        fail(errors, where, "numeric fixed-format description must explicitly state its unit or that it is dimensionless")


def validate_enum(errors, where, description, schemas):
    if not re.search(r"allowed values|permitted values|accepted values|valid values|possible values"
                     r"|accepts only|only accepts|limited to|restricted to|\bone of\b", description, re.I):
        fail(errors, where, "enum description must explicitly introduce its closed value set")
    values = enum_values(schemas)
    if not values:
        if not re.search(r"[^\s/／、]+\s*[（(][^）)]+[）)]", description):
            fail(errors, where, "enum values must each carry an applicable-situation description")
        return
    for value in values:
        pattern = rf"(?<![A-Za-z0-9_]){re.escape(value)}(?![A-Za-z0-9_])\s*[（(][^）)]+[）)]"
        if not re.search(pattern, description):
            fail(errors, where, f"enum value {value!r} is missing or has no applicable-situation description")


def return_keys(fn):
    keys = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Return) or node.value is None:
            continue
        value = node.value
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id == "str" and value.args):
            value = value.args[0]
        if isinstance(value, ast.Dict):
            for key in value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.add(key.value)
    return keys


def validate_function(fn, db_schema, errors):
    where = fn.name
    parameters = function_parameters(fn)
    doc = ast.get_docstring(fn, clean=True)
    if not doc:
        fail(errors, where, "missing runtime-schema docstring")
        return
    if fn.returns is None:
        fail(errors, where, "missing return type annotation")
    doc_lines = [line.strip() for line in doc.splitlines()]
    args_position = next((i for i, line in enumerate(doc_lines) if line == "Args:"), None)
    returns_position = next((i for i, line in enumerate(doc_lines) if line == "Returns:"), None)
    if args_position is None:
        fail(errors, where, "missing Args: section")
    if returns_position is None:
        fail(errors, where, "missing Returns: section")
    elif args_position is not None and returns_position <= args_position:
        fail(errors, where, "Returns: must follow Args:")

    summary, descriptions, returns, duplicates = parse_sections(doc)

    compact_summary = re.sub(r"\s+", "", summary)
    if len(compact_summary) < 45:
        fail(errors, where, "functional description is too thin; explain target, atomic business effect, visible result, and success receipt")

    if set(descriptions) != set(parameters):
        missing = sorted(set(parameters) - set(descriptions))
        extra = sorted(set(descriptions) - set(parameters))
        if missing:
            fail(errors, where, f"Args section is missing parameters: {missing}")
        if extra:
            fail(errors, where, f"Args section documents unknown parameters: {extra}")
    if duplicates:
        fail(errors, where, f"Args section documents parameters more than once: {sorted(set(duplicates))}")

    if returns_position is not None and not returns:
        fail(errors, where, "missing non-empty Returns: section describing the success receipt")
    elif returns:
        for key in sorted(return_keys(fn)):
            if key not in returns:
                fail(errors, where, f"Returns section does not describe returned field {key!r}")

    expectations = schema_expectations(fn, db_schema, parameters)
    for parameter in parameters:
        pwhere = f"{where}.{parameter}"
        if not annotation_name(fn, parameter):
            fail(errors, pwhere, "missing parameter type annotation")
        description = descriptions.get(parameter, "")
        if not description:
            continue
        classes = declared_class(description)
        if len(classes) != 1:
            fail(errors, pwhere, "must declare exactly one class: Id class — / Fixed-format class — / Enum class — / Verbatim class —")
            continue
        actual = classes[0]
        parameter_schemas = expectations.get(parameter, [])
        schema_types = {spec.get("type") for spec in parameter_schemas
                        if isinstance(spec, dict) and spec.get("type")}
        if len(schema_types) > 1:
            fail(errors, pwhere, f"flows into incompatible DB field types: {sorted(schema_types)}")
        expected = expected_class(fn, parameter, parameter_schemas)
        if expected and actual != expected:
            fail(errors, pwhere, f"declares {actual}, but its annotation/DB field contract requires {expected}")

        if actual == "id":
            body = description
            for marker in CLASS_MARKERS["id"]:          # the marker itself contains "id"; strip it first
                body = body.replace(marker, " ")
            if not re.search(r"\bids?\b|identif|\bnumbers?\b", body, re.I):
                fail(errors, pwhere, "id description must identify the kind of business record/object identifier")
        elif actual == "fixed_format":
            validate_fixed(errors, pwhere, description, expectations.get(parameter, []), annotation_name(fn, parameter))
        elif actual == "enum":
            validate_enum(errors, pwhere, description, expectations.get(parameter, []))
        elif actual == "verbatim":
            if not description.endswith(VERBATIM_SUFFIX):
                fail(errors, pwhere, f"verbatim description must end exactly with {VERBATIM_SUFFIX!r}")


def main():
    positional, task_selector = split_task_flag(sys.argv[1:])
    if len(positional) != 1:
        raise SystemExit("usage: check_task_tools.py env/<scenario>/tasks/<difficulty> [--task N]")
    diff = os.path.abspath(positional[0].rstrip("/"))
    tools_path = os.path.join(diff, "task_tools.py")
    if not os.path.isfile(tools_path):
        raise SystemExit(f"missing {tools_path}")

    scenario = os.path.dirname(os.path.dirname(diff))
    schema_path = os.path.join(scenario, "blueprint", "db_schema.json")
    if not os.path.isfile(schema_path):
        raise SystemExit(f"cannot find scenario DB schema at {schema_path}")
    with open(schema_path, encoding="utf-8") as handle:
        db_schema = json.load(handle)
    with open(tools_path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=tools_path)

    functions = {fn.name: fn for fn in tree.body
                 if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_tool_function(fn)}
    if task_selector is not None:
        task_path = select_task_paths(diff, task_selector)[0]
        with open(task_path, encoding="utf-8") as handle:
            task = json.load(handle)
        claimed = set(((task.get("charter_scope") or {}).get("task_tools") or []))
        missing = sorted(claimed - set(functions))
        if missing:
            raise SystemExit(f"task claims undefined task tools: {missing}")
        functions = {name: functions[name] for name in claimed}

    if not functions:
        raise SystemExit("no task tools selected for contract validation")

    errors = []
    for name in sorted(functions):
        validate_function(functions[name], db_schema, errors)

    print(f"🔎 TASK-TOOL-CONTRACT gate  ({len(functions)} tools)")
    if errors:
        for error in errors:
            print(f"  [FAIL] {error}")
        print(f"\nTASK TOOL CONTRACT FAIL ({len(errors)} issue(s))")
        raise SystemExit(1)
    print("  [PASS] complete business effects, Args coverage, four-way parameter typing, and success returns")
    print("TASK TOOL CONTRACT OK")


if __name__ == "__main__":
    main()
