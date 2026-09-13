"""COMPUTE gate (the core): machine-recompute every task's computed gold argument
from its `extended_policy.compute` over the world AS IT STANDS AT THAT WRITE'S HANDLING
TIME — the task's initial_state with every earlier gold write already landed — and assert
it EQUALS the declared `expected` AND the gold argument. Then gate suite-level difficulty means.

WHY. This skill puts task difficulty in a multi-factor computation over reconciled history, not
in tool selection. That is only real if the computed value is machine-recomputable and the
gold is forced by it. This script evaluates each `compute` (an ordered list of
{var: restricted-expression} bindings ending in `result`) in a sandbox whose primitives read
ONLY the world state, then checks result == the task's declared `expected` == the gold
argument at the named evaluation_criteria step. A mismatch is a hard failure (the difficulty is
fake or the gold is hand-picked).

WHY THE HANDLING-TIME STATE (this IS the definition of GT). The rollout world is stateful
and the agent works it like a real seat: read, write, read again. By the time the agent must
produce the parameter at evaluation_criteria step k, every earlier write of the same SOP has
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
SUM/COUNT/MAX/LATEST over event history (auto-scoped to the holding, optional within_months),
EXISTS/CPARAM/CFIELD over cross-category holdings, MONTHS/DAYS, MX/MN/RND/ABS and arithmetic.

Difficulty thresholds (check_extended enforces a configurable M-task suite):
  >= 1 key computation with >= 6 factors
  >= 8 history rows reconciled
  >= 5 if-else/fork branches
  >= 4 evaluation_criteria actions
plus: EVERY extended_policy reads a cross-category VALUE (CPARAM/CFIELD, not a bare EXISTS)
and that read is exercised by the task world, and >= 1 formula-forced write.

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
MEANS = {"factors": 5.0, "branches": 4.0, "steps": 4.0}
MIN_FACTORS_PER_COMP = 4           # each computed value must be a genuine multi-step computation
KEY_FACTORS = 6                    # Step 1/5: every task needs >=1 key computation with >=6 factors
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
_FUNCS = {"F", "P", "K", "SUM", "COUNT", "MAX", "LATEST", "EXISTS", "CPARAM", "CFIELD",
          "MONTHS", "DAYS", "MX", "MN", "RND", "ABS", "min", "max", "round", "abs", "float", "int"}
_CONSTS = {"NOW", "HID", "CUST", "True", "False", "None"}
_CALL_ONLY = {"EXISTS", "CPARAM", "CFIELD"}   # cross-category read primitives
_CROSS_QUANT = {"CPARAM", "CFIELD"}          # ... of which these return a VALUE, not a predicate


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

    The compute must read a cross-category VALUE (CPARAM/CFIELD): only a value can make the
    computed QUANTITY depend on the other category.  EXISTS may accompany it as a condition,
    but on its own it can only switch the whole result on or off — and that shape is how a
    base-pinned amount gets silently zeroed.

    This is a shape check on the compute: it does not evaluate the value it reads, so a tier
    parameter carrying the same value in every tier still passes here.  The load-bearing test
    further down evaluates it against the task world.
    """
    if not policy.get("cross_category"):
        return False
    return bool(policy_cross_calls(policy) & _CROSS_QUANT)


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
    """Sandbox namespace scoped to one target holding; also returns a touch-recorder set."""
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

    env = {
        "NOW": NOW, "HID": HID, "CUST": CUST,
        "F": lambda f: H.get(f), "P": lambda p: vindex.get(H.get("variant_name"), {}).get(p),
        "SUM": SUM, "COUNT": COUNT, "MAX": MAX, "LATEST": LATEST,
        "EXISTS": EXISTS, "CPARAM": CPARAM, "CFIELD": CFIELD,
        "MONTHS": MONTHS, "DAYS": DAYS,
        "MX": max, "MN": min, "RND": lambda x, n=2: round(float(x), n), "ABS": abs,
        "min": min, "max": max, "round": round, "abs": abs, "float": float, "int": int,
        "True": True, "False": False, "None": None,
    }
    return env, touched


