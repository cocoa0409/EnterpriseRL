"""Coordinator-built runtime DB access path for KB-layer auditors (read-only).
usage: db_query.py <difficulty> <task_index> --list
       db_query.py <difficulty> <task_index> '[["<tool>", {args}], ...]'
Runs share read finders, KB_search, grep and unlock_* against the task's opening DB at
its frozen_time and prints only the tool returns. Writes and call_* tools are refused."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..")))
from erlbench.loader import load_scenario

def main():
    d, i = sys.argv[1], int(sys.argv[2])
    sc = load_scenario(ROOT)
    p = os.path.join(ROOT, "tasks", d, "tasks", f"{i}.json")
    task = json.load(open(p))
    eng = sc.engine_for(task)
    share = {n: s for n, s in eng.registry.items() if s.kind == "share"}
    meta_ok = ("KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool")
    if sys.argv[3] == "--list":
        print("frozen_time:", task["frozen_time"])
        for n, s in sorted(share.items()):
            print(("READ  " if s.rw != "write" else "WRITE(refused) ") + n + "(" + ", ".join(s.parameters.get("properties", {})) + ")")
        print("META  " + ", ".join(meta_ok))
        return
    for name, args in json.loads(sys.argv[3]):
        if name in meta_ok:
            out = eng.call("agent", name, args)
        elif name in share and share[name].rw != "write":
            out = eng._run(share[name], args)
        else:
            out = f"REFUSED: {name} is not a runtime-visible read tool"
        print(f"### {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")

if __name__ == "__main__":
    main()
