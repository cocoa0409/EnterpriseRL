"""Runtime DB access path for KB audits (coordinator-built).

Seeds a fresh engine for one task's world exactly as erlbench does at rollout time and runs
tool-shaped calls against it; prints only the tool returns. The raw initial_state is never printed.

usage (from the repository root):
  .venv/bin/python env/env_0048_manufactured_home_community_operator/.audit_views/runtime/db_query.py <difficulty> <task_index> --list
  .venv/bin/python env/env_0048_manufactured_home_community_operator/.audit_views/runtime/db_query.py <difficulty> <task_index> '[["find_customers", {"phone_number": "..."}], ["find_lease_holdings", {"customer_id": "..."}]]'
Calls in one invocation share one engine (a write is visible to later reads in the same invocation); every
invocation starts again from the task's opening world. Callable: every share tool (as the agent) and the
base tools KB_search / grep. Task tools are listed (schemas) but not executable here.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0048_manufactured_home_community_operator"
diff, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = next(t for t in sc.tasks[diff] if t["task_index"] == idx)
eng = sc.engine_for(task)
if sys.argv[3] == "--list":
    print("frozen_time:", task["frozen_time"])
    tdir = os.path.join(ROOT, "tasks", diff, "task_tools.py")
    for s in sc.specs:
        if s.kind == "share" or (s.kind == "task" and s.func.__code__.co_filename.endswith(os.path.join(diff, "task_tools.py"))):
            print(json.dumps({"kind": s.kind, "owner": s.owner, "rw": s.rw, **s.openai_schema()["function"]}, ensure_ascii=False))
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in ("KB_search", "grep"):
        out = eng.call("agent", name, args)
    else:
        spec = eng.registry.get(name)
        if spec is None or spec.kind != "share":
            out = f"Error: '{name}' is not a share tool (task tools are not executable through this path)."
        else:
            out = eng._run(spec, args)
    print(f">>> {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")
