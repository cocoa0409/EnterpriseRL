"""SCOPE gate: check only structural policy ownership for one difficulty.

The task authoring contract is intentionally split in two. ``check_extended`` and the other
gates verify policy/GT structure and machine-recomputable values; this script verifies that
the assets claimed by each task are disjoint and that every extended policy has a declared
trigger and a unique ``(target_tool, computes)`` owner. It deliberately does *not* execute
foreign policies, infer obligations from a non-zero formula, mutate a seed, or require a tool
to reject anything. Whether a policy applies in a particular conversation is a semantic
decision for the agent and the runtime blind audit, not a third machine-authored rule.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_cross_fire.py \\
      env/<scenario>/tasks/<difficulty> [--task N]
Exit 0 = SCOPE OK, 1 = violations.
"""
import ast
import glob
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import paths_through_task, select_task_paths, split_task_flag


TRIGGERS = {"state_due", "on_request"}
CALL_WRAPPERS = {"call_agent_discoverable_tool", "call_user_discoverable_tool"}


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def task_tool_names(path):
    """Return names of @tool functions in a difficulty's task_tools.py."""
    if not os.path.exists(path):
        return set()
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    names = set()
    for fn in tree.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Name)
            and dec.func.id == "tool"
            for dec in fn.decorator_list
        ):
            names.add(fn.name)
    return names


def action_task_tool(action, known):
    """Resolve a direct or discoverable call without importing/executing the tool."""
    if not isinstance(action, dict):
        return None
    name = action.get("tool") or action.get("name")
    args = action.get("arguments") or {}
    if name in CALL_WRAPPERS:
        if not isinstance(args, dict):
            return None
        underlying = args.get("tool_name")
        return underlying if underlying in known else None
    return name if name in known else None


def scenario_root(start):
    path = os.path.abspath(start)
    while path != "/":
        if os.path.isdir(os.path.join(path, "blueprint")):
            return path
        path = os.path.dirname(path)
    raise SystemExit(f"cannot find scenario root (blueprint/) above {start}")


def main():
    positional, task_selector = split_task_flag(sys.argv[1:])
    if len(positional) != 1:
        print("usage: check_cross_fire.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    diff_dir = positional[0].rstrip("/")
    task_mode = task_selector is not None
    scenario_root(diff_dir)  # fail early with a useful path error

    ext_files = glob.glob(os.path.join(diff_dir, "*.extended.yaml"))
    if len(ext_files) != 1:
        raise SystemExit(f"expected exactly one <category>.extended.yaml under {diff_dir}, found {ext_files}")
    extended = load_yaml(ext_files[0]) or {}
    policies = {
        item.get("id"): item
        for item in (extended.get("extended_policies") or [])
        if isinstance(item, dict) and item.get("id")
    }

    known_task_tools = task_tool_names(os.path.join(diff_dir, "task_tools.py"))
    task_paths = select_task_paths(diff_dir, task_selector)
    if not task_paths:
        raise SystemExit(f"no task json under {diff_dir}/tasks/")
    # In --task mode include the completed prefix so scope overlap is caught immediately;
    # the final run checks the whole difficulty.
    scope_paths = paths_through_task(diff_dir, task_selector) if task_mode else task_paths

    fails = []
    if "workflows" in extended:
        fails.append("charter carries a `workflows` key — every problem is an extended_policy; delete the key")
    scopes = {}
    for task_path in scope_paths:
        tid = os.path.splitext(os.path.basename(task_path))[0]
        try:
            task = json.load(open(task_path, encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fails.append(f"task {tid}: invalid JSON ({exc})")
            continue

        computations = task.get("computations") or []
        own_policies = {
            item.get("policy_id")
            for item in computations
            if isinstance(item, dict) and item.get("policy_id")
        }
        gold_tools = {
            tool
            for action in (task.get("evaluation_criteria") or [])
            if (tool := action_task_tool(action, known_task_tools))
        }
        scope = task.get("charter_scope")
        if not isinstance(scope, dict):
            fails.append(
                f"charter_scope {tid}.json: missing — each task must register its policy "
                "and task-tool ownership"
            )
            scope = {}

        policy_scope = scope.get("extended_policies") or []
        tool_scope = scope.get("task_tools") or []
        if "workflows" in scope:
            fails.append(f"charter_scope {tid}.json: workflows is not a field — a task claims extended_policies "
                         "and task_tools only")
        if not isinstance(policy_scope, list):
            fails.append(f"charter_scope {tid}.json: extended_policies must be a list")
            policy_scope = []
        if not isinstance(tool_scope, list):
            fails.append(f"charter_scope {tid}.json: task_tools must be a list")
            tool_scope = []

        if set(policy_scope) != own_policies:
            fails.append(
                f"charter_scope {tid}.json: extended_policies {sorted(set(policy_scope))} "
                f"!= computation policy ids {sorted(own_policies)}"
            )
        if task.get("required_documents") != policy_scope:
            fails.append(
                f"charter_scope {tid}.json: required_documents must equal "
                "charter_scope.extended_policies in the same order"
            )
        if set(tool_scope) != gold_tools:
            fails.append(
                f"charter_scope {tid}.json: task_tools {sorted(set(tool_scope))} "
                f"!= task tools called by gold {sorted(gold_tools)}"
            )
        scopes[tid] = {
            "extended_policies": set(policy_scope),
            "task_tools": set(tool_scope),
        }

    # Keep numeric task ids in numeric order while remaining safe for a legacy/non-numeric
    # filename; returning one tuple shape avoids comparing ints and strings in Python 3.
    tids = sorted(
        scopes,
        key=lambda value: (0, int(value)) if value.isdigit() else (1, str(value)),
    )
    for index, left in enumerate(tids):
        for right in tids[index + 1:]:
            for key in ("extended_policies", "task_tools"):
                overlap = scopes[left][key] & scopes[right][key]
                if overlap:
                    fails.append(
                        f"charter_scope: tasks {left} and {right} share {key} {sorted(overlap)}"
                    )

    for policy_id, policy in policies.items():
        trigger = policy.get("trigger")
        if trigger not in TRIGGERS:
            fails.append(
                f"trigger: policy {policy_id!r} must declare one of {sorted(TRIGGERS)}, got {trigger!r}"
            )

    claims = {}
    for policy_id, policy in policies.items():
        claims.setdefault((policy.get("target_tool"), policy.get("computes")), []).append(policy_id)
    for (tool, parameter), policy_ids in sorted(claims.items(), key=lambda item: str(item[0])):
        if len(policy_ids) > 1:
            fails.append(
                f"claim: ({tool}, {parameter}) is assigned to multiple policies {policy_ids}; "
                "merge the branches into one policy or use distinct write parameters"
            )

    mode_label = f", selected_task={task_selector}" if task_mode else ""
    print(
        f"🔎 SCOPE gate  ({len(task_paths)} tasks{mode_label}, "
        f"policies={len(policies)}, hard-fails={len(fails)})"
    )
    if fails:
        print("  [FAIL]")
        for failure in fails:
            print("   -", failure)
        print("SCOPE NOT OK")
        sys.exit(1)
    print(
        "  [PASS] policy ownership, trigger declarations, and task scopes are structurally "
        "consistent; no business applicability or tool-rejection behavior was inferred"
    )
    print("SCOPE OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
