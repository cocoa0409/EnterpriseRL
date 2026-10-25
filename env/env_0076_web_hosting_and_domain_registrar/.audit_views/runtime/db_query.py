#!/usr/bin/env python
"""Runtime-visible DB access for KB auditors (no raw initial_state).
usage: .venv/bin/python env/<s>/.audit_views/runtime/db_query.py <difficulty> <idx> --list
       .venv/bin/python env/<s>/.audit_views/runtime/db_query.py <difficulty> <idx> --context
       .venv/bin/python env/<s>/.audit_views/runtime/db_query.py <difficulty> <idx> '[["find_customers", {"email": "..."}], ["KB_search", {"query": "..."}]]'
Calls run in order on one engine seeded at the task's frozen_time, through Engine.call("agent", ...) — exactly the
agent's runtime surface (share tools + KB_search/grep); only the tool returns are printed."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..")))
from erlbench.loader import load_scenario
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = sc.tasks[d][idx]
eng = sc.engine_for(task)
arg = sys.argv[3] if len(sys.argv) > 3 else "--list"
if arg == "--list":
    for s in eng.tool_list("agent"):
        f = s.get("function", s); print(f.get("name"), "-", (f.get("description") or "").split("\n")[0])
elif arg == "--context":
    print(json.dumps({"frozen_time": task["frozen_time"], "user_scenario": task["user_scenario"]}, indent=1, ensure_ascii=False))
else:
    for name, a in json.loads(arg):
        print(f"### {name} {json.dumps(a, ensure_ascii=False)}")
        print(eng.call("agent", name, a))
