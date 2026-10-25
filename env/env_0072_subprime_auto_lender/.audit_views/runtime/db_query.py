#!/usr/bin/env python
"""Runtime-visible DB access for KB auditors (coordinator-built; never reads initial_state as text).
usage: .venv/bin/python env/env_0072_subprime_auto_lender/.audit_views/runtime/db_query.py <difficulty> <idx> --list
       .venv/bin/python env/env_0072_subprime_auto_lender/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, args]>'
Only share READ tools and the agent KB tools (KB_search, grep) are callable; prints only tool returns."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
ROOT = "env/env_0072_subprime_auto_lender"
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = sc.tasks[d][idx]
eng = sc.engine_for(task)
reads = {s.name: s for s in sc.specs if s.kind == "share" and s.rw == "read"}
if sys.argv[3] == "--list":
    print("frozen_time:", task["frozen_time"])
    for n, s in sorted(reads.items()):
        print(n, json.dumps(s.parameters.get("properties", {})))
    print("KB_search {query}", "grep {pattern}")
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in ("KB_search", "grep"):
        out = eng.call("agent", name, args)
    elif name in reads:
        out = eng._run(reads[name], args)
    else:
        out = f"Error: {name} not permitted in this view"
    print(f"### {name} {json.dumps(args)}\n{out}\n")
