"""TRACEABILITY gate — every non-computed gold argument value must be copyable verbatim out of
context the agent can actually reach (the machine-checkable face of GT / source rule).

Scoring replays gold writes and compares final DB hashes, and every task tool derives its row id
from ALL of its arguments (ctx.make_id) — so a single argument value the agent cannot reach makes
the task unwinnable for ANY agent (expected score 0, not "hard").

Write-argument values have exactly TWO legitimate origins:
  - COMPUTED (numbers, dates): pinned by an extended_policy compute / policy date arithmetic and
    re-verified by check_compute + factor traces. Exempt here.
  - COPIED (every other string: reference numbers, enums, codes, verbatim phrases, row ids): the
    agent can only copy them from context it actually reaches. Required verbatim here.
There is NO third origin. "The system would generate it" fails BY DESIGN — no such system exists
in the environment.

The reachable context is rebuilt from the runtime-visible surfaces, cumulatively:
  static   published KB documents' title/content (the only policy surface)
         + the company background shown in the agent system prompt
         + schemas of directly listed share tools
  per-task + the user-simulator brief as the potential dialogue source + frozen_time
  dynamic  + the RETURN TEXT of every PRIOR agent-owned gold action, appended while replaying the
           gold in order with the real tools (a value minted by an earlier agent write — e.g. a
           request id a later step must quote — becomes reachable when that write returns).
           User-owned tool results are not visible to the agent unless the simulator relays them
           in dialogue. Hidden task-tool schemas are appended only after their unlock action,
           matching the runtime.

The authoring files `*.extended.yaml`, blueprint product YAML, `initial_state`, task JSON,
render metadata, and tool implementation source are deliberately not context: they are hidden
from the rollout agent. Database values become visible only through a tool return, not merely
because they were seeded.

Each evaluation_criteria argument leaf (including the inner `arguments` of call_* wrappers) that
is not numeric/date-like must appear verbatim in the context accumulated BEFORE its own action
executes. A comma-joined composite passes if every part passes. Any miss is a world defect, never
a gate defect — expose the value through a real query return or simulator dialogue. Only a truly
system-generated identifier may be removed from the agent-facing arguments and minted by the
atomic CRUD implementation; never move a policy-derived amount, status, or decision into a tool
to make this check pass.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/<scenario>/tasks/<difficulty> [--task N]
"""
import glob
import importlib.util
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import select_task_paths, split_task_flag

DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?([ T]\d{2}:\d{2}(:\d{2})?( [A-Z]{2,5})?)?$")


