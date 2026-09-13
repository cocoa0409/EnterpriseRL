"""Blueprint gate: verify the scenario constitution under env/<scenario>/blueprint/
is structurally COMPLETE and internally CONSISTENT.

WHAT THIS ENFORCES (the machine-checkable half of the skill's gate):

  Layout      blueprint/{blueprint.yaml, db_schema.json, share_tools.py,
              products/<category>.yaml (>=1).
  Schema      {table: {field: type-spec}} — every table's first field is its
              primary id (`_id` postfix); every field is typed exactly one of
              id / enum / fixed_format / verbatim; enum fields declare their
              values (holding status == lifecycle.states, variant_name ==
              official variant names, event_type domains drawn from and
              covering the category's declared event families, handoff
              reason exactly POLICY_NOT_COVERED + CUSTOMER_REQUESTED);
              fixed_format fields declare their format; `customers` exists;
              the two log tables registered in blueprint.yaml `logs` exist;
              holdings carry customer_id + variant/status fields; event
              tables carry customer_id, event_type and the holding table's
              primary id (child rows are joinable to their parents).
  Charter     per category: binding tables exist and are claimed by exactly
              one category (holding + event tables mandatory, intake tables
              optional — carrying customer_id); lifecycle states/transitions
              well-formed; variants >=6, official names globally unique,
              ranks 1..n, and EVERY variant assigns EVERY parameter_schema
              key with a non-null value (zero nulls, zero defaults);
              parameter_schema >=48 params; >=6 event families, each with a
              grain and a distinguish_by field set (drawn from its fields)
              so two real occurrences on one holding can never collapse
              into identical rows; event `fields` exist on a bound event
              table; accounts are first-class quantities (key+unit+meaning):
              quantity events post signed deltas (account+direction), every
              account has >=1 in-event and >=1 out-event, and holding
              quantity_fields bind a field to its account; measures are
              named window statistics (window+measure);
              >=8 policies in ONE unified shape (id / subject event list /
              rule / eligibility / params / measures); eligibility is explicit
              even when empty, and each non-empty gate binds a verbatim rule
              condition to pre-action authority, object-correlation fields and
              (for time gates) one frozen clock/anchor/counting/direction/boundary contract;
              state gates additionally pin the gated enum field and the proper
              subset of states they admit, and every write that can occur in a
              state — a create landing in the lifecycle entry state, a
              transition landing in its `to` state, and anything a trigger
              fires immediately after — must be able to clear that gate;
              a declared measure is read by some policy of its category;
              every event governed by >=1 policy,
              the multi-holding charter (<category>_agg_multi_holding)
              present exactly once, every
              per_tier table covers every variant, and at least one per_tier
              actually DIFFERS across tiers (tier differentiation is real,
              not decorative).
  Ids         one namespace: every policy/measure id
              and every event type is unique across the whole scenario, and
              carries its owner's prefix.
  Difficulty  a claim is exactly categories + event_types: primary
              categories exist and are pairwise DISJOINT across
              difficulties (the one disjointness axis — event types are
              category-namespaced and inherit disjointness); event_types
              drawn from the claimed categories' declared event types;
              scenario map is a function of N: #categories >= #difficulties
              + 2 (surplus categories are the distractors); summaries >=4
              sentences.

Prose-quality requirements (background sentence range, realism of values,
domain-scope-only summaries) stay with the author: they surface here as
warnings at most, never as passes.

Usage (from the repo root):
  python3 skills/erl-scenario-blueprint/scripts/check_blueprint.py env/<scenario>

Needs PyYAML (the runtime already depends on it). Files are parsed, never executed.
Exit 0 = BLUEPRINT OK; exit 1 = a structural requirement is violated.
"""
import json
import os
import re
import sys
from typing import NoReturn

import yaml

FAILS = []
WARNS = []


def fail(msg):
    FAILS.append(msg)


def warn(msg):
    WARNS.append(msg)


def sentences(text):
    """Count sentences in prose: split on sentence terminators,
    keep parts with real content (>=6 chars — a few words)."""
    flat = " ".join(str(text or "").split())
    parts = re.split(r"(?<=[.!?])\s*", flat)
    return [p for p in parts if len(p.strip()) >= 6]


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:  # noqa: BLE001
        fail(f"{os.path.basename(path)}: cannot parse: {e}")
        return None


def as_list(x):
    return x if isinstance(x, list) else []


def as_dict(x):
    return x if isinstance(x, dict) else {}


KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def check_per_tier(where, per_tier, variant_names):
    """A per_tier table must cover EXACTLY the category's variants."""
    if not isinstance(per_tier, dict) or not per_tier:
        fail(f"{where}: per_tier must be a non-empty mapping of variant name -> params")
        return
    got, want = set(per_tier), set(variant_names)
    if got != want:
        miss, extra = sorted(want - got), sorted(got - want)
        fail(f"{where}: per_tier must cover every variant exactly"
             + (f"; missing {miss}" if miss else "") + (f"; unknown {extra}" if extra else ""))


def tier_values_differ(per_tier, var_params=None):
    """Whether per_tier rows actually differ across tiers. "=<param>" references are
    resolved against the variants' catalog parameters first — a row of references is
    differentiated exactly when the referenced parameters are."""
    rows = []
    for name, vals in as_dict(per_tier).items():
        row = {}
        for k, v in as_dict(vals).items():
            if isinstance(v, str) and v.startswith("=") and var_params:
                v = as_dict(var_params.get(name)).get(v[1:], v)
            row[k] = v
        rows.append(json.dumps(row, sort_keys=True, default=str))
    return len(set(rows)) > 1


