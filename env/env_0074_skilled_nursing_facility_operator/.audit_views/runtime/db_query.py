"""Runtime-visible DB/KB access path for KB auditors (env_0074).
usage: .venv/bin/python env/env_0074_skilled_nursing_facility_operator/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
       .venv/bin/python .../db_query.py <difficulty> <task_idx> '<json list of [tool, {args}]>'
Runs only share (agent-visible) tools, KB_search and grep against that task's seeded world at its frozen_time;
prints only the tool returns, exactly as a rollout agent would see them. Each invocation starts from the seed."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(ROOT)))
from erlbench.loader import load_scenario
d, i = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = sc.tasks[d][i]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    print(json.dumps([t for t in eng.tool_list("agent")], indent=1)); sys.exit()
for name, args in json.loads(sys.argv[3]):
    print(f"### {name} {json.dumps(args)}")
    if name in ("KB_search", "grep"):
        print(eng.call("agent", name, args))
    else:
        spec = eng.registry.get(name)
        print(eng._run(spec, args) if spec is not None and spec.kind == "share" else f"Error: '{name}' is not a share tool")
