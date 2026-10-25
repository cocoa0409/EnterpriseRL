#!/usr/bin/env python3
"""Tool-shaped DB access for KB auditors.
usage: db_query.py <difficulty> <task_idx> --list
       db_query.py <difficulty> <task_idx> '<json list of [tool_name, {args}]>'
Runs share read tools (and KB_search / grep) against that task's seeded world; prints only tool returns."""
import sys, json, os
ROOT = "/home/ubuntu/github/enterprise_rl"
sys.path.insert(0, ROOT); os.chdir(ROOT)
from erlbench.loader import load_scenario
sc = load_scenario("env/env_0079_property_restoration_contractor")
d, i = sys.argv[1], int(sys.argv[2])
task = sc.tasks[d][i]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    for s in eng.registry.values():
        if s.kind == "share" and s.rw != "write":
            print(s.name, json.dumps(s.parameters.get("properties", {}))[:300])
    print("KB_search / grep via engine base tools"); sys.exit()
for name, args in json.loads(sys.argv[3]):
    spec = eng.registry.get(name)
    if spec is not None and spec.kind == "share":
        if spec.rw == "write":
            print(f"== {name}: refused (write tool)"); continue
        print(f"== {name} {json.dumps(args)}\n{eng._run(spec, args)}")
    else:
        print(f"== {name} {json.dumps(args)}\n{eng.call('agent', name, args)}")
