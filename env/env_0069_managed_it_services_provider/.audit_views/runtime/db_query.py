"""Runtime DB access path for KB audits (coordinator-built).
usage (from repo root):
  .venv/bin/python env/env_0069_managed_it_services_provider/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
  .venv/bin/python env/env_0069_managed_it_services_provider/.audit_views/runtime/db_query.py <difficulty> <task_idx> '[["find_customers", {"phone_number": "..."}], ["KB_search", {"query": "..."}]]'
Calls run in order against ONE fresh engine seeded with that task's world at its frozen_time; only tool returns are printed.
Share tools run as their owner; KB/base tools run as the agent. Task (unlockable) tools are not callable here.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
from erlbench.engine import BASE_SCHEMAS
sc = load_scenario("env/env_0069_managed_it_services_provider")
d, i = sys.argv[1], int(sys.argv[2])
task = sc.tasks[d][i]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    print("share tools:", sorted(s.name for s in eng.registry.values() if s.kind == "share"))
    print("base tools:", sorted(BASE_SCHEMAS))
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    spec = eng.registry.get(name)
    if spec is not None and spec.kind == "share":
        out = eng._run(spec, args)
    elif name in BASE_SCHEMAS:
        out = eng.call("agent", name, args)
    else:
        out = f"Error: '{name}' is not a share or base tool"
    print(f"### {name} {json.dumps(args)}\n{out}\n")
