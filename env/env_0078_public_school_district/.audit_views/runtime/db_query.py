"""Coordinator-built runtime DB access path for KB auditors (env_0078).
usage: db_query.py <difficulty> <task_index> --list
       db_query.py <difficulty> <task_index> '[["<tool>", {args}], ...]'
Runs agent-side share READ tools, KB_search, grep and unlock_* against the task's opening DB at its
frozen_time and prints only the tool returns. Write tools are refused. Never prints initial_state."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario
S = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
d, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(S)
tasks = sc.tasks[d]
task = next((t for t in tasks if int(t.get("task_index", -1)) == idx), tasks[idx])
eng = sc.engine_for(task)
share = {s.name: s for s in sc.specs if s.kind == "share"}
BASE = {"KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool"}
if sys.argv[3] == "--list":
    for n, s in sorted(share.items()):
        if s.owner == "agent" and s.rw != "write":
            print(n)
    print("KB_search\ngrep\nunlock_agent_discoverable_tool\nunlock_user_discoverable_tool")
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in BASE or (name in share and share[name].owner == "agent" and share[name].rw != "write"):
        out = eng.call("agent", name, args)
    else:
        out = f"REFUSED: '{name}' is not a runtime-visible read tool for the agent"
    print(f"### {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")
