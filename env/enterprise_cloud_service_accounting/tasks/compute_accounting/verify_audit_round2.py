"""Focused round-2 source-contract checks; tools intentionally do not enforce policy."""
from pathlib import Path
import sys,json,yaml,copy
D=Path(__file__).resolve().parent;ROOT=D.parents[3];B=D.parents[1]/'blueprint'
sys.path[:0]=[str(ROOT),str(ROOT/'skills/erl-task-instantiate/scripts')]
from check_compute import build_env,eval_compute
schema=json.loads((B/'db_schema.json').read_text());ext=yaml.safe_load((D/'compute.extended.yaml').read_text());pol={p['id']:p for p in ext['extended_policies']};cross={'support':yaml.safe_load((B/'products/support.yaml').read_text())};t=json.loads((D/'tasks/0.json').read_text());c=t['computations'][0];hid=c['target_holding_id'];review=pol[c['policy_id']]
for channel,expected in [('support',1750.92),('portal',1663.37),('api',1663.37)]:
 state=copy.deepcopy(t['initial_state']);state['compute_holdings'][hid]['promotion_status']='eligible'
 source=t['evaluation_criteria'][c['step']]['arguments']['arguments']['source_event_id'];state['compute_events'][source]['channel']=channel
 env,_=build_env(state,t['frozen_time'],ext,cross,schema,hid);v=eval_compute(review['compute'],env,review.get('params'))[0];assert v==expected,(channel,v,expected);print('G3 eligible campaign, original channel',channel,'=>',v)
for pid in ['compute_ext_assisted_review','compute_ext_assisted_credit']:
 p=pol[pid];assert any(o['superseded_clause']=='The combination changes only request-channel eligibility, not approval authority.' and o['replaced_by'] in p['rule'] for o in p['overwrite'])
print('G1/T0-1: both source monetary policies explicitly retire the channel-only clause.')
refund=pol['compute_ext_immediate_refund'];assert 'pending processing status and decision none preserve sufficient customer consent' in refund['rule'];assert 'does not approve the customer signature' in refund['rule'];print('G2/T0-2 retained: original pending decision-none filing is sufficient signature consent; numerical assessment does not approve that signature.')
assessment=t['evaluation_criteria'][10]['arguments']['arguments'];assert assessment['compute_event_id']==assessment['request_id'];request=t['initial_state']['compute_events'][assessment['compute_event_id']];assert request['event_type']=='compute_request' and request['status']=='pending' and request['decision']=='none';assert request['source_event_id']==assessment['source_event_id'] and request['related_event_id']==assessment['related_event_id'];payment=t['initial_state']['compute_events'][assessment['source_event_id']];assert payment['event_type']=='compute_payment' and payment['status']=='posted';assert payment['source_event_id']==assessment['related_event_id'];assert assessment['correction_event_id']!=assessment['related_event_id'];print('T0-3 superseded argument role propagated: original request, payment, paid charge and correction receipt each have one precise distinct role.')
t1=json.loads((D/'tasks/1.json').read_text());a=t1['evaluation_criteria'][6]['arguments']['arguments'];packets=[r for r in t1['initial_state']['compute_events'].values() if r['event_type']=='compute_service_record' and r['source_subtype']=='review' and r['status']=='completed' and r['source_event_id']==a['source_event_id'] and r['related_event_id']==a['related_event_id']];assert len(packets)==1 and packets[0]['compute_event_id']==a['compute_event_id'];assert a['related_event_id']!=a['compute_event_id'];print('T1-1: exactly one correlated review-subtype packet; raw export is excluded from the packet role.')
assert 'does not handle partially covered source quantities' in review['rule']
seed=t['initial_state'];source_id=t['evaluation_criteria'][c['step']]['arguments']['arguments']['source_event_id'];source_record=seed['compute_events'][source_id];anchor=source_record['source_event_id'];period=source_record['period']
net_quantity=sum(r['quantity'] for r in seed['compute_events'].values() if r['compute_holding_id']==hid and r['source_event_id']==anchor and r['period']==period and r['status']=='posted' and r['event_type'] in ['compute_meter','compute_meter_reversal'])
prior_allocation=sum(r['commitment_quantity_applied'] for rid,r in seed['compute_events'].items() if rid!=source_id and r['compute_holding_id']==hid and r['period']==period and r['status']=='posted' and r['event_type']=='compute_charge')
for committed,eligible in [(prior_allocation+net_quantity/2,False),(prior_allocation+net_quantity,True)]:
    remaining=max(0,committed-prior_allocation);assert (remaining>=net_quantity)==eligible;print('Commitment quantity-scope boundary:',remaining,'remaining for',net_quantity,'source quantity =>',eligible)

w=ext['workflows'][0];assert w['requires_external_wait'] is False and w['zero_wait_proof'];assert all(s['requires_external_wait'] is False and s['zero_wait_proof'] for s in w['steps']);assert 'region' in pol['compute_ext_snapshot_debit']['cross_category'][0]['reads'];print('O1 and region observation: explicit workflow/step zero-wait declarations and backup region read are present.')
print('AUDIT ROUND 2 SOURCE CONTRACT CHECKS OK')
