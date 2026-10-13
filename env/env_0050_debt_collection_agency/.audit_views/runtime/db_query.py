"""Tool-shaped DB access for render-layer audits (coordinator-supplied).

Usage (from the repository root):
  .venv/bin/python env/env_0050_debt_collection_agency/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list | --schemas | --system
  .venv/bin/python env/env_0050_debt_collection_agency/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool, args]>'

Seeds a fresh engine for that task's world at its frozen_time, runs the calls in order on one
engine (so a write is visible to later reads in the same invocation), and prints only the tool
returns. Share tools run as the runtime runs them; KB_search / grep go through the agent's base
tools. Nothing else of the task file is printed.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..")))
from erlbench.loader import load_scenario  # noqa: E402


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)
    diff, idx, payload = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sc = load_scenario(ROOT)
    tasks = sc.tasks.get(diff)
    if not tasks or idx >= len(tasks):
        print(f"no task {diff}/{idx}")
        sys.exit(2)
    eng = sc.engine_for(tasks[idx])
    if payload == "--system":
        sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..")))
        from rollout.prompts import build_agent_prompt
        bp = sc.blueprint or {}
        company = bp.get("company") or bp.get("company_name") or sc.name
        print("frozen_time:", tasks[idx]["frozen_time"])
        print(build_agent_prompt(company, bp.get("background"), tasks[idx]["frozen_time"]))
        return
    if payload == "--schemas":
        for s in sorted(eng.registry.values(), key=lambda s: (s.kind, s.name)):
            print(json.dumps({"kind": s.kind, "owner": s.owner, **s.openai_schema()}, ensure_ascii=False))
        return
    if payload == "--list":
        for s in sorted(eng.registry.values(), key=lambda s: (s.kind, s.name)):
            print(f"{s.kind:5} {s.owner:5} {s.rw:5} {s.name}  params={list(s.parameters.get('properties', {}))}")
        print("base  agent read  KB_search  params=['query']")
        print("base  agent read  grep  params=['pattern']")
        return
    calls = json.loads(payload)
    for i, (name, args) in enumerate(calls):
        if name in ("KB_search", "grep"):
            out = eng.call("agent", name, args)
        else:
            spec = eng.registry.get(name)
            out = f"Error: unknown tool '{name}'." if spec is None else eng._run(spec, args)
        print(f"### [{i}] {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")


if __name__ == "__main__":
    main()
