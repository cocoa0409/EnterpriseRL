"""Tool-shaped runtime access for KB audits (coordinator-built; never prints initial_state).
usage (repo root):
  .venv/bin/python env/env_0060_window_replacement_company/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0060_window_replacement_company/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, {args}]>'
Calls run in sequence on one freshly seeded engine at the task's frozen_time. Allowed: read-only
share tools (agent or user owned), KB_search, grep, unlock_agent_discoverable_tool,
unlock_user_discoverable_tool (to see a tool's runtime schema). Only tool returns are printed."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
ROOT = "env/env_0060_window_replacement_company"
diff, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = [t for t in sc.tasks[diff] if int(t.get("task_index", -1)) == idx or sc.tasks[diff].index(t) == idx][0]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    for s in eng.registry.values():
        if s.kind == "share":
            print(json.dumps({"name": s.name, "owner": s.owner, "rw": s.rw, "schema": s.openai_schema()}, ensure_ascii=False))
    sys.exit(0)
BASE = {"KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool"}
for name, args in json.loads(sys.argv[3]):
    print(f"### {name} {json.dumps(args, ensure_ascii=False)}")
    if name in BASE:
        print(eng.call("agent", name, args))
        continue
    spec = eng.registry.get(name)
    if spec is None or spec.kind != "share" or spec.rw != "read":
        print("Error: only read-only share tools and KB/unlock base tools are allowed here")
        continue
    print(eng._run(spec, args))
