"""Runtime-visible DB access path for the KB audit (tool-shaped queries only).

usage (from repo root):
  .venv/bin/python env/env_0054_ecommerce_marketplace_operator/.audit_views/runtime/db_query.py <difficulty> <idx> --list
  .venv/bin/python env/env_0054_ecommerce_marketplace_operator/.audit_views/runtime/db_query.py <difficulty> <idx> '[["<share tool>", {...}], ["KB_search", {...}], ...]'
Runs share read tools (and the agent's KB tools) against that task's world at its frozen_time and
prints only the tool returns. Never prints initial_state or any task field.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from erlbench.loader import load_scenario
from erlbench.engine import AGENT_BASE, BASE_SCHEMAS

ROOT = 'env/env_0054_ecommerce_marketplace_operator'
diff, idx = sys.argv[1], int(sys.argv[2])
sc = load_scenario(ROOT)
task = json.load(open(f'{ROOT}/tasks/{diff}/tasks/{idx}.json'))
eng = sc.engine_for(task)
shares = {s.name: s for s in sc.specs if s.kind == 'share' and s.rw == 'read'}
if sys.argv[3] == '--list':
    for s in shares.values():
        print(json.dumps(s.openai_schema()))
    for n in AGENT_BASE:
        if n.lower().startswith(('kb', 'grep')):
            print(json.dumps(BASE_SCHEMAS[n]))
    sys.exit(0)
for name, args in json.loads(sys.argv[3]):
    if name in shares:
        out = eng._run(shares[name], args)
    elif name in BASE_SCHEMAS and name.lower().startswith(('kb', 'grep')):
        out = eng.call('agent', name, args)
    else:
        out = f'Error: {name} is not a share read tool or KB tool'
    print(f'### {name} {json.dumps(args)}\n{out}\n')
