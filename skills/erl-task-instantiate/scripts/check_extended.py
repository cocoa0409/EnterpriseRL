"""EXTENDED gate: verify <category>.extended.yaml is a compatible superset of the
blueprint charter, its extended_policies are well-formed and machine-parseable, every
cross-category read is declared exactly and writes only the primary category, every task's
factors include a multi-source and a cross-difficulty one,
every prerequisite is stated by a prerequisite sentence in the blocked policy's own rule,
every task's gold calls at least one owner=user task tool, and all policies are covered
across the M task scopes.

Checks:
  compat   every base key of blueprint/products/<category>.yaml is present in the
           extended file and DEEP-EQUAL (extended only ADDS extended_policies).
  policy   each extended_policy: id prefixed <category>_ ; subject subset of base declared
           events; base_policy_refs include every base policy governing those refined events
           (and may additionally cite genuine input lineage); computes + target_tool present;
           rule non-empty; compute is a non-empty ordered list ending in `result`, every
           expression parses under the restricted grammar, and every P()/SUM()/EXISTS()/...
           name resolves against the real schema/params/categories; XSUM/XCOUNT/XMAX/XLATEST
           name another category and one of THAT category's event tables.
  baseline each extended_policy declares `baseline`: `rule`, a self-sufficient paragraph (every
           sentence verbatim in the policy's rule) stating the standard method and default values
           — the computation document the KB renders, and the fall-through of every factor — and
           `params`, the quantitative keys that are the defaults.
  factors  each extended_policy declares `factors`: 4 to 6 rules, each a TRIGGER CONDITION plus an
           EFFECT. Each owns a disjoint set of compute bindings, one of them `decides` (an
           input of the result, never `result`); `effect` is parameter (the tier selects a
           value) or method (the tier selects how the quantity is computed); the ladder has
           >= 3 tiers, pairwise disjoint as stated (`when` + `value` | `method`), its bindings
           fork at least tiers-1 times; a
           `baseline` for its `decides` binding; at least one binding reads history / a
           date span / another category (a tier is established from records, never read off
           a field that names the outcome). Per policy: >= 2 parameter, >= 1 method. Per task,
           over the policies its charter_scope claims: >= 1 multi-source (every tier beyond the
           fall-through combines >= 2 predicates over distinct evidence by and / or) and >= 1
           `cross_difficulty` — its tier is decided from another category's holding or ledger,
           and that category is among the policy's declared cross_category. Whether each factor
           bears weight on a task's world is check_compute's job (baseline substitution must
           change `result`).
  overwrite  extended MAY supersede base (they are successive versions of the same product law
           and extended wins on conflict) but ONLY clause by clause and only where declared:
           `overwrite` is required (write [] for none); each entry names a base_policy that
           exists and is itself in base_policy_refs, a `superseded_clause` that is a verbatim
           (whitespace-insensitive) substring of that base policy's rule, and a `replaced_by`
           that is a verbatim substring of THIS policy's own rule. Undeclared divergence is the
           red light; declaration makes the override legal and traceable. Granularity is the
           clause: sentences not named stay in force and stay inherited. What is superseded is
           the handling clause, never a params VALUE — base numbers remain valid and base-homed.
  crosscat every extended_policy carries cross_category ([] where compute reads no other
           category); its declarations exactly match both the categories read by compute through
           EXISTS/CPARAM/CFIELD/XSUM/XCOUNT/XMAX/XLATEST and inputs.cross_category; each category
           is REAL and != primary; and every policy's target_tool writes ONLY primary-category
           tables (cross-category rule).
  cardinality a non-empty consecutive tasks/0.json..tasks/M-1.json set; the charter carries no
           `workflows` key and no task claims one (every problem is an extended_policy resolved
           by one target_tool call, and the order of a task's writes is entailed by its
           prerequisite edges alone); all policies are covered across task scopes, no two
           tasks overlap.
  prereq   PROBLEM TREE. Every problem is one `extended_policy`; `prerequisite` declares
           problem->problem dependencies, and the edges of the difficulty form its execution
           graph. Every policy must carry `prerequisite` ([] when none): each entry names
           another SOLVABLE problem in this file (not a base policy, not itself), a kind
           (state_gate | value_input), the gate it unblocks, a `form` (state | action), the
           PREREQUISITE SENTENCE as `policy_source` — a VERBATIM sentence of this policy's OWN
           rule that states outright, with an ordering connective (before / after / only after /
           only once / until / first ...), that this policy's own result waits on something: in
           the state form (preferred) on a record-visible state named in the words the tables
           and finders use, with no action, performer or tool named; in the action form (a
           declared fallback carrying `fallback_reason`) on the depended-on action named in
           plain business language — in either form naming no tool, no policy id and no code
           token — the handling-time state as `condition` (an authoring field), the depended-on
           problem's own target_tool as `resolved_by`, and its effect. A rule names no other
           problem's tool or id, and the depended-on rule never restates the prerequisite
           sentence. The whole edge set must be acyclic. Per task, the tree rooted at the
           task's root problem must have 1 to 3 prerequisite PROBLEMS (exactly the count
           draw_counts.py draws for the task; any acyclic shape: chain, fan-out, diamond or a mix), >= max(n-1, 1) of its
           edges `value_input` for n prerequisite problems (state_gate edges alone leave
           A-then-B and B-then-A with the SAME terminal DB, so the ordering is not observable by
           hash scoring, and the larger the tree the more of its edges must carry a value into a
           calculation), and every problem in the tree must be inside that task's charter_scope.
  usertool every task's gold calls at least one owner=user task tool through
           unlock_user_discoverable_tool -> call_user_discoverable_tool: at least one problem
           of every tree is the customer's own write, handed over by the agent.
  nohandoff the blueprint may expose a transfer-to-human share tool, but task gold must
            never call it; this skill does not author handoff-type GT tasks.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_extended.py env/<scenario>/tasks/<difficulty> [--task N]
  # without --task: final difficulty-wide closure; with --task: validate one completed task
"""
import ast
import glob
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prereq_utils  # noqa: E402


