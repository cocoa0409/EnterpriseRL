"""Runtime-visible DB/KB access for KB-doc audits (coordinator-built).

Usage (from the repository root):
  .venv/bin/python env/env_0051_self_storage_operator/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0051_self_storage_operator/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, args]>'

Each invocation seeds a fresh engine for the task at its frozen_time, exactly as a
rollout would, and runs the given calls in order as the agent. Only read-only share
tools and the KB tools (KB_search, grep) are allowed. Only tool returns are printed;
nothing else of the task file is ever shown.
"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..")))
from erlbench.loader import load_scenario  # noqa: E402

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    diff, idx, spec = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sc = load_scenario(ROOT)
    task = next(t for t in sc.tasks.get(diff, []) if t["task_index"] == idx)
    eng = sc.engine_for(task)
    reads = {n: s for n, s in eng.registry.items() if s.kind == "share" and s.owner == "agent" and s.rw == "read"}
    if spec == "--list":
        for n in ("KB_search", "grep"):
            print(json.dumps({"name": n, "doc": getattr(eng, n).__doc__.strip()}))
        for n, s in sorted(reads.items()):
            print(json.dumps(s.openai_schema()))
        return
    for name, args in json.loads(spec):
        print(f"### {name} {json.dumps(args, ensure_ascii=False)}")
        if name in ("KB_search", "grep"):
            print(eng.call("agent", name, args))
        elif name in reads:
            print(eng._run(reads[name], args))
        else:
            print(f"Error: '{name}' is not an allowed read-only share tool here.")

if __name__ == "__main__":
    main()