def _find_repo_root(start):
    p = os.path.abspath(start)
    while p != "/":
        if os.path.isdir(os.path.join(p, "erlbench")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def _import(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def leaves(x, path=""):
    """(dotted_path, leaf) over nested argument structures — covers both the top-level
    `arguments` and the inner `arguments` of unlock_*/call_* wrappers in one walk."""
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{path}.{k}" if path else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, x


def computed_class(v):
    """Numbers and date-like strings are the compute-pinned class — check_compute territory."""
    if isinstance(v, bool):
        return True
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        pass
    return isinstance(v, str) and bool(DATE_RE.match(v.strip()))


def main():
    pos, task_selector = split_task_flag(sys.argv[1:])
    if len(pos) < 1:
        print("usage: check_traceability.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    target = pos[0].rstrip("/")
    sys.path.insert(0, _find_repo_root(target))
    from erlbench.tools import collect_specs, ToolContext
    from erlbench.db import DB
    from erlbench.determinism import Clock
    from erlbench.scoring import _resolve

    scen = os.path.dirname(os.path.dirname(target))  # env/<scenario>
    bp = os.path.join(scen, "blueprint")
    db_schema = json.load(open(os.path.join(bp, "db_schema.json")))

    specs = {}
    for s in collect_specs(_import(os.path.join(bp, "share_tools.py"), "_tr_share"), "share"):
        specs[s.name] = s
    tt = os.path.join(target, "task_tools.py")
    if os.path.exists(tt):
        for s in collect_specs(_import(tt, "_tr_task"), "task"):
            specs[s.name] = s

    # Only publish what the rollout can actually expose. Reading raw YAML or Python source
    # here would make an unwinnable task appear solvable simply because an internal id/value
    # happens to occur in an authoring file. The loader indexes title/content and the engine
    # exposes share schemas directly; hidden task schemas appear in the unlock response.
    static_parts = []
    docs_dir = os.path.join(scen, "docs")
    for p in sorted(glob.glob(os.path.join(docs_dir, "**", "*.json"), recursive=True)):
        try:
            obj = json.load(open(p, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict) and isinstance(obj.get("content"), str):
            static_parts.append(str(obj.get("title") or obj.get("id") or ""))
            static_parts.append(obj["content"])

    # The agent receives only this small, explicit part of blueprint.yaml in its system prompt.
    try:
        blueprint = yaml.safe_load(
            open(os.path.join(bp, "blueprint.yaml"), encoding="utf-8")
        ) or {}
    except (OSError, yaml.YAMLError):
        blueprint = {}
    for key in ("company", "background"):
        value = blueprint.get(key)
        if value:
            static_parts.append(str(value))

    for spec in specs.values():
        if spec.kind == "share" and spec.owner == "agent":
            static_parts.append(json.dumps(spec.openai_schema(), ensure_ascii=False, sort_keys=True))
    static = "\n".join(static_parts)

    task_paths = select_task_paths(target, task_selector)
    if not task_paths:
        raise SystemExit(f"no task json under {target}/tasks/")

    mode_label = f", selected_task={task_selector}" if task_selector is not None else ""
    print(f"🔎 TRACEABILITY gate  ({len(task_paths)} tasks{mode_label})")
    print(f"{'task':10} {'copied':>7} {'missing':>8} {'ok':>5}")
    fails = []
    for tp in task_paths:
        tid = os.path.basename(tp)
        t = json.loads(open(tp, encoding="utf-8").read())
        initial = t.get("initial_state") or {}
        clock = Clock.from_stamp(t.get("frozen_time"))
        db = DB.seeded(initial)
        # `user_scenario` is not an agent prompt; it is the simulator's complete brief. It is
        # retained as a potential source because the simulator can disclose a marked value when
        # asked, while the DB seed itself remains hidden until a read tool returns it.
        ctx_text = "\n".join((static, str(t.get("user_scenario", "")),
                              str(t.get("frozen_time", ""))))

        def reachable(s):
            if s in ctx_text:
                return True
            if "," in s:  # composite fixed-format: every part must itself be reachable
                parts = [p.strip() for p in s.split(",") if p.strip()]
                return bool(parts) and all(computed_class(p) or p in ctx_text for p in parts)
            return False

        missing = {}
        n_copied = 0
        for a in (t.get("evaluation_criteria") or []):
            # 1) check this action's args against context accumulated so far (prior actions only)
            for path, v in leaves(a.get("arguments") or {}):
                if v is None or v == "" or computed_class(v):
                    continue
                n_copied += 1
                if not reachable(str(v)):
                    missing.setdefault(str(v), []).append(f"{a.get('tool','?')}:{path}")
            # 2) execute it with the real tools and append its return — later actions may copy it
            tool, args = _resolve(a)
            spec = specs.get(tool) if tool else None
            if spec is not None and a.get("owner") == "agent":
                try:
                    out = str(spec.func(ToolContext(db, clock, db_schema,
                                                    writable=(spec.rw == "write")),
                                        **spec.coerce(args)))
                except Exception as e:  # noqa: BLE001 — replay gate owns error-freeness
                    out = str(e)
                ctx_text += "\n" + out

            # A hidden task schema is revealed by unlock_* and is therefore visible for later
            # calls, but must not be used as if it had been visible before that unlock.
            raw_tool = (a.get("tool") or a.get("name")) if isinstance(a, dict) else None
            if raw_tool in {"unlock_agent_discoverable_tool", "unlock_user_discoverable_tool"}:
                tool_name = (a.get("arguments") or {}).get("tool_name")
                unlocked = specs.get(tool_name)
                if unlocked is not None and unlocked.kind == "task":
                    ctx_text += "\n" + json.dumps(
                        unlocked.openai_schema(), ensure_ascii=False, sort_keys=True
                    )

        print(f"{tid:10} {n_copied:>7} {len(missing):>8} {str(not missing):>5}")
        for s, locs in missing.items():
            fails.append(f"{tid}: '{s}' ({', '.join(sorted(set(locs))[:4])}) has NO verbatim source in "
                         "the agent-reachable context (published KB / visible tool schemas / "
                         "simulator dialogue / frozen_time / prior tool returns). It enters the row id via "
                         "make_id, so the task is unwinnable for any agent. Fix the world by exposing "
                         "it through a query return or the simulator dialogue; only a truly system-"
                         "generated id may be removed from the call and minted by atomic CRUD.")

    if fails:
        print("\n  [FAIL]")
        for f in fails[:60]:
            print("   -", f)
        print("TRACEABILITY NOT OK")
        sys.exit(1)
    print("\nTRACEABILITY OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
