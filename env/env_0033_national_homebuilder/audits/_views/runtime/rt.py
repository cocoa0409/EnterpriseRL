"""Runtime-visible access path for the render-layer (KB) audit of env_0033_national_homebuilder.

Exposes ONLY what a rollout agent can see: the system prompt (company background + frozen_time),
the persona script that drives the user simulator, the runtime tool schemas, and DB records reached
through tool-shaped calls on a freshly seeded engine. It never prints initial_state or any GT field.

usage (from the repo root):
  .venv/bin/python env/env_0033_national_homebuilder/audits/_views/runtime/rt.py prompt <difficulty> <task>
  .venv/bin/python env/env_0033_national_homebuilder/audits/_views/runtime/rt.py persona <difficulty> <task>
  .venv/bin/python env/env_0033_national_homebuilder/audits/_views/runtime/rt.py tools
  .venv/bin/python env/env_0033_national_homebuilder/audits/_views/runtime/rt.py call <difficulty> <task> <owner> <tool> '<json args>'
  .venv/bin/python env/env_0033_national_homebuilder/audits/_views/runtime/rt.py session <difficulty> <task> <calls.jsonl>
      calls.jsonl: one {"owner": "agent"|"user", "tool": "...", "args": {...}} per line, run in order on ONE
      engine (writes persist within the session; nothing is ever written to disk). Hidden task tools are
      reached exactly as at runtime: unlock_agent_discoverable_tool / call_agent_discoverable_tool, and
      unlock_user_discoverable_tool (agent) + call_user_discoverable_tool (user).
"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario  # noqa: E402
from rollout.prompts import build_agent_prompt  # noqa: E402

SC = os.path.join(ROOT, "env/env_0033_national_homebuilder")

def _task(d, i):
    p = os.path.join(SC, "tasks", d, "tasks", f"{int(i)}.json")
    with open(p) as f:
        t = json.load(f)
    return {"frozen_time": t["frozen_time"], "user_scenario": t["user_scenario"], "initial_state": t["initial_state"]}

def _engine(d, i):
    sc = load_scenario(SC)
    return sc, sc.engine_for(_task(d, i))

def main(a):
    cmd = a[0]
    if cmd == "prompt":
        sc = load_scenario(SC); t = _task(a[1], a[2])
        print(build_agent_prompt(sc.blueprint.get("company") or sc.name, sc.blueprint.get("background"), t["frozen_time"]))
    elif cmd == "persona":
        t = _task(a[1], a[2]); print(json.dumps({"frozen_time": t["frozen_time"], "user_scenario": t["user_scenario"]}, indent=2, ensure_ascii=False))
    elif cmd == "tools":
        sc = load_scenario(SC); e = sc.engine_for({"frozen_time": "2026-01-01T00:00:00", "initial_state": {}})
        print(json.dumps({"agent": e.tool_list("agent"), "user": e.tool_list("user")}, indent=1))
    elif cmd == "call":
        _, e = _engine(a[1], a[2]); print(e.call(a[3], a[4], json.loads(a[5]) if len(a) > 5 else {}))
    elif cmd == "session":
        _, e = _engine(a[1], a[2])
        for n, line in enumerate(open(a[3])):
            if not line.strip(): continue
            c = json.loads(line)
            print(f"--- [{n}] {c['owner']}.{c['tool']} {json.dumps(c.get('args', {}))}")
            print(e.call(c["owner"], c["tool"], c.get("args", {})))
    else:
        print(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:] or ["help"])
