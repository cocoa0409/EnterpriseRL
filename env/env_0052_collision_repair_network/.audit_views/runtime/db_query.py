"""Runtime-visible DB access path for KB audits (coordinator-built).

usage (from the repository root):
  .venv/bin/python env/env_0052_collision_repair_network/.audit_views/runtime/db_query.py <difficulty> <task_index> --list
  .venv/bin/python env/env_0052_collision_repair_network/.audit_views/runtime/db_query.py <difficulty> <task_index> '<json list of [tool, {args}]>'

Loads the scenario, seeds the task's DB at its frozen_time and runs only what a
rollout agent could run without writing: the scenario's READ tools (shared finders and any read-type task tool) and the
KB tools KB_search / grep. Prints only the tool returns — never initial_state.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = "env/env_0052_collision_repair_network"


def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    diff, idx, q = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sc = load_scenario(ROOT)
    task = next(t for t in sc.tasks[diff] if int(t.get("task_index", -1)) == idx)
    eng = sc.engine_for(task)
    share = {s.name: s for s in sc.specs if s.rw == "read"}
    if q == "--list":
        print("frozen_time:", task.get("frozen_time"))
        print("KB tools: KB_search, grep")
        for n, s in sorted(share.items()):
            print(f"- {n}: {(s.description or '').strip().splitlines()[0] if getattr(s, 'description', None) else ''}")
        return
    for tool, args in json.loads(q):
        if tool in ("KB_search", "grep"):
            out = eng.call("agent", tool, args or {})
        elif tool in share:
            out = eng._run(share[tool], args or {})
        else:
            out = f"Error: '{tool}' is not a shared read tool or KB tool"
        print(f"### {tool} {json.dumps(args, ensure_ascii=False)}\n{out}\n")


if __name__ == "__main__":
    main()
