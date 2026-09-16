"""COMPUTE gate (the core): machine-recompute every task's computed gold argument
from its `extended_policy.compute` over the world AS IT STANDS AT THAT WRITE'S HANDLING
TIME — the task's initial_state with every earlier gold write already landed — and assert
it EQUALS the declared `expected` AND the gold argument. Then prove that every declared
FACTOR of that computation bears weight on this world, and gate suite-level means.

WHY. This skill puts task difficulty in a multi-factor computation over reconciled history, not
in tool selection. That is only real if (a) the computed value is machine-recomputable and the
gold is forced by it, and (b) every factor the policy declares actually changes the number on
this task's world. A "factor" here is NOT a line of compute: it is a declared RULE WITH A
LADDER that decides one input of the result (see references/product_extended.yaml, `factors`).
A rule whose baseline reading gives the same number is decoration: an agent that never found
its document falls back to the baseline and scores anyway, so it tests nothing.

WHY THE HANDLING-TIME STATE (this IS the definition of GT). The rollout world is stateful
and the agent works it like a real seat: read, write, read again. By the time the agent must
produce the parameter at evaluation_criteria step k, every earlier write of the same task has
landed; the only correct value of a policy formula is its value over THAT ledger. Evaluating
over the pristine initial_state would silently assume "none of my own earlier steps happened" —
whenever a formula aggregates the very table an earlier step writes into (running totals,
remaining quotas, highest-settled selections, deductible accumulators), the time-zero value
diverges from the handling-time value and punishes precisely the agent that follows the
documented procedure. A task whose declared `expected` disagrees with the handling-time
recompute carries a WRONG gold and must be re-authored — fix the expected / the seed / the
formula, never re-point the evaluation back at time zero.

Implementation: gold writes are replayed in order with the real tools (blueprint share_tools +
this difficulty's task_tools) onto the seeded DB; each computation is evaluated on the snapshot
taken just before its own step executes. Reads are stateless and skipped; a prior write that
errors is skipped (it changed nothing live either — replay_tasks gates error-freeness).

DSL primitives (see references/product_extended.yaml): NOW / HID / CUST, F(field), P(param),
K(key), SUM/COUNT/MAX/LATEST over this holding's event history (optional within_months),
EXISTS/CPARAM/CFIELD over another category's holdings, XSUM/XCOUNT/XMAX/XLATEST over another
category's EVENT HISTORY (scoped to this customer), MONTHS/DAYS, MX/MN/RND/ABS and arithmetic.

BASELINE + FACTORS (the design this gate enforces). Every computation has a BASELINE: a complete
standard method with default values, declared in the policy's `baseline` block and rendered as
ONE knowledge-base document. Each FACTOR changes that baseline — a value or the method — for
customers in a given situation, and is rendered as its OWN document; no document mentions
another (a discrete topology, never a star). An agent that never finds a factor document falls
back to the baseline and computes a definite, wrong number without any signal. So on every task
world EVERY declared factor must put the customer on a tier other than the baseline, and the
baseline as a whole must give a result different from gold. Per factor, `baseline` names the
expression its `decides` binding takes under the standard method / default value; the gate
substitutes it and requires `result` to move; substituting every factor's baseline at once
gives the fall-back result, recorded in the task as `baseline_result` and required to differ
from `expected`.

FACTOR gate (per computation, on the handling-time world). A factor = a TRIGGER CONDITION
(a ladder of >= 3 tiers; the factor is MULTI-SOURCE when every tier beyond the fall-through
combines >= 2 conditions over distinct evidence by AND or by OR — "gold card AND >= 3 purchases in
the last 3 months") + an EFFECT, labelled:
  effect: parameter  the tier selects a VALUE that enters an otherwise fixed formula
                     (a rate, a fee, a threshold, an allowance)
  effect: method     the tier selects HOW a quantity is computed — the operation applied, the
                     base it acts on, the rounding mode / precision / moment, the day-count or
                     window convention, the order of two operations, the moment of a cap, the
                     aggregation used, a multiplier on an intermediate or on the result
                     ("gold: overdue days halved and rounded down; silver: times 0.75 and
                     rounded up; otherwise as booked")
  - the policy declares `factors`; every factor names bindings that exist in compute, one of
    them as `decides`; no binding belongs to two factors; `effect` is parameter | method; the
    ladder has >= 3 tiers, pairwise disjoint as stated (each `when` + `value` for a parameter
    factor, `when` + `method` for a method factor), and the factor's bindings fork at least
    (tiers - 1) times (disjointness is read, not machine-checked);
  - 4 to 6 factors per computation (the count drawn uniformly at random per computation); >= 2
    of them effect=parameter and >= 2 effect=method; >= 2 multi-source; >= 2 of them `cross_difficulty` (their tier is decided from
    another category's holding or ledger, read through CFIELD/CPARAM/EXISTS/XSUM/XCOUNT/XMAX/
    XLATEST on that category, and the world seeds that evidence for this customer);
  - LOAD-BEARING: substituting the factor's `baseline` bindings (the standard method / default
    value the baseline document states) and recomputing MUST change `result`; the task's declared
    `factor_sensitivity[].baseline_result` must equal that recomputation; substituting EVERY
    factor's baseline at once must evaluate cleanly and give `computations[].baseline_result`,
    which must differ from `expected` (the fall-back answer is definite and wrong);
  - the older whole-input tests are kept as a floor: forcing every cross-category read off must
    change the result, and zeroing every history aggregate must change the result.
  There is deliberately NO requirement that some branch stay untriggered: an untriggered
  branch is invisible to the score, so it is not a difficulty and is never asked for.

Difficulty thresholds (check_extended enforces a configurable M-task suite):
  4 to 6 declared factors per computation: >= 2 parameter, >= 2 method, >= 2 cross-difficulty,
  >= 2 multi-source, every ladder >= 3 tiers
  >= 8 history rows reconciled (suite max)
  >= 5 if-else/fork branches (suite max)
  >= 4 evaluation_criteria actions (suite mean)
plus: EVERY extended_policy reads a cross-category VALUE (CPARAM/CFIELD/X-history, not a bare
EXISTS) and that read is exercised by the task world, and >= 1 formula-forced write.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_compute.py env/<scenario>/tasks/<difficulty> [--task N]
"""
import ast
import glob
import importlib.util
import json
import os
import sys
from copy import deepcopy

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import select_task_paths, split_task_flag

