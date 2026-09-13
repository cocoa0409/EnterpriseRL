"""Executable handling-time arithmetic and prerequisite sensitivity for this difficulty."""
from pathlib import Path
import sys,json,yaml,importlib.util,copy
D=Path(__file__).resolve().parent;ROOT=D.parents[3];B=D.parents[1]/'blueprint'
sys.path[:0]=[str(ROOT),str(ROOT/'skills/erl-task-instantiate/scripts')]
from check_compute import build_env,eval_compute
from erlbench import ToolContext
from erlbench.tools import collect_specs
from erlbench.db import DB
from erlbench.determinism import Clock
from erlbench.scoring import _resolve

def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
schema=json.loads((B/'db_schema.json').read_text());primary=yaml.safe_load((D/'compute.extended.yaml').read_text());pols={p['id']:p for p in primary['extended_policies']};cross={p.stem:yaml.safe_load(p.read_text()) for p in (B/'products').glob('*.yaml') if p.stem!='compute'}
specs={s.name:s for path,name in [(B/'share_tools.py','shared'),(D/'task_tools.py','task')] for s in collect_specs(load(path,name),'task')}
for path in sorted((D/'tasks').glob('*.json')):
 t=json.loads(path.read_text());db=DB.seeded(t['initial_state']);clock=Clock(t['frozen_time']);cs={c['step']:c for c in t['computations']}
 for i,a in enumerate(t['evaluation_criteria']):
  if i in cs:
   c=cs[i];p=pols[c['policy_id']];env,_=build_env(db.tables,t['frozen_time'],primary,cross,schema,c['target_holding_id']);v=eval_compute(p['compute'],env,p.get('params'))[0];assert v==c['expected'],(i,v,c['expected']);print(path.name,p['id'],v)
   for edge in p['prerequisite']:
    skip=pols[edge['problem']]['target_tool'];alt=DB.seeded(t['initial_state'])
    for prior in t['evaluation_criteria'][:i]:
     name,args=_resolve(prior);sp=specs.get(name)
     if sp and sp.rw=='write' and name!=skip:sp.func(ToolContext(alt,clock,schema,writable=True),**sp.coerce(args))
    env,_=build_env(alt.tables,t['frozen_time'],primary,cross,schema,c['target_holding_id']);vv=eval_compute(p['compute'],env,p.get('params'))[0];assert vv!=v,(edge,v,vv);print('  skip',edge['problem'],'=>',vv)
  name,args=_resolve(a);sp=specs.get(name)
  if sp and sp.rw=='write':sp.func(ToolContext(db,clock,schema,writable=True),**sp.coerce(args))
 print('terminal hash',db.hash())
