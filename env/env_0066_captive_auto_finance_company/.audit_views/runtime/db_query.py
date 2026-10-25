"""Coordinator-built runtime DB access path for KB auditors (env_0066).
Usage (from repo root):
  .venv/bin/python env/env_0066_captive_auto_finance_company/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
  .venv/bin/python env/env_0066_captive_auto_finance_company/.audit_views/runtime/db_query.py <difficulty> <task_idx> '[["tool_name", {"arg": "value"}], ...]'
Loads the scenario, seeds the task's opening DB via Scenario.engine_for, and runs the calls in order on ONE engine
(agent-owned share tools via Engine._run; KB_search / grep via Engine.call("agent", ...)). Prints only tool returns."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario
S = os.path.join(ROOT, "env", "env_0066_captive_auto_finance_company")
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(S)
task = sc.tasks[d][idx]
eng = sc.engine_for(task)
share = {n: s for n, s in eng.registry.items() if s.kind == "share" and s.owner == "agent"}
if sys.argv[3] == "--list":
    for n, s in sorted(share.items()):
        print(json.dumps(s.openai_schema(), ensure_ascii=False))
    print(json.dumps({"base_tools": ["KB_search(query)", "grep(pattern)"]}))
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in ("KB_search", "grep"):
        out = eng.call("agent", name, args)
    elif name in share:
        out = eng._run(share[name], args)
    else:
        out = f"Error: '{name}' is not an agent share tool or KB tool on this path."
    print(f"### {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")