# Suite-level metrics: means enforce breadth across M tasks; maxes enforce that the
# suite contains at least one genuinely deep history and branch workload.
MEANS = {"factors": 4.0, "branches": 4.0, "steps": 4.0}
MIN_FACTORS_PER_COMP = 4            # every computed value rests on 4 to 6 declared, load-bearing factors
MAX_FACTORS_PER_COMP = 6            # ... the count drawn uniformly at random per computation
MIN_CROSS_FACTORS_PER_COMP = 2      # ... of which >= 2 decide their tier from ANOTHER difficulty's records
MIN_PARAM_FACTORS_PER_COMP = 2      # ... >= 2 whose effect selects a value (effect: parameter)
MIN_METHOD_FACTORS_PER_COMP = 2     # ... >= 2 whose effect selects how a quantity is computed (effect: method)
MIN_MULTISOURCE_FACTORS_PER_COMP = 2  # ... >= 2 whose every tier beyond the fall-through combines >= 2 distinct evidence sources (and / or)
MIN_LADDER_TIERS = 3                # a factor partitions its input's space into >= 3 pairwise-disjoint tiers, the fall-through counted (the realistic shape)
_EFFECTS = {"parameter", "method"}
SUITE_MAX_HISTORY = 8              # at least one task must reconcile a substantial history
SUITE_MAX_BRANCHES = 5              # at least one task must traverse substantial conditional forks
_CALL_WRAPPERS = {"call_agent_discoverable_tool", "call_user_discoverable_tool"}
_FORK_FUNCS = {"MN", "MX", "min", "max"}   # min/max are conditional selections = forks

# ---- restricted-expression sandbox ---------------------------------------- #
_ALLOWED_NODES = (
    ast.Expression, ast.IfExp, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare,
    ast.Call, ast.Name, ast.Load, ast.Constant, ast.keyword,
    ast.And, ast.Or, ast.Not, ast.USub, ast.UAdd,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
)
_XHIST = {"XSUM", "XCOUNT", "XMAX", "XLATEST"}          # another category's event history
_FUNCS = {"F", "P", "K", "SUM", "COUNT", "MAX", "LATEST", "EXISTS", "CPARAM", "CFIELD",
          "MONTHS", "DAYS", "MX", "MN", "RND", "ABS", "min", "max", "round", "abs", "float", "int"} | _XHIST
_CONSTS = {"NOW", "HID", "CUST", "True", "False", "None"}
_CALL_ONLY = {"EXISTS", "CPARAM", "CFIELD"} | _XHIST     # cross-category read primitives
_CROSS_QUANT = {"CPARAM", "CFIELD"} | _XHIST            # ... of which these return a VALUE, not a predicate
_EVIDENCE_FUNCS = {"SUM", "COUNT", "MAX", "LATEST", "EXISTS", "CPARAM", "CFIELD",
                   "MONTHS", "DAYS"} | _XHIST            # a factor's tier must rest on at least one of these


def policy_cross_calls(policy):
    """Which cross-category primitives this policy's ordered compute actually calls."""
    called = set()
    for item in policy.get("compute") or []:
        if not isinstance(item, dict):
            continue
        for expr in item.values():
            try:
                tree = ast.parse(str(expr), mode="eval")
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id in _CALL_ONLY):
                    called.add(node.func.id)
    return called


def policy_has_cross_factor(policy):
    """A declaration alone is insufficient, and so is a bare existence test.

    The compute must read a cross-category VALUE (CPARAM/CFIELD, or an X-history aggregate):
    only a value can make the computed QUANTITY depend on the other category.  EXISTS may
    accompany it as a condition, but on its own it can only switch the whole result on or off —
    and that shape is how a base-pinned amount gets silently zeroed.

    This is a shape check on the compute: it does not evaluate the value it reads, so a tier
    parameter carrying the same value in every tier still passes here.  The load-bearing test
    further down evaluates it against the task world.
    """
    if not policy.get("cross_category"):
        return False
    return bool(policy_cross_calls(policy) & _CROSS_QUANT)


def expr_calls(expr):
    """{(func_name, first constant arg or None)} for every call in a restricted expression."""
    out = set()
    try:
        tree = ast.parse(str(expr), mode="eval")
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            first = None
            if node.args and isinstance(node.args[0], ast.Constant):
                first = node.args[0].value
            out.add((node.func.id, first))
    return out


def validate_ast(tree, known_names):
    """Whitelist node types + names; return (#IfExp, #cross-cat calls, #fork calls) — every
    ternary, cross-category call, and min/max selection is a conditional fork the agent must get right."""
    n_if, n_cross, n_fork = 0, 0, 0
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"disallowed syntax {type(node).__name__}")
        if isinstance(node, ast.IfExp):
            n_if += 1
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("only bare function calls allowed")
            if node.func.id in _CALL_ONLY:
                n_cross += 1
            if node.func.id in _FORK_FUNCS:
                n_fork += 1
        if isinstance(node, ast.Name) and node.id not in known_names:
            raise ValueError(f"unknown name '{node.id}'")
    return n_if, n_cross, n_fork


def _parse_date(d):
    p = str(d)[:10].split("-")
    return int(p[0]), int(p[1]), int(p[2])


def MONTHS(d1, d2):
    y1, m1, day1 = _parse_date(d1)
    y2, m2, day2 = _parse_date(d2)
    m = (y2 - y1) * 12 + (m2 - m1)
    if day2 < day1:
        m -= 1
    return m


def DAYS(d1, d2):
    from datetime import date
    a = date(*_parse_date(d1))
    b = date(*_parse_date(d2))
    return (b - a).days


