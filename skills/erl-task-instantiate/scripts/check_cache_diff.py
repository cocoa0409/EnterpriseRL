"""CACHE-DIFF diagnostic (optional history-difficulty lint).

When a task intentionally uses a stale displayed quantity as a history trap, this report helps
the author see the seeded value beside the signed event-stream total and whether the persona has
a natural re-check reaction. It is informational by default: cache freshness and a particular
customer reaction are task-design choices, not a third correctness relation. The diagnostic
never changes the GT, rejects a tool call, or infers a policy conclusion.

THE CHECK (per task). For each computation, find which accounts it SUMs over the event stream
(parse `SUM('<event_table>', <field>, event_type=...)`). Map each such account to the holding
quantity field that caches it (binding.quantity_fields). For the computation's target holding:
  - INFO: report whether the seeded quantity field differs from the true signed event sum for
    that account (in:+, out:-).
  - INFO: report whether the task's user_scenario contains a natural re-check reaction marker.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_cache_diff.py env/<scenario>/tasks/<difficulty> [--task N]
"""
import glob
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import select_task_paths, split_task_flag

RECHECK_MARKERS = ("that's not right", "that is not right", "not what i remember",
                   "not the number", "check that again", "check again", "double-check",
                   "double check", "re-check", "recheck", "go over the account",
                   "doesn't add up", "does not add up")
_ET_RE = re.compile(r"event_type\s*=\s*['\"]([^'\"]+)['\"]")


def load_yaml(p):
    with open(p) as f:
        return yaml.safe_load(f)


def value_field_for(account):
    """erlbench accounting convention: money accounts carry amount_usd, data accounts data_mb,
    points accounts points. (Same value fields the event tables declare.)"""
    a = str(account)
    if "data" in a:
        return "data_mb"
    if "point" in a:
        return "points"
    return "amount_usd"


def main():
    pos, task_selector = split_task_flag(sys.argv[1:])
    if len(pos) < 1:
        print("usage: check_cache_diff.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    target = pos[0].rstrip("/")
    # scenario root (holds blueprint/)
    p = os.path.abspath(target)
    scen = None
    while p != "/":
        if os.path.isdir(os.path.join(p, "blueprint")):
            scen = p; break
        p = os.path.dirname(p)
    if not scen:
        raise SystemExit(f"cannot find scenario root (blueprint/) above {target}")
    db_schema = json.load(open(os.path.join(scen, "blueprint", "db_schema.json")))

    ext_files = glob.glob(os.path.join(target, "*.extended.yaml"))
    if not ext_files:
        raise SystemExit(f"no <category>.extended.yaml under {target}")
    ext = load_yaml(ext_files[0])
    binding = ext.get("binding") or {}
    htable = binding["holding_table"]
    holding_pk = next(iter(db_schema[htable]))
    qfields = binding.get("quantity_fields") or {}          # holding_field -> account_key
    acc_to_qf = {v: k for k, v in qfields.items()}
    # event_type -> (account, direction) from the events section (accounting events only)
    emeta = {}
    for e in (ext.get("events") or []):
        if e.get("account"):
            emeta[e["type"]] = (e["account"], e.get("direction", "out"))
    policies = {p2["id"]: p2 for p2 in (ext.get("extended_policies") or [])}

    task_paths = select_task_paths(target, task_selector)
    if not task_paths:
        raise SystemExit(f"no task json under {target}/tasks/")

    mode_label = f", selected_task={task_selector}" if task_selector is not None else ""
    print(f"🔎 CACHE-DIFF diagnostic  ({len(task_paths)} tasks{mode_label})  holding={htable}  quantity_fields={list(qfields)}")
    print(f"{'task':12} {'reconciled QF (field: seeded vs true)':>52} {'recheck':>8} {'info':>4}")
    warnings = []
    for tp in task_paths:
        tid = os.path.basename(tp)
        t = json.loads(open(tp).read())
        persona = str(t.get("user_scenario", ""))
        initial = t.get("initial_state") or {}
        holdings = initial.get(htable) or {}
        checked = []

        for c in (t.get("computations") or []):
            pol = policies.get(c.get("policy_id"))
            if not pol:
                continue
            # accounts this computation reconciles (SUM over event stream)
            recon_accounts = set()
            for binding_item in (pol.get("compute") or []):
                (_, expr), = binding_item.items()
                s = str(expr)
                if "SUM(" not in s:
                    continue
                for et in _ET_RE.findall(s):
                    meta = emeta.get(et)
                    if meta:
                        recon_accounts.add(meta[0])
            hid = c.get("target_holding_id")
            hrow = holdings.get(hid)
            if not hrow:
                continue
            hev = [r for r in (initial.get(binding["event_tables"][0]) or {}).values()
                   if str(r.get(holding_pk)) == str(hid)]
            for acc in sorted(recon_accounts):
                qf = acc_to_qf.get(acc)
                if not qf or qf not in hrow:
                    continue
                vf = value_field_for(acc)
                true = 0.0
                for ev in hev:
                    m = emeta.get(ev.get("event_type"))
                    if not m or m[0] != acc:
                        continue
                    v = float(ev.get(vf) or 0)
                    true += v if m[1] == "in" else -v
                true = round(true, 2)
                seeded = round(float(hrow.get(qf) or 0), 2)
                same = abs(seeded - true) < 1e-6
                checked.append((qf, seeded, true, same))
                if same:
                    warnings.append(f"{tid}: cache {qf}={seeded} equals event-stream total "
                                    f"{true} for account {acc} (no stale-cache trap was selected)")

        has_recheck = any(m in persona.lower() for m in RECHECK_MARKERS)
        if checked and not has_recheck:
            warnings.append(f"{tid}: history computation has no explicit cache re-check reaction "
                            "(optional; add one only when the scenario intentionally uses this trap)")

        disp = "; ".join(f"{qf}:{s}≠{tr}" if not sm else f"{qf}:{s}==={tr}!" for qf, s, tr, sm in checked) or "(none)"
        print(f"{tid:12} {disp[:52]:>52} {str(bool(checked and has_recheck)):>8} {'-':>4}")

    if warnings:
        print("\n  [INFO]")
        for warning in warnings[:40]:
            print("   ~", warning)
    print("\nCACHE-DIFF INFO (optional; no correctness gate)")
    sys.exit(0)


if __name__ == "__main__":
    main()
