import json, sys, hashlib, os
S = "/home/ubuntu/github/enterprise_rl/env/env_0049_state_unemployment_insurance_agency"
d = sys.argv[1]; V = f"/tmp/coord0049/views/{d}"; os.makedirs(V, exist_ok=True)
for i in range(int(sys.argv[2])):
    t = json.load(open(f"{S}/tasks/{d}/tasks/{i}.json"))
    out = f"{V}/task_{i}.runtime.json"
    json.dump({"frozen_time": t["frozen_time"], "user_scenario": t["user_scenario"]}, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"sha256 {hashlib.sha256(open(out,'rb').read()).hexdigest()}  {out}")
