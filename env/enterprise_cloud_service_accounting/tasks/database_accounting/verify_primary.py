"""Executable handling-time calculation and real-CRUD sensitivity for the primary correction."""
from pathlib import Path
import sys,json,yaml,copy,importlib.util
ROOT=Path.cwd();D=ROOT/'env/enterprise_cloud_service_accounting/tasks/database_accounting';B=D.parents[1]/'blueprint'
sys.path[:0]=[str(ROOT),str(ROOT/'skills/erl-task-instantiate/scripts')]
from check_compute import build_env,eval_compute
from erlbench import ToolContext
from erlbench.db import DB
from erlbench.determinism import Clock
spec=importlib.util.spec_from_file_location('primary_tools',D/'task_tools.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
x=yaml.safe_load((D/'database.extended.yaml').read_text());t=json.loads((D/'tasks/1.json').read_text());ids=json.loads((D/'primary_ids.json').read_text());schema=json.loads((B/'db_schema.json').read_text());cross={p.stem:yaml.safe_load(p.read_text()) for p in (B/'products').glob('*.yaml')}
def run(skip=None):
 db=DB.seeded(copy.deepcopy(t['initial_state']));ctx=ToolContext(db,Clock.from_stamp(t['frozen_time']),schema,writable=True);out=[];request=''
 for i,p in enumerate(x['extended_policies'][3:]):
  env,_=build_env(db.tables,t['frozen_time'],x,cross,schema,ids['holding']);value,*_=eval_compute(p['compute'],env,p['params']);env['K']=lambda k:p['params'][k];trace=[]
  for b in p['compute']:
   k,e=next(iter(b.items()));env[k]=eval(e,{'__builtins__':{}},env);trace.append(f'{k}={env[k]!r}; {p["compute_basis"][k]}')
  if i==0:args=dict(database_event_id=ids['average'],quantity=value)
  elif i==1:args=dict(database_event_id=ids['review'],database_holding_id=ids['holding'],source_event_id=ids['source'],related_event_id=ids['average'],net_amount=value)
  elif i==2:
   args=dict(database_event_id=ids['source'],database_holding_id=ids['holding'],customer_id=ids['customer'],related_event_id=ids['review'],request_id='02639a90-5b5e-4816-91a6-776b48c5be8a',external_reference='RIVER-CORRECT-AUG',quantity=value)
   request=args['request_id']
  else:args=dict(database_event_id=ids['review'],database_holding_id=ids['holding'],customer_id=ids['customer'],source_event_id=ids['source'],related_event_id=ids['review'],request_id=request,amount=value)
  receipt='' if i==skip else getattr(mod,p['target_tool'])(ctx,**args)
  out.append(dict(policy=p['id'],value=value,args=args,trace=trace,receipt=receipt))
 return out
if __name__=='__main__':
 out={'gold':run(),'skip_average':run(0),'skip_review':run(1),'skip_consent':run(2)};print(json.dumps(out,indent=2));(D/'primary_verification.json').write_text(json.dumps(out,indent=2)+'\n')
