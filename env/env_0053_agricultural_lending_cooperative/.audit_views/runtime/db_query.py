"""Runtime-visible DB access for KB audits: run read-only share tools and KB_search/grep
against one task's seeded world, printing only the tool returns (never initial_state).
usage: .venv/bin/python env/<s>/.audit_views/runtime/db_query.py <difficulty> <idx> --list
       .venv/bin/python env/<s>/.audit_views/runtime/db_query.py <difficulty> <idx> '[["tool", {args}], ...]'
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = [t for t in sc.tasks[d] if t.get("task_index") == idx][0]
eng = sc.engine_for(task)
reads = {s.name: s for s in sc.specs if s.kind == "share" and s.rw == "read"}
if sys.argv[3] == "--list":
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
        out = f"Error: '{name}' is not a read-only share tool or KB tool"
    print(f"### {name} {json.dumps(args)}\n{out}\n")