def _untriggered_in(tree, env):
    """Count conditional forks that took their INACTIVE branch in this world:
    an `A if C else B` whose test C is falsy, or a cross-category EXISTS/CPARAM/CFIELD
    call that returned falsy. A general policy always has some factor that doesn't fire
    for a given customer — Step 1 requires >=1 such untriggered branch in the key comp."""
    n = 0
    for node in ast.walk(tree):
        try:
            if isinstance(node, ast.IfExp):
                testv = eval(compile(ast.Expression(body=node.test), "<t>", "eval"),
                             {"__builtins__": {}}, env)
                if not testv:
                    n += 1
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id in _CALL_ONLY):
                callv = eval(compile(ast.Expression(body=node), "<c>", "eval"),
                             {"__builtins__": {}}, env)
                if not callv:
                    n += 1
        except Exception:  # noqa: BLE001
            pass
    return n


def eval_compute(compute, env0, params=None):
    """Evaluate the ordered bindings; return (result, factor_count, branch_count, untriggered_count)."""
    env = dict(env0)
    env["K"] = lambda k: (params or {}).get(k)
    known = set(env.keys())
    factors = 0
    branches = 0
    untriggered = 0
    for binding in compute:
        if not isinstance(binding, dict) or len(binding) != 1:
            raise ValueError("each compute item must be a single {name: expr} mapping")
        (name, expr), = binding.items()
        tree = ast.parse(str(expr), mode="eval")
        n_if, n_cross, n_fork = validate_ast(tree, known | _FUNCS | _CONSTS)
        branches += n_if + n_cross + n_fork
        untriggered += _untriggered_in(tree, env)   # test in env BEFORE binding name
        env[name] = eval(compile(tree, "<compute>", "eval"), {"__builtins__": {}}, env)
        known.add(name)
        factors += 1
    if "result" not in env:
        raise ValueError("compute has no final `result` binding")
    return env["result"], factors, branches, untriggered


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
        """Every task tool that writes on behalf of problem `pid` (policy or workflow)."""
        pol = policies.get(pid)
        if pol and pol.get("target_tool"):
            return {pol["target_tool"]}
        for wf in (extended.get("workflows") or []):
            if wf.get("id") == pid:
                return {st.get("tool") for st in (wf.get("steps") or []) if isinstance(st, dict) and st.get("tool")}
        return set()

    cross_cat_policies = sum(1 for p2 in policies.values() if policy_has_cross_factor(p2))
    mode_label = f", selected_task={task_selector}" if task_mode else ""
    print(f"🔎 COMPUTE gate  ({len(task_paths)} tasks{mode_label}, {len(policies)} extended_policies, "
          f"{cross_cat_policies} cross-category)")
    print(f"{'task':28} {'comps':>5} {'fact':>4} {'hist':>4} {'brch':>4} {'step':>4} {'match':>6}")

    fails, per_task = [], []
    for tp in task_paths:
        tid = os.path.basename(tp)
        task = json.loads(open(tp).read())
        actions = task.get("evaluation_criteria") or []
        comps = task.get("computations") or []
        initial = task.get("initial_state") or {}
        ft = task.get("frozen_time")
        t_factors = t_hist = t_branch = 0
        t_key = False              # task has >=1 key computation (factors >= KEY_FACTORS)
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
                result, factors, branches, untrig = eval_compute(pol.get("compute") or [], env, pol.get("params"))
            except Exception as e:  # noqa: BLE001
                fails.append(f"{tid}: compute {pid} raised: {e}"); t_ok = False; continue
            t_factors += factors; t_hist += len(touched); t_branch += branches
            if factors < MIN_FACTORS_PER_COMP:
                fails.append(f"{tid}: {pid} has only {factors} compute factors (< {MIN_FACTORS_PER_COMP}) "
                             "— not a genuine multi-step computation"); t_ok = False
            # A KEY computation is >=6 factors AND must have >=1 untriggered branch
            # (a general policy never fires all its factors for one customer).
            if factors >= KEY_FACTORS:
                t_key = True
                if untrig < 1:
                    fails.append(f"{tid}: {pid} is a key computation ({factors} factors) but every "
                                 "if-else/cross-cat branch FIRES in this world — the formula looks "
                                 "hand-fit to this task (Step 1). Add a factor whose condition is "
                                 "untriggered (0/false) for this customer."); t_ok = False
            exp = c.get("expected")
            g = gold_arg(actions, c.get("step"), c.get("arg"))
            if not near(result, exp):
                fails.append(f"{tid}: {pid} recompute={result} != declared expected={exp}"); t_ok = False
            if not near(result, g):
                fails.append(f"{tid}: {pid} recompute={result} != gold arg[{c.get('step')}].{c.get('arg')}={g}"); t_ok = False
            # LOAD-BEARING cross-category: if a cross-category holding is seeded for this
            # customer, forcing cross-category off MUST change the result — else that holding
            # is decoration (a fork that changes nothing), which the difficulty forbids.
            hrow = None
            for _t, _rows in initial.items():
                if c.get("target_holding_id") in (_rows or {}):
                    hrow = _rows[c["target_holding_id"]]; break
            cust = (hrow or {}).get("customer_id")
            # Scope the search to the categories THIS policy declares: a seeded holding of some
            # unrelated category must not count as exercising this policy's dependency.
            declared_cats = {d.get("category") for d in (pol.get("cross_category") or [])
                             if isinstance(d, dict) and d.get("category")}
            cross_tables = [ct["binding"]["holding_table"] for cname, ct in cross.items()
                            if cname in declared_cats and ct.get("category") != primary.get("category")]
            has_cross = any(str(r.get("customer_id")) == str(cust)
                            for t in cross_tables for r in (initial.get(t) or {}).values())
            if declared_cats and not has_cross:
                # Skipping silently here used to let a declared cross-category dependency pass
                # without ever being exercised: with no such holding in the world the primitives
                # already read absent, so forcing them off proves nothing either way.
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
                naive, _, _, _ = eval_compute(pol.get("compute") or [], env2, pol.get("params"))
                if near(naive, result):
                    fails.append(f"{tid}: {pid} cross-category factor is NOT load-bearing "
                                 f"(result {result} unchanged when cross-category forced off) — "
                                 "the seeded cross-category holding is decoration, not a trap"); t_ok = False
            # HISTORY load-bearing: if this computation aggregates event history, zeroing the
            # aggregates must change the result — else the "reconciliation" is decorative.
            if len(touched) > 0:
                env3, _ = build_env(world, ft, primary, cross, db_schema, c.get("target_holding_id"))
                env3["SUM"] = lambda *a, **k: 0.0
                env3["COUNT"] = lambda *a, **k: 0
                env3["MAX"] = lambda *a, **k: 0.0
                try:
                    naive_h, _, _, _ = eval_compute(pol.get("compute") or [], env3, pol.get("params"))
                    if near(naive_h, result):
                        fails.append(f"{tid}: {pid} history is NOT load-bearing (result {result} unchanged "
                                     "when the history aggregates are zeroed) — the reconciliation is decorative"); t_ok = False
                except Exception:  # noqa: BLE001
                    pass  # zeroing broke the compute -> history is clearly load-bearing
        if comps and not t_key:
            fails.append(f"{tid}: no key computation — every task needs >=1 computation with >={KEY_FACTORS} "
                         "factors (Step 1). Deepen the formula with more real factors."); t_ok = False
        # ---- PREREQUISITE: topological write order + value_input load-bearingness ----
        pc = task.get("prerequisite_closure") or {}
        pc_edges = [e for e in (pc.get("edges") or []) if isinstance(e, dict)]
        comp_steps_by_pid = {}
        for c in comps:
            if c.get("policy_id") is not None:
                comp_steps_by_pid.setdefault(c["policy_id"], []).append(int(c.get("step") or 0))
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
        per_task.append({"factors": t_factors, "history_rows": t_hist, "branches": t_branch, "steps": n_steps})
        print(f"{tid:28} {len(comps):>5} {t_factors:>4} {t_hist:>4} {t_branch:>4} {n_steps:>4} {str(t_ok):>6}")

    n = len(per_task)
    if task_mode:
        # Suite breadth/depth thresholds are intentionally deferred: a single task
        # gate must be usable while later tasks are still being authored.  Per-task
        # formula, handling-time, load-bearing and key-computation checks above remain hard.
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
                     "VALUE via CPARAM/CFIELD (EVERY policy must; a bare EXISTS can only switch the "
                     "whole result on or off, which is how a base-pinned amount gets silently zeroed)")

    if fails:
        print("\n  [FAIL]")
        for f in fails[:40]:
            print("   -", f)
        print("COMPUTE NOT OK")
        sys.exit(1)
    print("\nCOMPUTE OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
