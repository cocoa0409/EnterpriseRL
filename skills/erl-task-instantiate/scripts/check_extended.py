"""EXTENDED gate: verify <category>.extended.yaml is a compatible superset of the
blueprint charter, its extended_policies are well-formed and machine-parseable, its
every policy has a real cross-category factor that computes only for the primary category,
and exactly one of the difficulty's M tasks closes one >=4-step workflow; all policies
are covered across the M task scopes.

Checks:
  compat   every base key of blueprint/products/<category>.yaml is present in the
           extended file and DEEP-EQUAL (extended only ADDS workflows + extended_policies).
  policy   each extended_policy: id prefixed <category>_ ; subject subset of base declared
           events; base_policy_refs include every base policy governing those refined events
           (and may additionally cite genuine input lineage); computes + target_tool present;
           rule non-empty; compute is a non-empty ordered list ending in `result`, every
           expression parses under the restricted grammar, and every P()/SUM()/EXISTS()/...
           name resolves against the real schema/params/categories.
  overwrite  extended MAY supersede base (they are successive versions of the same product law
           and extended wins on conflict) but ONLY clause by clause and only where declared:
           `overwrite` is required (write [] for none); each entry names a base_policy that
           exists and is itself in base_policy_refs, a `superseded_clause` that is a verbatim
           (whitespace-insensitive) substring of that base policy's rule, and a `replaced_by`
           that is a verbatim substring of THIS policy's own rule. Undeclared divergence is the
           red light; declaration makes the override legal and traceable. Granularity is the
           clause: sentences not named stay in force and stay inherited. What is superseded is
           the handling clause, never a params VALUE — base numbers remain valid and base-homed.
  crosscat EVERY extended_policy has a non-empty cross_category; its declarations exactly
           match both the categories read by compute through EXISTS/CPARAM/CFIELD and
           inputs.cross_category; each category is REAL and != primary; and the policy's
           target_tool writes ONLY primary-category tables (cross-category rule).
  cardinality a non-empty consecutive tasks/0.json..tasks/M-1.json set and exactly one workflow.
  exactly one task claims that workflow and its GT task-tool call sequence exactly matches
           the steps' tool + owner + order. Workflow refs == that task's computations ==
           that task's charter_scope; all policies are covered across task scopes.
  prereq   PROBLEM TREE. `extended_policy` and `workflow` are both "the solution to one
           problem"; `prerequisite` declares problem->problem dependencies (never step order
           inside one problem). Every policy and workflow must carry `prerequisite` ([] when
           none): each entry names another SOLVABLE problem in this file (not a base policy,
           not itself), a kind (state_gate | value_input), the gate it unblocks, the condition,
           a `policy_source` that is a VERBATIM sentence of this problem's own rule or of a base
           rule it inherits (a prerequisite absent from general prose never reaches the agent
           through the KB and is therefore undiscoverable), the depended-on problem's own action
           as `resolved_by`, and its effect. The whole edge set must be acyclic. Per task, the
           tree rooted at the task's root problem must have >= 2 prerequisite edges, >= 1 of
           them `value_input` (without one, doing A-then-B and B-then-A yield the SAME terminal
           DB, so the ordering the prerequisite asserts is not observable by hash scoring at
           all), and every problem in the tree must be inside that task's charter_scope.
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
_FUNCS = {"F", "P", "K", "SUM", "COUNT", "MAX", "LATEST", "EXISTS", "CPARAM", "CFIELD",
          "MONTHS", "DAYS", "MX", "MN", "RND", "ABS", "min", "max", "round", "abs", "float", "int"}
_CONSTS = {"NOW", "HID", "CUST", "True", "False", "None"}
_HIST = {"SUM", "COUNT", "MAX", "LATEST"}
_CROSS = {"EXISTS", "CPARAM", "CFIELD"}


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
            for shadow in ("may be zero in practice", "can be zero depending on the case",
                           "may or may not apply in practice", "this task", "this problem",
                           "that task", "in this case", "usually zero", "generally zero", "not triggered"):
                if shadow in rule_text.lower():
                    fails.append(f"{w}: rule contains task-shadow meta note '{shadow}' — a general policy "
                                 "knows no specific customer; write negative space as a conditional clause "
                                 "(those meeting X are charged/granted Y; those not meeting it are out of "
                                 "scope) instead")
            # rule must be detailed enough to stand alone (mirror of compute in prose)
            if len(rule_text) < 80:
                fails.append(f"{w}: rule too thin ({len(rule_text)} chars) — it must spell out every factor's "
                             "source/basis, condition criteria, combination order, rounding and caps so a reader "
                             "can recompute the value without seeing compute")
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
        cc = ep.get("cross_category") or []
        cc_cats = set()
        if not cc:
            fails.append(f"{w}: cross_category must be non-empty (EVERY extended_policy needs a real "
                         "cross-category factor)")
        else:
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
                             f"match compute's EXISTS/CPARAM/CFIELD categories "
                             f"{sorted(map(str, compute_cross_refs))} — declared-only dependencies are decoration")
            input_cc = {entry.get("category") if isinstance(entry, dict) else entry
                        for entry in ((ep.get("inputs") or {}).get("cross_category") or [])}
            if input_cc != cc_cats:
                fails.append(f"{w}: inputs.cross_category {sorted(map(str, input_cc))} must exactly match "
                             f"cross_category declarations {sorted(map(str, cc_cats))}")
            # writes-only-primary: the policy's target tool may write ONLY primary tables
            wt = writes.get(tgt, set())
            bad = {t for t in wt if table_cat.get(t) not in (cat, None)}
            if bad:
                fails.append(f"{w}: cross-category policy's target_tool '{tgt}' writes non-primary tables {sorted(bad)} "
                             f"(compute must target ONLY the primary category)")
    if cross_cat_count != len(eps):
        fails.append(f"only {cross_cat_count}/{len(eps)} extended_policies have cross-category factors "
                     "(EVERY policy must have one)")

    # ---- one workflow, with its policies nested at their exact write steps ----
    _SHADOW = ("may be zero in practice", "can be zero depending on the case",
               "may or may not apply in practice", "this task", "this problem",
               "that task", "in this case", "usually zero", "generally zero", "not triggered")
    wfs = extended.get("workflows") or []
    if task_mode:
        if len(wfs) > 1:
            fails.append(f"cardinality: an in-progress difficulty may have zero or one workflow, found {len(wfs)}")
    elif len(wfs) != 1:
        fails.append(f"cardinality: expected exactly one workflow per difficulty, found {len(wfs)}")
    wf_ids = [wf.get("id") for wf in wfs]
    if any(not wid for wid in wf_ids):
        fails.append("every workflow must have a non-empty id")
    if len(set(wf_ids)) != len(wf_ids):
        fails.append("workflow ids must be unique")
    wf_step_policy_refs = {}

    def normalize_policy_refs(raw, where):
        """computed_by accepts a scalar for compatibility; templates use a list."""
        if raw is None:
            return []
        if isinstance(raw, str) and raw:
            return [raw]
        if isinstance(raw, list) and all(isinstance(x, str) and x for x in raw):
            return raw
        fails.append(f"{where}: computed_by must be a policy id or a list of non-empty policy ids")
        return []

    for wf in wfs:
        wid = wf.get("id", "?")
        steps = wf.get("steps") or []
        if "computed_by" in wf:
            fails.append(f"workflow {wid}: top-level computed_by is ambiguous; nest policy ids on the exact "
                         "steps that trigger them")
        if len(steps) < 4:
            fails.append(f"workflow {wid}: {len(steps)} task-tool write steps (>=4 required for a declared workflow)")
        step_refs = []
        for step_index, st in enumerate(steps):
            t = st.get("tool") if isinstance(st, dict) else st
            owner = st.get("owner") if isinstance(st, dict) else None
            if t and t not in task_tool_set:
                fails.append(f"workflow {wid}: step tool '{t}' is not a task tool (workflow steps must be "
                             "task_tools.py writes, not share/read tools)")
            if t:
                named_tools.add(t)
            if owner not in {"agent", "user"}:
                fails.append(f"workflow {wid}: step tool '{t}' has owner {owner!r}; owner must be agent|user")
            subject = st.get("subject") if isinstance(st, dict) else None
            if not isinstance(subject, str) or subject not in base_events:
                fails.append(f"workflow {wid}.steps[{step_index}]: subject must name exactly one declared "
                             "base event realized by this atomic write")
            else:
                event_target = (base_events.get(subject) or {}).get("target")
                if st.get("writes") != event_target:
                    fails.append(f"workflow {wid}.steps[{step_index}]: writes={st.get('writes')!r} must "
                                 f"equal base event {subject!r} target={event_target!r}")
            step_base_refs = st.get("base_policy_refs") if isinstance(st, dict) else None
            if not isinstance(step_base_refs, list) or not step_base_refs or not all(
                    isinstance(ref, str) and ref for ref in step_base_refs):
                fails.append(f"workflow {wid}.steps[{step_index}]: base_policy_refs must be a non-empty "
                             "list containing every base policy that governs this subject")
                step_base_refs = []
            elif len(set(step_base_refs)) != len(step_base_refs):
                fails.append(f"workflow {wid}.steps[{step_index}]: duplicate base_policy_refs "
                             f"{step_base_refs}")
            if isinstance(subject, str) and subject in base_events:
                expected_step_refs = {
                    ref for ref, policy in base_policies.items()
                    if subject in (policy.get("subject") or [])
                }
                if set(step_base_refs) != expected_step_refs:
                    fails.append(f"workflow {wid}.steps[{step_index}]: base_policy_refs must exactly "
                                 f"cover subject {subject!r}; missing="
                                 f"{sorted(expected_step_refs - set(step_base_refs))}, extra="
                                 f"{sorted(set(step_base_refs) - expected_step_refs)}")
            refs = normalize_policy_refs(st.get("computed_by") if isinstance(st, dict) else None,
                                         f"workflow {wid}.steps[{step_index}]")
            step_refs.append(refs)
            if len(set(refs)) != len(refs):
                fails.append(f"workflow {wid}.steps[{step_index}]: duplicate computed_by policy ids {refs}")
            for pid in refs:
                pol = ep_by_id.get(pid)
                if not pol:
                    fails.append(f"workflow {wid}.steps[{step_index}]: computed_by names unknown policy '{pid}'")
                elif pol.get("target_tool") != t:
                    fails.append(f"workflow {wid}.steps[{step_index}]: policy '{pid}' targets "
                                 f"'{pol.get('target_tool')}', not this step's tool '{t}'")
                elif subject not in (pol.get("subject") or []):
                    fails.append(f"workflow {wid}.steps[{step_index}]: policy '{pid}' does not govern "
                                 f"this step's exact base subject {subject!r}")

        dataflow = wf.get("dataflow")
        if not isinstance(dataflow, list):
            fails.append(f"workflow {wid}: dataflow must be a list (use [] only when no later step "
                         "consumes an earlier step's object or state)")
            dataflow = []
        seen_links = set()
        for link_index, raw_link in enumerate(dataflow):
            link = raw_link if isinstance(raw_link, dict) else {}
            where = f"workflow {wid}.dataflow[{link_index}]"
            source_step = link.get("from_step")
            target_step = link.get("to_step")
            if (not isinstance(source_step, int) or isinstance(source_step, bool)
                    or not isinstance(target_step, int) or isinstance(target_step, bool)
                    or not (0 <= source_step < target_step < len(steps))):
                fails.append(f"{where}: from_step/to_step must satisfy 0 <= from < to < {len(steps)}")
                continue
            kind = link.get("kind")
            if kind not in {"object_binding", "state_effect"}:
                fails.append(f"{where}: kind must be object_binding|state_effect")
            source_table = link.get("source_table")
            source_field = link.get("source_field")
            if not isinstance(source_table, str) or source_table not in db_schema:
                fails.append(f"{where}: source_table {source_table!r} is not in db_schema.json")
            elif source_field not in (db_schema.get(source_table) or {}):
                fails.append(f"{where}: source_field {source_field!r} is not on {source_table!r}")
            declared_write = steps[source_step].get("writes") if isinstance(steps[source_step], dict) else None
            if source_table and declared_write != source_table:
                fails.append(f"{where}: source_table {source_table!r} must equal producer step "
                             f"writes={declared_write!r}")
            signature = (source_step, target_step, kind, source_table, source_field)
            if signature in seen_links:
                fails.append(f"{where}: duplicate dataflow link {signature}")
            seen_links.add(signature)

            bindings = link.get("consumer_bindings")
            if not isinstance(bindings, list):
                fails.append(f"{where}: consumer_bindings must be a list")
                bindings = []
            if kind == "object_binding" and not bindings:
                fails.append(f"{where}: object_binding requires at least one consumer binding")
            if kind == "state_effect" and bindings:
                fails.append(f"{where}: state_effect carries state, not an action argument; "
                             "consumer_bindings must be []")
            for binding_index, raw_binding in enumerate(bindings):
                binding = raw_binding if isinstance(raw_binding, dict) else {}
                bwhere = f"{where}.consumer_bindings[{binding_index}]"
                if not isinstance(binding.get("action_arg"), str) or not binding.get("action_arg"):
                    fails.append(f"{bwhere}: action_arg must be a non-empty task-tool parameter")
                role = binding.get("role")
                if role not in {"direct", "authorization"}:
                    fails.append(f"{bwhere}: role must be direct|authorization")
                if role == "authorization":
                    policy = base_policies.get(binding.get("policy_id"))
                    if not policy:
                        fails.append(f"{bwhere}: authorization policy_id must name a base policy")
                        continue
                    consumer_step = steps[target_step] if isinstance(steps[target_step], dict) else {}
                    if binding.get("policy_id") not in (consumer_step.get("base_policy_refs") or []):
                        fails.append(f"{bwhere}: authorization policy must be in the consumer step's "
                                     "base_policy_refs")
                    eligibility = {
                        gate.get("id"): gate for gate in (policy.get("eligibility") or [])
                        if isinstance(gate, dict) and gate.get("id")
                    }
                    gate = eligibility.get(binding.get("eligibility_id"))
                    if not gate:
                        fails.append(f"{bwhere}: eligibility_id must name a gate of the base policy")
                    else:
                        if consumer_step.get("subject") not in (gate.get("applies_to") or []):
                            fails.append(f"{bwhere}: eligibility gate does not apply to consumer subject "
                                         f"{consumer_step.get('subject')!r}")
                        allowed_gate_fields = {
                            field for group in ((gate.get("evidence_contract") or {}).get("correlation_keys") or [])
                            if isinstance(group, list) for field in group
                        }
                        if binding.get("gate_field") not in allowed_gate_fields:
                            fails.append(f"{bwhere}: gate_field {binding.get('gate_field')!r} is not a "
                                         "declared correlation key of that eligibility gate")
                        expected_arg = ((gate.get("evidence_contract") or {}).get("action_bindings") or {}).get(
                            binding.get("gate_field")
                        )
                        if binding.get("action_arg") != expected_arg:
                            fails.append(f"{bwhere}: action_arg {binding.get('action_arg')!r} must equal "
                                         f"the gate's canonical action binding {expected_arg!r}")
            establishes_gates = link.get("establishes_gates")
            if kind == "state_effect":
                if not isinstance(establishes_gates, list) or not establishes_gates:
                    fails.append(f"{where}: state_effect must declare a non-empty establishes_gates list "
                                 "tying the changed state to every affected consumer base eligibility")
                    establishes_gates = []
                consumer_step = steps[target_step] if isinstance(steps[target_step], dict) else {}
                seen_established_gates = set()
                for gate_index, raw_established_gate in enumerate(establishes_gates):
                    establishes_gate = raw_established_gate if isinstance(raw_established_gate, dict) else {}
                    ewhere = f"{where}.establishes_gates[{gate_index}]"
                    policy_id = establishes_gate.get("policy_id")
                    eligibility_id = establishes_gate.get("eligibility_id")
                    gate_key = (policy_id, eligibility_id)
                    if gate_key in seen_established_gates:
                        fails.append(f"{ewhere}: duplicate gate {gate_key}")
                    seen_established_gates.add(gate_key)
                    policy = base_policies.get(policy_id)
                    if not policy:
                        fails.append(f"{ewhere}: policy_id must name a base policy")
                    else:
                        if policy_id not in (consumer_step.get("base_policy_refs") or []):
                            fails.append(f"{ewhere}: policy must be in the consumer "
                                         "step's base_policy_refs")
                        gates = {
                            gate.get("id"): gate for gate in (policy.get("eligibility") or [])
                            if isinstance(gate, dict) and gate.get("id")
                        }
                        gate = gates.get(eligibility_id)
                        if not gate:
                            fails.append(f"{ewhere}: eligibility_id must name a gate "
                                         "of the base policy")
                        else:
                            if consumer_step.get("subject") not in (gate.get("applies_to") or []):
                                fails.append(f"{ewhere}: gate does not apply to consumer "
                                             f"subject {consumer_step.get('subject')!r}")
                            expected_field = f"{source_table}.{source_field}"
                            if establishes_gate.get("evidence_field") != expected_field:
                                fails.append(f"{ewhere}: evidence_field must equal the "
                                             f"changed source field {expected_field!r}")
                            if expected_field not in (gate.get("evidence_fields") or []):
                                fails.append(f"{ewhere}: changed source field "
                                             f"{expected_field!r} is not evidence for that gate")
                            authority = ((gate.get("evidence_contract") or {}).get("authority"))
                            if authority not in {"system_record", "mixed"}:
                                fails.append(f"{ewhere}: a prior DB state effect can only "
                                             "establish a system_record or mixed-authority gate")
                expected_field = f"{source_table}.{source_field}"
                expected_established_gates = {
                    (policy_id, gate.get("id"))
                    for policy_id in (consumer_step.get("base_policy_refs") or [])
                    for gate in ((base_policies.get(policy_id) or {}).get("eligibility") or [])
                    if isinstance(gate, dict)
                    and consumer_step.get("subject") in (gate.get("applies_to") or [])
                    and expected_field in (gate.get("evidence_fields") or [])
                }
                if seen_established_gates != expected_established_gates:
                    fails.append(f"{where}: establishes_gates must exactly cover consumer gates whose "
                                 f"evidence uses {expected_field!r}; missing="
                                 f"{sorted(expected_established_gates - seen_established_gates, key=str)}, "
                                 f"extra={sorted(seen_established_gates - expected_established_gates, key=str)}")
            elif establishes_gates is not None:
                fails.append(f"{where}: establishes_gates is only valid for kind=state_effect")
        wf_step_policy_refs[wid] = step_refs
        workflow_policy_ids = {pid for refs in step_refs for pid in refs}
        if not workflow_policy_ids:
            fails.append(f"workflow {wid}: step-level computed_by must reference at least one policy")
        if not workflow_policy_ids <= declared_ep_id_set:
            fails.append(f"workflow {wid}: step-level computed_by policies {sorted(workflow_policy_ids)} must "
                         f"be a subset of declared extended_policies {sorted(declared_ep_id_set)}; "
                         "no out-of-scope policy")
        # scenario / order_rationale are GENERAL clauses too (same discipline as policy rule)
        scen = str(wf.get("scenario") or "").strip()
        orat = str(wf.get("order_rationale") or "").strip()
        for field, text in (("scenario", scen), ("order_rationale", orat)):
            for shadow in _SHADOW:
                if shadow in text.lower():
                    fails.append(f"workflow {wid}.{field}: contains task-shadow meta note '{shadow}' — "
                                 "a general SOP clause knows no specific task")
        if not scen or len(scen) < 30:
            fails.append(f"workflow {wid}: scenario too thin ({len(scen)} chars) — it must state the SOP's "
                         "applicability (which holdings, in what state/condition, ending in what terminal state)")
        elif ("→" in scen or "->" in scen):
            fails.append(f"workflow {wid}: scenario restates the step sequence (arrow chain) — the order lives "
                         "in steps; scenario must describe the applicable business situation instead")
        if not orat or len(orat) < 80:
            fails.append(f"workflow {wid}: order_rationale too thin ({len(orat)} chars) — it must justify EACH "
                         "adjacent pair (step k before k+1) with the policy clause it rests on and what breaks "
                         "if swapped; a bare 'wrong if reordered' is a conclusion, not a justification")

    # ---- every defined task tool must be NAMED in extended.yaml (the structured KB) ----
    # extended.yaml IS the KB the agent reads to discover a hidden tool; a task tool named by
    # no extended_policy.target_tool and no workflow step is undiscoverable dead code.
    for tn in sorted(task_tool_set):
        if tn not in named_tools:
            fails.append(f"task tool '{tn}' is named by no extended_policy.target_tool and no workflow step "
                         "in extended.yaml — an agent could never discover/unlock it")

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

    wf_by_id = {wf.get("id"): wf for wf in wfs}

    # ---- every task closes its own policy -> computation -> exact GT call ----
    # The workflow task has an additional step-level closure below; local tasks do
    # not participate in workflow sequence matching.
    # ---- prerequisite: policy-side declarations (structure, refs, prose, acyclicity) ----
    prereq_utils.validate_declarations(extended, base_policies, task_tool_set, fails)
    prereq_idx = prereq_utils.problem_index(extended)
    prereq_out = {}
    for _oid, _okind, _node in prereq_utils.owners(extended):
        prereq_out[_oid] = [e.get("problem") for e in (_node.get("prerequisite") or [])
                            if isinstance(e, dict) and e.get("problem")]

    all_used_policies = set()
    scope_by_task = {}
    workflow_tool_set = {st.get("tool") for wf in wfs for st in (wf.get("steps") or [])
                         if isinstance(st, dict) and st.get("tool")}
    for tp, tk in loaded_tasks:
        tid = os.path.basename(tp)
        scope = tk.get("charter_scope") or {}
        claimed = scope.get("workflows") or []
        if not isinstance(claimed, list):
            fails.append(f"task {tid}: charter_scope.workflows must be a list")
            claimed = []
        if len(claimed) > 1 or any(wid not in wf_by_id for wid in claimed):
            fails.append(f"task {tid}: charter_scope.workflows must be [] or the one known workflow id, got {claimed}")
        if len(set(claimed)) != len(claimed):
            fails.append(f"task {tid}: charter_scope.workflows contains duplicates {claimed}")
        actions = tk.get("evaluation_criteria") or []
        calls = gold_task_tool_calls(actions, task_tool_set)
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
        if tk.get("required_documents") != scope_pids:
            fails.append(f"policy-closure {tid}: required_documents must exactly equal "
                         "charter_scope.extended_policies in the same order")
        if not claimed and set(scope_tools) & workflow_tool_set:
            fails.append(f"workflow-guidance {tid}: non-workflow task uses workflow tool(s) "
                         f"{sorted(set(scope_tools) & workflow_tool_set)}")
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
            prereq_utils.check_task_tree(tid, root, set(scope_pids) | set(claimed), extended, fails)

        all_used_policies.update(set(scope_pids))
        scope_by_task[tid] = {"extended_policies": set(scope_pids),
                              "workflows": set(claimed), "task_tools": set(scope_tools)}

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
                "workflows": set(prior_scope.get("workflows") or []),
                "task_tools": set(prior_scope.get("task_tools") or []),
            }
            for key in ("extended_policies", "workflows", "task_tools"):
                overlap = selected_scope.get(key, set()) & prior_assets[key]
                if overlap:
                    fails.append(f"charter_scope: selected task {selected_tid} overlaps completed task "
                                 f"{os.path.basename(prior_tp)} on {key} {sorted(overlap)} — "
                                 "redesign the selected task before continuing")

    # ---- exactly one task closes workflow -> policy -> computation -> exact GT call ----
    workflow_guided_tasks = 0
    for tp, tk in loaded_tasks:
        tid = os.path.basename(tp)
        scope = tk.get("charter_scope") or {}
        claimed = scope.get("workflows") or []
        sole_wid = wf_ids[0] if len(wf_ids) == 1 else None
        if claimed and claimed != ([sole_wid] if sole_wid else []):
            fails.append(f"workflow-guidance {tid}: charter_scope.workflows must be exactly "
                         f"{[sole_wid] if sole_wid else []}, got {claimed}")
        expected = []
        unknown = []
        for wid in claimed:
            wf = wf_by_id.get(wid)
            if not wf:
                unknown.append(wid)
                continue
            expected.extend((st.get("tool"), st.get("owner"))
                            for st in (wf.get("steps") or []) if isinstance(st, dict))
        if unknown:
            fails.append(f"workflow-guidance {tid}: charter_scope.workflows names unknown ids {unknown}")
            continue
        actions = tk.get("evaluation_criteria") or []
        calls = gold_task_tool_calls(actions, task_tool_set)
        actual = [(tool, owner) for tool, owner, _ in calls]
        if claimed and actual != expected:
            fails.append(f"workflow-guidance {tid}: GT task-tool sequence {actual} != claimed workflow "
                         f"steps {expected}; tool, owner, and order must match exactly")
            continue
        if len(claimed) != 1:
            continue

        wid = claimed[0]
        step_refs = wf_step_policy_refs.get(wid, [])
        action_to_workflow_step = {action_index: i for i, (_, _, action_index) in enumerate(calls)}
        comps = tk.get("computations") or []
        comp_pids = [c.get("policy_id") for c in comps if isinstance(c, dict) and c.get("policy_id")]
        scope_pids = scope.get("extended_policies") or []
        scope_tools = scope.get("task_tools") or []
        workflow_pids = [pid for refs in step_refs for pid in refs]
        all_pid_set = set(scope_pids)

        if len(set(scope_pids)) != len(scope_pids):
            fails.append(f"policy-closure {tid}: charter_scope.extended_policies has duplicates {scope_pids}")
        if set(scope_pids) != all_pid_set:
            fails.append(f"policy-closure {tid}: charter_scope.extended_policies {sorted(set(scope_pids))} must "
                         f"equal this task's policy scope {sorted(all_pid_set)}")
        if set(comp_pids) != all_pid_set:
            fails.append(f"policy-closure {tid}: computations policy ids {sorted(set(comp_pids))} must equal "
                         f"this task's policy scope {sorted(all_pid_set)}")
        if set(workflow_pids) != all_pid_set:
            fails.append(f"policy-closure {tid}: workflow step computed_by ids {sorted(set(workflow_pids))} must "
                         f"equal this task's policy scope {sorted(all_pid_set)}")
        if tk.get("required_documents") != scope_pids:
            fails.append(f"policy-closure {tid}: required_documents must exactly equal "
                         "charter_scope.extended_policies in the same order")
        actual_tools = []
        for tool, _owner, _action_index in calls:
            if tool not in actual_tools:
                actual_tools.append(tool)
        if scope_tools != actual_tools:
            fails.append(f"policy-closure {tid}: charter_scope.task_tools must equal the GT workflow tools "
                         f"in first-use order; got {scope_tools}, expected {actual_tools}")

        actual_computation_pairs = set()
        for comp_index, comp in enumerate(comps):
            if not isinstance(comp, dict):
                fails.append(f"policy-closure {tid}: computations[{comp_index}] must be an object")
                continue
            pid = comp.get("policy_id")
            pol = ep_by_id.get(pid)
            step = comp.get("step")
            if not isinstance(step, int) or isinstance(step, bool) or not (0 <= step < len(actions)):
                fails.append(f"policy-closure {tid}: computation '{pid}' has invalid evaluation action step {step!r}")
                continue
            workflow_step = action_to_workflow_step.get(step)
            if workflow_step is None:
                fails.append(f"policy-closure {tid}: computation '{pid}' step {step} is not a GT task-tool call")
                continue
            refs_here = step_refs[workflow_step] if workflow_step < len(step_refs) else []
            call_tool = calls[workflow_step][0]
            if pid not in refs_here:
                fails.append(f"policy-closure {tid}: computation '{pid}' occurs at GT action {step}, but workflow "
                             f"step {workflow_step} computed_by is {refs_here}")
            if pol:
                if pol.get("target_tool") != call_tool:
                    fails.append(f"policy-closure {tid}: computation '{pid}' occurs on tool '{call_tool}', but "
                                 f"the policy targets '{pol.get('target_tool')}'")
                if comp.get("arg") != pol.get("computes"):
                    fails.append(f"policy-closure {tid}: computation '{pid}' arg '{comp.get('arg')}' != policy "
                                 f"computes '{pol.get('computes')}'")
            actual_computation_pairs.add((workflow_step, pid))

        for workflow_step, refs in enumerate(step_refs):
            for pid in refs:
                if (workflow_step, pid) not in actual_computation_pairs:
                    action_index = calls[workflow_step][2] if workflow_step < len(calls) else "?"
                    fails.append(f"policy-closure {tid}: workflow step {workflow_step} computed_by '{pid}' has no "
                                 f"matching computation at GT call action {action_index}")
        workflow_guided_tasks += 1
    sole_wid = wf_ids[0] if len(wf_ids) == 1 else None
    workflow_claimed_tasks = sum(
        1 for _tp, tk in loaded_tasks
        if sole_wid and (tk.get("charter_scope") or {}).get("workflows") == [sole_wid]
    )
    if task_mode:
        selected_claims = [
            (tk.get("charter_scope") or {}).get("workflows") or []
            for _tp, tk in loaded_tasks
        ]
        selected_claims_workflow = bool(selected_claims and selected_claims[0])
        if selected_claims_workflow and (workflow_claimed_tasks != 1 or workflow_guided_tasks != 1):
            fails.append(f"workflow-guidance: selected task claims the workflow but does not close it "
                         f"(claims={workflow_claimed_tasks}, valid={workflow_guided_tasks})")
    else:
        if workflow_claimed_tasks != 1:
            fails.append(f"workflow-guidance: expected exactly one task claiming the workflow, found "
                         f"{workflow_claimed_tasks}")
        if workflow_guided_tasks != 1:
            fails.append(f"workflow-guidance: expected exactly one valid workflow-guided task, found "
                         f"{workflow_guided_tasks}")
        if all_used_policies != declared_ep_id_set:
            fails.append(f"policy coverage: M tasks use {sorted(all_used_policies)}, expected all extended policies "
                         f"{sorted(declared_ep_id_set)}")
    scope_items = list(scope_by_task.items())
    for i, (ta, sa) in enumerate(scope_items):
        for tb, sb in scope_items[i + 1:]:
            for key in ("extended_policies", "workflows", "task_tools"):
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
          f"workflows={len(wfs)}, task_tools={len(task_tool_set)}, tasks={task_count}{mode_label}, "
          f"workflow_guided_tasks={workflow_guided_tasks}, no_handoff=True)")
    if fails:
        print("  [FAIL]")
        for f in fails[:50]:
            print("   -", f)
        print("EXTENDED NOT OK")
        sys.exit(1)
    if task_mode:
        print("  [PASS] selected task closes its policy/tool scope; shared charter is structurally valid "
              "(difficulty-wide workflow/cardinality/coverage deferred to final run)")
    else:
        print("  [PASS] compatible charter; every policy has a real cross-category factor; one task "
              "closes the unique workflow and all policies are covered across the suite")
    print("EXTENDED OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
