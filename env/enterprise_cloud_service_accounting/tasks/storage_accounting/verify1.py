"""Executable handling-time calculation and prerequisite deletion sensitivity, real tools."""
import sys,json,yaml,copy,importlib.util
from pathlib import Path
sys.path.insert(0,'skills/erl-task-instantiate/scripts');sys.path.insert(0,'.')
from check_compute import build_env,eval_compute
from erlbench import ToolContext
from erlbench.tools import collect_specs
from erlbench.db import DB
from erlbench.determinism import Clock
D=Path('env/enterprise_cloud_service_accounting/tasks/storage_accounting');B=D.parents[1]/'blueprint';t=json.loads((D/'tasks/1.json').read_text());ids=json.loads((D/'verification_refs1.json').read_text());E=yaml.safe_load((D/'storage.extended.yaml').read_text());pol=E['extended_policies'][3:];schema=json.loads((B/'db_schema.json').read_text());cross={p.stem:yaml.safe_load(p.read_text()) for p in (B/'products').glob('*.yaml')}
s=importlib.util.spec_from_file_location('storage_tools',D/'task_tools.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);tools={s.name:s for s in collect_specs(m,'task')}
def run(skip=None):
 db=DB(copy.deepcopy(t['initial_state']));out=[];credit_id=''
 for j,p in enumerate(pol):
  env,_=build_env(db.tables,t['frozen_time'],E,cross,schema,ids['holding']);result,*_=eval_compute(p['compute'],env,p['params']);trace={}
  for item in p['compute']:
   for k,v in item.items():env[k]=eval(v,{'__builtins__':{}},env);trace[k]=env[k]
  args=[dict(storage_event_id=ids['incident'],request_id=ids['claim']),dict(storage_event_id=ids['review'],source_event_id=ids['invoice'],related_event_id=ids['incident'],storage_holding_id=ids['holding'],request_id=ids['claim']),dict(storage_event_id=ids['review'],storage_holding_id=ids['holding'],source_event_id=ids['invoice'],related_event_id=ids['review'],request_id=ids['claim'],customer_id=ids['customer']),dict(storage_event_id=ids['authorization'],request_id=ids['authorization'],source_event_id=ids['payment'],related_event_id=credit_id,storage_holding_id=ids['holding']),dict(storage_event_id=ids['authorization'],storage_holding_id=ids['holding'],source_event_id=ids['payment'],request_id=ids['authorization'],customer_id=ids['customer'])][j]
  args[p['computes']]=result
  ctx=ToolContext(db,Clock(t['frozen_time']),schema,writable=True)
  if j==2:credit_id=ctx.make_id('storage_credit',*[args[k] for k in ['storage_event_id','storage_holding_id','source_event_id','related_event_id','request_id','customer_id','amount']])
  receipt=tools[p['target_tool']].func(ctx,**args) if j!=skip else 'SKIPPED'
  out.append(dict(policy_id=p['id'],value=result,args=args,trace=trace,receipt=receipt))
  if j in (0,3) and j != skip:
   request_row=db.tables['storage_events'][ids['claim' if j==0 else 'authorization']]
   assert request_row['status']=='posted'
   assert request_row['notice_at']==ctx.now()==request_row['occurred_at']
   out[-1]['filed_record']={k:request_row.get(k) for k in ['storage_event_id','request_id','source_event_id','related_event_id','status','notice_at','occurred_at','credited_amount']}
   if j==3:
    assert args['storage_event_id']==args['request_id']==request_row['storage_event_id']
    assert request_row['source_event_id']==ids['payment']
 return out
if __name__=='__main__':
 r=dict(normal=run(),sensitivity={str(j):run(j) for j in range(4)});(D/'verification1.json').write_text(json.dumps(r,indent=2));print('NORMAL',[(v['policy_id'],v['value']) for v in r['normal']]);print('SENSITIVITY', {k:[v['value'] for v in vs] for k,vs in r['sensitivity'].items()})
