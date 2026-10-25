"""Runtime DB access path for KB auditors (tool-shaped queries only; never prints initial_state).

usage (from the repository root):
  .venv/bin/python env/env_0070_dental_and_vision_benefits_carrier/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
  .venv/bin/python env/env_0070_dental_and_vision_benefits_carrier/.audit_views/runtime/db_query.py <difficulty> <task_idx> '[["find_customers", {"phone_number": "..."}], ["KB_search", {"query": "..."}]]'
Calls run in order against one fresh engine for that task's world: share tools via the engine's
tool runner, base tools (KB_search / grep / unlock tools) via engine.call("agent", ...). Task tools
are not callable here (they write); only their published schemas are visible via --list.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0070_dental_and_vision_benefits_carrier"
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = [t for t in sc.tasks[d] if int(t.get("task_index", -1)) == idx or sc.tasks[d].index(t) == idx][0]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    print(json.dumps([s["function"]["name"] if "function" in s else s.get("name") for s in eng.tool_list("agent")], indent=1))
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    spec = eng.registry.get(name)
    if spec is not None and spec.kind == "share":
        if spec.rw == "write":
            print(f"## {name}: refused (write tool)"); continue
        out = eng._run(spec, args)
    else:
        out = eng.call("agent", name, args)
    print(f"## {name} {json.dumps(args)}\n{out}\n")