def _nows(s):
    """Whitespace-insensitive form for verbatim-quote matching.

    YAML folded scalars inject a space at every fold point, so a quote lifted from a
    folded `rule` can never be compared byte-for-byte.  Stripping all whitespace is the
    only stable comparison across fold points, where the injected space carries no meaning."""
    return re.sub(r"\s+", "", str(s or ""))

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import paths_through_task, select_task_paths, split_task_flag, task_index

_ALLOWED_NODES = (
    ast.Expression, ast.IfExp, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare,
    ast.Call, ast.Name, ast.Load, ast.Constant, ast.keyword,
    ast.And, ast.Or, ast.Not, ast.USub, ast.UAdd,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
)
_XHIST = {"XSUM", "XCOUNT", "XMAX", "XLATEST"}      # another category's event history
_FUNCS = {"F", "P", "K", "SUM", "COUNT", "MAX", "LATEST", "EXISTS", "CPARAM", "CFIELD",
          "MONTHS", "DAYS", "MX", "MN", "RND", "ABS", "min", "max", "round", "abs", "float", "int"} | _XHIST
_CONSTS = {"NOW", "HID", "CUST", "True", "False", "None"}
_HIST = {"SUM", "COUNT", "MAX", "LATEST"}
_CROSS = {"EXISTS", "CPARAM", "CFIELD"} | _XHIST
from check_compute import (factor_shape_errors, MIN_FACTORS_PER_COMP, MIN_CROSS_FACTORS_PER_TASK,  # noqa: E402
                           MIN_PARAM_FACTORS_PER_COMP, MIN_METHOD_FACTORS_PER_COMP,
                           MAX_FACTORS_PER_COMP, MIN_MULTISOURCE_FACTORS_PER_TASK, multi_source)
from draw_counts import draw_for_task  # noqa: E402


def load_yaml(p):
    with open(p) as f:
        return yaml.safe_load(f)


def deep_eq(a, b):
    return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)


def tool_write_tables(py_path):
    """{func_name: set(tables it writes via ctx.create/update/delete)} from a tools file."""
    out = {}
    if not os.path.exists(py_path):
        return out
    tree = ast.parse(open(py_path).read())
    for fn in tree.body:
        if not isinstance(fn, ast.FunctionDef):
            continue
        tables = set()
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "ctx"
                    and node.func.attr in ("create", "update", "delete")
                    and node.args and isinstance(node.args[0], ast.Constant)):
                tables.add(node.args[0].value)
        out[fn.name] = tables
    return out


def tool_names(py_path):
    if not os.path.exists(py_path):
        return set()
    tree = ast.parse(open(py_path).read())
    return {fn.name for fn in tree.body if isinstance(fn, ast.FunctionDef)}


_CALL_WRAPPERS = {"call_agent_discoverable_tool", "call_user_discoverable_tool"}


def gold_task_tool_calls(actions, task_tools):
    """Return [(underlying_task_tool, owner, action_index)] for scored task-tool calls."""
    out = []
    for action_index, action in enumerate(actions or []):
        if not isinstance(action, dict):
            continue
        name = action.get("tool") or action.get("name")
        args = action.get("arguments") or {}
        if name in _CALL_WRAPPERS:
            underlying = args.get("tool_name")
            if underlying in task_tools:
                owner = "user" if name == "call_user_discoverable_tool" else "agent"
                out.append((underlying, owner, action_index))
        elif name in task_tools:  # direct calls are legacy, but still reveal the intended write sequence
            out.append((name, action.get("owner"), action_index))
    return out