def main():
    if len(sys.argv) < 2:
        print("usage: check_blueprint.py env/<scenario>")
        sys.exit(2)
    root = sys.argv[1].rstrip("/")
    scen = os.path.basename(root)
    bdir = os.path.join(root, "blueprint")
    pdir = os.path.join(bdir, "products")

    print(f"🔎 blueprint constitution check  ({scen})")

    # ---------------------------------------------------------------- layout
    required = ["blueprint.yaml", "db_schema.json", "share_tools.py"]
    for fn in required:
        if not os.path.exists(os.path.join(bdir, fn)):
            fail(f"missing blueprint/{fn}")
    if not os.path.isdir(pdir):
        fail("missing blueprint/products/ directory")
    cat_files = sorted(f for f in os.listdir(pdir) if f.endswith(".yaml")) if os.path.isdir(pdir) else []
    if os.path.isdir(pdir) and not cat_files:
        fail("blueprint/products/ has no <category>.yaml file")
    if FAILS:
        finish()

    # ---------------------------------------------------------------- schema
    try:
        schema = json.load(open(os.path.join(bdir, "db_schema.json")))
    except Exception as e:  # noqa: BLE001
        fail(f"db_schema.json: cannot parse: {e}")
        finish()
    FIELD_TYPES = ("id", "enum", "fixed_format", "verbatim")
    if not isinstance(schema, dict) or not all(isinstance(v, dict) for v in schema.values()):
        fail("db_schema.json must be a {table: {field: type-spec}} map — every field is typed")
        finish()
    for t, fields in schema.items():
        if not fields or not str(next(iter(fields))).endswith("_id"):
            fail(f"db_schema.json: table '{t}' must lead with its primary id (`_id` postfix field)")
        for f, spec in fields.items():
            spec = as_dict(spec)
            ft = spec.get("type")
            if ft not in FIELD_TYPES:
                fail(f"db_schema.json: field '{t}.{f}' needs type in {FIELD_TYPES}")
                continue
            if ft == "enum" and not as_list(spec.get("values")):
                fail(f"db_schema.json: enum field '{t}.{f}' must declare non-empty values")
            if ft == "fixed_format" and not str(spec.get("format") or "").strip():
                fail(f"db_schema.json: fixed_format field '{t}.{f}' must declare its format")
            if not str(spec.get("meaning") or "").strip():
                fail(f"db_schema.json: field '{t}.{f}' lacks meaning "
                     "(the column's semantics — the authoritative gloss)")
    if "customers" not in schema:
        fail("db_schema.json: mandatory table 'customers' is missing")

    # ---------------------------------------------------------- blueprint.yaml
    bp = load_yaml(os.path.join(bdir, "blueprint.yaml")) or {}
    if bp.get("name") != scen:
        fail(f"blueprint.yaml: name '{bp.get('name')}' must equal the scenario directory '{scen}'")
    if not str(bp.get("company") or "").strip():
        fail("blueprint.yaml: company is empty")
    n_bg = len(sentences(bp.get("background")))
    if not 10 <= n_bg <= 20:
        warn(f"background counts ~{n_bg} sentences (target 10-20)")
    logs = as_dict(bp.get("logs"))
    for k in ("verification_log_table", "handoff_log_table"):
        t = logs.get(k)
        if not t:
            fail(f"blueprint.yaml: logs.{k} is missing")
        elif t not in schema:
            fail(f"blueprint.yaml: logs.{k} '{t}' is not a table in db_schema.json")
    hlt = logs.get("handoff_log_table")
    if hlt in schema:
        rspec = as_dict(schema[hlt].get("reason"))
        if rspec.get("type") == "enum" and \
                set(as_list(rspec.get("values"))) != {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}:
            fail(f"db_schema.json: handoff table '{hlt}'.reason enum must be exactly "
                 "POLICY_NOT_COVERED + CUSTOMER_REQUESTED")

    # ------------------------------------------------------------- categories
    ids_seen = {}      # id/event-type -> file (one global namespace)
    def claim_id(key, where):
        if key in ids_seen:
            fail(f"{where}: id '{key}' already defined in {ids_seen[key]}")
        else:
            ids_seen[key] = where

    categories = {}    # cat_key -> {"events": set, "variants": set}
    all_variant_names = {}
    tables_claimed = {}
    all_states = set()
    all_pschema = set()  # union of every category's parameter_schema keys
    all_evt_fields = set()   # union of event-table columns
    all_hold_fields = set()  # union of holding-table columns
    all_accounts = set()     # union of account keys
    all_measures = set()     # union of category measure ids   # union of every category's lifecycle states
    pending_triggers = []  # (file, source event_type, target "cat:evt") — validated after the loop
    pending_state_gates = []  # (file, cat, policy, gate, where, table, allowed, applies) — phase 2
    for fn in cat_files:
        path = os.path.join(pdir, fn)
        doc = load_yaml(path)
        if not isinstance(doc, dict):
            fail(f"{fn}: not a mapping")
            continue
        cat = doc.get("category")
        if cat != fn[:-len(".yaml")] or not (isinstance(cat, str) and KEY_RE.match(cat)):
            fail(f"{fn}: category key '{cat}' must be snake_case and equal the filename stem")
            continue
        if not str(doc.get("display_name") or "").strip():
            fail(f"{fn}: display_name is empty")

        # binding
        b = as_dict(doc.get("binding"))
        categories.setdefault(cat, {"events": set(), "variants": set()})["binding"] = b
        ht = b.get("holding_table")
        vf = b.get("variant_field") or "variant_name"
        sf = b.get("status_field") or "status"
        holding_pk = None
        if ht not in schema:
            fail(f"{fn}: binding.holding_table '{ht}' not in db_schema.json")
        else:
            if ht in tables_claimed:
                fail(f"{fn}: table '{ht}' already bound by {tables_claimed[ht]}")
            tables_claimed[ht] = fn
            holding_pk = next(iter(schema[ht]))
            for need in ("customer_id", vf, sf):
                if need not in schema[ht]:
                    fail(f"{fn}: holding table '{ht}' lacks field '{need}'")
        ets = as_list(b.get("event_tables"))
        if not ets:
            fail(f"{fn}: binding.event_tables must list at least one event table")
        if ht in schema:
            all_hold_fields |= set(schema[ht])
        qfields = as_dict(b.get("quantity_fields"))
        for qf in qfields:
            if ht in schema and qf not in schema[ht]:
                fail(f"{fn}: quantity field '{qf}' not on holding table '{ht}'")
        event_fields = set()
        event_field_specs = {}
        for et in ets:
            if et not in schema:
                fail(f"{fn}: binding event table '{et}' not in db_schema.json")
                continue
            if et in tables_claimed:
                fail(f"{fn}: table '{et}' already bound by {tables_claimed[et]}")
            tables_claimed[et] = fn
            event_fields |= set(schema[et])
            all_evt_fields |= set(schema[et])
            event_field_specs.update({f: as_dict(sp) for f, sp in schema[et].items()})
            for need in ("customer_id", "event_type", holding_pk):
                if need and need not in schema[et]:
                    fail(f"{fn}: event table '{et}' lacks field '{need}' "
                         "(child rows must join back to customer and holding)")
        for it in as_list(b.get("intake_tables")):
            if it not in schema:
                fail(f"{fn}: binding intake table '{it}' not in db_schema.json")
                continue
            if it in tables_claimed:
                fail(f"{fn}: table '{it}' already bound by {tables_claimed[it]}")
            tables_claimed[it] = fn
            if "customer_id" not in schema[it]:
                fail(f"{fn}: intake table '{it}' lacks field 'customer_id'")

        # lifecycle
        lc = as_dict(doc.get("lifecycle"))
        categories.setdefault(cat, {"events": set(), "variants": set()})["lifecycle"] = lc
        states = as_list(lc.get("states"))
        all_states |= set(states)
        if len(states) < 2 or len(set(states)) != len(states):
            fail(f"{fn}: lifecycle.states must be >=2 unique states")
        if not as_list(lc.get("transitions")):
            fail(f"{fn}: lifecycle.transitions is empty")
        for tr in as_list(lc.get("transitions")):
            tr = as_dict(tr)
            if tr.get("from") not in states or tr.get("to") not in states:
                fail(f"{fn}: transition {tr.get('from')}->{tr.get('to')} uses undeclared states")
            if tr.get("by") not in ("agent", "user", "system"):
                fail(f"{fn}: transition {tr.get('from')}->{tr.get('to')} needs by: agent|user|system")

        # accounts (first-class quantities every policy-touched amount must live in)
        accounts = {}
        all_accounts |= {str(as_dict(a).get("key") or "") for a in as_list(doc.get("accounts"))}
        for a in as_list(doc.get("accounts")):
            a = as_dict(a)
            ak = str(a.get("key") or "")
            if not KEY_RE.match(ak):
                fail(f"{fn}: account key '{ak}' must be snake_case")
                continue
            if ak in accounts:
                fail(f"{fn}: account '{ak}' declared twice")
            accounts[ak] = {"in": 0, "out": 0}
            if not str(a.get("unit") or "").strip():
                fail(f"{fn}: account '{ak}' lacks unit")
            if not str(a.get("meaning") or "").strip():
                fail(f"{fn}: account '{ak}' lacks meaning")
        for qf, qa in qfields.items():
            if qa not in accounts:
                fail(f"{fn}: quantity field '{qf}' maps to undeclared account '{qa}'")

        # parameter schema + variants
        pschema = as_dict(doc.get("parameter_schema"))
        all_pschema |= set(pschema)
        if not pschema:
            fail(f"{fn}: parameter_schema is empty")
        elif len(pschema) < 48:
            fail(f"{fn}: parameter_schema has {len(pschema)} params (<48 — a mature product's "
                 "real tunable dimensions run to dozens: gates, fees, rates, limits, deadlines, "
                 "quotas, benefit switches, override/exemption triggers, per-tier ladders — not a "
                 "handful of representative numbers. Each param backs a policy/event family; walk "
                 "param -> policy -> event -> distinguishable row and make sure every occurrence it "
                 "drives is recordable (grain/distinguish_by/event fields), no dangling params)")
        variants = as_list(doc.get("variants"))
        if len(variants) < 6:
            fail(f"{fn}: {len(variants)} variants — the ladder needs >=6 tiers")
        vnames, ranks = [], []
        for v in variants:
            v = as_dict(v)
            nm = str(v.get("name") or "").strip()
            if not nm:
                fail(f"{fn}: a variant has no official name")
                continue
            if nm in all_variant_names:
                fail(f"{fn}: variant name '{nm}' already used in {all_variant_names[nm]}")
            all_variant_names[nm] = fn
            vnames.append(nm)
            ranks.append(v.get("rank"))
            if "entry_gate" not in v:
                fail(f"{fn}: variant '{nm}' lacks entry_gate")
            params = as_dict(v.get("parameters"))
            missing = sorted(set(pschema) - set(params))
            extra = sorted(set(params) - set(pschema))
            nulls = sorted(k for k, val in params.items() if val is None)
            if missing:
                fail(f"{fn}: variant '{nm}' misses parameter(s) {missing} (full assignment required)")
            if extra:
                fail(f"{fn}: variant '{nm}' sets parameter(s) {extra} not in parameter_schema")
            if nulls:
                fail(f"{fn}: variant '{nm}' has null parameter(s) {nulls} (zero nulls allowed)")
        if vnames and sorted(r for r in ranks if isinstance(r, int)) != list(range(1, len(vnames) + 1)):
            fail(f"{fn}: variant ranks must be exactly 1..{len(vnames)}")

        # measures (named window statistics — the raw material of history-dependent policies)
        measure_ids = set()
        consumed_measures = set()   # ids some policy of this category actually reads
        for m in as_list(doc.get("measures")):
            m = as_dict(m)
            mid = str(m.get("id") or "")
            if not mid.startswith(f"{cat}_msr_"):
                fail(f"{fn}: measure id '{mid}' must start with '{cat}_msr_'")
                continue
            claim_id(mid, fn)
            measure_ids.add(mid)
            all_measures.add(mid)
            for need in ("window", "measure"):
                if not str(m.get(need) or "").strip():
                    fail(f"{fn}: measure '{mid}' lacks '{need}'")

        # events (ALL world writes: stream rows into event tables + holding-table CRUD)
        events = as_list(doc.get("events"))
        if len(events) < 6:
            fail(f"{fn}: {len(events)} event famil(y|ies) — >=6 event families required")
        legal_transitions = {(as_dict(t).get("from"), as_dict(t).get("to"))
                             for t in as_list(lc.get("transitions"))}
        create_events = 0
        for ev in events:
            ev = as_dict(ev)
            et = str(ev.get("type") or "")
            if not et.startswith(f"{cat}_"):
                fail(f"{fn}: event type '{et}' must start with '{cat}_'")
            claim_id(et, fn)
            categories.setdefault(cat, {"events": set(), "variants": set()})["events"].add(et)
            categories[cat].setdefault("event_defs", {})[et] = ev
            if not str(ev.get("meaning") or "").strip():
                fail(f"{fn}: event '{et}' has no meaning")
            if "triggers" not in ev:
                fail(f"{fn}: event '{et}' must declare triggers — register the consequences that "
                     "necessarily follow one real occurrence (cross-category allowed), or an explicit "
                     "[] when none. A missing key is a half-finished event, not 'no consequence'.")
            target = ev.get("target")
            holding_event = (target == ht)
            if target is None:
                fail(f"{fn}: event '{et}' must declare target (holding table or one of event_tables)")
            elif not holding_event and target not in ets:
                fail(f"{fn}: event '{et}' target '{target}' must be the holding table '{ht}' "
                     "or one of binding.event_tables")
            efields = as_dict(ev.get("fields"))
            if not efields:
                fail(f"{fn}: event '{et}' declares no fields")
            if holding_event:
                mut = ev.get("mutation")
                if mut is None:
                    fail(f"{fn}: holding event '{et}' must declare mutation "
                         "(create | {transition: {from,to}} | update)")
                elif mut == "create":
                    create_events += 1
                elif isinstance(mut, dict) and "transition" in mut:
                    trs = mut.get("transition")
                    trs = trs if isinstance(trs, list) else [trs]
                    for tr in trs:
                        tr = as_dict(tr)
                        if (tr.get("from"), tr.get("to")) not in legal_transitions:
                            fail(f"{fn}: holding event '{et}' transition "
                                 f"{tr.get('from')}->{tr.get('to')} is not a declared lifecycle transition")
                elif mut != "update":
                    fail(f"{fn}: holding event '{et}' mutation '{mut}' must be create | "
                         "{transition: {from,to}} | update")
                if mut == "update" and sf in efields:
                    fail(f"{fn}: update event '{et}' must not write the status field '{sf}' "
                         "— status is writable only via mutation: transition")
                if ht in schema:
                    for k in efields:
                        if k not in schema[ht]:
                            fail(f"{fn}: holding event '{et}' field '{k}' not on holding table '{ht}'")
            else:
                for k in efields:
                    if event_fields and k not in event_fields:
                        fail(f"{fn}: event '{et}' field '{k}' exists on none of the bound event tables")
                if not str(ev.get("grain") or "").strip():
                    fail(f"{fn}: event '{et}' has no grain (one row = what real-world occurrence?)")
                db = as_list(ev.get("distinguish_by"))
                if not db:
                    fail(f"{fn}: event '{et}' has no distinguish_by — two real occurrences of the "
                         "same family on one holding must differ in at least one recorded field "
                         "(identical rows collapse to one id under content hashing)")
                for k in db:
                    if k not in efields:
                        fail(f"{fn}: event '{et}' distinguish_by field '{k}' is not in its fields")
            acct, dire = ev.get("account"), ev.get("direction")
            if acct is not None:
                if acct not in accounts:
                    fail(f"{fn}: event '{et}' posts to undeclared account '{acct}'")
                elif dire not in ("in", "out"):
                    fail(f"{fn}: event '{et}' direction must be in|out (signed delta on the account)")
                else:
                    accounts[acct][dire] += 1
            elif dire is not None:
                fail(f"{fn}: event '{et}' has direction without account")
            for tg in as_list(ev.get("triggers")):
                pending_triggers.append((fn, cat, et, as_dict(tg)))
        if not create_events:
            fail(f"{fn}: no mutation: create holding event — every category needs a way "
                 "to open a holding (products have an opening path)")
        for ak, io in accounts.items():
            if not io["in"] or not io["out"]:
                fail(f"{fn}: account '{ak}' has {io['in']} in-event(s) and {io['out']} out-event(s)"
                     " — every account needs at least one of each, else the quantity is underivable")

        # policies (every policy binds >=1 declared event of its own category — it lives
        # only on the writes it governs; cross-category flows go through triggers)
        policies = as_list(doc.get("policies"))
        if len(policies) < 8:
            fail(f"{fn}: {len(policies)} polic(y|ies) — >=8 required")
        differentiated = False
        governed_events = set()
        agg_policies = 0
        charter_max = "absent"
        all_param_keys = set()   # category-wide registry: formula may reference params
        for p2 in policies:      # declared in ANY policy of this category (single source)
            pm2 = as_dict(as_dict(p2).get("params"))
            all_param_keys |= set(pm2)
            for row in as_dict(pm2.get("per_tier")).values():
                all_param_keys |= set(as_dict(row))
        for p in policies:
            p = as_dict(p)
            pid = str(p.get("id") or "")
            if not pid.startswith(f"{cat}_"):
                fail(f"{fn}: policy id '{pid}' must start with '{cat}_'")
            claim_id(pid, fn)
            if pid != f"{cat}_agg_multi_holding" and pid.startswith(f"{cat}_agg_"):
                agg_policies += 1
            subs = as_list(p.get("subject"))
            if not subs:
                fail(f"{fn}: policy '{pid}' must bind >=1 event (subject: [event_type, ...] — "
                     "policies live only on the writes they govern)")
            for et_ in subs:
                if et_ not in categories.get(cat, {}).get("events", set()):
                    fail(f"{fn}: policy '{pid}' binds undeclared event '{et_}' — bindings never "
                         "leave the home category; cross-category flows use triggers")
                else:
                    governed_events.add(et_)
            if pid == f"{cat}_agg_multi_holding":
                charter_max = as_dict(p.get("params")).get("max_per_customer", "absent")
                if charter_max != 1 and not (isinstance(charter_max, int) and charter_max > 1) \
                        and charter_max is not None:
                    fail(f"{fn}: charter '{pid}' params.max_per_customer must be an int or null (1 = single holding)")
                if not any((categories[cat].get("event_defs", {}).get(et_) or {}).get("mutation")
                           == "create" for et_ in subs):
                    fail(f"{fn}: multi-holding charter '{pid}' must bind a mutation: create "
                         "event (the write it gates)")
            rule_text = str(p.get("rule") or "").strip()
            if not rule_text:
                fail(f"{fn}: policy '{pid}' has no rule text")
            pms = as_dict(p.get("params"))

            # Eligibility is the structured shadow of the rule's PRE-ACTION gates.  It does
            # not attempt to understand the natural-language condition; it only proves that downstream
            # task authoring cannot silently drop a gate, swap its evidence object, or invent a
            # different time anchor without changing an explicit source field.
            if "eligibility" not in p:
                fail(f"{fn}: policy '{pid}' must declare eligibility (use [] when it has no "
                     "pre-action gate)")
                eligibility = []
            elif not isinstance(p.get("eligibility"), list):
                fail(f"{fn}: policy '{pid}' eligibility must be a list")
                eligibility = []
            else:
                eligibility = p.get("eligibility")
            gate_ids = set()
            allowed_gate_kinds = {"state", "time", "authorization", "dedup", "caller_fact"}
            for gate_index, raw_gate in enumerate(eligibility):
                gate = as_dict(raw_gate)
                gwhere = f"{fn}: policy '{pid}' eligibility[{gate_index}]"
                gate_id = str(gate.get("id") or "")
                if not KEY_RE.match(gate_id):
                    fail(f"{gwhere}: id {gate_id!r} must be non-empty snake_case")
                elif gate_id in gate_ids:
                    fail(f"{gwhere}: duplicate gate id {gate_id!r}")
                gate_ids.add(gate_id)
                applies = as_list(gate.get("applies_to"))
                if not applies:
                    fail(f"{gwhere}: applies_to must name at least one governed subject")
                elif not set(applies) <= set(subs):
                    fail(f"{gwhere}: applies_to {applies} must be a subset of policy subject {subs}")
                kind = gate.get("kind")
                if kind not in allowed_gate_kinds:
                    fail(f"{gwhere}: kind {kind!r} must be one of {sorted(allowed_gate_kinds)}")
                condition = str(gate.get("condition") or "").strip()
                if not condition:
                    fail(f"{gwhere}: condition is empty")
                elif condition not in rule_text:
                    fail(f"{gwhere}: condition must occur verbatim in policy.rule; structured "
                         "eligibility cannot legislate a second rule")

                evidence_fields = gate.get("evidence_fields")
                if not isinstance(evidence_fields, list) or not evidence_fields:
                    fail(f"{gwhere}: evidence_fields must be a non-empty list of table.field paths")
                    evidence_fields = []
                valid_evidence = set()
                for ref in evidence_fields:
                    if not isinstance(ref, str) or ref.count(".") != 1:
                        fail(f"{gwhere}: evidence field {ref!r} must be a table.field path")
                        continue
                    table, field = ref.split(".", 1)
                    if table not in schema or field not in as_dict(schema.get(table)):
                        fail(f"{gwhere}: evidence field {ref!r} does not exist in db_schema.json")
                        continue
                    valid_evidence.add(ref)

                evidence_contract = as_dict(gate.get("evidence_contract"))
                authority = evidence_contract.get("authority")
                if authority not in {"system_record", "caller_statement", "mixed"}:
                    fail(f"{gwhere}: evidence_contract.authority is invalid")
                if evidence_contract.get("timing") != "pre_action":
                    fail(f"{gwhere}: evidence_contract.timing must be pre_action")
                correlation_groups = evidence_contract.get("correlation_keys")
                if not isinstance(correlation_groups, list) or not correlation_groups:
                    fail(f"{gwhere}: evidence_contract.correlation_keys must be a non-empty list")
                    correlation_groups = []
                correlation_fields = set()
                for group in correlation_groups:
                    if not isinstance(group, list) or not group:
                        fail(f"{gwhere}: each correlation_keys entry must be a non-empty list")
                        continue
                    if not all(isinstance(field, str) for field in group):
                        fail(f"{gwhere}: every correlation key must be a table.field string")
                        continue
                    correlation_fields.update(group)
                    missing = set(group) - valid_evidence
                    if missing:
                        fail(f"{gwhere}: correlation key(s) {sorted(missing)} are not valid evidence_fields")
                action_bindings = evidence_contract.get("action_bindings")
                if not isinstance(action_bindings, dict) or not action_bindings:
                    fail(f"{gwhere}: evidence_contract.action_bindings must be a non-empty mapping")
                    action_bindings = {}
                if set(action_bindings) != correlation_fields:
                    fail(f"{gwhere}: action_bindings keys must exactly equal correlation key fields; "
                         f"got {sorted(action_bindings)}, expected {sorted(correlation_fields)}")
                for action_arg in action_bindings.values():
                    if not isinstance(action_arg, str) or not KEY_RE.match(action_arg):
                        fail(f"{gwhere}: action binding value {action_arg!r} must be a snake_case "
                             "future task-tool argument")

                if kind == "time":
                    temporal = as_dict(gate.get("temporal_basis"))
                    if temporal.get("clock") != "frozen_time":
                        fail(f"{gwhere}: temporal_basis.clock must be frozen_time")
                    anchor_event = str(temporal.get("anchor_event") or "").strip()
                    if not anchor_event:
                        fail(f"{gwhere}: temporal_basis.anchor_event must name the exact business event")
                    elif anchor_event not in condition:
                        fail(f"{gwhere}: temporal_basis.anchor_event must occur verbatim in condition; "
                             "the structured shadow cannot select a different clock origin")
                    anchor_source = temporal.get("anchor_source")
                    if anchor_source not in valid_evidence:
                        fail(f"{gwhere}: temporal_basis.anchor_source {anchor_source!r} must be one "
                             "of this gate's valid evidence_fields")
                    if temporal.get("relation") not in {"not_before", "not_after"}:
                        fail(f"{gwhere}: temporal_basis.relation must be not_before|not_after")
                    duration_source = str(temporal.get("duration_source") or "")
                    if duration_source.startswith("params."):
                        policy_param_keys = set(pms) - {"per_tier"}
                        for tier_params in as_dict(pms.get("per_tier")).values():
                            policy_param_keys.update(as_dict(tier_params))
                        if duration_source.split(".", 1)[1] not in policy_param_keys:
                            fail(f"{gwhere}: temporal duration {duration_source!r} is not a policy param")
                    elif duration_source.startswith("variants."):
                        if duration_source.split(".", 1)[1] not in pschema:
                            fail(f"{gwhere}: temporal duration {duration_source!r} is not a catalog param")
                    else:
                        fail(f"{gwhere}: temporal_basis.duration_source must be params.<key> or "
                             "variants.<param_key>")
                    if temporal.get("unit") not in {
                            "calendar_days", "elapsed_hours", "business_days", "calendar_months"}:
                        fail(f"{gwhere}: temporal_basis.unit is invalid")
                    counting_rule = str(temporal.get("counting_rule") or "").strip()
                    if not counting_rule:
                        fail(f"{gwhere}: temporal_basis.counting_rule must state the exact day/month "
                             "arithmetic in policy prose")
                    elif counting_rule not in rule_text:
                        fail(f"{gwhere}: temporal_basis.counting_rule must occur verbatim in policy.rule")
                    if temporal.get("boundary") not in {"inclusive", "exclusive"}:
                        fail(f"{gwhere}: temporal_basis.boundary must be inclusive|exclusive")
                elif "temporal_basis" in gate:
                    fail(f"{gwhere}: temporal_basis is only valid for kind=time")

                if kind == "state":
                    # A state gate says "only these states may be written on"; without the
                    # allowed set in structured form the constraint lives only in prose and
                    # nothing can tell whether a declared write can ever satisfy it.
                    state_c = as_dict(gate.get("state_contract"))
                    sfield = state_c.get("field")
                    if sfield not in valid_evidence:
                        fail(f"{gwhere}: state_contract.field {sfield!r} must be one of this gate's "
                             "evidence_fields — the state you gate on must be evidenced")
                    stable, _, scol = str(sfield or "").partition(".")
                    sspec = as_dict(as_dict(schema.get(stable)).get(scol))
                    domain = as_list(sspec.get("values"))
                    if sspec.get("type") != "enum":
                        fail(f"{gwhere}: state_contract.field {sfield!r} must be an enum field in "
                             "db_schema.json (a state gate ranges over a closed set)")
                    allowed_states = gate.get("allowed")
                    if allowed_states is None:
                        allowed_states = state_c.get("allowed")
                    if not isinstance(allowed_states, list) or not allowed_states:
                        fail(f"{gwhere}: state_contract.allowed must be a non-empty list of the "
                             "states this gate admits")
                        allowed_states = []
                    elif domain:
                        outside = [v for v in allowed_states if v not in domain]
                        if outside:
                            fail(f"{gwhere}: state_contract.allowed {outside} outside the enum "
                                 f"domain of {sfield!r}")
                    if allowed_states and domain and set(allowed_states) == set(domain):
                        fail(f"{gwhere}: state_contract.allowed covers the whole domain of "
                             f"{sfield!r} — a gate that admits every state gates nothing")
                    # phase 2 decides whether any declared write can actually land in `allowed`
                    pending_state_gates.append((fn, cat, pid, gate_id, gwhere,
                                                stable, set(allowed_states), list(applies)))
                elif "state_contract" in gate:
                    fail(f"{gwhere}: state_contract is only valid for kind=state")

                if kind == "dedup":
                    dedup = as_dict(gate.get("dedup_contract"))
                    table = dedup.get("table")
                    if table not in schema:
                        fail(f"{gwhere}: dedup_contract.table {table!r} is not in db_schema.json")
                    if dedup.get("mode") not in {"separate_record", "same_record"}:
                        fail(f"{gwhere}: dedup_contract.mode must be separate_record|same_record")
                    object_bindings = dedup.get("object_bindings")
                    if not isinstance(object_bindings, dict) or not object_bindings:
                        fail(f"{gwhere}: dedup_contract.object_bindings must be non-empty")
                        object_bindings = {}
                    duplicate_filters = dedup.get("duplicate_filters")
                    if not isinstance(duplicate_filters, dict) or not duplicate_filters:
                        fail(f"{gwhere}: dedup_contract.duplicate_filters must be non-empty")
                        duplicate_filters = {}
                    distinct_fields = dedup.get("distinct_fields")
                    if not isinstance(distinct_fields, list):
                        fail(f"{gwhere}: dedup_contract.distinct_fields must be a list")
                        distinct_fields = []
                    elif not all(isinstance(field, str) for field in distinct_fields):
                        fail(f"{gwhere}: dedup_contract.distinct_fields values must be field names")
                        distinct_fields = []
                    table_fields = set(as_dict(schema.get(table)))
                    for field in set(object_bindings) | set(duplicate_filters) | set(distinct_fields):
                        if field not in table_fields:
                            fail(f"{gwhere}: dedup field {field!r} is not on table {table!r}")
                    for action_arg in object_bindings.values():
                        if not isinstance(action_arg, str) or not KEY_RE.match(action_arg):
                            fail(f"{gwhere}: dedup action argument {action_arg!r} must be snake_case")
                elif "dedup_contract" in gate:
                    fail(f"{gwhere}: dedup_contract is only valid for kind=dedup")

            pt = pms.get("per_tier")
            if pt is not None:
                check_per_tier(f"{fn}: policy '{pid}'", pt, vnames)
                differentiated = differentiated or tier_values_differ(
                    pt, {as_dict(v).get("name"): as_dict(v.get("parameters")) for v in variants})
            for row in [pms] + [as_dict(r) for r in as_dict(pms.get("per_tier")).values()]:
                for k, v in row.items():
                    if isinstance(v, str) and v.startswith("=") and v[1:] not in pschema:
                        fail(f"{fn}: policy '{pid}' param '{k}' references unknown catalog "
                             f"parameter '{v[1:]}' (\"=<param>\" must name a parameter_schema key)")
            fm = as_dict(p.get("formula"))
            if fm:
                resolvable = (set(pschema) | all_param_keys | measure_ids
                              | set(accounts) | set(event_field_specs)
                              | set(schema.get(ht, {}))
                              | {k for k in fm if k not in ("when", "when_not")})
                for fk, expr in fm.items():
                    if not isinstance(expr, str):
                        continue
                    stripped = re.sub(r'"[^"]*"|\'[^\']*\'', ' ', expr)  # string literals
                    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stripped):
                        if tok.lower() in ("and", "or", "not", "in", "is", "true", "false",
                                           "none", "min", "max", "round", "abs", "if", "else"):
                            continue
                        if tok not in resolvable:
                            fail(f"{fn}: policy '{pid}' formula '{fk}' references unknown "
                                 f"identifier '{tok}' (must be a catalog/policy param, measure, "
                                 "account, or event field)")
            for mid in as_list(p.get("measures")):
                if mid not in measure_ids:
                    fail(f"{fn}: policy '{pid}' references undeclared measure '{mid}'")
                consumed_measures.add(mid)
            for mid in measure_ids:            # a measure named in prose is consumed too
                if mid in rule_text or any(mid in str(v) for v in as_dict(p.get("formula")).values()):
                    consumed_measures.add(mid)
        for mid in sorted(measure_ids - consumed_measures):
            fail(f"{fn}: measure '{mid}' is declared but no policy of this category reads it "
                 "(not in any policy.measures, rule or formula) — a window statistic nothing "
                 "consults is dead weight; either bind it to the policy that needs it or drop it")
        orphan = categories.get(cat, {}).get("events", set()) - governed_events
        if orphan:
            fail(f"{fn}: events {sorted(orphan)} have no policy bound — every declared event "
                 "must be governed (existence implies treatment)")
        if charter_max == "absent":
            fail(f"{fn}: missing the multi-holding charter '{cat}_agg_multi_holding' "
                 "(binds a create event, params.max_per_customer; every category has exactly one)")
        elif charter_max != 1 and not agg_policies:
            fail(f"{fn}: multi-holding allowed (max_per_customer != 1) requires >=1 "
                 "aggregation policy (<category>_agg_<key>) beyond the charter")
        if vnames and not differentiated:
            fail(f"{fn}: no policy per_tier actually differs across tiers — "
                 "tier differentiation must be real, not decorative")
        categories.setdefault(cat, {"events": set(), "variants": set()})
        categories[cat]["variants"] = set(vnames)
        categories[cat]["field_specs"] = event_field_specs

        # enum domains in the schema must be charter-sourced (single source of truth)
        if ht in schema:
            vspec = as_dict(schema[ht].get(vf))
            if vspec.get("type") == "enum" and set(as_list(vspec.get("values"))) != set(vnames):
                fail(f"{fn}: holding table '{ht}.{vf}' enum values must equal the "
                     "category's variant official names exactly")
            sspec = as_dict(schema[ht].get(sf))
            if sspec.get("type") == "enum" and set(as_list(sspec.get("values"))) != set(states):
                fail(f"{fn}: holding table '{ht}.{sf}' enum values must equal lifecycle.states")
        seen_event_vals = set()
        for et_ in ets:
            if et_ not in schema:
                continue
            espec = as_dict(schema[et_].get("event_type"))
            if espec.get("type") != "enum":
                fail(f"{fn}: event table '{et_}.event_type' must be an enum over declared families")
                continue
            vals = set(as_list(espec.get("values")))
            bad = vals - categories[cat]["events"]
            if bad:
                fail(f"{fn}: event table '{et_}.event_type' values {sorted(bad)} are not "
                     f"declared event families of '{cat}'")
            seen_event_vals |= vals
        homeless = {et for et in categories[cat]["events"]
                    if as_dict(categories[cat].get("event_defs", {}).get(et)).get("target") != ht
                    } - seen_event_vals
        if homeless:
            fail(f"{fn}: declared event families {sorted(homeless)} appear in no bound "
                 "event table's event_type values")

    # --------------------------------------------------- event triggers (phase 2)
    pair_seen = set()
    for fn, src_cat, src, tg in pending_triggers:
        tgt = str(tg.get("event") or "")
        if ":" not in tgt:
            fail(f"{fn}: event '{src}' trigger must carry event: <category>:<event_type>")
            continue
        tcat, tet = tgt.split(":", 1)
        if tcat not in categories:
            fail(f"{fn}: event '{src}' trigger '{tgt}' — unknown category '{tcat}'")
            continue
        tdef = categories[tcat].get("event_defs", {}).get(tet)
        if tdef is None:
            fail(f"{fn}: event '{src}' trigger '{tgt}' — '{tet}' is not a declared "
                 f"event family of '{tcat}'")
            continue
        if tet == src and tcat == src_cat:
            fail(f"{fn}: event '{src}' must not trigger itself")
        src_fields = set(as_dict(categories[src_cat].get("event_defs", {}).get(src)).get("fields"))
        src_fields |= set(categories[src_cat].get("field_specs", {}))  # own-family fields + event-table columns
        src_specs = categories[src_cat].get("field_specs", {})
        when = as_dict(tg.get("when"))
        for f, val in when.items():
            if f not in src_fields:
                fail(f"{fn}: event '{src}' trigger when field '{f}' is not on the "
                     "source event tables")
                continue
            if isinstance(val, dict):
                nv = val.get("not")
                vals = nv if isinstance(nv, list) else ([nv] if nv is not None else [])
                if not vals:
                    fail(f"{fn}: event '{src}' trigger when '{f}' must be a value, "
                         "a list, or {{'not': <value or list of values>}}")
            else:
                vals = val if isinstance(val, list) else [val]
            spec = src_specs.get(f) or {}
            if spec.get("type") == "enum":
                bad = [v for v in vals if v not in as_list(spec.get("values"))]
                if bad:
                    fail(f"{fn}: event '{src}' trigger when '{f}' value(s) {bad} "
                         "not in its enum domain")
        sig = json.dumps(when, sort_keys=True, default=str)
        pair = (src, tgt, sig)
        if pair in pair_seen:
            fail(f"{fn}: trigger {src} -> {tgt} with identical when declared twice")
        pair_seen.add(pair)
        tfields = set(as_dict(tdef.get("fields")))
        tgt_specs = categories[tcat].get("field_specs", {})
        for tf, mv in as_dict(tg.get("map")).items():
            if tf not in tfields:
                fail(f"{fn}: event '{src}' trigger map target '{tf}' is not a field of '{tet}'")
            elif isinstance(mv, str) and mv in src_fields:
                pass  # source-field reference: values flow from the source row
            else:
                ts = tgt_specs.get(tf) or {}
                if ts.get("type") == "enum" and mv not in as_list(ts.get("values")):
                    fail(f"{fn}: event '{src}' trigger map value '{mv}' for '{tf}' "
                         "not in its enum domain (use a source field name or a valid literal)")

    # ------------------------------------ state gates vs the states writes land in (phase 2)
    # A state gate is only meaningful if some declared write can actually satisfy it.  The
    # states a holding can be in when an event fires are derivable without reading any prose:
    # a `create` leaves it in the lifecycle's entry state, a `transition` leaves it in one of
    # its `to` states, and a trigger fires its target immediately after its source landed.
    def _entry_states(cat_name):
        """Lifecycle states reachable at creation: those no transition ever moves INTO."""
        lc = as_dict(categories[cat_name].get("lifecycle"))
        states = set(as_list(lc.get("states")))
        landed = {as_dict(t).get("to") for t in as_list(lc.get("transitions"))}
        return states - landed

    def _states_after(cat_name, event_type):
        """The holding states an event leaves behind, or None when it does not touch status."""
        ev = as_dict(categories[cat_name].get("event_defs", {}).get(event_type))
        mut = ev.get("mutation")
        if mut == "create":
            return _entry_states(cat_name)
        if isinstance(mut, dict) and mut.get("transition"):
            return {as_dict(t).get("to") for t in as_list(mut.get("transition"))}
        return None  # event-table write (or field update): status is whatever it already was

    for fn, cat, pid, gate_id, gwhere, stable, allowed_states, applies in pending_state_gates:
        if not allowed_states:
            continue
        holding_table = as_dict(categories[cat].get("binding")).get("holding_table")
        if stable != holding_table:
            continue  # gate ranges over some other table's state: nothing to derive here
        for governed in applies:
            # (a) the governed write is itself a status-setting event
            landing = _states_after(cat, governed)
            if landing is not None and landing and not (landing & allowed_states):
                fail(f"{gwhere}: gate admits {sorted(allowed_states)} but its own subject "
                     f"'{governed}' leaves the holding in {sorted(landing)} — this gate can "
                     "never be satisfied on that write")
            # (b) the governed write is fired by a trigger, right after its source landed
            for tfn, src_cat, src, tg in pending_triggers:
                if str(as_dict(tg).get("event") or "") != f"{cat}:{governed}":
                    continue
                if src_cat != cat:
                    continue  # cross-category source: the local status is not implied by it
                after_src = _states_after(src_cat, src)
                if after_src and not (after_src & allowed_states):
                    fail(f"{gwhere}: gate admits {sorted(allowed_states)}, but '{src}' triggers "
                         f"'{governed}' while the holding is in {sorted(after_src)} — the "
                         "declared consequence can never clear its own gate. Either widen the "
                         "gate for that occasion or drop the trigger.")

    # ------------------------------------------------------------ difficulties
    diffs = as_list(bp.get("difficulties"))
    if not diffs:
        fail("blueprint.yaml: difficulties is empty")
    if len(categories) < len(diffs) + 2:
        fail(f"{len(categories)} categories < {len(diffs)} difficulties + 2 — the map must "
             "exceed the claims (categories >= N + 2; surplus categories are the distractors)")
    primary_seen = {}
    for d in diffs:
        d = as_dict(d)
        dn = str(d.get("name") or "?")
        if not KEY_RE.match(dn):
            fail(f"difficulty '{dn}': name must be a snake_case directory name")
        claim = as_dict(d.get("claim"))
        cats = as_list(claim.get("categories"))
        if not cats:
            fail(f"difficulty '{dn}': claim.categories is empty")
        for c in cats:
            if c not in categories:
                fail(f"difficulty '{dn}': claimed category '{c}' has no products/{c}.yaml")
            elif c in primary_seen:
                fail(f"difficulty '{dn}': category '{c}' already claimed by '{primary_seen[c]}' "
                     "(primary categories must be pairwise disjoint)")
            else:
                primary_seen[c] = dn
        owned_events = set()
        for c in cats:
            owned_events |= categories.get(c, {}).get("events", set())
        for et in as_list(claim.get("event_types")):
            if et not in owned_events:
                fail(f"difficulty '{dn}': event_type '{et}' is not declared by its claimed categories")
        for bad in ("action_family", "context_categories"):
            if bad in claim:
                fail(f"difficulty '{dn}': claim.{bad} was removed — a claim is exactly "
                     "categories + event_types (writes are claimed, reads are free)")
        n_sum = len(sentences(d.get("summary")))
        if n_sum < 4:
            fail(f"difficulty '{dn}': summary counts ~{n_sum} sentences (>=4 required)")

    print(f"   categories: {len(categories)}   variants: {len(all_variant_names)}   "
          f"event types: {sum(len(c['events']) for c in categories.values())}   "
          f"difficulties: {len(diffs)}   registered ids: {len(ids_seen)}")
    finish()


def finish() -> NoReturn:
    for w in WARNS:
        print(f"   WARN: {w}")
    if FAILS:
        print("\n  [FAIL]")
        for m in FAILS:
            print(f"    - {m}")
        print("BLUEPRINT NOT OK — fix the items above and re-run")
        sys.exit(1)
    print("  [PASS] constitution is structurally complete and consistent")
    print("BLUEPRINT OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