def build_env(initial, frozen_time, primary, cross, db_schema, holding_id):
    """Sandbox namespace scoped to one target holding; also returns two touch-recorders:
    `touched` = this holding's event rows read, `xtouched` = {category: rows read from that
    category's event tables} (cross-difficulty history evidence)."""
    htable = primary["binding"]["holding_table"]
    H = (initial.get(htable) or {}).get(holding_id)
    if H is None:
        # fall back: search all tables for the id
        for t, rows in initial.items():
            if holding_id in (rows or {}):
                H = rows[holding_id]; htable = t; break
    if H is None:
        raise ValueError(f"target_holding_id {holding_id} not in initial_state")
    HID = holding_id
    CUST = H.get("customer_id")
    NOW = str(frozen_time)[:10]
    holding_pk = next(iter(db_schema[htable]))
    vindex = {v["name"]: (v.get("parameters") or {}) for v in (primary.get("variants") or [])}
    touched = set()
    xtouched = {}

    def _rows(table, eq):
        for rid, row in (initial.get(table) or {}).items():
            if all(str(row.get(k)) == str(v) for k, v in eq.items()):
                yield rid, row

    def _within(row, within_months, date_field):
        if within_months is None:
            return True
        d = row.get(date_field)
        if not d:
            return False
        m = MONTHS(str(d)[:10], NOW)
        return 0 <= m < within_months

    def SUM(table, field, within_months=None, date_field="event_date", **eq):
        eq = dict(eq); eq[holding_pk] = HID
        s = 0.0
        for rid, row in _rows(table, eq):
            if _within(row, within_months, date_field):
                touched.add((table, rid)); s += float(row.get(field) or 0)
        return round(s, 2)

    def COUNT(table, within_months=None, date_field="event_date", **eq):
        eq = dict(eq); eq[holding_pk] = HID
        n = 0
        for rid, row in _rows(table, eq):
            if _within(row, within_months, date_field):
                touched.add((table, rid)); n += 1
        return n

    def MAX(table, field, **eq):
        eq = dict(eq); eq[holding_pk] = HID
        vals = []
        for rid, row in _rows(table, eq):
            touched.add((table, rid)); vals.append(float(row.get(field) or 0))
        return max(vals) if vals else 0.0

    def LATEST(table, field, date_field="event_date", **eq):
        eq = dict(eq); eq[holding_pk] = HID
        best = None
        for rid, row in _rows(table, eq):
            touched.add((table, rid))
            key = str(row.get(date_field))
            if best is None or key > best[0]:
                best = (key, row.get(field))
        return best[1] if best else None

    def _cross(cat, eq):
        c = cross.get(cat)
        if not c:
            return []
        ct = c["binding"]["holding_table"]
        eq = dict(eq); eq["customer_id"] = CUST
        return [row for rid, row in (initial.get(ct) or {}).items()
                if all(str(row.get(k)) == str(v) for k, v in eq.items())]

    def EXISTS(cat, **eq):
        return len(_cross(cat, eq)) > 0

    def CPARAM(cat, param, **eq):
        hs = _cross(cat, eq)
        if not hs:
            return None
        vi = {v["name"]: (v.get("parameters") or {}) for v in (cross[cat].get("variants") or [])}
        return vi.get(hs[0].get("variant_name"), {}).get(param)

    def CFIELD(cat, field, **eq):
        hs = _cross(cat, eq)
        return hs[0].get(field) if hs else None

    # ---- another category's EVENT HISTORY, scoped to this customer ------------------- #
    # A row belongs to the customer when it carries customer_id = CUST, or when it points at
    # one of the customer's holdings of that category through that holding table's primary key.
    def _xrows(cat, table, eq):
        c = cross.get(cat)
        if not c:
            return
        ct = c["binding"]["holding_table"]
        cpk = next(iter(db_schema.get(ct) or {}), None)
        owned = {rid for rid, row in (initial.get(ct) or {}).items()
                 if str(row.get("customer_id")) == str(CUST)}
        for rid, row in (initial.get(table) or {}).items():
            if not all(str(row.get(k)) == str(v) for k, v in eq.items()):
                continue
            mine = str(row.get("customer_id")) == str(CUST) or (cpk and str(row.get(cpk)) in owned)
            if mine:
                xtouched.setdefault(cat, set()).add((table, rid))
                yield rid, row

    def XSUM(cat, table, field, within_months=None, date_field="event_date", **eq):
        s = 0.0
        for rid, row in _xrows(cat, table, eq):
            if _within(row, within_months, date_field):
                s += float(row.get(field) or 0)
        return round(s, 2)

    def XCOUNT(cat, table, within_months=None, date_field="event_date", **eq):
        n = 0
        for rid, row in _xrows(cat, table, eq):
            if _within(row, within_months, date_field):
                n += 1
        return n

    def XMAX(cat, table, field, **eq):
        vals = [float(row.get(field) or 0) for rid, row in _xrows(cat, table, eq)]
        return max(vals) if vals else 0.0

    def XLATEST(cat, table, field, date_field="event_date", **eq):
        best = None
        for rid, row in _xrows(cat, table, eq):
            key = str(row.get(date_field))
            if best is None or key > best[0]:
                best = (key, row.get(field))
        return best[1] if best else None

    env = {
        "NOW": NOW, "HID": HID, "CUST": CUST,
        "F": lambda f: H.get(f), "P": lambda p: vindex.get(H.get("variant_name"), {}).get(p),
        "SUM": SUM, "COUNT": COUNT, "MAX": MAX, "LATEST": LATEST,
        "EXISTS": EXISTS, "CPARAM": CPARAM, "CFIELD": CFIELD,
        "XSUM": XSUM, "XCOUNT": XCOUNT, "XMAX": XMAX, "XLATEST": XLATEST,
        "MONTHS": MONTHS, "DAYS": DAYS,
        "MX": max, "MN": min, "RND": lambda x, n=2: round(float(x), n), "ABS": abs,
        "min": min, "max": max, "round": round, "abs": abs, "float": float, "int": int,
        "True": True, "False": False, "None": None,
    }
    env["__xtouched__"] = xtouched
    return env, touched