def main():
    pos, task_selector = split_task_flag(sys.argv[1:])
    if len(pos) < 1:
        print("usage: check_extended.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    diff = pos[0].rstrip("/")
    task_mode = task_selector is not None
    p = os.path.abspath(diff)
    scen = None
    while p != "/":
        if os.path.isdir(os.path.join(p, "blueprint")):
            scen = p; break
        p = os.path.dirname(p)
    if not scen:
        raise SystemExit(f"cannot find scenario root above {diff}")
    bp = os.path.join(scen, "blueprint")
    db_schema = json.load(open(os.path.join(bp, "db_schema.json")))

    ext_files = glob.glob(os.path.join(diff, "*.extended.yaml"))
    if len(ext_files) != 1:
        raise SystemExit(f"expected exactly one <category>.extended.yaml under {diff}, found {ext_files}")
    extended = load_yaml(ext_files[0])
    cat = extended.get("category")
    base = load_yaml(os.path.join(bp, "products", f"{cat}.yaml"))

    # table -> category (from every blueprint product binding)
    table_cat, cats = {}, {}
    for f in glob.glob(os.path.join(bp, "products", "*.yaml")):
        d = load_yaml(f)
        if not isinstance(d, dict) or not d.get("category"):
            continue
        c = d["category"]; cats[c] = d
        b = d.get("binding") or {}
        for t in [b.get("holding_table")] + list(b.get("event_tables") or []) + list(b.get("intake_tables") or []):
            if t:
                table_cat[t] = c
    primary_binding = base.get("binding") or {}
    primary_tables = set([primary_binding.get("holding_table")]
                         + list(primary_binding.get("event_tables") or [])
                         + list(primary_binding.get("intake_tables") or []))
    base_events = {e["type"]: e for e in (base.get("events") or [])}
    primary_events = set(base_events)
    base_policies = {p2.get("id"): p2 for p2 in (base.get("policies") or []) if p2.get("id")}
    primary_params = set(base.get("parameter_schema") or {})
    primary_holding = primary_binding.get("holding_table")
    holding_fields = set(db_schema.get(primary_holding, {}))

    fails = []

    # ---- compat: base is a verbatim subset ----
    for k, v in base.items():
        if k not in extended:
            fails.append(f"compat: base key '{k}' missing from extended.yaml")
        elif not deep_eq(v, extended[k]):
            fails.append(f"compat: base key '{k}' was modified in extended.yaml (must be verbatim)")

    tt_path = os.path.join(diff, "task_tools.py")
    task_tool_set = tool_names(tt_path)          # hidden task tools (unlock/call only)
    writes = tool_write_tables(tt_path)
    named_tools = set()                          # task tools named in extended.yaml (the structured KB)
    _SHADOW = ("may be zero in practice", "can be zero depending on the case",
               "may or may not apply in practice", "this task", "this problem",
               "that task", "in this case", "usually zero", "generally zero", "not triggered")

    cur_params = {}

    def check_expr(expr, where):
        cross_refs = set()
        try:
            tree = ast.parse(str(expr), mode="eval")
        except SyntaxError as e:
            fails.append(f"{where}: cannot parse expr: {e}"); return cross_refs
        for node in ast.walk(tree):
            if not isinstance(node, _ALLOWED_NODES):
                fails.append(f"{where}: disallowed syntax {type(node).__name__}"); continue
            if isinstance(node, ast.Name) and node.id not in (_FUNCS | _CONSTS | known_vars):
                fails.append(f"{where}: unknown name '{node.id}'")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                fn = node.func.id
                if fn == "P" and node.args and isinstance(node.args[0], ast.Constant):
                    if node.args[0].value not in primary_params:
                        fails.append(f"{where}: P('{node.args[0].value}') not a parameter_schema key")
                if fn == "F" and node.args and isinstance(node.args[0], ast.Constant):
                    if node.args[0].value not in holding_fields:
                        fails.append(f"{where}: F('{node.args[0].value}') not a field of {primary_holding}")
                if fn in _HIST and node.args and isinstance(node.args[0], ast.Constant):
                    if node.args[0].value not in db_schema:
                        fails.append(f"{where}: {fn}('{node.args[0].value}') not a table in db_schema")
                    elif table_cat.get(node.args[0].value) != cat:
                        fails.append(f"{where}: {fn} reads table '{node.args[0].value}' not owned by primary category '{cat}'")
                if fn in _CROSS and node.args and isinstance(node.args[0], ast.Constant):
                    oc = node.args[0].value
                    cross_refs.add(oc)
                    if oc not in cats:
                        fails.append(f"{where}: {fn}('{oc}') not a known category")
                    elif oc == cat:
                        fails.append(f"{where}: {fn}('{oc}') references the primary category (cross_category must be OTHER categories)")
                    if fn in _XHIST:
                        # second positional arg: an event table OWNED by that other category
                        if len(node.args) < 2 or not isinstance(node.args[1], ast.Constant):
                            fails.append(f"{where}: {fn}('{oc}', ...) needs the other category's event table as its second argument")
                        else:
                            xt = node.args[1].value
                            if xt not in db_schema:
                                fails.append(f"{where}: {fn} reads table '{xt}' not in db_schema")
                            elif table_cat.get(xt) != oc:
                                fails.append(f"{where}: {fn}('{oc}', '{xt}') — table '{xt}' is not an event table of category '{oc}'")
                if fn == "K" and node.args and isinstance(node.args[0], ast.Constant):
                    if node.args[0].value not in cur_params:
                        fails.append(f"{where}: K('{node.args[0].value}') not a key in this policy's params")
        return cross_refs

    # ---- extended_policies ----
    eps = extended.get("extended_policies") or []
    if not eps:
        fails.append("no extended_policies")
    ep_ids = [ep.get("id") for ep in eps]
    valid_ep_ids = [pid for pid in ep_ids if isinstance(pid, str) and pid]
    if len(valid_ep_ids) != len(ep_ids):
        fails.append("every extended_policy must have a non-empty string id")
    if len(set(valid_ep_ids)) != len(valid_ep_ids):
        fails.append(f"extended_policy ids must be unique; got {ep_ids}")
    ep_by_id = {ep.get("id"): ep for ep in eps
                if isinstance(ep.get("id"), str) and ep.get("id")}
    declared_ep_id_set = set(ep_by_id)
    cross_cat_count = 0
    for ep in eps:
        pid = ep.get("id", "?")
        w = f"policy {pid}"
        if not str(pid).startswith(f"{cat}_"):
            fails.append(f"{w}: id must be prefixed '{cat}_'")
        base_refs = ep.get("base_policy_refs") or []
        if not isinstance(base_refs, list) or not base_refs:
            fails.append(f"{w}: base_policy_refs must be non-empty — extended policy must declare its "
                         "base-policy lineage, never invent local product law")
        else:
            if len(set(base_refs)) != len(base_refs):
                fails.append(f"{w}: base_policy_refs contains duplicate ids {base_refs}")
            unknown_refs = set(base_refs) - set(base_policies)
            if unknown_refs:
                fails.append(f"{w}: base_policy_refs contains unknown base policy ids "
                             f"{sorted(unknown_refs)}")
            ep_subjects = set(ep.get("subject") or [])
            expected_refs = {
                ref for ref, policy in base_policies.items()
                if ep_subjects & set(policy.get("subject") or [])
            }
            missing_governing_refs = expected_refs - set(base_refs)
            if missing_governing_refs:
                fails.append(f"{w}: base_policy_refs must include every base policy governing its "
                             f"subject events; missing={sorted(missing_governing_refs)}")
        # ---- overwrite: every divergence from base must be declared clause by clause ----
        # extended IS allowed to supersede base (they are successive versions of the same
        # product law, extended wins on conflict), but only where it names the base sentence
        # it replaces.  An undeclared divergence is the red light; a declared one is legal.
        refs_set = set(base_refs) if isinstance(base_refs, list) else set()
        own_rule = ep.get("rule")
        ow = ep.get("overwrite")
        if ow is None:
            fails.append(f"{w}: missing overwrite — declare each base clause this policy supersedes, or "
                         "write [] when it supersedes none. Diverging from base without declaring it here "
                         "is the red light; declaring it makes the override legal and traceable")
        elif not isinstance(ow, list):
            fails.append(f"{w}: overwrite must be a list (use [] when this policy supersedes no base clause)")
        else:
            seen_ow = set()
            for oi, entry in enumerate(ow):
                ew = f"{w}.overwrite[{oi}]"
                if not isinstance(entry, dict):
                    fails.append(f"{ew}: each entry must be a mapping with base_policy / "
                                 "superseded_clause / replaced_by")
                    continue
                ow_bp = entry.get("base_policy")
                sc = str(entry.get("superseded_clause") or "").strip()
                rb = str(entry.get("replaced_by") or "").strip()
                if not ow_bp:
                    fails.append(f"{ew}: missing base_policy")
                elif ow_bp not in base_policies:
                    fails.append(f"{ew}: base_policy '{ow_bp}' is not a base policy of '{cat}'")
                elif ow_bp not in refs_set:
                    fails.append(f"{ew}: base_policy '{ow_bp}' must also appear in base_policy_refs — a policy "
                                 "whose lineage was never declared cannot be superseded")
                if not sc:
                    fails.append(f"{ew}: missing superseded_clause — quote the base sentence being replaced")
                elif ow_bp in base_policies and _nows(sc) not in _nows(base_policies[ow_bp].get("rule")):
                    fails.append(f"{ew}: superseded_clause is not a verbatim sentence of base policy "
                                 f"'{ow_bp}' rule — quote it, do not paraphrase")
                if not rb:
                    fails.append(f"{ew}: missing replaced_by — quote the sentence of THIS policy's rule that "
                                 "takes its place, so the new basis is legislated in prose and not only in compute")
                elif _nows(rb) not in _nows(own_rule):
                    fails.append(f"{ew}: replaced_by is not a verbatim sentence of this policy's own rule")
                key = (ow_bp, _nows(sc))
                if key in seen_ow:
                    fails.append(f"{ew}: duplicate (base_policy, superseded_clause) declaration")
                seen_ow.add(key)
        for et in (ep.get("subject") or []):
            if et not in primary_events:
                fails.append(f"{w}: subject '{et}' is not a declared event of '{cat}'")
        if not ep.get("computes"):
            fails.append(f"{w}: missing computes")
        tgt = ep.get("target_tool")
        if not tgt:
            fails.append(f"{w}: missing target_tool")
        elif tgt not in task_tool_set:
            fails.append(f"{w}: target_tool '{tgt}' is not a hidden task tool in task_tools.py "
                         "(the computed write must be a task tool reached via unlock/call)")
        if tgt:
            named_tools.add(tgt)
        rule_text = str(ep.get("rule") or "").strip()
        if not rule_text:
            fails.append(f"{w}: empty rule")
        else:
            # rule is a GENERAL clause for all customers — it must carry no task shadow
            # (authoring-viewpoint meta notes about which factor happens to be zero in a task)
            for shadow in _SHADOW:
                if shadow in rule_text.lower():
                    fails.append(f"{w}: rule contains task-shadow meta note '{shadow}' — a general policy "
                                 "knows no specific customer; write negative space as a conditional clause "
                                 "(those meeting X are charged/granted Y; those not meeting it are out of "
                                 "scope) instead")
        cur_params = ep.get("params") or {}
        compute = ep.get("compute") or []
        compute_cross_refs = set()
        if not compute or not isinstance(compute, list):
            fails.append(f"{w}: compute must be a non-empty list")
        else:
            known_vars = set()
            for item in compute:
                if not isinstance(item, dict) or len(item) != 1:
                    fails.append(f"{w}: each compute item must be a single {{name: expr}}"); continue
                (name, expr), = item.items()
                compute_cross_refs |= check_expr(expr, f"{w}.compute[{name}]")
                known_vars.add(name)
            if "result" not in known_vars:
                fails.append(f"{w}: compute has no final 'result' binding")
        # ---- baseline: the standard method + default values, the root every factor falls back to ----
        bl = ep.get("baseline")
        if not isinstance(bl, dict) or not str(bl.get("rule") or "").strip():
            fails.append(f"{w}: missing `baseline.rule` — every computation states its standard method and default "
                         "values in a self-sufficient paragraph (rendered as the computation document; every factor's "
                         "fall-through tier is this baseline)")
        else:
            for sent in re.split(r"(?<=[.!?])\s+", str(bl.get("rule")).strip()):
                if len(_nows(sent)) < 12:
                    continue
                if _nows(sent) not in _nows(own_rule):
                    fails.append(f"{w}: baseline.rule sentence {sent.strip()[:70]!r} is not a verbatim sentence of the "
                                 "policy's rule — the baseline is a subset of the rule, quoted, never a second text")
            bp_keys = bl.get("params")
            if not isinstance(bp_keys, list):
                fails.append(f"{w}: baseline.params must be a list of the quantitative keys that are the defaults "
                             "(this policy's params keys and/or tier parameter keys); [] when there is none")
            else:
                for k in bp_keys:
                    if k not in cur_params and k not in primary_params:
                        fails.append(f"{w}: baseline.params key '{k}' is neither a params key of this policy nor a "
                                     "parameter_schema key")
        # ---- factors: declared rules with ladders (structure only; weight is check_compute's) ----
        f_errs, factors = factor_shape_errors(ep, w)
        fails.extend(f_errs)
        if factors:
            if not (MIN_FACTORS_PER_COMP <= len(factors) <= MAX_FACTORS_PER_COMP):
                fails.append(f"{w}: declares {len(factors)} factors (outside {MIN_FACTORS_PER_COMP}..{MAX_FACTORS_PER_COMP}) "
                             "— a computation rests on 4 to 6 rules that each decide one of its inputs")
            n_param = sum(1 for f in factors if f.get("effect") == "parameter")
            n_method = sum(1 for f in factors if f.get("effect") == "method")
            if n_param < MIN_PARAM_FACTORS_PER_COMP:
                fails.append(f"{w}: only {n_param} effect=parameter factors (< {MIN_PARAM_FACTORS_PER_COMP})")
            if n_method < MIN_METHOD_FACTORS_PER_COMP:
                fails.append(f"{w}: only {n_method} effect=method factors (< {MIN_METHOD_FACTORS_PER_COMP}) — at least "
                             "one factor must change how a quantity is computed, in a way that line of business "
                             "genuinely varies, not only which number enters it")
            xds = [f.get("cross_difficulty") for f in factors if f.get("cross_difficulty")]
            for xd in xds:
                if xd == cat:
                    fails.append(f"{w}: a cross_difficulty factor names the primary category '{cat}'")
                elif xd not in cats:
                    fails.append(f"{w}: cross_difficulty '{xd}' is not a known category")
        cc = ep.get("cross_category")
        if not isinstance(cc, list):
            fails.append(f"{w}: cross_category is required — the list of the other categories compute reads, "
                         "[] where it reads none")
            cc = []
        cc_cats = set()
        if cc:
            cross_cat_count += 1
        for entry in cc:
            oc = entry.get("category") if isinstance(entry, dict) else entry
            cc_cats.add(oc)
            if oc not in cats:
                fails.append(f"{w}: cross_category '{oc}' is not a known category")
            elif oc == cat:
                fails.append(f"{w}: cross_category names the primary category")
        if compute_cross_refs != cc_cats:
            fails.append(f"{w}: cross_category declarations {sorted(map(str, cc_cats))} must exactly "
                         f"match compute's EXISTS/CPARAM/CFIELD/XSUM/XCOUNT/XMAX/XLATEST categories "
                         f"{sorted(map(str, compute_cross_refs))} — a declared-only dependency is decoration, "
                         "an undeclared read is hidden")
        for f in factors:
            xd = f.get("cross_difficulty")
            if xd and xd not in cc_cats:
                fails.append(f"{w}: factor '{f.get('id')}' is cross_difficulty='{xd}' but that category is not "
                             "declared in cross_category")
        input_cc = {entry.get("category") if isinstance(entry, dict) else entry
                    for entry in ((ep.get("inputs") or {}).get("cross_category") or [])}
        if input_cc != cc_cats:
            fails.append(f"{w}: inputs.cross_category {sorted(map(str, input_cc))} must exactly match "
                         f"cross_category declarations {sorted(map(str, cc_cats))}")
        # writes-only-primary: the policy's target tool may write ONLY primary tables
        wt = writes.get(tgt, set())
        bad = {t for t in wt if table_cat.get(t) not in (cat, None)}
        if bad:
            fails.append(f"{w}: target_tool '{tgt}' writes non-primary tables {sorted(bad)} "
                         f"(a policy's result drives a write in the primary category only)")

    # ---- no workflows: every problem is an extended_policy; order comes from prerequisite edges ----
    if "workflows" in extended:
        fails.append("charter carries a `workflows` key — this pipeline has no workflow problems: every problem is an "
                     "extended_policy resolved by one target_tool call, and the order of a task's writes is entailed by "
                     "its prerequisite edges alone; delete the key")

    # ---- every defined task tool must be NAMED in extended.yaml (the structured KB) ----
    # extended.yaml IS the KB the agent reads to discover a hidden tool; a task tool named by
    # no extended_policy.target_tool is undiscoverable dead code.
    for tn in sorted(task_tool_set):
        if tn not in named_tools:
            fails.append(f"task tool '{tn}' is named by no extended_policy.target_tool in extended.yaml — an "
                         "agent could never discover/unlock it")

    # ---- M tasks, at continuous loader-visible paths tasks/0.json..tasks/M-1.json ----
    all_task_paths = select_task_paths(diff)
    task_paths = select_task_paths(diff, task_selector)
    task_basenames = [os.path.basename(tp) for tp in task_paths]
    if task_mode:
        if len(task_paths) != 1:
            fails.append(f"cardinality: per-task mode expected one selected task, found {task_basenames}")
    else:
        expected_basenames = [f"{i}.json" for i in range(len(all_task_paths))]
        if not all_task_paths or [os.path.basename(tp) for tp in all_task_paths] != expected_basenames:
            fails.append(f"cardinality: expected a non-empty consecutive task set 0.json..{len(all_task_paths)-1}.json, "
                         f"found {[os.path.basename(tp) for tp in all_task_paths]}")
    loaded_tasks = []
    for tp in task_paths:
        try:
            tk = json.load(open(tp))
        except Exception as exc:  # noqa: BLE001
            fails.append(f"task {os.path.basename(tp)} is not valid JSON: {exc}")
            continue
        loaded_tasks.append((tp, tk))
    task_count = len(task_paths)

    # ---- every task closes its own policy -> computation -> exact GT call ----
    # ---- prerequisite: policy-side declarations (structure, refs, prerequisite sentences, acyclicity) ----
    prereq_utils.validate_declarations(extended, task_tool_set, fails)
    prereq_idx = prereq_utils.problem_index(extended)
    prereq_out = {}
    for _oid, _okind, _node in prereq_utils.owners(extended):
        prereq_out[_oid] = [e.get("problem") for e in (_node.get("prerequisite") or [])
                            if isinstance(e, dict) and e.get("problem")]

    all_used_policies = set()
    scope_by_task = {}
    for tp, tk in loaded_tasks:
        tid = os.path.basename(tp)
        scope = tk.get("charter_scope") or {}
        if "workflows" in scope:
            fails.append(f"task {tid}: charter_scope.workflows is not a field — a task claims extended_policies "
                         "and task_tools only; its write order is the topological order of its problem tree")
        actions = tk.get("evaluation_criteria") or []
        calls = gold_task_tool_calls(actions, task_tool_set)
        # ---- at least one problem of every tree is the customer's own write ----
        if not any(_o == "user" for _t, _o, _i in calls):
            fails.append(f"user-tool {tid}: gold calls no owner=user task tool — every task's tree contains at "
                         "least one problem whose target_tool is owner=user, unlocked and handed over by the agent "
                         "and run by the customer (unlock_user_discoverable_tool -> call_user_discoverable_tool)")
        for ai, act in enumerate(actions):
            for fld in ("objective", "necessity"):
                if not str(act.get(fld) or "").strip():
                    fails.append(f"task {tid}: evaluation_criteria[{ai}] ({act.get('tool')}) has empty {fld}")
            if "call_" not in str(act.get("tool") or ""):
                continue
            wrapper = act.get("arguments") or {}
            passed = wrapper.get("arguments") or {}
            traced = act.get("argument_uniqueness_tracing")
            if not isinstance(traced, dict):
                fails.append(f"task {tid}: {wrapper.get('tool_name','?')} has no argument_uniqueness_tracing object")
                continue
            missing = [k for k in passed if not str(traced.get(k) or "").strip()]
            if missing:
                fails.append(f"task {tid}: {wrapper.get('tool_name','?')} argument_uniqueness_tracing "
                             f"missing or empty for {missing} (every argument needs one, calculated or not)")
        actual_tools = []
        for tool, _owner, _action_index in calls:
            if tool not in actual_tools:
                actual_tools.append(tool)
        scope_tools = scope.get("task_tools") or []
        if scope_tools != actual_tools:
            fails.append(f"policy-closure {tid}: charter_scope.task_tools must equal the GT task tools "
                         f"in first-use order; got {scope_tools}, expected {actual_tools}")
        scope_pids = scope.get("extended_policies") or []
        comps = tk.get("computations") or []
        comp_pids = [c.get("policy_id") for c in comps
                     if isinstance(c, dict) and c.get("policy_id")]
        if len(set(scope_pids)) != len(scope_pids):
            fails.append(f"policy-closure {tid}: charter_scope.extended_policies has duplicates {scope_pids}")
        if set(scope_pids) != set(comp_pids):
            fails.append(f"policy-closure {tid}: charter_scope.extended_policies {sorted(set(scope_pids))} "
                         f"!= computations policy ids {sorted(set(comp_pids))}")
        unknown_pids = set(scope_pids) - declared_ep_id_set
        if unknown_pids:
            fails.append(f"policy-closure {tid}: unknown extended policy ids {sorted(unknown_pids)}")
        # ---- per-task floors: multi-source and cross-difficulty are asked of the task, not of every policy ----
        scope_eps = [ep_by_id[p] for p in scope_pids if p in ep_by_id]
        scope_factors = [(sp, f) for sp in scope_eps for f in (sp.get("factors") or []) if isinstance(f, dict)]
        n_multi_task = sum(1 for sp, f in scope_factors if multi_source(sp, f))
        n_cross_task = sum(1 for _sp, f in scope_factors if f.get("cross_difficulty"))
        if scope_eps and n_multi_task < MIN_MULTISOURCE_FACTORS_PER_TASK:
            fails.append(f"factors {tid}: only {n_multi_task} multi-source factors over this task's policies "
                         f"(< {MIN_MULTISOURCE_FACTORS_PER_TASK}) — at least one factor of the task combines, on every "
                         "tier beyond the fall-through, two conditions over distinct evidence by and / or")
        if scope_eps and n_cross_task < MIN_CROSS_FACTORS_PER_TASK:
            fails.append(f"factors {tid}: only {n_cross_task} cross_difficulty factors over this task's policies "
                         f"(< {MIN_CROSS_FACTORS_PER_TASK}) — at least one factor of the task decides its tier from "
                         "the customer's holdings or ledger in another difficulty")
        if tk.get("required_documents") != scope_pids:
            fails.append(f"policy-closure {tid}: required_documents must exactly equal "
                         "charter_scope.extended_policies in the same order")
        action_to_call = {action_index: i for i, (_, _, action_index) in enumerate(calls)}
        seen_pairs = set()
        for comp_index, comp in enumerate(comps):
            if not isinstance(comp, dict):
                fails.append(f"policy-closure {tid}: computations[{comp_index}] must be an object")
                continue
            pid = comp.get("policy_id")
            pol = ep_by_id.get(pid)
            if not pol:
                fails.append(f"policy-closure {tid}: computations[{comp_index}] names unknown policy '{pid}'")
            action_index = comp.get("step")
            call_index = action_to_call.get(action_index)
            if call_index is None:
                fails.append(f"policy-closure {tid}: computation '{pid}' step {action_index!r} "
                             "is not a GT task-tool call")
                continue
            call_tool = calls[call_index][0]
            if pol and pol.get("target_tool") != call_tool:
                fails.append(f"policy-closure {tid}: computation '{pid}' occurs on tool '{call_tool}', "
                             f"but the policy targets '{pol.get('target_tool')}'")
            if pol and comp.get("arg") != pol.get("computes"):
                fails.append(f"policy-closure {tid}: computation '{pid}' arg '{comp.get('arg')}' "
                             f"!= policy computes '{pol.get('computes')}'")
            pair = (call_index, pid)
            if pair in seen_pairs:
                fails.append(f"policy-closure {tid}: duplicate computation for call {action_index}, policy '{pid}'")
            seen_pairs.add(pair)
        # ---- prerequisite: the task claims the WHOLE problem tree, not just its root ----
        pc = tk.get("prerequisite_closure") or {}
        root = pc.get("root_problem")
        if not isinstance(pc, dict) or not root:
            fails.append(f"prereq {tid}: missing prerequisite_closure.root_problem — every task is a problem "
                         "tree whose root is the problem the customer's surface request points at")
        else:
            _idx = task_index(tp)
            prereq_utils.check_task_tree(tid, root, set(scope_pids), extended, fails,
                                         expected=draw_for_task(diff, _idx)["prerequisite_problems"] if _idx is not None else None)

        all_used_policies.update(set(scope_pids))
        scope_by_task[tid] = {"extended_policies": set(scope_pids), "task_tools": set(scope_tools)}

    # In per-task mode, compare the selected task with all earlier completed
    # tasks immediately.  Future tasks do not exist yet and are deliberately not
    # required; the final run repeats this check across the full suite.
    if task_mode and loaded_tasks:
        selected_tp, _selected_tk = loaded_tasks[0]
        selected_tid = os.path.basename(selected_tp)
        selected_scope = scope_by_task.get(selected_tid, {})
        selected_idx = task_index(selected_tp)
        for prior_tp in paths_through_task(diff, task_selector):
            if os.path.abspath(prior_tp) == os.path.abspath(selected_tp):
                continue
            if selected_idx is not None and (task_index(prior_tp) is None or task_index(prior_tp) >= selected_idx):
                continue
            try:
                prior_tk = json.load(open(prior_tp))
            except Exception:
                continue
            prior_scope = prior_tk.get("charter_scope") or {}
            prior_assets = {
                "extended_policies": set(prior_scope.get("extended_policies") or []),
                "task_tools": set(prior_scope.get("task_tools") or []),
            }
            for key in ("extended_policies", "task_tools"):
                overlap = selected_scope.get(key, set()) & prior_assets[key]
                if overlap:
                    fails.append(f"charter_scope: selected task {selected_tid} overlaps completed task "
                                 f"{os.path.basename(prior_tp)} on {key} {sorted(overlap)} — "
                                 "redesign the selected task before continuing")

    if not task_mode:
        if all_used_policies != declared_ep_id_set:
            fails.append(f"policy coverage: M tasks use {sorted(all_used_policies)}, expected all extended policies "
                         f"{sorted(declared_ep_id_set)}")
    scope_items = list(scope_by_task.items())
    for i, (ta, sa) in enumerate(scope_items):
        for tb, sb in scope_items[i + 1:]:
            for key in ("extended_policies", "task_tools"):
                overlap = sa[key] & sb[key]
                if overlap:
                    fails.append(f"charter_scope: tasks {ta} and {tb} share {key} {sorted(overlap)}")

    # ---- no handoff-type GT tasks ----
    # The blueprint keeps this general environment capability, but instantiate must not
    # turn it into a scored path. Resolve the scenario-specific tool by its log table.
    handoff_table = ((load_yaml(os.path.join(bp, "blueprint.yaml")) or {}).get("logs") or {}).get("handoff_log_table")
    share_writes = tool_write_tables(os.path.join(bp, "share_tools.py"))
    transfer_tools = {n for n, ts in share_writes.items() if handoff_table and handoff_table in ts}
    for tp, tk in loaded_tasks:
        tid = os.path.basename(tp)
        crit = tk.get("evaluation_criteria") or []
        hits = [(i, a) for i, a in enumerate(crit)
                if (a.get("tool") or a.get("name")) in transfer_tools]
        if hits:
            fails.append(f"no-handoff {tid}: gold calls blueprint transfer tool(s) "
                         f"{sorted({(a.get('tool') or a.get('name')) for _, a in hits})}; "
                         "instantiate does not author handoff-type GT tasks")
    mode_label = f", selected_task={task_selector}" if task_mode else ""
    print(f"🔎 EXTENDED gate  (category={cat}, extended_policies={len(eps)}, cross-cat={cross_cat_count}, "
          f"task_tools={len(task_tool_set)}, tasks={task_count}{mode_label}, no_handoff=True)")
    if fails:
        print("  [FAIL]")
        for f in fails[:50]:
            print("   -", f)
        print("EXTENDED NOT OK")
        sys.exit(1)
    if task_mode:
        print("  [PASS] selected task closes its policy/tool scope and calls a customer's own tool; shared charter is "
              "structurally valid, every prerequisite is stated by a prerequisite sentence (difficulty-wide "
              "cardinality/coverage deferred to final run)")
    else:
        print("  [PASS] compatible charter; cross-category reads declared exactly; every task has a multi-source and "
              "a cross-difficulty factor; every prerequisite is stated by a prerequisite sentence; every task calls a "
              "customer's own tool; all policies are covered across the suite with disjoint scopes")
    print("EXTENDED OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
