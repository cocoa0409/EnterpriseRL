"""Runtime-visible DB access path for KB auditors (coordinator-built).
usage: .venv/bin/python env/env_0073_regional_hospital_system/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
       .venv/bin/python env/env_0073_regional_hospital_system/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool_name, {args}]>'
Calls go through Engine.call("agent", ...) on a fresh engine seeded exactly as a rollout's
(frozen_time + initial_state); only what the agent-side tools return is printed."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario

SCEN = os.path.join(ROOT, "env", "env_0073_regional_hospital_system")

def main():
    d, idx = sys.argv[1], int(sys.argv[2])
    sc = load_scenario(SCEN)
    task = [t for t in sc.tasks[d] if int(t.get("task_index", -1)) == idx or sc.tasks[d].index(t) == idx][0]
    eng = sc.engine_for(task)
    if sys.argv[3] == "--list":
        for s in eng.tool_list("agent"):
            f = s.get("function", s)
            print(f.get("name"), "-", (f.get("description") or "")[:120].replace("\n", " "))
        return
    for name, args in json.loads(sys.argv[3]):
        print(f">>> {name} {json.dumps(args)}")
        print(eng.call("agent", name, args))

if __name__ == "__main__":
    main()