def eval_compute(compute, env0, params=None):
    """Evaluate the ordered bindings; return (result, binding_count, branch_count)."""
    env = dict(env0)
    env["K"] = lambda k: (params or {}).get(k)
    known = set(env.keys())
    bindings = 0
    branches = 0
    for binding in compute:
        if not isinstance(binding, dict) or len(binding) != 1:
            raise ValueError("each compute item must be a single {name: expr} mapping")
        (name, expr), = binding.items()
        tree = ast.parse(str(expr), mode="eval")
        n_if, n_cross, n_fork = validate_ast(tree, known | _FUNCS | _CONSTS)
        branches += n_if + n_cross + n_fork
        env[name] = eval(compile(tree, "<compute>", "eval"), {"__builtins__": {}}, env)
        known.add(name)
        bindings += 1
    if "result" not in env:
        raise ValueError("compute has no final `result` binding")
    return env["result"], bindings, branches


def substitute(compute, baseline):
    """compute with the bindings named in `baseline` replaced by their baseline expressions (order kept)."""
    out = []
    for binding in compute:
        (name, expr), = binding.items()
        out.append({name: baseline[name] if name in baseline else expr})
    return out


def _bool_sources(test):
    """The distinct evidence sources a tier test combines by `and` or `or` — a name or a primitive
    read that differ — or the empty set when the test is neither an `A and B` nor an `A or B`."""
    if not (isinstance(test, ast.BoolOp) and isinstance(test.op, (ast.And, ast.Or))):
        return set()
    srcs = set()
    for opnd in test.values:
        for sub in ast.walk(opnd):
            if isinstance(sub, ast.Name) and sub.id not in _FUNCS and sub.id not in _CONSTS:
                srcs.add(("name", sub.id))
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                    and sub.func.id in (_EVIDENCE_FUNCS | {"F", "P", "K"})):
                first = sub.args[0].value if sub.args and isinstance(sub.args[0], ast.Constant) else None
                srcs.add(("call", sub.func.id, first))
    return srcs


def ladder_shape(pol, bindings):
    """(n_forks, n_compound) over the bindings of one factor: how many ternary forks its compute
    carries (each ladder tier beyond the fall-through needs one), and how many of those forks
    test a combination (and / or) of >= 2 predicates over DISTINCT evidence ("the account's tier
    AND a count over a window"). The factor is MULTI-SOURCE when every fork is such a combination."""
    n_if, n_compound = 0, 0
    for b in pol.get("compute") or []:
        if not isinstance(b, dict) or len(b) != 1:
            continue
        (name, expr), = b.items()
        if name not in bindings:
            continue
        try:
            tree = ast.parse(str(expr), mode="eval")
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.IfExp):
                n_if += 1
                if len(_bool_sources(node.test)) >= 2:
                    n_compound += 1
    return n_if, n_compound


def multi_source(pol, f):
    """True when every tier of this factor's ladder beyond the fall-through combines >= 2 conditions
    over distinct evidence by and / or (every fork of its bindings is an `A and B` or an `A or B`)."""
    n_forks, n_compound = ladder_shape(pol, set(f.get("bindings") or []))
    return n_forks > 0 and n_compound == n_forks


def factor_shape_errors(pol, where):
    """Structural legality of a policy's `factors` block. Returns (errors, factors)."""
    errs = []
    compute = pol.get("compute") or []
    binding_names = [str(next(iter(b))) for b in compute if isinstance(b, dict) and len(b) == 1]
    factors = pol.get("factors")
    if not isinstance(factors, list) or not factors:
        return [f"{where}: declares no `factors` — every computation rests on {MIN_FACTORS_PER_COMP} to {MAX_FACTORS_PER_COMP} "
                "declared factors (a rule with a ladder deciding one input of the result); "
                "a line of compute is not a factor"], []
    seen_ids, owned = set(), {}
    for i, f in enumerate(factors):
        fw = f"{where}.factors[{i}]"
        if not isinstance(f, dict):
            errs.append(f"{fw}: must be a mapping"); continue
        fid = f.get("id")
        if not isinstance(fid, str) or not fid.strip():
            errs.append(f"{fw}: missing id")
        elif fid in seen_ids:
            errs.append(f"{fw}: duplicate factor id '{fid}'")
        seen_ids.add(fid)
        bl = f.get("bindings")
        if not isinstance(bl, list) or not bl:
            errs.append(f"{fw}: `bindings` must be a non-empty list of compute binding names"); bl = []
        for b in bl:
            if b not in binding_names:
                errs.append(f"{fw}: binding '{b}' is not a compute binding")
            elif b in owned:
                errs.append(f"{fw}: binding '{b}' already belongs to factor '{owned[b]}' (one factor per binding)")
            else:
                owned[b] = fid
        dec = f.get("decides")
        if not dec:
            errs.append(f"{fw}: missing `decides` (the input of the result this factor decides)")
        elif dec not in bl:
            errs.append(f"{fw}: `decides` '{dec}' must be one of its own bindings")
        elif dec == "result":
            errs.append(f"{fw}: a factor decides an INPUT of the result, never `result` itself")
        effect = f.get("effect")
        if effect not in _EFFECTS:
            errs.append(f"{fw}: `effect` must be one of {sorted(_EFFECTS)} — parameter (the tier selects a value "
                        "that enters a fixed formula) or method (the tier selects how the quantity is computed)")
        tier_key = "method" if effect == "method" else "value"
        ladder = f.get("ladder")
        if not isinstance(ladder, list) or len(ladder) < MIN_LADDER_TIERS:
            errs.append(f"{fw}: `ladder` needs >= {MIN_LADDER_TIERS} tiers (each with `when` and `{tier_key}`)")
        else:
            for j, t in enumerate(ladder):
                if not isinstance(t, dict) or not str(t.get("when") or "").strip():
                    errs.append(f"{fw}.ladder[{j}]: each tier needs a `when` (the trigger condition, in business words)")
                elif tier_key not in t or not str(t.get(tier_key) or "").strip():
                    errs.append(f"{fw}.ladder[{j}]: a {effect or 'parameter'} factor's tier needs `{tier_key}` "
                                + ("(the computation rule this tier applies: the operation, base, rounding, window "
                                   "or order)" if effect == "method" else "(the value or parameter this tier selects)"))
            if bl:
                n_forks, _ = ladder_shape(pol, set(bl))
                if n_forks + 1 < len(ladder):
                    errs.append(f"{fw}: ladder declares {len(ladder)} tiers but its bindings fork only {n_forks} "
                                "time(s) — every tier beyond the fall-through is a branch in compute")
        base = f.get("baseline")
        if not isinstance(base, dict) or not base:
            errs.append(f"{fw}: `baseline` must map >= 1 of this factor's bindings (its `decides` at least) to the "
                        "expression that binding takes under the standard method / default value — what the "
                        "baseline document states and what an agent who never finds this factor falls back to")
        else:
            if dec and dec not in base:
                errs.append(f"{fw}: `baseline` must include the `decides` binding '{dec}'")
            for k, v in base.items():
                if k not in bl:
                    errs.append(f"{fw}: baseline names '{k}', which is not one of this factor's bindings")
                try:
                    ast.parse(str(v), mode="eval")
                except SyntaxError as e:
                    errs.append(f"{fw}: baseline['{k}'] does not parse: {e}")
        # evidence: the tier must rest on records, never on a stamp alone
        calls = set()
        for b in compute:
            (name, expr), = b.items()
            if name in bl:
                calls |= {fn for fn, _ in expr_calls(expr)}
        if not (calls & _EVIDENCE_FUNCS):
            errs.append(f"{fw}: none of its bindings reads history, a date span or another category "
                        f"({sorted(_EVIDENCE_FUNCS)}) — a factor's tier is established from records, "
                        "never read off a field that names the outcome")
        xd = f.get("cross_difficulty")
        if xd:
            cats = set()
            for b in compute:
                (name, expr), = b.items()
                if name in bl:
                    cats |= {arg for fn, arg in expr_calls(expr) if fn in _CALL_ONLY}
            if xd not in cats:
                errs.append(f"{fw}: cross_difficulty='{xd}' but none of its bindings reads category "
                            f"'{xd}' through EXISTS/CPARAM/CFIELD/XSUM/XCOUNT/XMAX/XLATEST")
    return errs, [f for f in factors if isinstance(f, dict)]


