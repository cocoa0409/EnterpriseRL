"""Local, in-memory regression checks for policy-audit findings F1, F2 and F3.

These probes evaluate calculation selection. They never require a task tool to reject
an ineligible state, and never change either published initial_state.
"""
import ast
import importlib.util
import json
import uuid
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

D = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('network_verification', D / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def snapshot(task_number, before_write):
    task = json.loads((D / f'tasks/{task_number}.json').read_text())
    gold, _ = v.run(task_number)
    db = v.DB.seeded(deepcopy(task['initial_state']))
    ctx = v.ToolContext(db, v.Clock.from_stamp(task['frozen_time']), v.schema, writable=True)
    for entry in gold[:before_write]:
        policy = next(p for p in v.ex['extended_policies'] if p['id'] == entry['policy_id'])
        getattr(v.mod, policy['target_tool'])(ctx, **entry['arguments'])
    holding = task['computations'][0]['target_holding_id']
    return task, db.tables, holding


def compute(task, world, holding, policy_id):
    policy = next(p for p in v.ex['extended_policies'] if p['id'] == policy_id)
    env, _ = v.build_env(world, task['frozen_time'], v.ex, v.cross, v.schema, holding)
    return v.eval_compute(policy['compute'], env, policy['params'])[0]


def older_unrelated_review(task_number, world, holding):
    rows = world['network_events']
    current = next(r for r in rows.values() if r['event_type'] == 'network_review')
    old_charge = next(r for r in rows.values()
                      if r['event_type'] == 'network_charge' and r['period'] != '2026-08')
    old = deepcopy(current)
    rid = str(uuid.uuid4())
    old.update(network_event_id=rid, source_event_id=old_charge['network_event_id'],
               related_event_id=old_charge['source_event_id'], request_id='',
               occurred_at=old_charge['period'] + '-28T23:00:00Z', period=old_charge['period'],
               status='approved', decision='incorrect' if task_number == 0 else 'correct',
               cause='rate_error' if task_number == 0 else 'none', net_amount=100.0,
               amount=0.0, tax_amount=0.0, external_reference='AUDIT-OLDER-UNRELATED-REVIEW')
    rows[rid] = old
    # Keep the countermodel's unrelated old source arithmetically credible and settled.
    # These are isolated alternate-history records, never edits to a task's initial_state.
    old_meter = rows[old_charge['source_event_id']]
    if task_number == 0:
        old_meter['quantity'] = 11492.537313  # (quantity - 10000) * .067 rounds to 100.00.
        adjustment_id, payment_id = str(uuid.uuid4()), str(uuid.uuid4())
        adjustment = deepcopy(old_charge)
        adjustment.update(network_event_id=adjustment_id, event_type='network_debit_adjustment',
                          source_event_id=old_charge['network_event_id'], related_event_id=rid,
                          source_subtype='correction', net_amount=33.0, tax_amount=0.0,
                          amount=33.0, occurred_at=old_charge['period']+'-28T23:01:00Z')
        payment = deepcopy(old_charge)
        payment.update(network_event_id=payment_id, event_type='network_payment',
                       source_event_id=old_charge['network_event_id'], related_event_id='',
                       source_subtype='remittance', method='ach', net_amount=-33.0,
                       tax_amount=0.0, amount=-33.0,
                       occurred_at=old_charge['period']+'-28T23:02:00Z')
        rows[adjustment_id], rows[payment_id] = adjustment, payment
    else:
        old_meter['quantity'] = 6408.450704  # (quantity - 5000) * .071 rounds to 100.00.
        old_charge.update(quantity=1408.450704, net_amount=100.0, tax_amount=8.25, amount=108.25)
        old['tax_amount'] = 8.25
        old_payment = next(r for r in rows.values() if r['event_type'] == 'network_payment'
                           and r['source_event_id'] == old_charge['network_event_id'])
        old_payment.update(net_amount=-100.0, tax_amount=-8.25, amount=-108.25)
    return rid


def has_filter(policy_id, binding_name, primitive, field, value):
    policy = next(p for p in v.ex['extended_policies'] if p['id'] == policy_id)
    expression = next(b[binding_name] for b in policy['compute'] if binding_name in b)
    for node in ast.walk(ast.parse(expression, mode='eval')):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == primitive:
            for kw in node.keywords:
                if kw.arg == field:
                    actual = kw.value.value if isinstance(kw.value, ast.Constant) else kw.value.id if isinstance(kw.value, ast.Name) else None
                    if actual == value:
                        return True
    return False


def main():
    findings = {}
    t0, w0, h0 = snapshot(0, 0)
    review = next(r for r in w0['network_events'].values()
                  if r['event_type'] == 'network_review' and r['cause'] == 'rate_error')
    source = w0['network_events'][review['source_event_id']]
    monthly = sum(Decimal(str(r['quantity'])) for r in w0['network_events'].values()
                  if r['network_holding_id'] == h0 and r['event_type'] == 'network_meter'
                  and r['status'] == 'posted' and r['meter_code'] == 'internet_egress'
                  and r['source_subtype'] == 'primary' and r['period'] == source['period'])
    assert monthly == Decimal(str(source['quantity'])) == Decimal('20000')
    assessed = compute(t0, w0, h0, 'network_ext_assess')
    assert assessed == 643.2
    ep = next(p for p in v.ex['extended_policies'] if p['id'] == 'network_ext_assess')
    expected_overrides = [
        ('network_evt_pricing', 'Allocate included_quantity across primary meter sources of the same holding and period in interval_start then source_event_id order; prorate it by actual active UTC seconds divided by actual seconds in that UTC calendar month.'),
        ('network_evt_pricing', 'Only the positive quantity beyond the remaining included allowance is charged.'),
        ('network_evt_category_meters', 'An allowance is consumed chronologically by interval_start then source_event_id within the named holding and UTC period; reversal of its source returns only that source allocation.'),
    ]
    declared = {(o['base_policy'], o['superseded_clause']) for o in ep['overwrite']}
    assert set(expected_overrides) <= declared
    findings['F1'] = {'monthly_quantity': str(monthly), 'corrected_target': assessed,
                      'retired_source_allocation_clauses': len(expected_overrides),
                      'result': 'The sole aggregate charge has the expressly declared monthly target; first-export-only target zero is outside the replacement basis.'}

    t0, w0, h0 = snapshot(0, 1)
    before = compute(t0, w0, h0, 'network_ext_credit')
    older_unrelated_review(0, w0, h0)
    after = compute(t0, w0, h0, 'network_ext_credit')
    assert before == after == -16.8
    findings['F2_credit_countermodel'] = {'older_unrelated_review_net': 100.0,
                                         'before': before, 'after': after,
                                         'legacy_unfiltered_result': 0.0}

    t1, w1, h1 = snapshot(1, 2)
    before = compute(t1, w1, h1, 'network_ext_invoice')
    older_unrelated_review(1, w1, h1)
    after = compute(t1, w1, h1, 'network_ext_invoice')
    assert before == after == 2055.45
    findings['F2_invoice_countermodel'] = {'older_unrelated_review_net': 100.0,
                                          'before': before, 'after': after,
                                          'legacy_unfiltered_result': 2155.45}
    t1, w1, h1 = snapshot(1, 3)
    older_unrelated_review(1, w1, h1)
    tax = compute(t1, w1, h1, 'network_ext_tax')
    assert tax == 169.57
    findings['F2_tax_countermodel'] = {'actual_tax': tax, 'legacy_contaminated_invoice_tax': 177.82}

    checks = [
        ('network_ext_assess', 'source_period', 'LATEST', 'network_event_id', 'source_charge'),
        ('network_ext_credit', 'original', 'SUM', 'status', 'posted'),
        ('network_ext_credit', 'target', 'SUM', 'network_event_id', 'selected_review'),
        ('network_ext_credit', 'target', 'SUM', 'source_event_id', 'source_charge'),
        ('network_ext_invoice', 'assessed', 'SUM', 'network_event_id', 'selected_review'),
        ('network_ext_invoice', 'assessed', 'SUM', 'source_event_id', 'source_bundle'),
        ('network_ext_tax', 'issued', 'SUM', 'meter_code', 'internet_egress'),
        ('network_ext_tax', 'issued', 'SUM', 'period', 'source_period'),
    ]
    for check in checks:
        assert has_filter(*check), check
    findings['F2_additional_selector_gaps'] = {'checked_predicates': len(checks), 'result': 'All reported source, status, meter and period selectors are explicit.'}
    # F3: the actual below-threshold source must have explicit, scoped price authority.
    expected_price_overrides = {
        ('network_agg_usage', 'Use msr_portfolio_usage to select the portfolio discount.'),
        ('network_agg_usage', 'The threshold comparison is inclusive.'),
        ('network_agg_usage', 'Portfolio discount applies only to primary service usage and only if no higher-priority price applies; it is neither a cash credit nor a deduction from ancillary service fees.'),
        ('network_evt_pricing', 'For every quantity component choose the first applicable item in discount_priority: an approved negotiated rate when negotiated_rate_allowed, then the committed fraction, then a recorded eligible promotion from promotion_channels, then portfolio eligibility, then standard.'),
    }
    for policy_id in ['network_ext_price', 'network_ext_invoice']:
        policy = next(p for p in v.ex['extended_policies'] if p['id'] == policy_id)
        declarations = {(o['base_policy'], o['superseded_clause']): o['replaced_by']
                        for o in policy['overwrite']}
        assert expected_price_overrides <= declarations.keys()
        for clause in expected_price_overrides:
            replacement = declarations[clause]
            assert replacement in policy['rule']
            assert 'independently of msr_portfolio_usage and portfolio_threshold' in replacement
        assert 'ordinary portfolio aggregation, eligibility and price priority remain unchanged outside that route' in policy['rule']
    t1, w1, h1 = snapshot(1, 1)
    holding = w1['network_holdings'][h1]
    tier = next(t for t in v.ex['variants'] if t['name'] == holding['variant_name'])['parameters']
    quantity = sum(Decimal(str(r['quantity'])) for r in w1['network_events'].values()
                   if r['network_holding_id'] == h1 and r['event_type'] == 'network_meter'
                   and r['status'] == 'posted' and r['source_subtype'] == 'primary'
                   and r['period'] == '2026-08')
    usage = quantity * Decimal(str(tier['unit_rate']))
    threshold = Decimal(str(tier['portfolio_threshold']))
    assert usage == Decimal('2485') < threshold == Decimal('25000')
    standard_net = (quantity - Decimal(str(tier['included_transfer_gb']))) * Decimal(str(tier['unit_rate']))
    standard_tax = (standard_net * Decimal('0.0825')).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    price = compute(t1, w1, h1, 'network_ext_price')
    t1, w1, h1 = snapshot(1, 2)
    invoice = compute(t1, w1, h1, 'network_ext_invoice')
    t1, w1, h1 = snapshot(1, 3)
    tax = compute(t1, w1, h1, 'network_ext_tax')
    assert price == invoice == 2055.45 and tax == 169.57
    findings['F3'] = {
        'standard_portfolio_usage': str(usage), 'portfolio_threshold': str(threshold),
        'ordinary_net_excluded_by_explicit_overrides': str(standard_net),
        'ordinary_tax_excluded_by_explicit_overrides': str(standard_tax),
        'price': price, 'invoice': invoice, 'tax': tax,
        'scoped_override_clauses_per_policy': len(expected_price_overrides),
        'result': 'Both assessment and invoice have exact threshold/priority replacements; source and amount uniqueness do not depend on misstating monetary usage as GB.'}
    workflow = v.ex['workflows'][0]
    assert workflow['requires_external_wait'] is False and workflow['zero_wait_proof']
    assert all(s['requires_external_wait'] is False and s['zero_wait_proof'] for s in workflow['steps'])
    findings['O1'] = {'workflow_zero_wait': True, 'step_zero_wait_proofs': len(workflow['steps'])}
    report = {'result': 'AUDIT REGRESSIONS OK', 'findings': findings}
    (D / 'audit_regressions_round_4.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
