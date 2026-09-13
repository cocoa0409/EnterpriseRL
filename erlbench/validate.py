"""Validate that a generated scenario is well-formed and scorable.

Checks, per scenario and per task:
  - tool modules import; share/task kinds come from their source files
  - every tool's rw declaration matches its implementation (write => calls
    ctx.create/ctx.update/ctx.delete; read => never writes) and tools use ONLY
    the ctx CRUD interface (any other ctx attribute, incl. ctx.db, is rejected)
  - every discoverable (task) tool name is actually buried in some KB document
    (otherwise the agent could never discover it)
  - generated tool sources contain no real-clock or randomness calls (every
    timestamp must come from the task's frozen_time via ctx.now())
  - each task's ground-truth trajectory (evaluation_criteria) is the task's
    full standard-operation replay: read and/or write actions (reads select the
    seed rows the task depends on, writes add the new nodes); it must replay
    without error — read or write — and yield a stable hash (determinism)
  - the ground truth is non-vacuous (changes the DB — a do-nothing agent must
    score 0) and every action it names is a real tool whose declared owner
    matches the action's owner (the permission boundary)
  - every required document id exists in the KB
"""

from __future__ import annotations

import ast
import glob
import os
import re
from typing import List, Tuple

from .loader import Scenario, load_scenario, blueprint_dir
from .scoring import _resolve, replay
from .engine import BASE_SCHEMAS


def _replay_checked(engine, actions):
    """Replay the FULL ground truth — reads and writes — and surface tool-level
    soft errors: a guard misfire returns an "Error: ..." string without raising
    (a write silently never lands, a read silently sees nothing) — that must
    fail validation loudly. Reads cannot change the hash (rw enforcement), but
    they must execute cleanly: they are the part of the replay that pins the
    task's information rows."""
    errs = []
    for i, a in enumerate(actions):
        tool, args = _resolve(a)
        if not tool:
            continue
        spec = engine.registry.get(tool)
        if spec is None:
            continue
        out = str(spec.func(engine._ctx(), **spec.coerce(args)))
        if out.startswith("Error"):
            errs.append(f"gold action #{i} ({tool}) hit a guard: {out[:120]}")
    return engine.db.hash(), errs

# Real-clock and randomness sources are banned in generated tool code: every
# timestamp must come from ctx.now() (the task's frozen_time) and
# every id from ctx.create / erlbench.row_id, or replay is not reproducible.
_FORBIDDEN_TOKENS = [
    ("import datetime", "real clock"),
    ("from datetime", "real clock"),
    ("import time", "real clock"),
    ("time.time(", "real clock"),
    ("date.today(", "real clock"),
    (".utcnow(", "real clock"),
    ("import random", "randomness"),
    ("random.", "randomness"),
    ("import uuid", "randomness"),
    ("uuid.", "randomness"),
    ("import secrets", "randomness"),
]


def _tool_source_paths(root: str) -> List[str]:
    """Every generated tool module of a scenario: the blueprint's share_tools.py
    plus each difficulty's task_tools.py (current tasks/ layout, then legacy)."""
    paths = [os.path.join(blueprint_dir(root), "share_tools.py")]
    paths += sorted(glob.glob(os.path.join(root, "tasks", "*", "task_tools.py")))
    paths += sorted(glob.glob(os.path.join(root, "*", "tools", "task_tools.py")))
    return paths


def _lint_tool_sources(root: str) -> List[str]:
    errs = []
    for p in _tool_source_paths(root):
        if not os.path.exists(p):
            continue
        text = open(p).read()
        for token, why in _FORBIDDEN_TOKENS:
            if token in text:
                errs.append(
                    f"{os.path.relpath(p, root)}: forbidden '{token}' ({why}) — "
                    "use ctx.now() for time and ctx.create for ids"
                )
    return errs


_CTX_WRITES = {"create", "update", "delete"}
# The COMPLETE ctx interface a generated tool may use. Anything else on ctx
# (including ctx.db) is rejected — the CRUD layer is the only door to the DB.
_CTX_ALLOWED = {"make_id", "find", "create", "update", "delete", "now"}


def _decorator_rw(fn: ast.FunctionDef):
    """Return the rw declared in @tool(...) on this function, or None if not a tool."""
    for dec in fn.decorator_list:
        if isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "tool":
            for kw in dec.keywords:
                if kw.arg == "rw" and isinstance(kw.value, ast.Constant):
                    return kw.value.value
            if len(dec.args) >= 2 and isinstance(dec.args[1], ast.Constant):
                return dec.args[1].value
            return "<missing>"
    return None


