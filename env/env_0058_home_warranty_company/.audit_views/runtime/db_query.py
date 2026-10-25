"""Tool-shaped, read-only access to one task's runtime world for KB audits.

usage (from the repository root):
  .venv/bin/python env/env_0058_home_warranty_company/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0058_home_warranty_company/.audit_views/runtime/db_query.py <difficulty> <idx> '[["find_customer_by_phone", {"phone_number": "..."}], ["KB_search", {"query": "..."}]]'

Seeds the task's initial_state at its frozen_time exactly as the runtime does
(erlbench.loader.load_scenario + Scenario.engine_for) and prints ONLY the
returns of the requested calls. Allowed: every share tool (read or write; writes
land in this throw-away in-memory DB only) and the agent meta tools KB_search /
grep. Hidden task tools, unlocks and every GT field are not reachable here.
"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario  # noqa: E402

SCEN = os.path.join(ROOT, "env", "env_0058_home_warranty_company")


def main():
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(2)
    diff, idx, req = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sc = load_scenario(SCEN)
    task = next(t for t in sc.tasks[diff] if int(t.get("task_index", -1)) == idx) \
        if any("task_index" in t for t in sc.tasks[diff]) else sc.tasks[diff][idx]
    eng = sc.engine_for(task)
    shares = {s.name: s for s in sc.specs if s.kind == "share"}
    if req == "--list":
        for s in shares.values():
            print(json.dumps({"name": s.name, "owner": s.owner, "rw": s.rw,
                              "description": s.description, "parameters": s.parameters}))
        print(json.dumps({"name": "KB_search", "parameters": {"query": "string"}}))
        print(json.dumps({"name": "grep", "parameters": {"pattern": "string"}}))
        return
    for name, args in json.loads(req):
        if name in ("KB_search", "grep"):
            out = eng.call("agent", name, args)
        elif name in shares:
            out = eng._run(shares[name], args)
        else:
            out = f"Error: '{name}' is not available through this access path."
        print(f"### {name} {json.dumps(args)}\n{out}\n")


if __name__ == "__main__":
    main()
