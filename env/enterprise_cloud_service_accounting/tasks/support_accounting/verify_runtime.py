"""Verify the fictional support bundle through unchanged Engine and scoring.

Only this difficulty and its scenario blueprint are loaded. All mutations are
inside fresh in-memory DB instances. No network or artifact writes occur.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_solution import MODULES, SCHEMA, replay as decimal_replay
from erlbench.db import DB
from erlbench.determinism import Clock
from erlbench.engine import Engine
from erlbench.kb import KnowledgeBase
from erlbench.tools import collect_specs
from erlbench.scoring import replay as scoring_replay

SPECS = collect_specs(MODULES[0], 'share') + collect_specs(MODULES[1], 'task')

def engine_for(task):
    return Engine(DB.seeded(task['initial_state']),
                  Clock.from_stamp(task['frozen_time']), KnowledgeBase([]),
                  SPECS, schema=SCHEMA)


def live_replay(task, skip=()):
    engine = engine_for(task)
    receipts = {}
    for index, action in enumerate(task['evaluation_criteria']):
        if index in skip:
            continue
        result = engine.call(action['owner'], action['tool'], action['arguments'])
        assert not result.startswith('Error:'), (index, result)
        receipts[index] = result
        if action['arguments'].get('tool_name') == 'review_support_overcharge_b721fa46' and action['tool'].startswith('call_'):
            rid = task['evaluation_criteria'][10]['arguments']['arguments']['request_id']
            review_id = action['arguments']['arguments']['support_event_id']
            assert rid in result
            assert engine.db.tables['support_events'][review_id]['request_id'] == rid
            assert rid not in engine.db.tables['support_events']
            assert not any(r.get('event_type') == 'support_request' for r in engine.db.tables['support_events'].values())
            print('  review receipt exposes reservation without a customer request:', result)
        if action['owner'] == 'user':
            rid = action['arguments']['arguments']['request_id']
            request = engine.db.tables['support_events'][rid]
            assert request['event_type'] == 'support_request'
            assert request['status'] == 'pending'
            assert request['amount'] == 6000.0
            assert request['source_event_id'] == action['arguments']['arguments']['source_event_id']
            assert rid in result
            print('  actual customer receipt:', result)
    return engine, receipts


def main():
    for path in sorted((HERE / 'tasks').glob('*.json')):
        task = json.loads(path.read_text())
        live, receipts = live_replay(task)
        gold_hash = scoring_replay(engine_for(task), task['evaluation_criteria'], strict=True)
        decimal_db, _ = decimal_replay(task)
        assert live.db.hash() == gold_hash == decimal_db.hash()
        print(path.name, 'Engine actions', len(receipts), 'strict scoring and Decimal replay match', gold_hash)
        if path.name == '1.json':
            user_action = task['evaluation_criteria'][10]
            probe = engine_for(task)
            original_hash = probe.db.hash()
            result = probe.call('user', user_action['tool'], user_action['arguments'])
            assert result.startswith('Error:') and probe.db.hash() == original_hash
            print('  frozen Engine handover enforcement:', result)
            for action in task['evaluation_criteria'][:10]:
                result = probe.call(action['owner'], action['tool'], action['arguments'])
                assert not result.startswith('Error:')
            before_wrong_owner = probe.db.hash()
            result = probe.call('agent', user_action['tool'], user_action['arguments'])
            assert result.startswith('Error:') and probe.db.hash() == before_wrong_owner
            print('  frozen Engine customer ownership enforcement:', result)
            omitted, omitted_receipts = live_replay(task, skip=(10,))
            rid = user_action['arguments']['arguments']['request_id']
            assert rid not in omitted.db.tables['support_events']
            assert omitted_receipts[12].startswith('Support refund posted:')
            assert omitted.db.hash() != gold_hash
            print('  omitted customer filing: final refund remains callable; consent request absent; terminal differs', omitted.db.hash())
            print('  final live refund receipt:', receipts[12])
    print('EXACT RUNTIME VERIFICATION OK')


if __name__ == '__main__':
    main()
