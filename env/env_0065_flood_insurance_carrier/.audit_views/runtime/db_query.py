"""Runtime-visible DB access path for KB audits (coordinator-built).
usage: .venv/bin/python env/env_0065_flood_insurance_carrier/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
       .venv/bin/python env/env_0065_flood_insurance_carrier/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool, {args}]>'
Calls run in order on one engine seeded from the task world at its frozen_time, as the agent would:
only the agent's read-only share tools plus KB_search / grep are allowed. Prints tool returns only."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

S = "env/env_0065_flood_insurance_carrier"
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(S)
task = [t for t in sc.tasks[d] if int(t.get("task_index", -1)) == idx or sc.tasks[d].index(t) == idx][0]
eng = sc.engine_for(task)
allowed = {s.name: s for s in sc.specs if s.kind == "share" and s.owner == "agent" and s.rw == "read"}
if sys.argv[3] == "--list":
    for n, s in sorted(allowed.items()):
        print(n, json.dumps(s.parameters.get("properties", {}))[:300])
    print("KB_search {'query': str}\ngrep {'pattern': str}")
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name not in allowed and name not in ("KB_search", "grep"):
        print(f"## {name}: not allowed on this access path"); continue
    print(f"## {name} {json.dumps(args)}")
    print(eng.call("agent", name, args))
