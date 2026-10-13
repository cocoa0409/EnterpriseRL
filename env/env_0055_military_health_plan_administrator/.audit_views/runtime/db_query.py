"""Tool-shaped DB access for the KB runtime blind audit (coordinator-supplied).

usage (from repo root):
  .venv/bin/python env/env_0055_military_health_plan_administrator/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0055_military_health_plan_administrator/.audit_views/runtime/db_query.py <difficulty> <idx> '<json list of [tool, {args}]>'

Each invocation seeds a fresh copy of that task's world at its frozen_time and runs the
calls in order (so writes made earlier in the list are visible to later calls).
Share tools and task tools run through the engine; KB_search / grep run as the agent.
Only tool returns are printed — never the raw seed.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario

ROOT = 'env/env_0055_military_health_plan_administrator'
diff, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = sc.tasks[diff][idx]
eng = sc.engine_for(task)
if sys.argv[3] == '--list':
    for s in sorted(eng.registry.values(), key=lambda s: (s.kind, s.name)):
        if s.kind == 'share':
            print(json.dumps({'name': s.name, 'owner': s.owner, 'rw': s.rw, 'schema': s.openai_schema()}, ensure_ascii=False))
    print('# base tools: KB_search, grep (agent); task tools are discovered through the KB and may be called here by name')
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in ('KB_search', 'grep'):
        out = eng.call('agent', name, args)
    else:
        spec = eng.registry.get(name)
        out = f"Error: unknown tool '{name}'." if spec is None else eng._run(spec, args)
    print(f'>>> {name} {json.dumps(args, ensure_ascii=False)}\n{out}\n')
