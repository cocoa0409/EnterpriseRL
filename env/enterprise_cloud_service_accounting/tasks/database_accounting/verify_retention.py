"""Recompute retention assessment values and prerequisite sensitivity from source policy and seed."""
from pathlib import Path
import sys,json,yaml,copy,importlib.util
ROOT=Path.cwd();D=ROOT/'env/enterprise_cloud_service_accounting/tasks/database_accounting';B=D.parents[1]/'blueprint'
sys.path[:0]=[str(ROOT),str(ROOT/'skills/erl-task-instantiate/scripts')]
from check_compute import build_env,eval_compute
from erlbench import ToolContext
from erlbench.db import DB
from erlbench.determinism import Clock
spec=importlib.util.spec_from_file_location('retention_tools',D/'task_tools.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ext=yaml.safe_load((D/'database.extended.yaml').read_text());task=json.loads((D/'tasks/0.json').read_text());ids=json.loads((D/'retention_ids.json').read_text());schema=json.loads((B/'db_schema.json').read_text());cross={p.stem:yaml.safe_load(p.read_text()) for p in (B/'products').glob('*.yaml')}
def run(skip=None):
 db=DB.seeded(copy.deepcopy(task['initial_state']));ctx=ToolContext(db,Clock.from_stamp(task['frozen_time']),schema,writable=True);out=[]
 for i,p in enumerate(ext['extended_policies'][:3]):
  env,_=build_env(db.tables,task['frozen_time'],ext,cross,schema,ids['holding']);value,*_=eval_compute(p['compute'],env,p['params']);trace=[]
  for bind in p['compute']:
   k,e=next(iter(bind.items()));env[k]=eval(e,{'__builtins__':{}},env);trace.append(f'{k}={env[k]!r}; {p["compute_basis"][k]}')
  out.append(dict(policy=p['id'],value=value,trace=trace))
  if i!=skip:getattr(mod,p['target_tool'])(ctx,ids['assessments'][i],value)
 return out
if __name__=='__main__':
 out={'gold':run(),'skip_external':run(0),'skip_native':run(1)}
 print(json.dumps(out,indent=2));(D/'retention_verification.json').write_text(json.dumps(out,indent=2)+'\n')
