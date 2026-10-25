"""Runtime-visible DB access for KB auditors (no raw initial_state).
usage: .venv/bin/python env/env_0071_nonstandard_auto_insurer/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
       .venv/bin/python .../db_query.py <difficulty> <task_idx> '<json list of [tool, {args}]>'
Calls run as the agent through Engine.call (share tools + KB_search/grep), in order, on one seeded engine."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario  # noqa: E402

def main():
    d, idx = sys.argv[1], int(sys.argv[2])
    sc = load_scenario(os.path.join(ROOT, "env", "env_0071_nonstandard_auto_insurer"))
    task = next(t for t in sc.tasks[d] if int(t.get("task_index", -1)) == idx) if any("task_index" in t for t in sc.tasks[d]) else sc.tasks[d][idx]
    eng = sc.engine_for(task)
    if sys.argv[3] == "--list":
        for s in eng.tool_list("agent"):
            f = s.get("function", s)
            print(f.get("name"), json.dumps(f.get("parameters", {}).get("properties", {}))[:300])
        return
    for name, args in json.loads(sys.argv[3]):
        print(f"### {name} {json.dumps(args)}")
        print(eng.call("agent", name, args))

if __name__ == "__main__":
    main()
