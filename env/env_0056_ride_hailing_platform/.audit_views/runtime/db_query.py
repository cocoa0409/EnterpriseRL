"""Runtime DB access path for KB audits (coordinator-built).

usage (from repo root):
  .venv/bin/python env/env_0056_ride_hailing_platform/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0056_ride_hailing_platform/.audit_views/runtime/db_query.py <difficulty> <idx> '[["find_customers", {"phone_number": "..."}], ["KB_search", {"query": "..."}]]'

Seeds the task's world exactly as a rollout does (load_scenario + engine_for) and prints only
what the runtime returns. Allowed: share READ tools (agent-owned) and KB_search / grep.
Never prints initial_state or any other task field.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0056_ride_hailing_platform"


def main():
    diff, idx, q = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sc = load_scenario(ROOT)
    task = sc.tasks[diff][idx]
    eng = sc.engine_for(task)
    reads = {n: s for n, s in eng.registry.items() if s.kind == "share" and s.owner == "agent" and s.rw == "read"}
    if q == "--list":
        print("now:", task["frozen_time"])
        for n, s in sorted(reads.items()):
            print(f"- {n}({', '.join(s.parameters.get('properties', {}))})")
        print("- KB_search(query)  - grep(pattern)  [see erlbench/engine.py for exact signatures]")
        writes = sorted(n for n, s in eng.registry.items() if s.kind == "share" and s.rw == "write")
        print("share WRITE tools also visible to a rollout (listed only, not callable here):", ", ".join(writes))
        return
    for name, args in json.loads(q):
        if name in ("KB_search", "grep"):
            out = eng.call("agent", name, args)
        elif name in reads:
            out = eng._run(reads[name], args)
        else:
            out = f"refused: {name} is not a share read tool or KB tool"
        print(f"### {name} {json.dumps(args)}\n{out}\n")


if __name__ == "__main__":
    main()
