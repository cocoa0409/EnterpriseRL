"""Runtime-visible DB access for KB auditors (coordinator-owned; execute only).
usage: .venv/bin/python env/env_0075_franchised_auto_dealer_group/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
       .venv/bin/python env/env_0075_franchised_auto_dealer_group/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool, {args}]>'
Seeds the task's opening DB at its frozen_time and runs agent-visible SHARE tools and base KB tools
(e.g. KB_search / grep) exactly as a rollout would. Prints only the tool returns. Task tools are not callable."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario
SCEN = os.path.join(ROOT, "env", "env_0075_franchised_auto_dealer_group")
d, i = sys.argv[1], int(sys.argv[2])
sc = load_scenario(SCEN)
eng = sc.engine_for(sc.tasks[d][i])
if sys.argv[3] == "--list":
    for s in sorted(eng.registry.values(), key=lambda s: s.name):
        if s.kind == "share" and s.owner == "agent":
            print(s.name, "-", s.description.splitlines()[0][:120])
    print("(plus base KB tools available to the agent via the engine)")
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    spec = eng.registry.get(name)
    if (spec is not None and spec.kind != "share") or name.startswith("call_"):
        out = "Error: read-only access: share finders, KB_search, grep and unlock_* only"
    else:
        out = eng.call("agent", name, args)
    print(f"### {name} {json.dumps(args)}\n{out}\n")
