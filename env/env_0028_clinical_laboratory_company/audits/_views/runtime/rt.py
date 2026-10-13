"""Runtime-visible access path for the KB-side blind audit (coordinator-built).

Usage (from the repo root):
  .venv/bin/python env/env_0028_clinical_laboratory_company/audits/_views/runtime/rt.py context <difficulty> <task_index>
      -> agent system prompt (company + background + frozen_time), user_scenario,
         agent/user share-tool schemas and this difficulty's task-tool schemas.
  .venv/bin/python env/env_0028_clinical_laboratory_company/audits/_views/runtime/rt.py call <difficulty> <task_index> '<json list of calls>'
      -> runs the calls in order on ONE fresh engine seeded with that task's world and prints
         each result. Each call is {"owner": "agent"|"user", "tool": "<name>", "args": {...}}.
         Share tools are called directly; task tools are unlocked automatically and called
         through the runtime's discoverable-tool route, exactly as a rollout would.
         Nothing persists between invocations.
Only runtime-visible output is printed; no GT / evaluation field is ever emitted.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
from rollout.prompts import build_agent_prompt

ROOT = "env/env_0028_clinical_laboratory_company"

def _task(sc, d, i):
    return sc.tasks[d][int(i)]

def context(d, i):
    sc = load_scenario(ROOT); t = _task(sc, d, i); eng = sc.engine_for(t)
    company = (sc.blueprint or {}).get("company") or sc.name
    if isinstance(company, dict): company = company.get("name", sc.name)
    print("=== AGENT SYSTEM PROMPT ==="); print(build_agent_prompt(company, sc.blueprint.get("background"), t["frozen_time"]))
    print("\n=== frozen_time ==="); print(t["frozen_time"])
    print("\n=== user_scenario ==="); print(json.dumps(t["user_scenario"], indent=2, ensure_ascii=False))
    for owner in ("agent", "user"):
        print(f"\n=== {owner} base+share tool schemas ==="); print(json.dumps(eng.tool_list(owner), indent=1, ensure_ascii=False))
    print("\n=== task tool schemas of this difficulty (discoverable; unlock first) ===")
    for s in sc.specs:
        if s.kind != "share":
            print(json.dumps({"owner": s.owner, "rw": s.rw, **s.openai_schema()}, ensure_ascii=False))

def call(d, i, calls):
    sc = load_scenario(ROOT); t = _task(sc, d, i); eng = sc.engine_for(t)
    for c in json.loads(calls):
        owner, name, args = c.get("owner", "agent"), c["tool"], c.get("args", {})
        spec = eng.registry.get(name)
        if spec is not None and spec.kind != "share":
            if owner == "agent":
                eng.unlock_agent_discoverable_tool(name); out = eng.call_agent_discoverable_tool(name, json.dumps(args))
            else:
                eng.unlock_user_discoverable_tool(name); out = eng.call_user_discoverable_tool(name, json.dumps(args))
        else:
            out = eng.call(owner, name, args)
        print(f">>> {owner}:{name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "context": context(sys.argv[2], sys.argv[3])
    elif cmd == "call": call(sys.argv[2], sys.argv[3], sys.argv[4])
    else: sys.exit(__doc__)
