"""Runtime DB access path for KB audits (coordinator-supplied).

usage (from the repository root):
  .venv/bin/python env/env_0059_residential_mortgage_lender/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
  .venv/bin/python env/env_0059_residential_mortgage_lender/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool_name, {args}]>'

Builds that task's runtime engine (seeded DB + frozen clock + published KB) exactly as a
rollout does, runs the calls IN ORDER on one engine (writes persist within one invocation,
nothing is saved), and prints only the tool returns. Share tools and task tools run as their
owner would call them; KB_search / grep go through the agent's base tools. It never prints
initial_state, task JSON fields or tool source.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0059_residential_mortgage_lender"
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = sc.tasks[d][idx]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    print("frozen_time:", task["frozen_time"])
    for s in sorted(eng.registry.values(), key=lambda s: (s.kind, s.name)):
        if s.kind == "share":
            print(f"[share/{s.owner}] {s.name}{json.dumps(s.parameters.get('properties', {}))}")
    print("[base/agent] KB_search{query}, grep{pattern}")
    print("task tools: pass their exact names (as found in the KB) to run them on this world")
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in ("KB_search", "grep"):
        out = eng.call("agent", name, args)
    else:
        spec = eng.registry.get(name)
        out = f"Error: unknown tool '{name}'." if spec is None else eng._run(spec, args)
    print(f"### {name} {json.dumps(args)}\n{out}\n")
