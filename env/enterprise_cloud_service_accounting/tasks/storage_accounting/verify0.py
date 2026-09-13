"""Recompute every binding and sensitivity using real CRUD; run from repository root."""
import sys,json,yaml,copy,importlib.util
from pathlib import Path
sys.path.insert(0,'skills/erl-task-instantiate/scripts');sys.path.insert(0,'.')
from check_compute import build_env,eval_compute
from erlbench import ToolContext
from erlbench.tools import collect_specs
from erlbench.db import DB
from erlbench.determinism import Clock
D=Path('env/enterprise_cloud_service_accounting/tasks/storage_accounting');B=D.parents[1]/'blueprint'
t=json.loads((D/'tasks/0.json').read_text());ids=json.loads((D/'verification_refs0.json').read_text());E=yaml.safe_load((D/'storage.extended.yaml').read_text());schema=json.loads((B/'db_schema.json').read_text());cross={p.stem:yaml.safe_load(p.read_text()) for p in (B/'products').glob('*.yaml')};
spec=importlib.util.spec_from_file_location('storage_tools',D/'task_tools.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);tools={s.name:s for s in collect_specs(m,'task')}
args=[dict(storage_event_id=ids['entitlement']),dict(storage_event_id=ids['review'],source_event_id=ids['charge'],related_event_id=ids['export'],storage_holding_id=ids['holding']),dict(storage_event_id=ids['review'],storage_holding_id=ids['holding'],source_event_id=ids['charge'],related_event_id=ids['review'],customer_id=ids['customer'])]
def run(skip=None):
 db=DB(copy.deepcopy(t['initial_state']));out=[]
 for i,p in enumerate(E['extended_policies'][:3]):
  env,_=build_env(db.tables,t['frozen_time'],E,cross,schema,ids['holding']);result,*_=eval_compute(p['compute'],env,p['params']);trace={}
  for bind in p['compute']:
   for k,v in bind.items(): env[k]=eval(v,{'__builtins__':{}},env);trace[k]=env[k]
  a=dict(args[i],**{p['computes']:result});out.append(dict(policy_id=p['id'],value=result,trace=trace,args=a))
  if i!=skip:tools[p['target_tool']].func(ToolContext(db,Clock(t['frozen_time']),schema,writable=True),**a)
 return out
if __name__=='__main__':
 normal=run();sensitivity={str(i):run(i) for i in range(2)};r=dict(normal=normal,sensitivity=sensitivity);(D/'verification0.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
