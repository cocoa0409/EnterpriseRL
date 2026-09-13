"""Recompute selected task in prerequisite order and replay real atomic writes."""
import sys,json,yaml,importlib.util
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'skills/erl-task-instantiate/scripts'))
from check_compute import build_env,eval_compute
from erlbench import ToolContext
from erlbench.db import DB
from erlbench.determinism import Clock
D=Path(__file__).parent;B=D.parents[1]/'blueprint';schema=json.loads((B/'db_schema.json').read_text());ex=yaml.safe_load((D/'network.extended.yaml').read_text());cross={'support':yaml.safe_load((B/'products/support.yaml').read_text())}
spec=importlib.util.spec_from_file_location('net_tools',D/'task_tools.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def run(n=0,skip=None):
 baseline=run(n,None)[0] if skip is not None else None
 t=json.loads((D/f'tasks/{n}.json').read_text());plan=json.loads((D/f'verification_plan_{n}.json').read_text());db=DB.seeded(deepcopy(t['initial_state']));ctx=ToolContext(db,Clock.from_stamp(t['frozen_time']),schema,writable=True);out=[]
 for i,step in enumerate(plan):
  p=next(p for p in ex['extended_policies'] if p['id']==step['policy_id']);env,_=build_env(db.tables,t['frozen_time'],ex,cross,schema,step['holding']);value,*metrics=eval_compute(p['compute'],env,p['params']);args={k:(out[v['from_step']]['receipt']['event_id'] if isinstance(v,dict) else v) for k,v in step['args'].items()};args[p['computes']]=value
  factors={};local=dict(env);local['K']=lambda k:p['params'][k]
  for item in p['compute']:
   for name,expr in item.items():local[name]=eval(expr,{'__builtins__':{}},local);factors[name]=local[name]
  write_args=baseline[i]['arguments'] if baseline is not None else args
  if i!=skip:receipt=getattr(mod,p['target_tool'])(ctx,**write_args)
  else:
   shadow=DB.seeded(deepcopy(db.tables));receipt=getattr(mod,p['target_tool'])(ToolContext(shadow,Clock.from_stamp(t['frozen_time']),schema,writable=True),**write_args)
  out.append({'policy_id':p['id'],'value':value,'arguments':args,'factors':factors,'receipt':receipt})
 return out,db.hash()
if __name__=='__main__':
 n=int(sys.argv[1]) if len(sys.argv)>1 else 0;out,h=run(n);report={'steps':out,'terminal_hash':h,'sensitivity':{str(i):run(n,i)[0] for i in range(len(out)-1)}};(D/f'verification_{n}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
