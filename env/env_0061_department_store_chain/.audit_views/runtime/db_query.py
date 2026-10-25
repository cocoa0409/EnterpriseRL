"""Runtime-visible DB access for KB audits (coordinator-built).
usage (repo root):
  .venv/bin/python env/env_0061_department_store_chain/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0061_department_store_chain/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, {args}]>'
Runs share tools (as their owner) and the agent base tools (KB_search / grep / ...) on a fresh engine
seeded from that task's world at its frozen_time; prints only the tool returns. Never prints initial_state."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
ROOT = "env/env_0061_department_store_chain"
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = [t for t in sc.tasks[d] if int(t.get("task_index", -1)) == idx or sc.tasks[d].index(t) == idx][0]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    for s in sc.specs:
        if s.kind == "share":
            print(f"{s.owner:5s} {s.rw:5s} {s.name}")
    print("agent base tools:", [x["function"]["name"] if "function" in x else x.get("name") for x in eng.tool_list("agent")][:12])
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    spec = eng.registry.get(name)
    if spec is not None and spec.kind == "share":
        out = eng._run(spec, args)
    else:
        out = eng.call("agent", name, args)
    print(f"### {name} {json.dumps(args)}\n{out}\n")