def _scan_ctx_usage(fn: ast.FunctionDef):
    """Return (ctx_write_calls, off_interface_attrs) found in the function body."""
    writes, offside = set(), set()
    for node in ast.walk(fn):
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "ctx"):
            if node.attr in _CTX_ALLOWED:
                if node.attr in _CTX_WRITES:
                    writes.add(node.attr)
            else:
                offside.add(f"ctx.{node.attr}")
    return writes, offside


def _rw_consistency_errors(root: str) -> List[str]:
    """Statically verify each tool's rw declaration against its implementation:
    write => calls ctx.create/ctx.update/ctx.delete at least once; read => never;
    and every ctx usage stays inside the closed interface (_CTX_ALLOWED)."""
    errs = []
    for p in _tool_source_paths(root):
        if not os.path.exists(p):
            continue
        rel = os.path.relpath(p, root)
        try:
            tree = ast.parse(open(p).read())
        except SyntaxError as e:
            errs.append(f"{rel}: syntax error: {e}")
            continue
        for fn in tree.body:
            if not isinstance(fn, ast.FunctionDef):
                continue
            rw = _decorator_rw(fn)
            if rw is None:
                continue
            writes, offside = _scan_ctx_usage(fn)
            if offside:
                errs.append(f"{rel}: '{fn.name}' uses {', '.join(sorted(offside))} — outside the tool "
                            "interface (allowed: ctx.make_id/find/create/update/delete/now)")
            if rw == "write" and not writes:
                errs.append(f"{rel}: '{fn.name}' is declared rw='write' but never calls "
                            "ctx.create/ctx.update/ctx.delete")
            elif rw == "read" and writes:
                errs.append(f"{rel}: '{fn.name}' is declared rw='read' but calls {', '.join('ctx.'+w for w in sorted(writes))}")
            elif rw == "<missing>":
                errs.append(f"{rel}: '{fn.name}' @tool(...) is missing the required rw declaration")
    return errs