# ---- task-side plumbing --------------------------------------------------- #
def gold_arg(actions, step, arg):
    a = actions[step]
    tool = a.get("tool") or a.get("name")
    args = a.get("arguments") or {}
    if tool in _CALL_WRAPPERS:
        inner = args.get("arguments") or {}
        if isinstance(inner, str):
            inner = json.loads(inner) if inner else {}
        return inner.get(arg)
    return args.get(arg)


def near(a, b, tol=1e-6):
    try:
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return str(a) == str(b)


def load_yaml(p):
    with open(p) as f:
        return yaml.safe_load(f)


def _find_repo_root(start):
    p = os.path.abspath(start)
    while p != "/":
        if os.path.isdir(os.path.join(p, "erlbench")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def _import(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    pos, task_selector = split_task_flag(sys.argv[1:])
    if len(pos) < 1:
        print("usage: check_compute.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    target = pos[0].rstrip("/")
    task_mode = task_selector is not None
    diff_dir = target
    # locate scenario root (holds blueprint/)
    p = os.path.abspath(target)
    scen = None
    while p != "/":
        if os.path.isdir(os.path.join(p, "blueprint")):
            scen = p; break
        p = os.path.dirname(p)
    if not scen:
        raise SystemExit(f"cannot find scenario root (blueprint/) above {target}")
    bp = os.path.join(scen, "blueprint")
    db_schema = json.load(open(os.path.join(bp, "db_schema.json")))

    # Real tools, for replaying gold writes to the handling-time state (GT's evaluation state).
    sys.path.insert(0, _find_repo_root(target))
    from erlbench.tools import collect_specs, ToolContext
    from erlbench.db import DB
    from erlbench.determinism import Clock
    from erlbench.scoring import _resolve
    specs = {}
    for s in collect_specs(_import(os.path.join(bp, "share_tools.py"), "_cc_share"), "share"):
        specs[s.name] = s
    tt_path = os.path.join(diff_dir, "task_tools.py")
    if os.path.exists(tt_path):
        for s in collect_specs(_import(tt_path, "_cc_task"), "task"):
            specs[s.name] = s

    ext_files = [f for f in glob.glob(os.path.join(diff_dir, "*.extended.yaml"))]
    if not ext_files:
        raise SystemExit(f"no <category>.extended.yaml under {diff_dir}")
    extended = load_yaml(ext_files[0])
    primary = extended
    policies = {p2["id"]: p2 for p2 in (extended.get("extended_policies") or [])}
    # cross-category charters from blueprint/products/
    cross = {}
    for f in glob.glob(os.path.join(bp, "products", "*.yaml")):
        d = load_yaml(f)
        if isinstance(d, dict) and d.get("category"):
            cross[d["category"]] = d

    task_paths = select_task_paths(diff_dir, task_selector)
    if not task_paths:
        raise SystemExit(f"no task json under {diff_dir}/tasks/")

    def state_before(initial, frozen_time, actions, step):
        """The world at handling time: initial_state with every gold WRITE before `step` landed.
        This is the state GT is defined over — the agent standing at step k has already executed
        steps 0..k-1, so a formula evaluated anywhere else is a formula about a different world."""
        db = DB.seeded(deepcopy(initial))
        clock = Clock.from_stamp(frozen_time)
        for a in actions[:max(0, step)]:
            tool, args = _resolve(a)
            spec = specs.get(tool) if tool else None
            if spec is None or spec.rw != "write":
                continue
            try:
                spec.func(ToolContext(db, clock, db_schema, writable=True), **spec.coerce(args))
            except Exception:  # noqa: BLE001 — errored writes changed nothing live; replay gate owns them
                pass
        return db.tables

    def state_before_skipping(initial, frozen_time, actions, step, skip):
        """Same handling-time state, but pretending the gold calls in `skip` never happened.

        Used to gate PREREQUISITE load-bearingness: an edge declared `value_input` claims that
        solving the depended-on problem CHANGES a compute binding of the dependent problem.  If
        the dependent problem's result is identical with and without it, the edge is decorative
        and the problem tree is a declaration rather than a difficulty."""
        db = DB.seeded(deepcopy(initial))
        clock = Clock.from_stamp(frozen_time)
        for i, a in enumerate(actions[:max(0, step)]):
            if i in skip:
                continue
            tool, args = _resolve(a)
            spec = specs.get(tool) if tool else None
            if spec is None or spec.rw != "write":
                continue
            try:
                spec.func(ToolContext(db, clock, db_schema, writable=True), **spec.coerce(args))
            except Exception:  # noqa: BLE001
                pass
        return db.tables

    def action_indices_for_tools(actions, tools):
        """Gold call indices that invoke any of `tools` (unwrapping unlock/call meta tools)."""
        out = set()
        for i, a in enumerate(actions):
            tool = a.get("tool") or a.get("name")
            args = a.get("arguments") or {}
            inner_name = args.get("tool_name") if isinstance(args, dict) else None
            if tool in _CALL_WRAPPERS:
                if inner_name in tools:
                    out.add(i)
            elif tool in tools:
                out.add(i)
        return out

    def problem_tools(pid):
        """Every task tool that writes on behalf of problem `pid` (an extended policy)."""
        pol = policies.get(pid)
        if pol and pol.get("target_tool"):
            return {pol["target_tool"]}
        return set()

    cross_cat_policies = sum(1 for p2 in policies.values() if policy_has_cross_factor(p2))
    mode_label = f", selected_task={task_selector}" if task_mode else ""
    print(f"🔎 COMPUTE gate  ({len(task_paths)} tasks{mode_label}, {len(policies)} extended_policies, "
          f"{cross_cat_policies} cross-category)")
    print(f"{'task':28} {'comps':>5} {'fact':>4} {'xfac':>4} {'hist':>4} {'brch':>4} {'step':>4} {'match':>6}")

    fails, per_task = [], []
    for tp in task_paths:
        tid = os.path.basename(tp)
        task = json.loads(open(tp).read())
        actions = task.get("evaluation_criteria") or []
        comps = task.get("computations") or []
        initial = task.get("initial_state") or {}
        ft = task.get("frozen_time")
        t_factors = t_xfactors = t_hist = t_branch = 0
        t_ok = True
        if not comps:
            fails.append(f"{tid}: no computations (every task needs >=1 formula-forced write)")
            t_ok = False
        for c in comps:
            pid = c.get("policy_id")
            pol = policies.get(pid)
            if not pol:
                fails.append(f"{tid}: computations references unknown policy_id {pid}"); t_ok = False; continue
            try:
                # GT is defined over the handling-time state: initial_state ⊕ all earlier gold writes.
                world = state_before(initial, ft, actions, int(c.get("step") or 0))
                env, touched = build_env(world, ft, primary, cross, db_schema, c.get("target_holding_id"))
                result, n_bind, branches = eval_compute(pol.get("compute") or [], env, pol.get("params"))
                xtouched = env["__xtouched__"]
            except Exception as e:  # noqa: BLE001
                fails.append(f"{tid}: compute {pid} raised: {e}"); t_ok = False; continue
            t_hist += len(touched); t_branch += branches
            exp = c.get("expected")
            g = gold_arg(actions, c.get("step"), c.get("arg"))
            if not near(result, exp):
                fails.append(f"{tid}: {pid} recompute={result} != declared expected={exp}"); t_ok = False
            if not near(result, g):
                fails.append(f"{tid}: {pid} recompute={result} != gold arg[{c.get('step')}].{c.get('arg')}={g}"); t_ok = False

            # ---- FACTORS: declared rules with ladders, each proved load-bearing on THIS world ----
            shape_errs, factors = factor_shape_errors(pol, f"{tid}: {pid}")
            for e in shape_errs:
                fails.append(e); t_ok = False
            declared_sens = {}
            for s in (c.get("factor_sensitivity") or []):
                if isinstance(s, dict) and s.get("factor"):
                    declared_sens[s["factor"]] = s
            n_cross_factors = 0
            all_baseline = {}
            for f in factors:
                fid = f.get("id") or "?"
                base = f.get("baseline") if isinstance(f.get("baseline"), dict) else {}
                if not base or not f.get("bindings"):
                    continue
                all_baseline.update(base)
                try:
                    env_n, _ = build_env(world, ft, primary, cross, db_schema, c.get("target_holding_id"))
                    r_base, _, _ = eval_compute(substitute(pol.get("compute") or [], base), env_n, pol.get("params"))
                except Exception as e:  # noqa: BLE001
                    fails.append(f"{tid}: {pid} factor '{fid}': baseline substitution raised ({e}) — the baseline "
                                 "expression must evaluate on the same world"); t_ok = False
                    continue
                if near(r_base, result):
                    fails.append(f"{tid}: {pid} factor '{fid}' is DECORATIVE on this world: substituting its "
                                 f"baseline {base} leaves result={result} unchanged — this customer sits on the "
                                 "factor's fall-through tier, so an agent that never finds the factor document "
                                 "scores anyway; move the world onto a tier where the factor changes the number"); t_ok = False
                sens = declared_sens.get(fid)
                if sens is None:
                    fails.append(f"{tid}: {pid} computations[].factor_sensitivity has no entry for factor '{fid}' "
                                 "(record tier_taken and baseline_result per factor)"); t_ok = False
                elif not near(sens.get("baseline_result"), r_base):
                    fails.append(f"{tid}: {pid} factor '{fid}': declared baseline_result={sens.get('baseline_result')} "
                                 f"!= recomputed {r_base}"); t_ok = False
                xd = f.get("cross_difficulty")
                if xd:
                    n_cross_factors += 1
                    if xd not in cross or xd == primary.get("category"):
                        fails.append(f"{tid}: {pid} factor '{fid}': cross_difficulty '{xd}' is not another "
                                     "category of this scenario"); t_ok = False
                    else:
                        ct = cross[xd]["binding"]["holding_table"]
                        cust = env.get("CUST")
                        has_holding = any(str(r.get("customer_id")) == str(cust)
                                          for r in (world.get(ct) or {}).values())
                        uses_xhist = False
                        for b in (pol.get("compute") or []):
                            (name, expr), = b.items()
                            if name in (f.get("bindings") or []):
                                uses_xhist |= any(fn in _XHIST and arg == xd for fn, arg in expr_calls(expr))
                        if not has_holding:
                            fails.append(f"{tid}: {pid} factor '{fid}': cross_difficulty '{xd}' but this task's "
                                         "world seeds no holding of that category for the customer — the "
                                         "evidence the tier rests on must be laid down in initial_state"); t_ok = False
                        if uses_xhist and not xtouched.get(xd):
                            fails.append(f"{tid}: {pid} factor '{fid}': reads '{xd}' event history but the "
                                         "world seeds no matching rows for this customer — seed the other "
                                         "product's ledger the tier is decided from"); t_ok = False
            # ---- the FALL-BACK: every factor at its baseline = the computation document alone ----
            if factors and all_baseline:
                try:
                    env_b, _ = build_env(world, ft, primary, cross, db_schema, c.get("target_holding_id"))
                    r_all, _, _ = eval_compute(substitute(pol.get("compute") or [], all_baseline), env_b, pol.get("params"))
                except Exception as e:  # noqa: BLE001
                    fails.append(f"{tid}: {pid} the baseline (every factor substituted) does not evaluate ({e}) — the "
                                 "standard method must be a complete computation on its own, or the fall-back is "
                                 "an error rather than a wrong number"); t_ok = False
                    r_all = None
                if r_all is not None:
                    if near(r_all, result):
                        fails.append(f"{tid}: {pid} the baseline result {r_all} equals gold — an agent that reads only "
                                     "the computation document scores; the factors must move the number"); t_ok = False
                    if "baseline_result" not in c:
                        fails.append(f"{tid}: {pid} computations[] lacks baseline_result (the figure the standard "
                                     "method gives on this world with every factor at its fall-through)"); t_ok = False
                    elif not near(c.get("baseline_result"), r_all):
                        fails.append(f"{tid}: {pid} declared baseline_result={c.get('baseline_result')} != "
                                     f"recomputed {r_all}"); t_ok = False
            n_factors = len(factors)
            t_factors += n_factors; t_xfactors += n_cross_factors
            n_param = sum(1 for f in factors if f.get("effect") == "parameter")
            n_method = sum(1 for f in factors if f.get("effect") == "method")
            n_multi = sum(1 for f in factors if multi_source(pol, f))
            if factors and not (MIN_FACTORS_PER_COMP <= n_factors <= MAX_FACTORS_PER_COMP):
                fails.append(f"{tid}: {pid} declares {n_factors} factors (outside {MIN_FACTORS_PER_COMP}..{MAX_FACTORS_PER_COMP}) — "
                             "every computation rests on 4 to 6 load-bearing rules"); t_ok = False
            if factors and n_param < MIN_PARAM_FACTORS_PER_COMP:
                fails.append(f"{tid}: {pid} has only {n_param} effect=parameter factors (< {MIN_PARAM_FACTORS_PER_COMP})"); t_ok = False
            if factors and n_method < MIN_METHOD_FACTORS_PER_COMP:
                fails.append(f"{tid}: {pid} has only {n_method} effect=method factors (< {MIN_METHOD_FACTORS_PER_COMP}) "
                             "— at least two factors must change HOW a quantity is computed (operation, base, "
                             "rounding, window, order, cap moment, multiplier), not only which number enters it"); t_ok = False
            if factors and n_multi < MIN_MULTISOURCE_FACTORS_PER_COMP:
                fails.append(f"{tid}: {pid} has only {n_multi} multi-source factors (< {MIN_MULTISOURCE_FACTORS_PER_COMP}) "
                             "— every tier of such a factor beyond the fall-through combines two conditions over "
                             "distinct evidence by and / or"); t_ok = False
            if factors and n_cross_factors < MIN_CROSS_FACTORS_PER_COMP:
                fails.append(f"{tid}: {pid} has only {n_cross_factors} cross-difficulty factors "
                             f"(< {MIN_CROSS_FACTORS_PER_COMP}) — at least two factors must decide their tier "
                             "from the customer's holdings or ledger in ANOTHER difficulty"); t_ok = False
            for fid in declared_sens:
                if fid not in {f.get("id") for f in factors}:
                    fails.append(f"{tid}: {pid} factor_sensitivity names unknown factor '{fid}'"); t_ok = False

            # ---- floor tests kept from before: whole-input load-bearingness --------------------
            # LOAD-BEARING cross-category: if a cross-category holding is seeded for this
            # customer, forcing cross-category off MUST change the result — else that holding
            # is decoration (a fork that changes nothing), which the difficulty forbids.
            hrow = None
            for _t, _rows in initial.items():
                if c.get("target_holding_id") in (_rows or {}):
                    hrow = _rows[c["target_holding_id"]]; break
            cust = (hrow or {}).get("customer_id")
            declared_cats = {d.get("category") for d in (pol.get("cross_category") or [])
                             if isinstance(d, dict) and d.get("category")}
            cross_tables = [ct["binding"]["holding_table"] for cname, ct in cross.items()
                            if cname in declared_cats and ct.get("category") != primary.get("category")]
            has_cross = any(str(r.get("customer_id")) == str(cust)
                            for t in cross_tables for r in (initial.get(t) or {}).values())
            if declared_cats and not has_cross:
                fails.append(f"{tid}: {pid} declares a cross-category dependency on "
                             f"{sorted(declared_cats)}, but this task's world seeds no such holding "
                             "for the customer — the factor changes nothing here, so this task does "
                             "not exercise it. Seed the cross-category holding, or claim a computed "
                             "quantity this world genuinely makes depend on the other category."); t_ok = False
            elif declared_cats:
                env2, _ = build_env(world, ft, primary, cross, db_schema, c.get("target_holding_id"))
                env2["EXISTS"] = lambda *a, **k: False
                env2["CPARAM"] = lambda *a, **k: None
                env2["CFIELD"] = lambda *a, **k: None
                env2["XSUM"] = lambda *a, **k: 0.0
                env2["XCOUNT"] = lambda *a, **k: 0
                env2["XMAX"] = lambda *a, **k: 0.0
                env2["XLATEST"] = lambda *a, **k: None
                try:
                    naive, _, _ = eval_compute(pol.get("compute") or [], env2, pol.get("params"))
                    if near(naive, result):
                        fails.append(f"{tid}: {pid} cross-category reads are NOT load-bearing as a whole "
                                     f"(result {result} unchanged when every cross-category read is forced off) — "
                                     "the seeded cross-category holding is decoration, not a trap"); t_ok = False
                except Exception:  # noqa: BLE001 — a raise without the reads is itself a change
                    pass
            # HISTORY load-bearing: if this computation aggregates event history, zeroing the
            # aggregates must change the result — else the "reconciliation" is decorative.
            if len(touched) > 0:
                env3, _ = build_env(world, ft, primary, cross, db_schema, c.get("target_holding_id"))
                env3["SUM"] = lambda *a, **k: 0.0
                env3["COUNT"] = lambda *a, **k: 0
                env3["MAX"] = lambda *a, **k: 0.0
                try:
                    naive_h, _, _ = eval_compute(pol.get("compute") or [], env3, pol.get("params"))
                    if near(naive_h, result):
                        fails.append(f"{tid}: {pid} history is NOT load-bearing (result {result} unchanged "
                                     "when the history aggregates are zeroed) — the reconciliation is decorative"); t_ok = False
                except Exception:  # noqa: BLE001
                    pass  # zeroing broke the compute -> history is clearly load-bearing
        # ---- PREREQUISITE: topological write order + value_input load-bearingness ----
        pc = task.get("prerequisite_closure") or {}
        pc_edges = [e for e in (pc.get("edges") or []) if isinstance(e, dict)]
        for ei, e in enumerate(pc_edges):
            frm, to = e.get("from"), e.get("to")
            frm_tools, to_tools = problem_tools(frm), problem_tools(to)
            frm_idx = action_indices_for_tools(actions, frm_tools) if frm_tools else set()
            to_idx = action_indices_for_tools(actions, to_tools) if to_tools else set()
            # 1) every write of the depended-on problem precedes every write of the dependent one
            if frm_idx and to_idx and max(to_idx) >= min(frm_idx):
                fails.append(f"{tid}: prerequisite edges[{ei}] '{frm}' <- '{to}': gold writes are not in "
                             f"topological order (last '{to}' call at index {max(to_idx)} is not before "
                             f"first '{frm}' call at index {min(frm_idx)}) — each problem must be handled "
                             "only after all of its prerequisites are resolved")
                t_ok = False
            # 2) a value_input edge must actually change the dependent problem's computed value
            if e.get("kind") == "value_input" and to_idx:
                changed = False
                for c in comps:
                    if c.get("policy_id") != frm and frm not in (c.get("policy_id") or ""):
                        continue
                    pol = policies.get(c.get("policy_id"))
                    if not pol:
                        continue
                    try:
                        step = int(c.get("step") or 0)
                        w_with = state_before(initial, ft, actions, step)
                        w_without = state_before_skipping(initial, ft, actions, step, to_idx)
                        env_a, _ = build_env(w_with, ft, primary, cross, db_schema, c.get("target_holding_id"))
                        env_b, _ = build_env(w_without, ft, primary, cross, db_schema, c.get("target_holding_id"))
                        r_a, *_ = eval_compute(pol.get("compute") or [], env_a, pol.get("params"))
                        r_b, *_ = eval_compute(pol.get("compute") or [], env_b, pol.get("params"))
                    except Exception:  # noqa: BLE001 — a raise without the prerequisite is itself a change
                        changed = True
                        continue
                    if not near(r_a, r_b):
                        changed = True
                if not changed:
                    fails.append(f"{tid}: prerequisite edges[{ei}] declares kind=value_input, but skipping "
                                 f"'{to}' leaves every computed value of '{frm}' unchanged — the edge is "
                                 "decorative; make it load-bearing or redesign the tree "
                                 "(state_gate load-bearingness is not machine-checkable here and stays "
                                 "with the policy audit)")
                    t_ok = False

        n_steps = sum(1 for a in actions if (a.get("tool") or a.get("name")))
        n_comps = max(1, len(comps))
        per_task.append({"factors": t_factors / n_comps, "history_rows": t_hist, "branches": t_branch, "steps": n_steps})
        print(f"{tid:28} {len(comps):>5} {t_factors:>4} {t_xfactors:>4} {t_hist:>4} {t_branch:>4} {n_steps:>4} {str(t_ok):>6}")

    n = len(per_task)
    if task_mode:
        # Suite breadth/depth thresholds are intentionally deferred: a single task
        # gate must be usable while later tasks are still being authored.  Per-task
        # formula, handling-time, load-bearing and factor checks above remain hard.
        print("\nper-task mode: suite means/history/branch maxima deferred to final difficulty run")
    else:
        means = {k: sum(t[k] for t in per_task) / n for k in MEANS} if n else {k: 0 for k in MEANS}
        hist_max = max((t["history_rows"] for t in per_task), default=0)
        branch_max = max((t["branches"] for t in per_task), default=0)
        print("\nsuite means:  " + "   ".join(f"{k}={means[k]:.2f}(>= {MEANS[k]})" for k in MEANS))
        print(f"suite depth:  history_rows_max={hist_max}(>= {SUITE_MAX_HISTORY})   "
              f"branches_max={branch_max}(>= {SUITE_MAX_BRANCHES})")
        for k, thr in MEANS.items():
            if means[k] < thr:
                fails.append(f"difficulty mean {k}={means[k]:.2f} < {thr}")
        if hist_max < SUITE_MAX_HISTORY:
            fails.append(f"suite history_rows_max={hist_max} < {SUITE_MAX_HISTORY} — "
                         "add a heavy history-reconciliation task")
        if branch_max < SUITE_MAX_BRANCHES:
            fails.append(f"suite branches_max={branch_max} < {SUITE_MAX_BRANCHES} — "
                         "add a heavy conditional-fork task")
    if cross_cat_policies != len(policies):
        fails.append(f"only {cross_cat_policies}/{len(policies)} extended_policies read a cross-category "
                     "VALUE via CPARAM/CFIELD/XSUM/XCOUNT/XMAX/XLATEST (EVERY policy must; a bare EXISTS can "
                     "only switch the whole result on or off, which is how a base-pinned amount gets silently zeroed)")

    if fails:
        print("\n  [FAIL]")
        for f in fails[:60]:
            print("   -", f)
        print("COMPUTE NOT OK")
        sys.exit(1)
    print("\nCOMPUTE OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
