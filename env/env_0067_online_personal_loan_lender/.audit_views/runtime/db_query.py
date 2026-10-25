#!/usr/bin/env python
"""Runtime-shaped DB/KB access for KB audits (coordinator-built; read-only).
usage (from repo root):
  .venv/bin/python env/env_0067_online_personal_loan_lender/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0067_online_personal_loan_lender/.audit_views/runtime/db_query.py <difficulty> <idx> '[["find_customers", {"phone_number": "..."}], ["KB_search", {"query": "..."}]]'
Each call runs on a fresh engine seeded with that task's world at its frozen_time; only tool returns are printed.
Read share tools and the KB tools (KB_search, grep) are allowed; write tools are refused."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
diff, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(os.path.normpath(ROOT))
task = next(t for t in sc.tasks[diff] if t["task_index"] == idx)
eng = sc.engine_for(task)
KB = ("KB_search", "grep")
if sys.argv[3] == "--list":
    for s in eng.registry.values():
        if s.kind == "share" and s.rw != "write":
            print(json.dumps({"tool": s.name, "owner": s.owner, "parameters": s.parameters}))
    print(json.dumps({"tool": "KB_search / grep", "owner": "agent", "note": "runtime KB tools"}))
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    print(f"### {name} {json.dumps(args)}")
    if name in KB:
        print(eng.call("agent", name, args))
        continue
    s = eng.registry.get(name)
    if s is None or s.kind != "share" or s.rw == "write":
        print(f"refused: {name} is not a read share tool")
        continue
    print(eng._run(s, args))
