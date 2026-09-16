"""SOLVABILITY gate: prove every gold write is positively and uniquely executable.

This is the structural half of the policy-evidence audit. It verifies that each task begins
with the runtime-mandatory locate -> in-session identity-verification write, each scored
task-tool call has a contract, every base policy governing that exact write subject is retained,
and each applicable eligibility gate is covered by reachable evidence while unrelated gates are
absent. Evidence is required to be
authoritative, pre-action, and object-correlated to the actual call arguments; time conditions
are checked against the frozen clock, required user inputs occur verbatim in the persona, and
every seeded primary holding/event row has an explicit consistency audit. The gate checks only
the declared policy/GT correspondence; a separate human semantic audit must reject a CRUD status
write that merely pretends an external event happened. Task tools are atomic CRUD operations: no inferred
business semantics, counterfactual mutations, or rejection behavior are tested here.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/check_solvability.py \
      env/<scenario>/tasks/<difficulty> [--task N]
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


_CALL_WRAPPERS = {"call_agent_discoverable_tool", "call_user_discoverable_tool"}

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def as_list(value):
    return value if isinstance(value, list) else []


def as_dict(value):
    return value if isinstance(value, dict) else {}


def _nows(s):
    return "".join(str(s or "").split())


def retired_gates_of(base_policies, ext_policies):
    """Eligibility gates an extended policy's `overwrite` has retired: a superseded_clause that quotes a
    gate's condition sentence (whitespace-insensitive containment either way) retires that gate, so it is
    no longer inherited into base_preconditions (erl-task-instantiate Step 1)."""
    retired = set()
    for ep in ext_policies.values():
        for entry in as_list(as_dict(ep).get("overwrite")):
            entry = as_dict(entry)
            bpid = entry.get("base_policy")
            clause = _nows(entry.get("superseded_clause"))
            if not bpid or not clause or bpid not in base_policies:
                continue
            for gate in as_list(as_dict(base_policies[bpid]).get("eligibility")):
                gate = as_dict(gate)
                cond = _nows(gate.get("condition"))
                if cond and (cond in clause or clause in cond):
                    retired.add((bpid, gate.get("id")))
    return retired


def scenario_root(start):
    path = os.path.abspath(start)
    while path != "/":
        if os.path.isdir(os.path.join(path, "blueprint")):
            return path
        path = os.path.dirname(path)
    raise SystemExit(f"cannot find scenario root (blueprint/) above {start}")


def repo_root(start):
    path = os.path.abspath(start)
    while path != "/":
        if os.path.isdir(os.path.join(path, "erlbench")):
            return path
        path = os.path.dirname(path)
    raise SystemExit(f"cannot find repository root (erlbench/) above {start}")


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task_call_steps(actions):
    """Return indices of scored task-tool calls, excluding unlock and share reads."""
    out = []
    for index, action in enumerate(actions):
        action = as_dict(action)
        name = action.get("tool") or action.get("name")
        if name in _CALL_WRAPPERS:
            out.append(index)
    return out


def action_business_args(action):
    """Return the underlying tool arguments for direct or discoverable-tool calls."""
    action = as_dict(action)
    args = as_dict(action.get("arguments"))
    if action.get("tool") in _CALL_WRAPPERS:
        return as_dict(args.get("arguments"))
    return args


def _tool_rw(fn):
    for dec in fn.decorator_list:
        if not (isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "tool"):
            continue
        for kw in dec.keywords:
            if kw.arg == "rw" and isinstance(kw.value, ast.Constant):
                return kw.value.value
    return None


def _ctx_tables(fn, method):
    tables = set()
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if not (isinstance(node.func.value, ast.Name) and node.func.value.id == "ctx"):
            continue
        if node.func.attr != method or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            tables.add(first.value)
    return tables


def _module_int_constants(tree):
    """Module-level `NAME = <int>` bindings, so a threshold written as a named constant is read
    the same as one written inline."""
    out = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        v = node.value
        if isinstance(v, ast.Constant) and isinstance(v.value, int) and not isinstance(v.value, bool):
            for t in targets:
                if isinstance(t, ast.Name):
                    out[t.id] = v.value
    return out


def _literal_match_threshold(fn, consts=None):
    """Find `matched = sum(...)` compared against a determinable positive integer threshold.
    The threshold may be written inline or as a module-level named constant, and the comparison
    may be written either way round; what matters is that K is determinable, not how it is spelled."""
    consts = consts or {}

    def as_int(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.Name):
            return consts.get(node.id)
        return None

    sum_names = set()
    for node in ast.walk(fn):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id == "sum"):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        sum_names.update(t.id for t in targets if isinstance(t, ast.Name))
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Compare) and len(node.ops) == 1
                and len(node.comparators) == 1):
            continue
        op, left, right = node.ops[0], node.left, node.comparators[0]
        if isinstance(op, ast.GtE) and isinstance(left, ast.Name) and left.id in sum_names:
            k = as_int(right)
        elif isinstance(op, ast.LtE) and isinstance(right, ast.Name) and right.id in sum_names:
            k = as_int(left)
        else:
            continue
        if isinstance(k, int) and k > 0:
            return k
    return None


def identity_preamble_contract(blueprint_dir):
    blueprint = load_yaml(os.path.join(blueprint_dir, "blueprint.yaml")) or {}
    verification_table = as_dict(blueprint.get("logs")).get("verification_log_table")
    if not verification_table:
        raise SystemExit("blueprint.logs.verification_log_table is required")

    share_path = os.path.join(blueprint_dir, "share_tools.py")
    tree = ast.parse(open(share_path).read(), filename=share_path)
    fns = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    customer_finders = [
        fn for fn in fns if _tool_rw(fn) == "read" and "customers" in _ctx_tables(fn, "find")
    ]
    verification_writers = [
        fn for fn in fns
        if _tool_rw(fn) == "write"
        and "customers" in _ctx_tables(fn, "find")
        and verification_table in (_ctx_tables(fn, "create") | _ctx_tables(fn, "update"))
    ]
    if len(customer_finders) != 1:
        names = [fn.name for fn in customer_finders]
        raise SystemExit(f"expected exactly one customers finder in share_tools.py, found {names}")
    if len(verification_writers) != 1:
        names = [fn.name for fn in verification_writers]
        raise SystemExit(
            f"expected exactly one writer of verification log table {verification_table!r}, found {names}"
        )

    verify_fn = verification_writers[0]
    params = [arg.arg for arg in verify_fn.args.args if arg.arg != "ctx"]
    params.extend(arg.arg for arg in verify_fn.args.kwonlyargs)
    if "customer_id" not in params:
        raise SystemExit(f"identity-verification tool {verify_fn.name} lacks customer_id")
    credential_params = [param for param in params if param != "customer_id"]
    threshold = _literal_match_threshold(verify_fn, _module_int_constants(tree))
    if threshold is None:
        raise SystemExit(
            f"identity-verification tool {verify_fn.name} must compare the match count against a "
            f"determinable positive integer K (`matched >= K` or `K <= matched`, K written inline "
            f"or as a module-level constant)"
        )
    if threshold > len(credential_params):
        raise SystemExit(
            f"identity-verification threshold {threshold} exceeds credential params {credential_params}"
        )
    return {
        "finder": customer_finders[0].name,
        "verifier": verify_fn.name,
        "verification_table": verification_table,
        "credential_params": credential_params,
        "threshold": threshold,
    }


def main():
    positional, task_selector = split_task_flag(sys.argv[1:])
    if len(positional) != 1:
        print("usage: check_solvability.py env/<scenario>/tasks/<difficulty> [--task N]")
        sys.exit(2)
    target = positional[0].rstrip("/")
    root = repo_root(target)
    if root not in sys.path:
        sys.path.insert(0, root)
    from erlbench.db import DB
    from erlbench.determinism import Clock
    from erlbench.scoring import _resolve
    from erlbench.tools import ToolContext, collect_specs

    scen = scenario_root(target)
    bp = os.path.join(scen, "blueprint")
    identity = identity_preamble_contract(bp)
    db_schema = json.load(open(os.path.join(bp, "db_schema.json")))

    ext_files = glob.glob(os.path.join(target, "*.extended.yaml"))
    if len(ext_files) != 1:
        raise SystemExit(f"expected one <category>.extended.yaml under {target}, found {ext_files}")
    extended = load_yaml(ext_files[0]) or {}
    category = extended.get("category")
    base = load_yaml(os.path.join(bp, "products", f"{category}.yaml")) or {}
    base_policies = {p.get("id"): p for p in as_list(base.get("policies")) if as_dict(p).get("id")}
    ext_policies = {p.get("id"): p for p in as_list(extended.get("extended_policies"))
                    if as_dict(p).get("id")}
    retired_gates = retired_gates_of(base_policies, ext_policies)
    binding = as_dict(base.get("binding"))
    primary_seed_tables = {binding.get("holding_table"), *as_list(binding.get("event_tables"))}
    primary_seed_tables.discard(None)

    specs = {}
    share_module = import_file(os.path.join(bp, "share_tools.py"), "_solvability_share")
    for spec in collect_specs(share_module, "share"):
        specs[spec.name] = spec
    task_tools_path = os.path.join(target, "task_tools.py")
    if os.path.exists(task_tools_path):
        task_module = import_file(task_tools_path, "_solvability_task")
        for spec in collect_specs(task_module, "task"):
            specs[spec.name] = spec

    task_paths = select_task_paths(target, task_selector)
    if not task_paths:
        suffix = f" matching --task {task_selector}" if task_selector is not None else ""
        raise SystemExit(f"no task json{suffix} under {target}/tasks/")

    loaded_tasks = {os.path.basename(path): json.load(open(path)) for path in task_paths}

    print(f"🔎 SOLVABILITY gate  ({len(task_paths)} tasks, category={category})")
    print(f"   identity preamble: {identity['finder']} -> {identity['verifier']} "
          f"(K={identity['threshold']}, log={identity['verification_table']})")
    print(f"{'task':12} {'verify':>6} {'calls':>5} {'base gates':>10} "
          f"{'seed rows':>10} {'ok':>4}")
    all_fails = []

    for task_path in task_paths:
        tid = os.path.basename(task_path)
        task = loaded_tasks[tid]
        persona = str(task.get("user_scenario") or "")
        initial = as_dict(task.get("initial_state"))
        actions = as_list(task.get("evaluation_criteria"))
        computations = as_list(task.get("computations"))
        contract = task.get("solvability_contract")
        fails = []

        def fail(message):
            fails.append(f"{tid}: {message}")

        def check_evidence(ref, where, current_step=None):
            if ref == "frozen_time":
                if not str(task.get("frozen_time") or "").strip():
                    fail(f"{where}: frozen_time is empty")
                return None
            if isinstance(ref, str) and ref.startswith("prior_step:"):
                raw = ref.split(":", 1)[1]
                try:
                    prior = int(raw)
                except ValueError:
                    fail(f"{where}: invalid prior_step reference {ref!r}")
                    return None
                if current_step is None or prior < 0 or prior >= current_step or prior >= len(actions):
                    fail(f"{where}: {ref!r} must name an existing action earlier than this call")
                return None
            if isinstance(ref, str) and ref.startswith("user_scenario:"):
                snippet = ref.split(":", 1)[1]
                if not snippet or snippet not in persona:
                    fail(f"{where}: user_scenario snippet is not present verbatim: {snippet!r}")
                return None
            if isinstance(ref, str) and ref.startswith("initial_state."):
                parts = ref.split(".")
                if len(parts) not in (3, 4):
                    fail(f"{where}: initial_state evidence must be row or field path, got {ref!r}")
                    return None
                _, table, row_id, *field = parts
                rows = as_dict(initial.get(table))
                if row_id not in rows:
                    fail(f"{where}: evidence row does not exist: {ref!r}")
                    return None
                if field and field[0] not in as_dict(rows[row_id]):
                    fail(f"{where}: evidence field does not exist: {ref!r}")
                    return None
                return f"{table}.{field[0]}" if field else None
            fail(f"{where}: unsupported evidence reference {ref!r}")
            return None

        def binding_source_value(binding, where, current_step):
            """Resolve a pre-action evidence binding to the value consumed by this call."""
            source = binding.get("source")
            if isinstance(source, str) and source.startswith("initial_state."):
                parts = source.split(".")
                if len(parts) != 4:
                    fail(f"{where}: initial_state binding source must be a field path")
                    return None, "system"
                _, table, row_id, field = parts
                row = as_dict(as_dict(initial.get(table)).get(row_id))
                if not row or field not in row:
                    fail(f"{where}: binding source does not exist: {source!r}")
                    return None, "system"
                return row.get(field), "system"
            if isinstance(source, str) and source.startswith("prior_step:"):
                raw = source.split(":", 1)[1]
                try:
                    prior = int(raw)
                except ValueError:
                    fail(f"{where}: invalid prior_step binding source {source!r}")
                    return None, "system"
                if prior < 0 or prior >= current_step or prior >= len(actions):
                    fail(f"{where}: prior_step binding source must name an earlier action")
                    return None, "system"
                source_arg = binding.get("source_arg")
                source_table = binding.get("source_table")
                source_field = binding.get("source_field")
                prior_args = action_business_args(actions[prior])
                if source_arg not in (None, ""):
                    if source_table not in (None, "") or source_field not in (None, ""):
                        fail(f"{where}: prior_step source must use source_arg or source_table/source_field, "
                             "not both")
                        return None, "system"
                    if not isinstance(source_arg, str) or source_arg not in prior_args:
                        fail(f"{where}: source_arg must name an argument of {source}")
                        return None, "system"
                    return prior_args.get(source_arg), "system"
                if not isinstance(source_table, str) or not isinstance(source_field, str):
                    fail(f"{where}: prior_step binding must provide source_arg or paired "
                         "source_table/source_field")
                    return None, "system"
                before_db, before_error = replay_prefix(deepcopy(initial), deepcopy(actions), prior)
                after_db, after_error = replay_prefix(deepcopy(initial), deepcopy(actions), prior + 1)
                if before_error or after_error:
                    fail(f"{where}: cannot resolve prior_step DB delta: {before_error or after_error}")
                    return None, "system"
                before_rows = as_dict(before_db.tables.get(source_table))
                after_rows = as_dict(after_db.tables.get(source_table))
                values = {
                    as_dict(row).get(source_field)
                    for row_id, row in after_rows.items()
                    if as_dict(before_rows.get(row_id)) != as_dict(row)
                    and source_field in as_dict(row)
                }
                values.discard(None)
                if len(values) != 1:
                    fail(f"{where}: {source} must produce exactly one changed "
                         f"{source_table}.{source_field} value, got {sorted(values, key=str)}")
                    return None, "system"
                return next(iter(values)), "system"
            if isinstance(source, str) and source.startswith("user_scenario:"):
                snippet = source.split(":", 1)[1]
                source_value = binding.get("source_value")
                if source_value in (None, ""):
                    fail(f"{where}: user_scenario binding requires non-empty source_value")
                    return None, "caller"
                if str(source_value) not in snippet or snippet not in persona:
                    fail(f"{where}: source_value must occur in the cited user_scenario snippet")
                return source_value, "caller"
            fail(f"{where}: binding source must be initial_state field, prior_step, or user_scenario")
            return None, None

        def replay_prefix(seed, replay_actions, stop):
            """Replay successful gold writes before one business call."""
            db = DB.seeded(seed)
            clock = Clock.from_stamp(task.get("frozen_time"))
            for prefix_step, prefix_action in enumerate(replay_actions[:stop]):
                tool_name, tool_args = _resolve(as_dict(prefix_action))
                spec = specs.get(tool_name)
                if spec is None or spec.rw != "write":
                    continue
                try:
                    out = str(spec.func(
                        ToolContext(db, clock, db_schema, writable=True),
                        **spec.coerce(tool_args),
                    ))
                except Exception as exc:  # noqa: BLE001
                    return None, f"prefix action {prefix_step} ({tool_name}) raised: {exc}"
                if out.startswith("Error"):
                    return None, f"prefix action {prefix_step} ({tool_name}) returned Error: {out[:120]}"
            return db, None

        # Runtime security writes are scored state.  A correct task therefore starts by
        # locating the customer once and recording exactly one successful in-session
        # verification before any account read or business write.
        finder_steps = [
            index for index, action in enumerate(actions)
            if as_dict(action).get("tool") == identity["finder"]
        ]
        verifier_steps = [
            index for index, action in enumerate(actions)
            if as_dict(action).get("tool") == identity["verifier"]
        ]
        if finder_steps != [0]:
            fail(f"customers finder must occur exactly once as step 0, got {finder_steps}")
        if verifier_steps != [1]:
            fail(f"in-session identity verification must occur exactly once as step 1, got {verifier_steps}")

        verification_ok = False
        if len(actions) >= 2 and finder_steps == [0] and verifier_steps == [1]:
            finder_action = as_dict(actions[0])
            verify_action = as_dict(actions[1])
            if finder_action.get("owner") != "agent":
                fail("customers finder step 0 must have owner='agent'")
            if verify_action.get("owner") != "agent":
                fail("identity-verification step 1 must have owner='agent'")
            finder_args = as_dict(finder_action.get("arguments"))
            verify_args = as_dict(verify_action.get("arguments"))
            customer_id = verify_args.get("customer_id")
            customer_rows = as_dict(initial.get("customers"))
            customer = as_dict(customer_rows.get(customer_id))
            if not customer_id or customer_id not in customer_rows:
                fail("identity verification customer_id must name an initial_state.customers row")
            if finder_args.get("customer_id") not in (None, ""):
                fail("customers finder must bootstrap by caller-stateable attributes, not internal customer_id")
            locator_args = {key: value for key, value in finder_args.items()
                            if key != "customer_id" and value not in (None, "")}
            if not locator_args:
                fail("customers finder must provide at least one non-empty caller-stateable attribute")
            for field, value in locator_args.items():
                if field not in customer:
                    fail(f"customers finder locator {field!r} is not a field of the target customer")
                elif str(customer.get(field)) != str(value):
                    fail(f"customers finder locator {field!r}={value!r} does not match target customer")
                if str(value) not in persona:
                    fail(f"customers finder locator value for {field!r} is absent from user_scenario")

            supplied = {
                field: verify_args.get(field)
                for field in identity["credential_params"]
                if verify_args.get(field) not in (None, "")
            }
            unexpected = sorted(set(verify_args) - ({"customer_id"} | set(identity["credential_params"])))
            if unexpected:
                fail(f"identity verification has unexpected arguments {unexpected}")
            if len(supplied) < identity["threshold"]:
                fail(f"identity verification supplies {len(supplied)} non-empty credential(s), "
                     f"below threshold K={identity['threshold']}")
            for field, value in supplied.items():
                if field not in customer:
                    fail(f"verification credential {field!r} is not a target customer field")
                elif str(customer.get(field)) != str(value):
                    fail(f"verification credential {field!r}={value!r} does not match target customer")
                if str(value) not in persona:
                    fail(f"verification credential value for {field!r} is absent from user_scenario")
            verification_ok = not any(
                "customers finder" in message or "identity verification" in message
                or "verification credential" in message
                for message in fails
            )

        if not isinstance(contract, dict):
            fail("missing solvability_contract mapping")
            contract = {}

        request_binding_version = contract.get("request_binding_version", 1)
        if request_binding_version != 1:
            fail(f"request_binding_version, when given, must be 1, got {request_binding_version!r}")
            # Keep checking the v1 fields: omitting the version must not also bypass
            # request-to-action disambiguation diagnostics.
            request_binding_version = 1

        # The request itself must be grounded in the customer's reachable script.
        request_alignment = contract.get("request_alignment")
        if not isinstance(request_alignment, list) or not request_alignment:
            fail("request_alignment must be a non-empty list")
        else:
            for index, item in enumerate(request_alignment):
                item = as_dict(item)
                where = f"request_alignment[{index}]"
                if not str(item.get("claim") or "").strip():
                    fail(f"{where}: claim is empty")
                evidence = item.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    fail(f"{where}: evidence must be non-empty")
                else:
                    for ref in evidence:
                        check_evidence(ref, where)
                    if not any(isinstance(ref, str) and ref.startswith("user_scenario:")
                               for ref in evidence):
                        fail(f"{where}: must include a verbatim user_scenario reference")

        call_steps = task_call_steps(actions)
        gold_actions = contract.get("gold_actions")
        if not isinstance(gold_actions, list):
            fail("gold_actions must be a list")
            gold_actions = []
        by_step = {}
        for index, item in enumerate(gold_actions):
            item = as_dict(item)
            step = item.get("step")
            if not isinstance(step, int) or isinstance(step, bool):
                fail(f"gold_actions[{index}].step must be an integer")
                continue
            if step in by_step:
                fail(f"gold_actions repeats call step {step}")
            by_step[step] = item
        if set(by_step) != set(call_steps):
            fail(f"gold_actions steps {sorted(by_step)} must exactly equal task call steps {call_steps}")

        gates_checked = 0
        required_time_gates = {}
        for step in call_steps:
            item = as_dict(by_step.get(step))
            where = f"gold_actions[step={step}]"
            if not str(item.get("business_effect") or "").strip():
                fail(f"{where}: business_effect is empty")

            # The request must select this exact business write, not merely a generic domain
            # such as "fees" or "service".  on_request is caller-triggered; state_due is
            # system-obligation-triggered.  Neither tool names nor hidden policy scope are intent.
            step_policies = []
            for comp in computations:
                comp = as_dict(comp)
                if comp.get("step") == step and comp.get("policy_id") in ext_policies:
                    step_policies.append(ext_policies[comp["policy_id"]])
            request_binding = item.get("request_binding")
            if request_binding_version == 1:
                if not isinstance(request_binding, dict):
                    fail(f"{where}: request_binding must be a mapping")
                    request_binding = {}
                if not str(request_binding.get("action_semantics") or "").strip():
                    fail(f"{where}.request_binding.action_semantics is empty")

                intent_source = request_binding.get("intent_source")
                if not isinstance(intent_source, dict):
                    fail(f"{where}.request_binding.intent_source must be a mapping")
                    intent_source = {}
                intent_kind = intent_source.get("kind")
                intent_evidence = intent_source.get("evidence")
                if intent_kind not in {"user_scenario", "initial_state", "prior_step"}:
                    fail(f"{where}.request_binding.intent_source.kind is invalid")
                if not isinstance(intent_evidence, list) or not intent_evidence:
                    fail(f"{where}.request_binding.intent_source.evidence must be non-empty")
                    intent_evidence = []
                for ref in intent_evidence:
                    check_evidence(ref, f"{where}.request_binding.intent_source", step)

                triggers = {ep.get("trigger") for ep in step_policies}
                if "on_request" in triggers:
                    if intent_kind != "user_scenario":
                        fail(f"{where}: on_request policy must be triggered by a verbatim "
                             "user_scenario intent source")
                    if not any(isinstance(ref, str) and ref.startswith("user_scenario:")
                               for ref in intent_evidence):
                        fail(f"{where}: on_request intent evidence must cite user_scenario")
                elif triggers == {"state_due"}:
                    if intent_kind not in {"initial_state", "prior_step"}:
                        fail(f"{where}: state_due policy must cite a pre-action object-level "
                             "system obligation, not caller intent")
                    if not any(isinstance(ref, str) and (
                            ref.startswith("initial_state.") or ref.startswith("prior_step:"))
                               for ref in intent_evidence):
                        fail(f"{where}: state_due intent evidence must cite initial_state or prior_step")

                discriminator = request_binding.get("discriminator")
                if not isinstance(discriminator, dict):
                    fail(f"{where}.request_binding.discriminator must be a mapping")
                    discriminator = {}
                meaning = str(discriminator.get("business_meaning") or "").strip()
                if not meaning:
                    fail(f"{where}.request_binding.discriminator.business_meaning is empty")
                discriminator_evidence = discriminator.get("evidence")
                if not isinstance(discriminator_evidence, list) or not discriminator_evidence:
                    fail(f"{where}.request_binding.discriminator.evidence must be non-empty")
                    discriminator_evidence = []
                for ref in discriminator_evidence:
                    check_evidence(ref, f"{where}.request_binding.discriminator", step)
                if "on_request" in triggers:
                    cited_snippets = [
                        ref.split(":", 1)[1] for ref in discriminator_evidence
                        if isinstance(ref, str) and ref.startswith("user_scenario:")
                    ]
                    if not cited_snippets or not any(meaning in snippet for snippet in cited_snippets):
                        fail(f"{where}: on_request discriminator business_meaning {meaning!r} must "
                             "occur verbatim in cited user_scenario evidence")

                action_arg = discriminator.get("action_arg")
                current_args = action_business_args(actions[step])
                if action_arg not in (None, ""):
                    if action_arg not in current_args:
                        fail(f"{where}.request_binding.discriminator.action_arg must name a current "
                             "task-tool argument")
                    elif discriminator.get("value") != current_args.get(action_arg):
                        fail(f"{where}.request_binding.discriminator.value="
                             f"{discriminator.get('value')!r} != gold {action_arg}="
                             f"{current_args.get(action_arg)!r}")
                elif discriminator.get("value") in (None, ""):
                    fail(f"{where}.request_binding.discriminator needs either a gold action_arg/value "
                         "or a non-empty structured system value")

            # A conversation may reveal a pre-existing external completion, but it may
            # not manufacture one. Every write declares where its stage fact came from.
            # The independent semantic audit must still compare the fact text with the
            # policy, persona, and actual tool effect.
            provenance = item.get("stage_provenance")
            if not isinstance(provenance, dict):
                fail(f"{where}: stage_provenance must be a mapping")
                provenance = {}
            provenance_kind = provenance.get("kind")
            allowed_provenance = {
                "performed_by_this_tool",
                "preexisting_before_conversation",
                "established_by_prior_tool",
            }
            if provenance_kind not in allowed_provenance:
                fail(f"{where}.stage_provenance.kind must be one of "
                     f"{sorted(allowed_provenance)}, got {provenance_kind!r}")
            if not str(provenance.get("fact") or "").strip():
                fail(f"{where}.stage_provenance.fact is empty")
            provenance_evidence = provenance.get("evidence")
            if not isinstance(provenance_evidence, list) or not provenance_evidence:
                fail(f"{where}.stage_provenance.evidence must be non-empty")
                provenance_evidence = []
            for ref in provenance_evidence:
                check_evidence(ref, f"{where}.stage_provenance", step)

            has_prior = any(
                isinstance(ref, str) and ref.startswith("prior_step:")
                for ref in provenance_evidence
            )
            if provenance_kind == "preexisting_before_conversation":
                has_system_record = any(
                    isinstance(ref, str) and ref.startswith("initial_state.")
                    for ref in provenance_evidence
                )
                if not has_system_record:
                    fail(f"{where}.stage_provenance: a pre-existing external fact must cite "
                         "an authoritative initial_state record; user_scenario alone is not authority")
                if has_prior:
                    fail(f"{where}.stage_provenance: a pre-existing fact may not be "
                         "created by a prior_step")
            elif provenance_kind == "established_by_prior_tool" and not has_prior:
                fail(f"{where}.stage_provenance: established_by_prior_tool must cite "
                     "the establishing prior_step")

            required_refs = set()
            required_gates = set()
            scope_free_policies = set()   # governing policies whose every applicable gate an overwrite retired
            required_subjects = set()
            extended_lineage_refs = set()
            for comp in computations:
                comp = as_dict(comp)
                if comp.get("step") != step:
                    continue
                ep = ext_policies.get(comp.get("policy_id"))
                if not ep:
                    fail(f"{where}: computation names unknown extended policy "
                         f"{comp.get('policy_id')!r}")
                    continue
                required_subjects.update(as_list(ep.get("subject")))
                extended_lineage_refs.update(as_list(ep.get("base_policy_refs")))
            required_subjects.discard(None)
            for policy_id in extended_lineage_refs:
                if policy_id not in base_policies:
                    fail(f"{where}: extended lineage references unknown base policy {policy_id!r}")
            governing_refs = {
                policy_id for policy_id, base_policy in base_policies.items()
                if required_subjects & set(as_list(base_policy.get("subject")))
            }
            missing_lineage = governing_refs - extended_lineage_refs
            if missing_lineage:
                fail(f"{where}: extended base_policy_refs omit governing base policies "
                     f"{sorted(missing_lineage)}")
            required_refs.update(governing_refs)
            if not required_subjects or not required_refs:
                fail(f"{where}: every business call must resolve an exact base event subject and all "
                     "base policies governing that write; a gold write with no computation is not a "
                     "problem of the tree")
            for policy_id in required_refs:
                base_policy = base_policies.get(policy_id)
                if base_policy is None:
                    fail(f"{where}: write lineage references unknown base policy {policy_id!r}")
                    continue
                gates_all = [as_dict(gate) for gate in as_list(base_policy.get("eligibility"))
                             if set(as_list(as_dict(gate).get("applies_to"))) & required_subjects]
                gates = [gate for gate in gates_all if (policy_id, gate.get("id")) not in retired_gates]
                if gates:
                    for gate in gates:
                        required_gates.add((policy_id, gate.get("id")))
                elif gates_all:
                    scope_free_policies.add(policy_id)
                else:
                    required_gates.add((policy_id, "policy_scope"))

            preconditions = item.get("base_preconditions")
            if not isinstance(preconditions, list):
                fail(f"{where}: base_preconditions must be a list")
                preconditions = []
            declared_refs, declared_gates = set(), set()
            for pindex, precondition in enumerate(preconditions):
                precondition = as_dict(precondition)
                pwhere = f"{where}.base_preconditions[{pindex}]"
                policy_id = precondition.get("policy_id")
                eligibility_id = precondition.get("eligibility_id")
                gate = None
                if policy_id not in base_policies:
                    fail(f"{pwhere}: unknown policy_id {policy_id!r}")
                else:
                    declared_refs.add(policy_id)
                    policy_gates = {as_dict(g).get("id"): as_dict(g)
                                    for g in as_list(base_policies[policy_id].get("eligibility"))}
                    required_key = (policy_id, eligibility_id)
                    if eligibility_id == "policy_scope":
                        gate = None
                        if policy_id in scope_free_policies:
                            continue      # every applicable gate of this policy is retired by an extended overwrite
                        if required_key not in required_gates:
                            fail(f"{pwhere}: policy_scope is not applicable here; {policy_id} has "
                                 "subject-scoped eligibility gates for this write")
                    elif eligibility_id not in policy_gates:
                        fail(f"{pwhere}: eligibility_id {eligibility_id!r} is not a gate of {policy_id}")
                        gate = None
                    else:
                        gate = policy_gates[eligibility_id]
                        if required_key in retired_gates:
                            continue      # retired by an extended overwrite: tolerated when declared, never required
                        if required_key not in required_gates:
                            fail(f"{pwhere}: eligibility gate {eligibility_id!r} does not apply to any "
                                 "exact base event subject realized by this business call")
                    if required_key in declared_gates:
                        fail(f"{pwhere}: duplicate base precondition {required_key}")
                    declared_gates.add(required_key)
                if not str(precondition.get("condition") or "").strip():
                    fail(f"{pwhere}: condition is empty")
                evidence = precondition.get("evidence")
                evidence_fields = set()
                if not isinstance(evidence, list) or not evidence:
                    fail(f"{pwhere}: evidence must be non-empty")
                else:
                    for ref in evidence:
                        field_ref = check_evidence(ref, pwhere, step)
                        if field_ref:
                            evidence_fields.add(field_ref)
                if precondition.get("satisfied") is not True:
                    fail(f"{pwhere}: satisfied must be true")
                if policy_id in base_policies and gate is not None:
                    if str(precondition.get("condition") or "").strip() != str(gate.get("condition") or "").strip():
                        fail(f"{pwhere}: condition must quote the eligibility gate verbatim")
                    needed_fields = set(as_list(gate.get("evidence_fields")))
                    # A preceding write may establish an authoritative evidence row in an
                    # earlier step.  The evidence list names the producing step,
                    # while its structured correlation bindings name the table in
                    # that step's real DB delta.  When that delta changes exactly
                    # one row, the row is the cited system evidence: count all of
                    # its fields, not only the subset copied into current args.
                    # The correlation values are still resolved and compared below.
                    prior_sources = set()
                    for binding in as_list(precondition.get("evidence_bindings")):
                        binding = as_dict(binding)
                        source = binding.get("source")
                        source_table = binding.get("source_table")
                        if (
                            isinstance(source, str)
                            and source.startswith("prior_step:")
                            and isinstance(source_table, str)
                        ):
                            try:
                                prior_sources.add((int(source.split(":", 1)[1]), source_table))
                            except ValueError:
                                pass
                    for prior, source_table in prior_sources:
                        before_db, before_error = replay_prefix(
                            deepcopy(initial), deepcopy(actions), prior)
                        after_db, after_error = replay_prefix(
                            deepcopy(initial), deepcopy(actions), prior + 1)
                        if before_error or after_error:
                            continue
                        before_rows = as_dict(before_db.tables.get(source_table))
                        after_rows = as_dict(after_db.tables.get(source_table))
                        changed_rows = [
                            as_dict(row) for row_id, row in after_rows.items()
                            if as_dict(before_rows.get(row_id)) != as_dict(row)
                        ]
                        if len(changed_rows) == 1:
                            evidence_fields.update(
                                f"{source_table}.{field}" for field in changed_rows[0]
                            )
                    if not needed_fields <= evidence_fields:
                        fail(f"{pwhere}: evidence does not cover gate fields "
                             f"{sorted(needed_fields - evidence_fields)}")
                    if gate.get("kind") == "time" and "frozen_time" not in evidence:
                        fail(f"{pwhere}: a time eligibility gate must cite frozen_time")
                    if gate.get("kind") == "time":
                        required_time_gates[(step, policy_id, eligibility_id)] = gate
                    evidence_contract = gate.get("evidence_contract")
                    if not isinstance(evidence_contract, dict):
                        fail(f"{pwhere}: gate lacks evidence_contract")
                        evidence_contract = {}
                    authority = evidence_contract.get("authority")
                    timing = evidence_contract.get("timing")
                    correlation_groups = evidence_contract.get("correlation_keys")
                    expected_action_bindings = evidence_contract.get("action_bindings")
                    if authority not in {"system_record", "caller_statement", "mixed"}:
                        fail(f"{pwhere}: evidence_contract.authority is invalid")
                    if timing != "pre_action":
                        fail(f"{pwhere}: evidence_contract.timing must be pre_action")
                    if not isinstance(correlation_groups, list) or not correlation_groups:
                        fail(f"{pwhere}: evidence_contract.correlation_keys must be non-empty")
                        correlation_groups = []
                    if not isinstance(expected_action_bindings, dict) or not expected_action_bindings:
                        fail(f"{pwhere}: evidence_contract.action_bindings must be a non-empty mapping")
                        expected_action_bindings = {}

                    evidence_refs = set(evidence) if isinstance(evidence, list) else set()
                    has_system_evidence = any(
                        isinstance(ref, str)
                        and (ref.startswith("initial_state.") or ref.startswith("prior_step:"))
                        for ref in evidence_refs
                    )
                    has_caller_evidence = any(
                        isinstance(ref, str) and ref.startswith("user_scenario:")
                        for ref in evidence_refs
                    )
                    if authority == "system_record" and not has_system_evidence:
                        fail(f"{pwhere}: authoritative system_record gate lacks pre-action system evidence")
                    elif authority == "caller_statement" and not has_caller_evidence:
                        fail(f"{pwhere}: caller_statement gate lacks user_scenario evidence")
                    elif authority == "mixed" and not (has_system_evidence and has_caller_evidence):
                        fail(f"{pwhere}: mixed-authority gate requires both system and caller evidence")

                    bindings = precondition.get("evidence_bindings")
                    if not isinstance(bindings, list) or not bindings:
                        fail(f"{pwhere}: evidence_bindings must be a non-empty list")
                        bindings = []
                    bound_fields = set()
                    binding_authorities = {}
                    current_args = action_business_args(actions[step])
                    allowed_fields = {
                        field for group in correlation_groups if isinstance(group, list)
                        for field in group
                    }
                    for bindex, binding in enumerate(bindings):
                        binding = as_dict(binding)
                        bwhere = f"{pwhere}.evidence_bindings[{bindex}]"
                        gate_field = binding.get("gate_field")
                        if gate_field not in allowed_fields:
                            fail(f"{bwhere}: gate_field {gate_field!r} is not in correlation_keys")
                        if gate_field in bound_fields:
                            fail(f"{bwhere}: duplicate gate_field binding {gate_field!r}")
                        bound_fields.add(gate_field)
                        source = binding.get("source")
                        if source not in evidence_refs:
                            fail(f"{bwhere}: source must also appear in this precondition's evidence list")
                        action_arg = binding.get("action_arg")
                        if not isinstance(action_arg, str) or action_arg not in current_args:
                            fail(f"{bwhere}: action_arg must name an argument of the current task-tool call")
                            continue
                        expected_action_arg = expected_action_bindings.get(gate_field)
                        if action_arg != expected_action_arg:
                            fail(f"{bwhere}: action_arg {action_arg!r} must equal the blueprint's fixed "
                                 f"action_bindings[{gate_field!r}]={expected_action_arg!r}")
                        source_value, source_authority = binding_source_value(binding, bwhere, step)
                        binding_authorities[gate_field] = source_authority
                        if source_value is not None and str(source_value) != str(current_args.get(action_arg)):
                            fail(f"{bwhere}: source value {source_value!r} != "
                                 f"current action argument {action_arg}={current_args.get(action_arg)!r}")

                    satisfied_groups = [
                        set(group) for group in correlation_groups
                        if isinstance(group, list) and group and set(group) <= bound_fields
                    ]
                    if not satisfied_groups:
                        fail(f"{pwhere}: evidence_bindings do not completely cover any correlation_keys group")
                    else:
                        group_authorities = {
                            binding_authorities.get(field)
                            for field in satisfied_groups[0]
                        }
                        if authority == "system_record" and group_authorities != {"system"}:
                            fail(f"{pwhere}: system_record correlation group must bind only pre-action system values")
                        if authority == "caller_statement" and group_authorities != {"caller"}:
                            fail(f"{pwhere}: caller_statement correlation group must bind caller values")
                        if authority == "mixed" and not {"system", "caller"} <= group_authorities:
                            fail(f"{pwhere}: mixed correlation group must bind both system and caller values")
                    if gate.get("kind") == "dedup":
                        dedup = gate.get("dedup_contract")
                        if not isinstance(dedup, dict):
                            fail(f"{pwhere}: kind=dedup gate lacks dedup_contract")
                        else:
                            current_args = action_business_args(actions[step])
                            missing_args = sorted(
                                action_arg for action_arg in as_dict(
                                    dedup.get("object_bindings")).values()
                                if action_arg not in current_args
                            )
                            if missing_args:
                                fail(f"{pwhere}: dedup object_bindings name absent current action "
                                     f"arguments {missing_args}")
                elif gate is None and precondition.get("evidence_bindings") not in (None, []):
                    fail(f"{pwhere}: policy_scope must not declare evidence_bindings")
            if required_refs != declared_refs:
                missing = sorted(required_refs - declared_refs)
                extra = sorted(declared_refs - required_refs)
                fail(f"{where}: base_preconditions policy refs must exactly match every base policy "
                     f"governing this write subject; missing={missing}, extra={extra}")
            if required_gates != declared_gates:
                missing = sorted(required_gates - declared_gates, key=str)
                extra = sorted(declared_gates - required_gates, key=str)
                fail(f"{where}: base_preconditions must exactly match subject-scoped eligibility; "
                     f"missing={missing}, extra={extra}")
            gates_checked += len(required_gates)

        temporal = contract.get("temporal_feasibility")
        if not isinstance(temporal, list):
            fail("temporal_feasibility must be a list")
            temporal = []
        declared_time_gates = set()
        for index, item in enumerate(temporal):
            item = as_dict(item)
            where = f"temporal_feasibility[{index}]"
            temporal_step = item.get("step")
            policy_id = item.get("policy_id")
            eligibility_id = item.get("eligibility_id")
            valid_key = (
                isinstance(temporal_step, int) and not isinstance(temporal_step, bool)
                and isinstance(policy_id, str) and bool(policy_id)
                and isinstance(eligibility_id, str) and bool(eligibility_id)
            )
            if not valid_key:
                fail(f"{where}: step/policy_id/eligibility_id must be an integer call step and "
                     "non-empty string ids")
                key = None
            else:
                key = (temporal_step, policy_id, eligibility_id)
                if key in declared_time_gates:
                    fail(f"{where}: duplicate time gate {key}")
                declared_time_gates.add(key)
            gate = required_time_gates.get(key) if key is not None else None
            if gate is None:
                fail(f"{where}: {key} is not a time eligibility used by that gold action")
            if not str(item.get("condition") or "").strip():
                fail(f"{where}: condition is empty")
            elif gate is not None and str(item.get("condition")).strip() != str(gate.get("condition") or "").strip():
                fail(f"{where}: condition must quote the base time eligibility verbatim")
            declared_temporal_basis = item.get("temporal_basis")
            if not isinstance(declared_temporal_basis, dict):
                fail(f"{where}: temporal_basis must copy the base time contract")
            elif gate is not None and declared_temporal_basis != as_dict(gate.get("temporal_basis")):
                fail(f"{where}: temporal_basis must deep-equal the base eligibility contract; "
                     "task authoring may not change anchor, counting rule, direction, or boundary")
            if item.get("as_of") != "frozen_time":
                fail(f"{where}: as_of must be 'frozen_time'")
            if item.get("satisfied") is not True:
                fail(f"{where}: satisfied must be true")
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                fail(f"{where}: evidence must be non-empty")
            else:
                for ref in evidence:
                    check_evidence(ref, where, temporal_step if valid_key else None)
                if "frozen_time" not in evidence:
                    fail(f"{where}: time feasibility evidence must cite frozen_time")
            boundary_check = item.get("boundary_check")
            if not isinstance(boundary_check, dict):
                fail(f"{where}: boundary_check must record the adjacent failing and passing cases")
            else:
                if not str(boundary_check.get("just_before") or "").strip():
                    fail(f"{where}: boundary_check.just_before is empty")
                if not str(boundary_check.get("at_boundary") or "").strip():
                    fail(f"{where}: boundary_check.at_boundary is empty")
        if set(required_time_gates) != declared_time_gates:
            fail("temporal_feasibility must exactly cover time eligibility gates used by gold actions; "
                 f"missing={sorted(set(required_time_gates) - declared_time_gates, key=str)}, "
                 f"extra={sorted(declared_time_gates - set(required_time_gates), key=str)}")

        user_inputs = contract.get("required_user_inputs")
        if not isinstance(user_inputs, list) or not user_inputs:
            fail("required_user_inputs must be a non-empty list")
            user_inputs = []
        for index, item in enumerate(user_inputs):
            item = as_dict(item)
            where = f"required_user_inputs[{index}]"
            if not str(item.get("information") or "").strip():
                fail(f"{where}: information is empty")
            source = item.get("source")
            if not isinstance(source, str) or not source.startswith("user_scenario:"):
                fail(f"{where}: source must be user_scenario:<verbatim snippet>")
            else:
                check_evidence(source, where)

        seeded_rows = {(table, row_id) for table in primary_seed_tables
                       for row_id in as_dict(initial.get(table))}
        consistency = contract.get("seed_consistency")
        if not isinstance(consistency, list):
            fail("seed_consistency must be a list")
            consistency = []
        covered_rows = set()
        for index, item in enumerate(consistency):
            item = as_dict(item)
            where = f"seed_consistency[{index}]"
            row_ref = item.get("row")
            check_evidence(row_ref, where)
            parts = row_ref.split(".") if isinstance(row_ref, str) else []
            if len(parts) == 3:
                pair = (parts[1], parts[2])
                if pair in covered_rows:
                    fail(f"{where}: row {row_ref!r} is covered more than once")
                covered_rows.add(pair)
            else:
                fail(f"{where}: row must be an initial_state.<table>.<row_id> path")
            policy_id = item.get("policy_id")
            if policy_id not in base_policies:
                fail(f"{where}: policy_id {policy_id!r} is not a base policy")
            elif len(parts) == 3 and parts[1] in set(as_list(binding.get("event_tables"))):
                row = as_dict(as_dict(initial.get(parts[1])).get(parts[2]))
                event_type = row.get("event_type")
                if event_type not in as_list(base_policies[policy_id].get("subject")):
                    fail(f"{where}: policy {policy_id} does not govern seeded event type "
                         f"{event_type!r}")
            if not str(item.get("check") or "").strip():
                fail(f"{where}: check is empty")
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                fail(f"{where}: evidence must be non-empty")
            else:
                for ref in evidence:
                    check_evidence(ref, where)
        if not seeded_rows <= covered_rows:
            missing = [f"initial_state.{table}.{row}" for table, row in sorted(seeded_rows - covered_rows)]
            fail(f"seed_consistency misses primary holding/event rows {missing}")

        # ---- prerequisite_closure: the TASK-side facts of the problem tree ----
        # The policy side (edge shape, refs, acyclicity, prose sourcing) is gated by
        # check_extended; here we gate what only the task can assert: that each declared
        # prerequisite is REALLY unsatisfied at frozen_time, that every edge is load-bearing,
        # that the resolution order is topological, that the persona never hints, and that
        # no tool blocks.  The most common silent degradation is a prerequisite that the seed
        # already satisfies: the task still has a unique solution, so every other gate stays
        # green while the task quietly stops testing what it was designed to test.
        pc = task.get("prerequisite_closure")
        if not isinstance(pc, dict):
            fail("missing prerequisite_closure mapping — every task is a problem tree")
        else:
            root = pc.get("root_problem")
            if not str(root or "").strip():
                fail("prerequisite_closure.root_problem is empty")
            edges = as_list(pc.get("edges"))
            dep_problems = {str(e.get("to") or "").strip() for e in edges if isinstance(e, dict)} - {"", str(root or "")}
            if len(dep_problems) < 3:
                fail(f"prerequisite_closure declares {len(dep_problems)} prerequisite problem(s); at least 3 are "
                     "required, the root not counted (any acyclic shape: chain, fan-out, diamond or a mix)")
            kinds = [e.get("kind") for e in edges if isinstance(e, dict)]
            if edges and kinds.count("value_input") < 2:
                fail(f"prerequisite_closure has {kinds.count('value_input')} value_input edge(s); at least 2 are "
                     "required — state_gate edges alone leave the terminal DB identical whichever order the "
                     "writes take, and a single value_input edge hangs the whole calculation test on one number")
            for ei, e in enumerate(edges):
                where = f"prerequisite_closure.edges[{ei}]"
                if not isinstance(e, dict):
                    fail(f"{where}: must be a mapping")
                    continue
                for key in ("from", "to", "kind", "form", "condition", "policy_source", "resolved_by"):
                    if not str(e.get(key) or "").strip():
                        fail(f"{where}: missing {key}")
                unres = e.get("unresolved_at_frozen_time")
                if not isinstance(unres, dict):
                    fail(f"{where}: missing unresolved_at_frozen_time — a prerequisite that the seed "
                         "already satisfies is not a prerequisite, it is a satisfied eligibility")
                    continue
                if not str(unres.get("why_false") or "").strip():
                    fail(f"{where}.unresolved_at_frozen_time: missing why_false")
                if not str(unres.get("flips_to_true_by") or "").strip():
                    fail(f"{where}.unresolved_at_frozen_time: missing flips_to_true_by")
                ev = as_list(unres.get("evidence"))
                if not ev:
                    fail(f"{where}.unresolved_at_frozen_time: missing evidence — point at the "
                         "initial_state rows that make this condition FALSE at frozen_time")
                for ref in ev:
                    raw = str(ref).split("=", 1)[0].strip()
                    if not raw.startswith("initial_state."):
                        fail(f"{where}.unresolved_at_frozen_time: evidence {ref!r} must be an "
                             "initial_state.<table>.<row_id>[.<field>] path — the condition must be "
                             "false as a matter of world FACT, not by authorial assertion")
                        continue
                    check_evidence(raw, f"{where}.unresolved_at_frozen_time")
            order = as_list(pc.get("resolution_order"))
            if not order:
                fail("prerequisite_closure.resolution_order is empty")
            else:
                pos = {n: i for i, n in enumerate(order)}
                if len(pos) != len(order):
                    fail(f"prerequisite_closure.resolution_order has duplicates: {order}")
                if root and root in pos and pos[root] != len(order) - 1:
                    fail("prerequisite_closure.resolution_order must end at root_problem — every "
                         "prerequisite is solved before the problem the customer actually asked about")
                for ei, e in enumerate(edges):
                    if not isinstance(e, dict):
                        continue
                    frm, to = e.get("from"), e.get("to")
                    if frm in pos and to in pos and pos[to] >= pos[frm]:
                        fail(f"prerequisite_closure.resolution_order is not topological: '{to}' must "
                             f"precede '{frm}' (edges[{ei}])")
                    for node in (frm, to):
                        if node and node not in pos:
                            fail(f"prerequisite_closure: '{node}' appears in edges[{ei}] but not in "
                                 "resolution_order")
            for key in ("order_uniqueness", "no_user_hint", "tools_do_not_block"):
                if not str(pc.get(key) or "").strip():
                    fail(f"prerequisite_closure.{key} is empty")
            lb = as_list(pc.get("edge_load_bearing"))
            if len(lb) < len(edges):
                fail(f"prerequisite_closure.edge_load_bearing covers {len(lb)} of {len(edges)} edges — "
                     "every edge needs the recorded effect of skipping it; an edge whose removal "
                     "changes no scored parameter and no terminal field is decorative")
            for li, item in enumerate(lb):
                if not isinstance(item, dict) or not str(item.get("skipped_effect") or "").strip():
                    fail(f"prerequisite_closure.edge_load_bearing[{li}]: missing skipped_effect")
            # the persona must never surface a prerequisite problem by name
            for e in edges:
                if not isinstance(e, dict):
                    continue
                dep = str(e.get("to") or "").strip()
                if dep and dep in persona:
                    fail(f"user_scenario names the prerequisite problem '{dep}' — the customer does not "
                         "know the policy; the existence of a prerequisite may only reach the agent "
                         "through the KB")

        task_ok = not fails
        print(f"{tid:12} {str(verification_ok):>6} {len(call_steps):>5} "
              f"{gates_checked:>10} {len(seeded_rows):>10} {str(task_ok):>4}")
        all_fails.extend(fails)

    if all_fails:
        print("\n  [FAIL]")
        for message in all_fails[:80]:
            print("   -", message)
        if len(all_fails) > 80:
            print(f"   ... {len(all_fails) - 80} more")
        print("SOLVABILITY NOT OK")
        sys.exit(1)
    print("\nSOLVABILITY OK")


if __name__ == "__main__":
    main()
