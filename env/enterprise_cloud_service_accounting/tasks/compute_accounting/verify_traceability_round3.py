"""Verify the redesigned customer handoff in live runtime and frozen-gate producer order.

The historical user-write omission demonstration is retained verbatim in
traceability_round3_diagnosis.txt. This verifier tests the permitted redesign.
"""
from pathlib import Path
import sys,json,importlib.util,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[3];B=D.parents[1]/'blueprint';sys.path.insert(0,str(ROOT))
from erlbench.engine import Engine
from erlbench.tools import collect_specs,ToolContext
from erlbench.db import DB
from erlbench.determinism import Clock
from erlbench.scoring import _resolve

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
specs=[]
for path,name,kind in [(B/'share_tools.py','share_r3','share'),(D/'task_tools.py','tasks_r3','task')]:specs.extend(collect_specs(load(path,name),kind))
registry={s.name:s for s in specs};schema=json.loads((B/'db_schema.json').read_text());t=json.loads((D/'tasks/0.json').read_text());acts=t['evaluation_criteria'];clock=Clock.from_stamp(t['frozen_time']);user_steps=[i for i,a in enumerate(acts) if a['tool']=='call_user_discoverable_tool'];assert user_steps==[len(acts)-1]
final=acts[-1]['arguments']['arguments'];request=final['request_id'];assessment=final['related_event_id'];assert request==final['compute_event_id'];assert request in t['initial_state']['compute_events'];assert assessment not in t['user_scenario'];assert assessment not in t['initial_state']['compute_events'];original=t['initial_state']['compute_events'][request];assert original['status']=='pending' and original['decision']=='none'
# KB is unused by this recorded trajectory; actual unlock, ownership and routing run through Engine.
live=Engine(DB.seeded(t['initial_state']),clock,None,specs,schema);agent_receipts=[]
for i,a in enumerate(acts[:-1]):
 out=live.call(a['owner'],a['tool'],a.get('arguments',{}));assert not out.startswith('Error:'),(i,out);agent_receipts.append(out)
assert assessment in '\n'.join(agent_receipts);assessment_row=live.db.tables['compute_events'][assessment];assert assessment_row['event_type']=='compute_review' and assessment_row['credited_amount']==3450;assert assessment_row['request_id']==request and assessment_row['source_event_id']==final['source_event_id']
# The frozen gate executes agent-owned resolved tools only: every consumed ID producer now qualifies.
gate_db=DB.seeded(t['initial_state']);gate_receipts=[]
for a in acts[:-1]:
 name,args=_resolve(a);spec=registry.get(name)
 if spec is not None and a.get('owner')=='agent':gate_receipts.append(str(spec.func(ToolContext(gate_db,clock,schema,writable=spec.rw=='write'),**spec.coerce(args))))
assert assessment in '\n'.join(gate_receipts);assert gate_db.hash()==live.db.hash()
before=live.db.hash();a=acts[-1];out=live.call(a['owner'],a['tool'],a['arguments']);assert not out.startswith('Error:'),out;refund_id=out.split()[-1].rstrip('.');refund=live.db.tables['compute_events'][refund_id];assert refund['event_type']=='compute_refund' and refund['status']=='posted' and refund['amount']==3450;assert refund['request_id']==request and refund['related_event_id']==assessment;assert live.db.hash()!=before;assert live.db.hash()=='f5c1ceae4365257448b312c691598441a5f663d6b1ed2a9a240b019b5a4d1589'
print(json.dumps({'user_step':user_steps[0],'original_customer_request':request,'original_consent_status':original['status'],'assessment_from_agent_receipt':assessment,'assessment_amount':assessment_row['credited_amount'],'frozen_gate_and_runtime_agent_prefix_hashes_match':True,'final_user_receipt':out,'final_customer_refund_amount':refund['amount'],'user_receipt_is_shared_runtime_output':True,'downstream_consumers_of_user_receipt':0,'live_terminal_hash':live.db.hash(),'source_fingerprints':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'compute.extended.yaml',D/'task_tools.py']}},indent=2));print('ROUND 3 LIVE CUSTOMER EXECUTION AND GENERATED-ID PRODUCER ORDER OK')
