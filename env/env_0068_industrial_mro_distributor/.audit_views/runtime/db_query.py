#!/usr/bin/env python3
"""Runtime-visible access path for KB audits (coordinator-built, read-only).

usage (from the repo root):
  .venv/bin/python env/env_0068_industrial_mro_distributor/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0068_industrial_mro_distributor/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, {args}]>'

Runs the agent-visible share tools (read tools only) and KB_search / grep /
unlock_agent_discoverable_tool / unlock_user_discoverable_tool on a fresh engine seeded
from that task's world, and prints only the tool returns — never the raw seed.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0068_industrial_mro_distributor"
KB_TOOLS = {"KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool"}

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    diff, idx, payload = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sc = load_scenario(ROOT)
    task = next(t for t in sc.tasks[diff] if t["task_index"] == idx)
    eng = sc.engine_for(task)
    share = {s.name: s for s in sc.specs if s.kind == "share" and s.owner == "agent" and s.rw != "write"}
    if payload == "--list":
        print("KB tools:", sorted(KB_TOOLS))
        for n, s in sorted(share.items()):
            print(f"share read tool: {n}{tuple(s.parameters.get('properties', {}).keys())}")
        return
    for i, (name, args) in enumerate(json.loads(payload)):
        if name in KB_TOOLS:
            out = eng.call("agent", name, args)
        elif name in share:
            out = eng._run(share[name], args)
        else:
            out = f"Error: '{name}' is not on the audit access path (only share read tools and KB tools)."
        print(f"### [{i}] {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")

if __name__ == "__main__":
    main()
