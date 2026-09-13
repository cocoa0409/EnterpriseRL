"""Check the real Engine's customer filing and reference provenance in memory.

This is runtime evidence, not a KB discovery test: publication remains pending.
No documents, persona hints, runtime behavior or permission state are fabricated.
"""
import ast
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

D = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('network_verification', D / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
from erlbench.engine import Engine
from erlbench.kb import KnowledgeBase
from erlbench.scoring import replay
from erlbench.tools import collect_specs

shared_spec = importlib.util.spec_from_file_location('network_shared', v.B / 'share_tools.py')
shared = importlib.util.module_from_spec(shared_spec)
shared_spec.loader.exec_module(shared)
specs = collect_specs(shared, 'share') + collect_specs(v.mod, 'task')


def main():
    task = json.loads((D / 'tasks/1.json').read_text())
    form_id = task['evaluation_criteria'][6]['arguments']['arguments']['request_id']
    opening = task['initial_state']['network_events'][form_id]
    assert opening['event_type'] == 'network_service_record'
    assert opening['net_amount'] == 0 and opening['notice_at'] == ''
    assert form_id not in json.dumps(task['user_scenario'])
    user_spec = next(s for s in specs if s.name == 'authorize_network_11d4a76e')
    assert user_spec.owner == 'user' and user_spec.rw == 'write'

    def fresh():
        return Engine(v.DB.seeded(deepcopy(task['initial_state'])),
                      v.Clock.from_stamp(task['frozen_time']), KnowledgeBase([]),
                      specs, schema=v.schema)

    engine = fresh()
    transcript = []
    observed_id = False
    holding = task['computations'][0]['target_holding_id']
    pricing = next(p for p in v.ex['extended_policies'] if p['id'] == 'network_ext_price')

    def price_value():
        env, _ = v.build_env(engine.db.tables, task['frozen_time'], v.ex,
                             v.cross, v.schema, holding)
        return v.eval_compute(pricing['compute'], env, pricing['params'])[0]

    assert price_value() == 0
    for step, action in enumerate(task['evaluation_criteria']):
        if step == 6:
            assert observed_id
            assert price_value() == 0
            assert engine.db.tables['network_events'][form_id]['event_type'] == 'network_service_record'
        result = engine.call(action['owner'], action['tool'], action['arguments'])
        assert not result.startswith('Error:'), (step, result)
        transcript.append({'step': step, 'owner': action['owner'], 'tool': action['tool'],
                           'arguments': action['arguments'], 'return': result})
        if step == 3:
            observed_id = form_id in result
            assert observed_id
        if step == 6:
            receipt = ast.literal_eval(result)
            assert receipt['event_id'] == form_id and receipt['net_amount'] == 2225.85
            filed = engine.db.tables['network_events'][form_id]
            assert filed['event_type'] == 'network_request' and filed['status'] == 'pending'
            assert filed['net_amount'] == 2225.85 and filed['notice_at']
            assert price_value() == 2055.45

    target_hash = replay(fresh(), task['evaluation_criteria'], strict=True)
    assert engine.db.hash() == target_hash
    _, _ = v.run(1)
    omitted, _ = v.run(1, 0)
    assert omitted[1]['value'] == 0
    report = {
        'result': 'LIVE PROVENANCE OK',
        'publication_scope': 'KB empty by design: this verifies Engine execution and references, not tool-name discovery.',
        'form_id': form_id, 'id_visible_in_prior_agent_query': observed_id,
        'real_user_receipt_visible': True, 'opening_price': 0,
        'post_user_price': 2055.45, 'omit_user_price': omitted[1]['value'],
        'live_hash': engine.db.hash(), 'strict_scoring_hash': target_hash,
        'transcript': transcript,
    }
    (D / 'live_provenance_round_4.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: val for k, val in report.items() if k != 'transcript'}, indent=2))


if __name__ == '__main__':
    main()