def validate_scenario(root: str) -> Tuple[List[str], List[str], dict]:
    errors: List[str] = []
    warnings: List[str] = []

    try:
        sc: Scenario = load_scenario(root)
    except Exception as e:  # noqa: BLE001
        return [f"failed to load scenario: {e}"], [], {}

    errors += _lint_tool_sources(sc.root)
    errors += _rw_consistency_errors(sc.root)

    doc_ids = set(d.id for d in sc.docs)
    # The current pipeline's tasks reference policies, not doc files: a required
    # document id is satisfied by any rendered doc carrying it as meta.policy_id.
    doc_ids |= {d.meta.get("policy_id") for d in sc.docs if d.meta.get("policy_id")}
    doc_blob = "\n".join(d.content for d in sc.docs)
    registry = {s.name: s for s in sc.specs}

    # discoverable tools must be discoverable via the KB
    for s in sc.specs:
        if s.kind == "task" and s.name not in doc_blob:
            warnings.append(f"task tool '{s.name}' is not mentioned in any KB document")

    # cross-task identifier collisions: lookup reads (by phone/email/name) match
    # against the MERGED big DB during closure extraction, so an identifier value
    # shared by two tasks' rows leaks each task's row into the other's closure
    ident_seen: dict = {}
    for difficulty, task in sc.all_tasks():
        tid = f"{difficulty}/{task.get('task_index')}"
        for tbl in ("customers", "lines"):
            for rid, row in (task.get("initial_state") or {}).get(tbl, {}).items():
                for fld in ("phone_number", "email", "name"):
                    v = (row or {}).get(fld)
                    if not v:
                        continue
                    prev = ident_seen.setdefault((tbl, fld, v), (tid, rid))
                    if prev[0] != tid:
                        warnings.append(f"{tid}: {tbl}.{fld} '{v}' ({rid}) collides with "
                                        f"{prev[0]} ({prev[1]}) — lookup reads will leak "
                                        "rows across tasks")

    n_tasks = 0
    n_ok = 0
    for difficulty, task in sc.all_tasks():
        n_tasks += 1
        tid = f"{difficulty}/{task.get('task_index')}"
        gt = task.get("evaluation_criteria") or []
        if not isinstance(gt, list):
            errors.append(f"{tid}: evaluation_criteria must be a list of actions")
            continue

        # design_rationale is a REQUIRED per-task field: a detailed account of
        # the task's design logic (exam point, traps, why the gold set and the
        # seed are shaped the way they are)
        dr = task.get("design_rationale")
        if not isinstance(dr, str) or len(dr.split()) < 20:
            errors.append(f"{tid}: missing or too-thin 'design_rationale' (>=20 words required)")

        # frozen_time is a REQUIRED per-task field (the task's only clock)
        ft = task.get("frozen_time")
        if not ft:
            errors.append(f"{tid}: missing required field 'frozen_time'")
        elif not re.match(r"^\d{4}-\d{2}-\d{2}\b", str(ft)):
            errors.append(f"{tid}: frozen_time '{ft}' must start with YYYY-MM-DD")

        # initial_state only seeds tables/fields the schema declares
        for tbl, rows in (task.get("initial_state") or {}).items():
            if sc.db_schema and tbl not in sc.db_schema:
                warnings.append(f"{tid}: initial_state seeds unknown table '{tbl}' (not in db_schema.json)")
                continue
            declared = sc.db_schema.get(tbl) or []
            for row_key, row in (rows or {}).items():
                unknown = [f for f in (row or {}) if f not in declared]
                if unknown:
                    warnings.append(f"{tid}: initial_state row '{tbl}/{row_key}' has "
                                    f"field(s) not in db_schema: {unknown}")

        # required documents exist
        for did in task.get("required_documents") or []:
            if did not in doc_ids:
                errors.append(f"{tid}: required document '{did}' not found")

        # permission boundary + existence: every named tool must be a real tool
        # whose declared owner matches the action's owner. Reads are NOT required —
        # a task whose rows are all touched by writes (a write's own ctx.find) or
        # named in write arguments has a complete closure with zero read actions;
        # per-task read count is governed by the suite-level calibration (range 0-6),
        # not a hard floor here.
        for a in gt:
            tool = a.get("tool") or a.get("name")
            owner = a.get("owner")
            resolved, _ = _resolve(a)
            target = resolved or tool
            # meta/base actions (unlock_*, KB_search, grep) carry no DB tool to bind:
            # they are legitimate trajectory steps (an agent task tool is reached as
            # unlock_agent_discoverable_tool -> call_agent_discoverable_tool; a user task
            # tool as unlock_user_discoverable_tool -> call_user_discoverable_tool). The
            # call_* wrapper already resolved to its inner tool above, so only the bare
            # meta actions land here — skip them, they have no owner/rw to check.
            if target in BASE_SCHEMAS:
                continue
            spec = registry.get(target)
            if spec is None:
                errors.append(f"{tid}: ground-truth action names unknown tool '{target}'")
                continue
            # meta-tool routing must be well-formed: a hidden TASK tool is reachable
            # ONLY through the call_* wrapper (of the matching owner side), and a
            # directly-named tool must be a SHARE tool. This keeps evaluation_criteria
            # faithful to the live runtime, where task tools are never directly callable.
            wrapped = tool in ("call_agent_discoverable_tool", "call_user_discoverable_tool")
            if wrapped:
                side = "agent" if tool == "call_agent_discoverable_tool" else "user"
                if spec.kind != "task":
                    errors.append(f"{tid}: {tool} wraps '{target}', a {spec.kind} tool — only hidden "
                                  "TASK tools are reached via call_*; share tools are named directly")
                if spec.owner != side:
                    errors.append(f"{tid}: {tool} wraps '{target}' (owner '{spec.owner}') — this wrapper "
                                  f"is for {side}-owned task tools")
            else:
                if spec.kind == "task":
                    u = spec.owner  # "agent" | "user"
                    errors.append(f"{tid}: '{target}' is a hidden TASK tool and cannot be named directly — "
                                  f"reach it via unlock_{u}_discoverable_tool + call_{u}_discoverable_tool")
                if owner and owner != spec.owner:
                    errors.append(f"{tid}: action owner '{owner}' != tool owner '{spec.owner}' for '{target}'")
        # deterministic clean replay x2 + non-vacuous + no guard misfires
        try:
            h1, gt_errs = _replay_checked(sc.engine_for(task), gt)
            h2, _ = _replay_checked(sc.engine_for(task), gt)
            empty = replay(sc.engine_for(task), [])
            for e in gt_errs:
                errors.append(f"{tid}: {e}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{tid}: ground-truth replay raised: {e}")
            continue
        if h1 != h2:
            errors.append(f"{tid}: ground-truth replay is non-deterministic")
        elif h1 == empty:
            errors.append(f"{tid}: ground truth produced no DB change (would pass a do-nothing agent)")
        else:
            n_ok += 1

    summary = {
        "scenario": sc.name,
        "difficulties": len(sc.tasks),
        "tasks": n_tasks,
        "tasks_ok": n_ok,
        "tools": len(sc.specs),
        "documents": len(sc.docs),
    }
    return errors, warnings, summary
