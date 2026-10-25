"""Runtime-visible DB access path for KB audits (coordinator-built).

usage (from the repo root):
  .venv/bin/python env/env_0063_diabetes_and_medical_supply_company/.audit_views/runtime/db_query.py <difficulty> <task_idx> --list
  .venv/bin/python env/env_0063_diabetes_and_medical_supply_company/.audit_views/runtime/db_query.py <difficulty> <task_idx> '<json list of [tool, args]>'

Calls run in order on one fresh engine seeded with that task's world at its frozen_time.
Allowed: agent-owned share READ tools (e.g. find_* lookups, verify_customer_identity is a
write and is refused), KB_search and grep. Only tool returns are printed; the raw
initial_state is never printed.
"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario

def main():
    diff, idx = sys.argv[1], int(sys.argv[2])
    sc = load_scenario(os.path.join(ROOT, 'env', 'env_0063_diabetes_and_medical_supply_company'))
    task = sc.tasks[diff][idx]
    eng = sc.engine_for(task)
    share = {n: s for n, s in eng.registry.items() if s.kind == 'share' and s.owner == 'agent' and s.rw != 'write'}
    if sys.argv[3] == '--list':
        print('frozen_time:', task['frozen_time'])
        for n, s in sorted(share.items()):
            print(n, json.dumps(s.parameters.get('properties', {}))[:400])
        print('KB_search {"query": str}'); print('grep {"pattern": str}')
        return
    for name, args in json.loads(sys.argv[3]):
        print(f'>>> {name} {json.dumps(args)}')
        if name in ('KB_search', 'grep'):
            print(eng.call('agent', name, args))
        elif name in share:
            print(eng._run(share[name], args))
        else:
            print(f'refused: {name} is not an agent-owned share read tool / KB_search / grep')

if __name__ == '__main__':
    main()
