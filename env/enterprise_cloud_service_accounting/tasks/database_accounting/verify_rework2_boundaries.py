"""Audit P1/P2/P3 witnesses plus integer-price boundary regression, no source mutations."""
from pathlib import Path
import json,yaml
from decimal import Decimal,ROUND_HALF_UP
D=Path(__file__).resolve().parent
x=yaml.safe_load((D/'database.extended.yaml').read_text());ap=x['extended_policies'][3];tp=x['extended_policies'][4]
def calculate(q,n,rate,configuration,region):
 e={'net_quantity':float(q),'resources':n,'int':int}
 for b in ap['compute']:
  k,expr=next(iter(b.items()))
  if k in ['net_hundredths','result']:e[k]=eval(expr,{'__builtins__':{}},e)
 avg=e['result'];e.update(average=avg,rate=float(rate),configuration=float(configuration),region=float(region))
 begun=False
 for b in tp['compute']:
  k,expr=next(iter(b.items()))
  if k=='average_millionths':begun=True
  if begun:e[k]=eval(expr,{'__builtins__':{}},e)
 decimal=(Decimal(str(q))*Decimal(str(rate))*Decimal(str(configuration))*Decimal(str(region))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
 assert Decimal(str(e['result']))==decimal,(q,n,rate,configuration,region,e,decimal)
 assert e['aggregate_hundredths']==int(Decimal(str(q))*100)
 return {'average':avg,'aggregate_hundredths':e['aggregate_hundredths'],'integer_subtotal_trillionths':e['subtotal_trillionths'],'target':e['result'],'decimal_target':str(decimal)}
results={}
p1=calculate(5200,8,.5,.9,1.04);results['P1']={**p1,'original':2000,'prior_correction':0,'credit_workflow_admitted':2000>p1['target'],'inherited_action':'positive debit adjustment','inherited_amount':str(Decimal(str(p1['target']))-Decimal('2000'))};assert results['P1']['credit_workflow_admitted'] is False
results['P2']=calculate(.01,3,.5,1,1);assert results['P2']['target']==.01
results['P3']=calculate(.1,1,.35,1,1);assert results['P3']['target']==.04
samples=0
rates=[.186,.372,.744,1.488,2.976,5.952,.5,.35,.123456]
for n in range(1,65):
 for cents in [1,2,3,7,10,11,49,50,99,100,101,10001,74400*n]:
  for rate in rates:
   for conf in [1,.9,1.95]:
    for region in [1,1.04,1.12]:
     calculate(Decimal(cents)/100,n,rate,conf,region);samples+=1
results['regression']={'decimal_reference_matches':samples,'resource_counts':'1 through 64','quantity_grain':'hundredths','maximum_quantity':'744 node-hours per node','passed':True}
(D/'rework2_boundary_results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
