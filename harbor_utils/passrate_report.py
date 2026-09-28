#!/usr/bin/env python3
"""Pass-rate report for harbor jobs: per env x product line (the scenario's difficulty dirs),
plus per env x EASY/MEDIUM/HARD label from task.toml. Trials without result.json are in flight."""
import json, sys, tomllib
from collections import defaultdict
from pathlib import Path
REPO = Path("/home/ubuntu/github/enterprise_rl")
JOBS = sys.argv[1:] or ["dsv41_max_13_15_20_26_8runs_raw", "glm53_max_13_15_20_26_8runs_raw"]
_label = {}
def label(task):
    if task not in _label:
        p = REPO / "harbor_tasks" / task / "task.toml"
        _label[task] = tomllib.loads(p.read_text())["metadata"].get("difficulty", "?") if p.exists() else "?"
    return _label[task]
def short(env):  # env_0013_workplace_dining_and_catering_provider -> 0013 workplace_dining
    parts = env.split("_", 2); return f"{parts[1]} {parts[2][:22]}"
def collect(job):
    jd = REPO / "jobs" / job
    cfg = json.loads((jd / "config.json").read_text()) if (jd / "config.json").exists() else {}
    k = cfg.get("n_attempts") or 0
    rows, inflight, errors = [], 0, 0
    for t in jd.iterdir():
        if not t.is_dir(): continue
        rf = t / "result.json"
        if not rf.exists(): inflight += 1; continue
        r = json.loads(rf.read_text())
        task = Path(r["task_id"]["path"]).name
        scen, diff, idx, _ = task.split("__")
        exc = r.get("exception_info")
        rew = ((r.get("verifier_result") or {}).get("rewards") or {}).get("reward")
        if exc or rew is None: errors += 1
        rows.append({"env": scen, "diff": diff, "idx": idx, "label": label(task), "reward": rew or 0.0,
                     "exc": bool(exc), "term": ((r.get("agent_result") or {}).get("metadata") or {}).get("termination")})
    return rows, inflight, errors, k, cfg
def rate(rs): return f"{sum(r['reward'] for r in rs)/len(rs)*100:5.1f}% ({sum(r['reward']>0 for r in rs)}/{len(rs)})" if rs else "   -"
data = {j: collect(j) for j in JOBS}
names = [j.split("_")[0] for j in JOBS]
print(f"{'':32s}" + "".join(f"{n:>18s}" for n in names))
for j, (rows, inflight, errors, k, cfg) in data.items():
    total = 40 * k
    print(f"{j:32s} done {len(rows)}/{total}  in-flight {inflight}  errors/exceptions {errors}  k={k}")
print()
envs = sorted({r["env"] for rows, *_ in data.values() for r in rows})
print("== per env x product line (scenario difficulty dir)")
for env in envs:
    rs_by = {j: [r for r in data[j][0] if r["env"] == env] for j in JOBS}
    print(f"{short(env):32s}" + "".join(f"{rate(rs_by[j]):>18s}" for j in JOBS) + "   <- env total")
    diffs = sorted({r["diff"] for rs in rs_by.values() for r in rs})
    for d in diffs:
        print(f"   {d[:29]:29s}" + "".join(f"{rate([r for r in rs_by[j] if r['diff']==d]):>18s}" for j in JOBS))
print()
print("== per env x task label (task.toml EASY/MEDIUM/HARD)")
for env in envs + ["ALL"]:
    for lab in ("EASY", "MEDIUM", "HARD"):
        cells = []
        for j in JOBS:
            rs = [r for r in data[j][0] if (env == "ALL" or r["env"] == env) and r["label"] == lab]
            cells.append(rate(rs))
        if any(c.strip() != "-" for c in cells):
            print(f"{(short(env) if env!='ALL' else 'ALL'):24s} {lab:7s}" + "".join(f"{c:>18s}" for c in cells))
print()
print("== overall" + "".join(f"{rate(data[j][0]):>18s}" for j in JOBS))
terms = {j: defaultdict(int) for j in JOBS}
for j in JOBS:
    for r in data[j][0]: terms[j][r["term"] or ("EXC" if r["exc"] else "?")] += 1
print("terminations: " + " | ".join(f"{j.split('_')[0]} {dict(terms[j])}" for j in JOBS))
import subprocess
def trunc(job):
    out = subprocess.run(["grep", "-rl", "--include=*.json", '"finish_reason": "length"', str(REPO / "jobs" / job)],
                         capture_output=True, text=True).stdout.split()
    files = [f for f in out if "/llm_debug/" in f]
    agent = sum("_agent_response" in f for f in files)
    return f"{len(files)} calls hit max_tokens ({agent} agent, {len(files)-agent} user)"
print("truncation:   " + " | ".join(f"{j.split('_')[0]} {trunc(j)}" for j in JOBS))
