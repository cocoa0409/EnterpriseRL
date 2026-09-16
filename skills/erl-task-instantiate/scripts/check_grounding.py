"""GROUNDING & DISCLOSURE gate — align what the persona says with what the world/gold holds.

`user_scenario` IS the user simulator's COMPLETE knowledge — the simulator can only state what
is written there. Two opposite obligations follow, both checked here:

A. IDENTITY MUST BE PRESENT (persona step, HARD). Every value the CUSTOMER supplies to a gold tool
   must appear in `user_scenario`. The blueprint's identity-verification share tool checks several
   customer-stated credential attributes (as many as its match threshold requires; its customer_id
   locator param never counts), and those parameters, plus the common defaults below, are the
   attributes checked here. If the gold passes an
   attribute value (e.g. an ssn_last4) that appears nowhere in `user_scenario`, no real simulator
   could produce it — the author lifted it from a locate/DB return (the god's-eye defect). Internal
   ids (customer_id, holding uuids) are EXEMPT: those legitimately come from a locate/find return,
   not the customer.

B. THE ANSWER MUST BE ABSENT (persona disclosure rule, HARD for non-integers). The difficulty of a task lives in
   the GAP between the customer's minimal surface goal and the long+wide policy chain the agent must
   discover. If the persona states the computed ANSWER (a `computations.expected` result), the sim
   can parrot it and any agent copies it — difficulty collapses. So a computed answer with a
   fractional part (e.g. 26.55, 14.35) must NOT appear verbatim in `user_scenario`. (Round-integer
   answers are only WARNed, since integers like caps/tiers legitimately occur.)

Plus a DISCLOSURE lint (persona disclosure rule, WARN): a multi-write task whose persona contains no
natural conditional reaction cues is likely a flat monologue that proactively telegraphs the solution path /
prerequisites instead of letting the agent discover them and the customer react passively. The cues
may be phrased freely; this check does not prescribe headings, numbered blocks, or an X→Y template.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_grounding.py env/<scenario>/tasks/<difficulty> [--task N]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import select_task_paths, split_task_flag

# Fallback only, used when the blueprint's identity-verification tool cannot be read: the credential
# attributes are normally derived from that tool's own parameters, whatever the scenario names them.
ID_ATTRS = ("name", "phone_number", "ssn_last4", "email", "service_password", "registered_address")


def identity_attrs(target):
    """Customer attributes that count as self-stated credentials: the parameters of the blueprint's
    identity-verification share tool (customer_id excluded); the generic defaults only when that tool
    cannot be read."""
    attrs = []
    path, bp = os.path.abspath(target), None
    while path != "/":
        if os.path.isdir(os.path.join(path, "blueprint")):
            bp = os.path.join(path, "blueprint")
            break
        path = os.path.dirname(path)
    if bp:
        try:
            import ast
            from check_solvability import identity_preamble_contract
            verifier = identity_preamble_contract(bp).get("verifier")
            tree = ast.parse(open(os.path.join(bp, "share_tools.py")).read())
            for fn in tree.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == verifier:
                    attrs += [a.arg for a in fn.args.args if a.arg not in ("ctx", "customer_id")]
        except (Exception, SystemExit):  # noqa: BLE001 — fall back to the defaults when the blueprint cannot be read
            pass
    return tuple(dict.fromkeys(attrs or list(ID_ATTRS)))
# passive-reaction openers, matched on word boundaries so they cannot fire inside longer words
COND_MARKERS = re.compile(
    r"\b(?:if|whenever|once|unless|in case|should you|as long as|provided that|suppose)\b"
    r"|\bwhen\s+(?:the\s+)?(?:agent|rep|representative|staff|advisor|you)\b"
    r"|\bwhen\s+(?:i\s+am\s+|i'm\s+)?(?:asked|told|prompted|informed)\b", re.I)
CALL_TOOLS = ("call_agent_discoverable_tool", "call_user_discoverable_tool")


def leaves(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from leaves(v)
    elif isinstance(x, list):
        for v in x:
            yield from leaves(v)
    else:
        yield x


def as_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def money_str(f):
    """Canonical 2-decimal string, e.g. 26.55 -> '26.55'."""
    return f"{f:.2f}"


def main():
    pos, task_selector = split_task_flag(sys.argv[1:])
    if len(pos) < 1:
        print("usage: check_grounding.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    target = pos[0].rstrip("/")
    task_paths = select_task_paths(target, task_selector)
    if not task_paths:
        raise SystemExit(f"no task json under {target}/tasks/")
    id_attrs = identity_attrs(target)

    mode_label = f", selected_task={task_selector}" if task_selector is not None else ""
    print(f"🔎 GROUNDING & DISCLOSURE gate  ({len(task_paths)} tasks{mode_label})")
    print(f"{'task':14} {'idAttrsUsed':>11} {'answers':>8} {'writes':>7} {'cond':>5} {'ok':>5}")
    fails = []
    warns = []
    for tp in task_paths:
        tid = os.path.basename(tp)
        t = json.loads(open(tp).read())
        persona = str(t.get("user_scenario", ""))

        # ---- A. identity attributes used in gold must be in persona ----
        custs = (t.get("initial_state") or {}).get("customers", {}) or {}
        attr_val_to_field = {}
        for row in custs.values():
            for f in id_attrs:
                v = row.get(f)
                if v not in (None, ""):
                    attr_val_to_field[str(v)] = f
        used = set()
        for a in (t.get("evaluation_criteria") or []):
            for v in leaves(a.get("arguments") or {}):
                if isinstance(v, str):
                    used.add(v)
        used_attrs = [v for v in used if v in attr_val_to_field]
        task_ok = True
        for v in sorted(used_attrs):
            if v not in persona:
                fails.append(f"{tid}: customer {attr_val_to_field[v]}='{v}' is used in the gold but is NOT "
                             "stated in user_scenario — the simulator cannot supply it (god's-eye value). "
                             "Pin it verbatim in user_scenario.")
                task_ok = False

        # ---- B. computed answers must not be telegraphed in persona ----
        comps = t.get("computations") or []
        n_answers = 0
        for c in comps:
            f = as_float(c.get("expected"))
            if f is None:
                continue
            n_answers += 1
            frac = abs(f - round(f)) > 1e-9
            s2 = money_str(f)
            if frac:
                # distinctive decimal answer must be absent — HARD
                if s2 in persona or (f"{f:g}" in persona):
                    fails.append(f"{tid}: computed answer expected={s2} (policy {c.get('policy_id')}) "
                                 "appears verbatim in user_scenario — the customer is telegraphing the "
                                 "answer (persona disclosure rule). Replace with \"I don't remember, you look "
                                 "it up\" or a WRONG number.")
                    task_ok = False
            else:
                # round-integer answer — WARN only, and only when it reads as a telegraphed AMOUNT
                # (int glued to a money unit like '9 USD' / 'USD 9' / '$9'); bare digits inside
                # phone/id/password runs, and tier prices like '159 USD plan', are NOT flagged.
                iv = str(int(round(f)))
                # currency-agnostic: any ISO-style currency code, currency word or currency symbol
                money = re.compile(
                    rf"(?:(?<![\d.]){re.escape(iv)}\s*(?:[A-Z]{{3}}|dollars?|euros?|pounds?|yuan|yen|francs?|rupees?)\b(?!\s*(?:tier|plan|package))"
                    rf"|(?:[A-Z]{{3}}|[$€£¥₹])\s*{re.escape(iv)}(?![\d.]))")
                if money.search(persona):
                    warns.append(f"{tid}: integer answer expected={iv} (policy {c.get('policy_id')}) "
                                 "appears as an amount in user_scenario — check it is not telegraphing the answer.")

        # ---- disclosure lint: multi-write persona should express passive conditions naturally ----
        n_writes = sum(1 for a in (t.get("evaluation_criteria") or [])
                       if a.get("tool") in CALL_TOOLS)
        n_cond = len(COND_MARKERS.findall(persona))
        if n_writes >= 2 and n_cond < 2:
            warns.append(f"{tid}: {n_writes} gold writes but only {n_cond} natural conditional-reaction "
                         "markers in user_scenario — likely a flat monologue that telegraphs the solution path. "
                         "Add clear passive reactions in the customer's own voice; do not convert it "
                         "into headings, numbered blocks, or a repeated X→Y template.")

        print(f"{tid:14} {len(used_attrs):>11} {n_answers:>8} {n_writes:>7} {n_cond:>5} {str(task_ok):>5}")

    if warns:
        print("\n  [WARN]")
        for w in warns[:40]:
            print("   ~", w)
    if fails:
        print("\n  [FAIL]")
        for f in fails[:40]:
            print("   -", f)
        print("GROUNDING NOT OK")
        sys.exit(1)
    print("\nGROUNDING OK" + ("  (with warnings — see above)" if warns else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
