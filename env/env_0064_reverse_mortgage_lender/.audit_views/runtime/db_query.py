"""Runtime-visible access path for KB audits (coordinator-built).
usage (from repo root):
  .venv/bin/python env/env_0064_reverse_mortgage_lender/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0064_reverse_mortgage_lender/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, args]>'
Runs the calls, in order, against a fresh engine seeded with that task's world, exactly as the
rollout agent would see them: share tools (direct), KB_search, grep, unlock_agent_discoverable_tool,
unlock_user_discoverable_tool. Task tools cannot be called. Prints only the tool returns."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
S = os.path.join(os.getcwd(), "env/env_0064_reverse_mortgage_lender")
ALLOWED_BASE = {"KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool"}
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(S)
task = [t for t in sc.tasks[d] if int(t.get("task_index", -1)) == idx or sc.tasks[d].index(t) == idx][0]
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    for s in eng.registry.values():
        if s.kind == "share":
            print(json.dumps(s.openai_schema(), ensure_ascii=False))
    sys.exit()
for name, args in json.loads(sys.argv[3]):
    if name in ALLOWED_BASE:
        out = eng.call("agent", name, args)
    else:
        spec = eng.registry.get(name)
        if spec is None or spec.kind != "share":
            out = f"Error: '{name}' is not callable on this access path (share tools and KB tools only)."
        else:
            out = eng._run(spec, args)
    print(f"### {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")
