#!/usr/bin/env python
"""Coordinator-supplied runtime DB access path for KB audits (tool-shaped, read-only).
usage: .venv/bin/python env/env_0080_big_box_general_merchandise_retailer/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
       .venv/bin/python env/env_0080_big_box_general_merchandise_retailer/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool_name, {args}]>'
Runs share READ tools (and the agent base KB tools) against that task's seeded world and prints only the returns."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
ROOT = "env/env_0080_big_box_general_merchandise_retailer"
d, i = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = sc.tasks[d][i]
eng = sc.engine_for(task)
share = {s.name: s for s in sc.specs if s.kind == "share"}
if sys.argv[3] == "--list":
    for n, s in sorted(share.items()):
        if s.rw != "write" and s.owner == "agent":
            print(n, "-", (s.description or "").split("\n")[0][:120])
    print("(agent base tools such as KB search are also callable by name)")
    sys.exit(0)
calls = json.loads(sys.argv[3])
for name, args in calls:
    s = share.get(name)
    if s is not None and (s.rw == "write" or s.owner != "agent"):
        print(f"## {name}: refused (write or non-agent tool)"); continue
    print(f"## {name} {json.dumps(args)}")
    print(eng.call("agent", name, args))
