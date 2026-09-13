"""Independently verify the fictional support fixtures using Decimal accounting.

Run from repository root with .venv/bin/python and this file's path. This script
reads only this difficulty, its scenario blueprint and erlbench; replay stays in
fresh in-memory DBs. It never modifies benchmark artifacts or uses external I/O.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from importlib.util import spec_from_file_location, module_from_spec
import json
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from erlbench import ToolContext
from erlbench.db import DB
from erlbench.determinism import Clock

BLUEPRINT = HERE.parents[1] / 'blueprint'
SCHEMA = json.loads((BLUEPRINT / 'db_schema.json').read_text())
CHARTERS = {cat: yaml.safe_load((BLUEPRINT / 'products' / (cat + '.yaml')).read_text()) for cat in ['support', 'compute']}

def module(path, name):
    spec = spec_from_file_location(name, path)
    obj = module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

MODULES = [module(BLUEPRINT / 'share_tools.py', 'support_verify_share'), module(HERE / 'task_tools.py', 'support_verify_task')]
TOOLS = {name: value for mod in MODULES for name, value in vars(mod).items() if callable(value)}
D = lambda value: Decimal(str(value or 0))

def rounded(value, places=2):
    return float(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))

def source_context(task, tables):
    hid = task['computations'][0]['target_holding_id']
    holding = tables['support_holdings'][hid]
    rows = [r for r in tables['support_events'].values() if r.get('support_holding_id') == hid]
    reviews = [r for r in rows if r.get('event_type') == 'support_review']
    review = max(reviews, key=lambda r: r['occurred_at'])
    source, period = review['source_event_id'], review['period']
    cloud = next(r for r in tables['compute_holdings'].values() if r['customer_id'] == holding['customer_id'] and r['billing_entity'] == holding['billing_entity'] and r['status'] == 'active')
    def params(cat, obj):
        return next(v['parameters'] for v in CHARTERS[cat]['variants'] if v['name'] == obj['variant_name'])
    cp, sp = params('compute', cloud), params('support', holding)
    cloud_negotiated = cloud['negotiated_approval'] == 'approved'
    cloud_rate = D(cloud['negotiated_unit_rate'] if cloud_negotiated else cp['unit_rate'])
    if not cloud_negotiated and cloud['promotion_status'] == 'eligible':
        cloud_rate *= 1 - D(cp['promotion_discount'])
    support_negotiated = holding['negotiated_approval'] == 'approved'
    support_rate = D(holding['negotiated_unit_rate'] if support_negotiated else sp['unit_rate'])
    if not support_negotiated and holding['promotion_status'] == 'eligible':
        support_rate *= 1 - D(sp['promotion_discount'])
    return rows, review, source, period, cloud_rate, support_rate, D(sp['minimum_monthly_fee']), sp

def calculate(task, tables, policy):
    rows, review, source, period, cr, sr, floor, sp = source_context(task, tables)
    def total(field, **filters):
        return sum((D(r.get(field)) for r in rows if all(r.get(k) == v for k, v in filters.items())), Decimal(0))
    boundary = dict(source_event_id=source, period=period)
    missing = total('quantity', event_type='support_service_record', status='completed', source_subtype='primary', **boundary)
    baseline = total('quantity', event_type='support_service_record', status='completed', source_subtype='supplemental', **boundary)
    recognized = total('quantity', event_type='support_meter', status='posted', source_subtype='primary', **boundary)
    original = total('net_amount', event_type='support_charge', status='posted', support_event_id=source)
    prior = sum((total('net_amount', event_type=kind, status='posted', source_subtype='correction', **boundary) for kind in ['support_credit', 'support_debit_adjustment']), Decimal(0))
    if policy == 'support_ext_missing_spend':
        return rounded(max(Decimal(0), missing * cr), 6)
    if policy == 'support_ext_corrected_fee':
        return rounded(max(floor, (recognized + baseline * cr) * sr))
    if policy == 'support_ext_review_quantity':
        return rounded(max(Decimal(0), baseline + (recognized / cr if cr > 0 else 0)), 6)
    if policy == 'support_ext_invoice_debit':
        reviewed_hours = total('quantity', event_type='support_review', status='approved', decision='incorrect', **boundary)
        return rounded(max(Decimal(0), max(floor, reviewed_hours * cr * sr) - original - prior))
    corrected = D(rounded(max(floor, missing * cr * sr)))
    if policy == 'support_ext_paid_review':
        return float(corrected)
    if policy == 'support_ext_paid_credit':
        approved = any(r.get('event_type') == 'support_review' and r.get('status') == 'approved' and r.get('decision') == 'incorrect' and r.get('source_event_id') == source and r.get('period') == period for r in rows)
        return -rounded(max(Decimal(0), original + prior - corrected)) if approved else 0.0
    if policy in {'support_ext_retained_fee_authorization', 'support_ext_surplus_refund'}:
        kinds = {'support_charge', 'support_credit', 'support_debit_adjustment', 'support_payment', 'support_payment_return', 'support_refund'}
        receivable = sum((D(r.get('amount')) for r in rows if r.get('status') == 'posted' and r.get('event_type') in kinds), Decimal(0))
        payments = [r for r in rows if r.get('event_type') == 'support_payment' and r.get('status') == 'posted' and r.get('source_event_id') == source]
        payment = max(payments, key=lambda r: r['occurred_at'])
        principal = -D(payment['amount']) - total('amount', event_type='support_payment_return', status='posted', source_event_id=payment['support_event_id']) - total('amount', event_type='support_refund', status='posted', source_event_id=payment['support_event_id'])
        candidate = min(max(Decimal(0), -receivable - corrected), max(Decimal(0), principal))
        return rounded(candidate) if candidate >= D(sp['refund_minimum']) else 0.0
    raise ValueError(policy)

def replay(task, skip=(), check=True):
    db = DB.seeded(task['initial_state'])
    clock = Clock.from_stamp(task['frozen_time'])
    values = {}
    by_step = {}
    for comp in task['computations']:
        by_step.setdefault(comp['step'], []).append(comp)
    for index, action in enumerate(task['evaluation_criteria']):
        if index in skip:
            continue
        for comp in by_step.get(index, []):
            value = calculate(task, db.tables, comp['policy_id'])
            values[comp['policy_id']] = value
            if check:
                if comp['policy_id'] == 'support_ext_missing_spend':
                    rows, selected_review, source, period, *_ = source_context(task, db.tables)
                    locator = action['arguments']['arguments']['support_event_id']
                    assert locator == selected_review['related_event_id']
                    fragments = [r for r in rows if r.get('event_type') == 'support_service_record' and r.get('status') == 'completed' and r.get('source_subtype') == 'primary' and r.get('source_event_id') == source and r.get('period') == period]
                    assert sum(r['support_event_id'] == locator for r in fragments) == 1
                supplied = action['arguments']['arguments'][comp['arg']]
                assert value == comp['expected'] == supplied, (comp['policy_id'], value, comp['expected'], supplied)
        name, args = action['tool'], action['arguments']
        if name.startswith('unlock_'):
            continue
        if name.startswith('call_'):
            name, args = args['tool_name'], args['arguments']
        TOOLS[name](ToolContext(db, clock, SCHEMA), **args)
    return db, values

def main():
    for path in sorted((HERE / 'tasks').glob('*.json')):
        task = json.loads(path.read_text())
        final, values = replay(task)
        repeated, _ = replay(task)
        assert final.hash() == repeated.hash()
        print(path.name, 'independent Decimal values', values, 'deterministic hash', final.hash())
        for edge in task['prerequisite_closure']['edges']:
            skipped_steps = [c['step'] for c in task['computations'] if c['policy_id'] == edge['to']]
            alternative, altered = replay(task, skipped_steps, check=False)
            assert alternative.hash() != final.hash()
            if edge['kind'] == 'value_input':
                assert altered[edge['from']] != values[edge['from']]
            print('  omit', edge['to'], '=>', edge['from'], 'gold', values[edge['from']], 'alternative', altered[edge['from']], 'terminal differs')
    print('INDEPENDENT VERIFICATION OK')

if __name__ == '__main__':
    main()
