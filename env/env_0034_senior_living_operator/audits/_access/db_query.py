"""Runtime-shaped DB access for blind KB audits (coordinator-supplied).

Usage (from the repository root):
  .venv/bin/python env/env_0034_senior_living_operator/audits/_access/db_query.py <difficulty> <task_index> list
  .venv/bin/python env/env_0034_senior_living_operator/audits/_access/db_query.py <difficulty> <task_index> call <tool_name> '<json args>'

Seeds that task's world exactly as a rollout would (frozen_time + initial_state, read
by this script, never printed) and routes the call through erlbench Engine.call as the
"agent" owner. Only shared READ tools and the KB_search / grep base tools are allowed,
so the output is exactly what a rollout agent could observe; nothing is written back.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0034_senior_living_operator"

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    diff, idx, cmd = sys.argv[1], sys.argv[2], sys.argv[3]
    sc = load_scenario(ROOT)
    with open(os.path.join(ROOT, "tasks", diff, "tasks", f"{int(idx)}.json")) as f:
        task = json.load(f)
    eng = sc.engine_for(task)
    allowed = {s.name: s for s in sc.specs if s.kind == "share" and s.owner == "agent" and s.rw == "read"}
    if cmd == "list":
        for n, s in sorted(allowed.items()):
            print(json.dumps(s.openai_schema(), ensure_ascii=False))
        print('{"base tools also allowed": ["KB_search", "grep"]}')
        return
    if cmd == "call":
        name = sys.argv[4]; args = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        if name not in allowed and name not in ("KB_search", "grep"):
            print(f"Error: '{name}' is not a shared read tool or KB tool; not available in the audit access path."); sys.exit(1)
        print(eng.call("agent", name, args))
        return
    print(__doc__); sys.exit(2)

if __name__ == "__main__":
    main()
