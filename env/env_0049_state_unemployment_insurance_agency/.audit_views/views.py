# usage: views.py <difficulty>  -> /tmp/coord0049/views/<difficulty>/task_<i>.blind.json + hashes
import json, sys, hashlib, glob, os
S = "/home/ubuntu/github/enterprise_rl/env/env_0049_state_unemployment_insurance_agency"
d = sys.argv[1]; T = f"{S}/tasks/{d}"; V = f"/tmp/coord0049/views/{d}"
os.makedirs(V, exist_ok=True)
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
for p in sorted(glob.glob(f"{T}/*.extended.yaml")) + [f"{T}/task_tools.py"]:
    print(f"sha256 {h(p)}  {p}")
for p in sorted(glob.glob(f"{T}/tasks/*.json"), key=lambda x: int(os.path.basename(x)[:-5])):
    t = json.load(open(p)); i = os.path.basename(p)[:-5]
    blind = {k: t[k] for k in ("frozen_time", "user_scenario", "initial_state")}
    out = f"{V}/task_{i}.blind.json"
    json.dump(blind, open(out, "w"), indent=1, ensure_ascii=False)
    masked = [k for k in t if k not in blind]
    print(f"sha256 {h(out)}  {out}   (from {p} sha256 {h(p)}; masked keys: {', '.join(masked)})")
