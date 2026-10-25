"""Runtime DB access path for KB audits (coordinator-built).

Usage (from the repository root):
  .venv/bin/python env/env_0057_durable_medical_equipment_supplier/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
  .venv/bin/python env/env_0057_durable_medical_equipment_supplier/.audit_views/runtime/db_query.py <difficulty> <task_idx> '[["find_customers", {"phone_number": "..."}], ["KB_search", {"query": "..."}]]'

Loads the scenario with erlbench.loader.load_scenario, builds the task's engine (seeded DB at frozen_time,
published KB) and routes each call exactly as a rollout agent would (Engine.call with owner "agent"):
share tools plus the agent base tools. Calls in one invocation run in order on one engine; nothing persists
between invocations. Only tool returns are printed — never initial_state or any other task field.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

S = "env/env_0057_durable_medical_equipment_supplier"

def main():
    d, idx = sys.argv[1], int(sys.argv[2])
    sc = load_scenario(S)
    tasks = sc.tasks[d]
    task = next((t for t in tasks if t.get("task_index") == idx), None) or tasks[idx]
    eng = sc.engine_for(task)
    if sys.argv[3] == "--list":
        for sch in eng.tool_list("agent"):
            fn = sch.get("function", sch)
            print(json.dumps({"name": fn.get("name"), "description": fn.get("description"),
                              "parameters": fn.get("parameters")}, ensure_ascii=False))
        return
    for name, args in json.loads(sys.argv[3]):
        print(f">>> {name} {json.dumps(args, ensure_ascii=False)}")
        print(eng.call("agent", name, args))

if __name__ == "__main__":
    main()
