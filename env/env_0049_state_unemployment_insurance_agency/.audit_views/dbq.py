"""Runtime-shaped DB access for KB audits (env_0049). Never prints initial_state.
usage (repo root, .venv/bin/python -I /tmp/coord0049/dbq.py ...):
  dbq.py <difficulty> <task_idx> info                      -> frozen_time + runtime tool list names
  dbq.py <difficulty> <task_idx> tools <agent|user>        -> runtime tool schemas for that owner
  dbq.py <difficulty> <task_idx> call <agent|user> <tool> '<json args>' [--session FILE]
     Routes through erlbench Engine.call exactly as at runtime (share finders directly; task tools via
     unlock_agent_discoverable_tool / call_agent_discoverable_tool etc.). With --session, every prior call
     recorded in FILE is replayed first on a fresh engine, then this call is appended — so writes persist
     within a session. Without --session each call runs on the fresh opening world.
"""
import json, os, sys
ROOT = "/home/ubuntu/github/enterprise_rl"; sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario
S = f"{ROOT}/env/env_0049_state_unemployment_insurance_agency"
d, i, cmd = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sc = load_scenario(S)
task = [t for t in sc.tasks[d] if os.path.basename(str(t.get("_path", ""))) in (f"{i}.json",) or t.get("task_index") in (i, str(i))]
task = task[0] if task else sc.tasks[d][i]
eng = sc.engine_for(task)
if cmd == "info":
    print("frozen_time:", task["frozen_time"])
    for o in ("agent", "user"): print(o, [s["function"]["name"] if "function" in s else s.get("name") for s in eng.tool_list(o)])
elif cmd == "tools":
    print(json.dumps(eng.tool_list(sys.argv[4]), indent=1))
elif cmd == "call":
    owner, name, args = sys.argv[4], sys.argv[5], json.loads(sys.argv[6] if len(sys.argv) > 6 else "{}")
    sess = sys.argv[sys.argv.index("--session") + 1] if "--session" in sys.argv else None
    hist = [json.loads(l) for l in open(sess)] if sess and os.path.exists(sess) else []
    for h in hist: eng.call(h["owner"], h["name"], h["args"])
    print(eng.call(owner, name, args))
    if sess:
        with open(sess, "a") as f: f.write(json.dumps({"owner": owner, "name": name, "args": args}) + "\n")
