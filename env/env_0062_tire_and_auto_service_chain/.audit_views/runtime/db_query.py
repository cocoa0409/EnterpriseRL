"""Coordinator-built runtime access path for KB audits (env_0062).
usage (from repo root):
  .venv/bin/python env/env_0062_tire_and_auto_service_chain/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0062_tire_and_auto_service_chain/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, {args}]>'
Each invocation seeds a fresh engine for that task (DB at frozen_time, published KB, all tools) and prints
only the tool returns. Allowed: every share tool (by name) and the agent base tools KB_search, grep,
unlock_agent_discoverable_tool, unlock_user_discoverable_tool (which show a task tool's schema). Task tools
cannot be called. Calls in one list run in order against the same engine.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d, idx = sys.argv[1], sys.argv[2]
sc = load_scenario(S)
task = json.load(open(os.path.join(S, "tasks", d, "tasks", f"{idx}.json")))
eng = sc.engine_for(task)
BASE = {"KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool"}
if sys.argv[3] == "--list":
    print("base:", sorted(BASE))
    for s in sorted(eng.registry.values(), key=lambda s: s.name):
        if s.kind == "share":
            print(f"share: {s.name}({', '.join(s.parameters.get('properties', {}))}) owner={s.owner} rw={s.rw}")
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in BASE:
        out = eng.call("agent", name, args)
    else:
        spec = eng.registry.get(name)
        out = eng._run(spec, args) if spec is not None and spec.kind == "share" else f"Error: '{name}' is not available on this path."
    print(f"### {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n")
