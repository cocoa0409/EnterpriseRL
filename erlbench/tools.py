"""The tool-authoring API used by every generated ``share_tools.py`` /
``tools/task_tools.py`` file.

A tool is a plain function decorated with ``@tool(owner, rw)`` whose first
parameter is a :class:`ToolContext` (giving it the schema-aware CRUD and the
frozen clock).
The runtime introspects the signature + Google docstring to build the
OpenAI-form schema IN MEMORY at request time — the code is the only source of
truth; no schema file exists anywhere. The six base tools in engine.py get
their schemas the same way, from their own implementations.

Two things are declared on the decorator (both required):
  - owner: "agent" | "user"  -- who is allowed to invoke the tool
  - rw:    "read" | "write"  -- whether the tool changes the DB.
    "write" tools MUST perform their writes via ctx.create/ctx.update/ctx.delete (the
    validator statically checks this, and a "read" tool that attempts a write
    fails at runtime). Only "write" tools may appear in evaluation_criteria.

Everything else is structural:
  - a tool defined in ``share_tools.py``  is a SHARE tool -- always in its
    owner's tool list, directly callable;
  - a tool defined in ``tools/task_tools.py`` is a TASK tool -- hidden, its name
    lives only in the KB, and it is reached through the unlock/call meta tools.
The loader tags each spec with ``kind`` ("share" | "task") from its source file.
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .db import DB
from .determinism import Clock, make_id

OWNERS = ("agent", "user")
KINDS = ("share", "task")
RW = ("read", "write")

_PY_TO_JSON = {str: "string", int: "integer", float: "number", bool: "boolean"}
_COERCE = {"string": str, "integer": int, "number": float, "boolean": bool}


class ToolContext:
    """Everything a tool may touch. Nothing else is in scope -- that is the point.

    DB access goes through the shared, schema-aware CRUD below — the COMPLETE
    tool-facing interface is:
      id    : ctx.make_id(prefix, *parts)       deterministic sha256 content
              hash — the same prefix+parts always yield the same id
      reads : ctx.find(table, **match) -> list of matching rows
              (no match kwargs = all rows)
      writes: ctx.create(table, row_key, **fields) / ctx.update(table, key,
              **fields) / ctx.delete(table, key)   (rw="write" tools only)
      time  : ctx.now()                         (the task's frozen_time,
               verbatim; slice ctx.now()[:10] for the date part)
    db_schema.json is a plain {table: [field, ...]} map; every call validates
    the table and field names against it, so a typo fails loudly instead of
    silently writing/reading nothing. Inserts are idempotent on the row key.
    Tool bodies keep only the business logic. Generated tools may not touch
    anything else on ctx (the validator enforces this).
    """

    def __init__(self, db: DB, clock: Clock, schema: dict | None = None,
                 writable: bool = True):
        self.db = db
        self._clock = clock
        self._schema = schema or {}
        self._writable = writable

    def now(self) -> str:
        return self._clock.now()

    # -- shared schema-aware CRUD ------------------------------------------ #
    def make_id(self, prefix: str, *parts, length: int = 12) -> str:
        """Deterministic row id: ``prefix + sha256(prefix:parts...)``. Build it
        from the arguments that identify the row (same parts => same id)."""
        return make_id(prefix, *parts, length=length)

    # the single read
    def find(self, table: str, **match) -> list:
        """Return all rows whose fields equal ``match`` (field names schema-checked).
        No kwargs returns the whole table."""
        self._check_fields(table, self._declared(table), match)
        return self.db.find(table, **match)

    # writes
    def _declared(self, table: str) -> list:
        declared = self._schema.get(table)
        if declared is None:
            raise ValueError(f"unknown table '{table}' (not in db_schema.json)")
        return declared

    def _check_fields(self, table: str, declared: list, fields: dict) -> None:
        unknown = [f for f in fields if f not in declared]
        if unknown:
            raise ValueError(f"unknown field(s) for table '{table}': {unknown}")

    def create(self, table: str, row_key: str, **fields) -> str:
        """Insert one row under ``row_key`` (compute it with ctx.make_id and put
        the id field in ``fields`` too). Idempotent; field names schema-checked.
        Returns the row key."""
        if not self._writable:
            raise PermissionError("this tool is declared rw='read' and cannot write to the DB")
        self._check_fields(table, self._declared(table), fields)
        self.db.insert(table, row_key, fields)
        return row_key

    def update(self, table: str, row_key: str, **fields) -> bool:
        """Update fields on an existing row (schema-checked). Returns False if absent."""
        if not self._writable:
            raise PermissionError("this tool is declared rw='read' and cannot write to the DB")
        self._check_fields(table, self._declared(table), fields)
        return self.db.update(table, row_key, **fields)

    def delete(self, table: str, row_key: str) -> bool:
        """Delete a row (schema-checked table). Returns False if absent."""
        if not self._writable:
            raise PermissionError("this tool is declared rw='read' and cannot write to the DB")
        self._declared(table)
        return self.db.delete(table, row_key)


@dataclass
class ToolSpec:
    name: str
    owner: str
    rw: str  # "read" | "write" -- declared on the decorator
    kind: str  # "share" | "task" -- derived from the source file, not declared
    func: Callable
    description: str
    parameters: Dict[str, Any]  # OpenAI JSON-schema "parameters" object
    param_types: Dict[str, str]  # name -> json type, for coercion

    def openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def coerce(self, arguments: dict) -> dict:
        out = {}
        for k, v in (arguments or {}).items():
            jt = self.param_types.get(k)
            if v is None or jt is None:
                out[k] = v
                continue
            try:
                if jt == "boolean" and isinstance(v, str):
                    out[k] = v.strip().lower() in ("true", "1", "yes")
                else:
                    out[k] = _COERCE[jt](v)
            except (ValueError, TypeError):
                out[k] = v
        return out


def tool(owner: str, rw: str):
    """Mark a function as a tool: owner "agent"|"user", rw "read"|"write"."""
    assert owner in OWNERS, f"owner must be one of {OWNERS}"
    assert rw in RW, f"rw must be one of {RW}"

    def deco(func: Callable) -> Callable:
        func.__toolmeta__ = {"owner": owner, "rw": rw}
        return func

    return deco


# "name: desc" or "name (type): desc" -- the name must be a bare identifier, so a
# wrapped description line such as "+8613800000000: no spaces" cannot open a param.
_PARAM_LINE = re.compile(r"^([A-Za-z_]\w*)\s*(?:\([^)]*\))?\s*:(.*)$")


def _parse_docstring(doc: str):
    """Return (short_description, {param_name: description}) from a Google-style docstring."""
    doc = inspect.cleandoc(doc or "")
    short, args, in_args = [], {}, False
    cur, param_indent = None, None
    for ln in doc.splitlines():
        s = ln.strip()
        if s.lower() in ("args:", "arguments:", "parameters:"):
            in_args, cur, param_indent = True, None, None
            continue
        if s.lower() in ("returns:", "return:", "raises:"):
            in_args = False
            continue
        if in_args and s:
            m = _PARAM_LINE.match(s)
            indent = len(ln) - len(ln.lstrip())
            # A line indented deeper than the first param line CONTINUES that
            # param, even when it happens to look like "name: ...". Only an
            # identifier at the param indent opens a new param. Descriptions
            # carry the full candidate set for closed-valued params, so losing
            # a wrapped tail silently truncates the contract the agent sees.
            continues = cur is not None and param_indent is not None and indent > param_indent
            if m and not continues:
                cur = m.group(1)
                args[cur] = m.group(2).strip()
                if param_indent is None:
                    param_indent = indent
            elif cur:
                args[cur] = (args[cur] + " " + s).strip()
        elif not in_args and s:
            short.append(s)
    return " ".join(short).strip(), args


def _introspect(func: Callable, skip: tuple):
    """Signature + docstring -> (description, properties, required, param_types)."""
    sig = inspect.signature(func)
    short, arg_docs = _parse_docstring(func.__doc__)
    props, required, ptypes = {}, [], {}
    for pname, p in sig.parameters.items():
        if pname in skip or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        jt = _PY_TO_JSON.get(p.annotation, "string")
        ptypes[pname] = jt
        prop = {"type": jt}
        if pname in arg_docs:
            prop["description"] = arg_docs[pname]
        props[pname] = prop
        if p.default is inspect._empty:
            required.append(pname)
    return short, props, required, ptypes


def function_schema(func: Callable, skip: tuple = ("self", "ctx")) -> dict:
    """OpenAI-form tool schema introspected from any function's signature + docstring."""
    short, props, required, _ = _introspect(func, skip)
    return {"type": "function", "function": {
        "name": func.__name__,
        "description": short or func.__name__,
        "parameters": {"type": "object", "properties": props, "required": required}}}


def build_spec(name: str, func: Callable, kind: str) -> ToolSpec:
    """Introspect a decorated function into a ToolSpec (schema + metadata)."""
    meta = getattr(func, "__toolmeta__", None)
    if meta is None:
        raise ValueError(f"function '{name}' is not decorated with @tool")
    assert kind in KINDS, f"kind must be one of {KINDS}"
    short, props, required, ptypes = _introspect(func, ("ctx",))
    return ToolSpec(
        name=name,
        owner=meta["owner"],
        rw=meta["rw"],
        kind=kind,
        func=func,
        description=short or name,
        parameters={"type": "object", "properties": props, "required": required},
        param_types=ptypes,
    )


def collect_specs(module, kind: str) -> List[ToolSpec]:
    """Collect every @tool-decorated function in a module, tagged as share/task."""
    specs = []
    for name, obj in vars(module).items():
        if callable(obj) and getattr(obj, "__toolmeta__", None) is not None:
            specs.append(build_spec(name, obj, kind))
    return specs
