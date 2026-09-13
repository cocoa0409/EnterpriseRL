"""Shared PREREQUISITE helpers for this skill's gates.

A task is a PROBLEM TREE, not a single problem.  `extended_policy` and `workflow`
are both "the solution to one problem"; `prerequisite` declares problem->problem
dependencies (never step order inside one problem — that lives in workflow.steps
and order_rationale).

Edge shape (policy side, general prose — no task-specific facts):
    problem        another extended_policy id or workflow id in the SAME file
    kind           state_gate | value_input
    gate           <policy>.<eligibility> | <table>.<field> | <compute binding name>
    condition      the sentence that must hold before this problem may be handled
    policy_source  verbatim sentence from THIS policy's rule or one of its
                   base_policy_refs' rules — proves the prerequisite is stated in
                   general prose and therefore reaches the agent through the KB
    resolved_by    the depended-on problem's target_tool, or its workflow id
    effect         which gate flips true / which compute binding changes value
"""

KINDS = ("state_gate", "value_input")
EDGE_KEYS = ("problem", "kind", "gate", "condition", "policy_source", "resolved_by", "effect")
# Authoring-view leakage: `prerequisite` is general product law, never task narration.
TASK_VIEW_WORDS = ("this task", "this problem", "the opening world", "the current world",
                   "this customer currently", "this seed")


def _nows(s):
    return "".join(str(s or "").split())


def problem_index(ext):
    """Map every solvable problem id -> ('policy'|'workflow', node)."""
    idx = {}
    for ep in ext.get("extended_policies") or []:
        pid = ep.get("id")
        if isinstance(pid, str) and pid:
            idx[pid] = ("policy", ep)
    for wf in ext.get("workflows") or []:
        wid = wf.get("id")
        if isinstance(wid, str) and wid:
            idx[wid] = ("workflow", wf)
    return idx


def owners(ext):
    """Yield (owner_id, owner_kind, owner_node) for everything that may declare prerequisites."""
    for ep in ext.get("extended_policies") or []:
        yield ep.get("id", "?"), "policy", ep
    for wf in ext.get("workflows") or []:
        yield wf.get("id", "?"), "workflow", wf


def edges_of(ext):
    """All declared edges as (from_problem, to_problem, entry, owner_kind)."""
    out = []
    for oid, okind, node in owners(ext):
        for e in (node.get("prerequisite") or []):
            if isinstance(e, dict):
                out.append((oid, e.get("problem"), e, okind))
    return out


def find_cycle(edges):
    """Return one cycle as a list of ids, or None.  edges = [(frm, to, ...), ...]."""
    adj = {}
    for frm, to, *_ in edges:
        if frm and to:
            adj.setdefault(frm, []).append(to)
    WHITE, GREY, BLACK = 0, 1, 2
    color, stack, found = {}, [], []

    def visit(n):
        color[n] = GREY
        stack.append(n)
        for m in adj.get(n, []):
            if color.get(m, WHITE) == GREY:
                found.extend(stack[stack.index(m):] + [m])
                return True
            if color.get(m, WHITE) == WHITE and visit(m):
                return True
        stack.pop()
        color[n] = BLACK
        return False

    for n in list(adj):
        if color.get(n, WHITE) == WHITE and visit(n):
            return found
    return None


def compute_binding_names(policy):
    names = []
    for step in (policy.get("compute") or []):
        if isinstance(step, dict):
            names.extend(step.keys())
    return names


def rule_pool(policy, base_policies):
    """Normalised text this policy may legally quote a policy_source from."""
    pool = [_nows(policy.get("rule"))]
    for ref in (policy.get("base_policy_refs") or []):
        bp = base_policies.get(ref) or {}
        pool.append(_nows(bp.get("rule")))
    return [p for p in pool if p]


def workflow_rule_pool(wf, ext, base_policies):
    """A workflow may quote from any policy its steps invoke, or those policies' bases."""
    pool = []
    by_id = {ep.get("id"): ep for ep in (ext.get("extended_policies") or [])}
    for st in (wf.get("steps") or []):
        for pid in (st.get("computed_by") or []):
            ep = by_id.get(pid)
            if ep:
                pool.extend(rule_pool(ep, base_policies))
        for ref in (st.get("base_policy_refs") or []):
            bp = base_policies.get(ref) or {}
            if bp.get("rule"):
                pool.append(_nows(bp.get("rule")))
    return [p for p in pool if p]


def validate_declarations(ext, base_policies, task_tool_set, fails):
    """Policy-side structural validation of every `prerequisite` block."""
    idx = problem_index(ext)
    for oid, okind, node in owners(ext):
        w = f"{okind} {oid}"
        pr = node.get("prerequisite")
        if pr is None:
            fails.append(f"{w}: missing prerequisite — declare each OTHER problem that must be solved "
                         "before this one can be handled, or write [] when there is none")
            continue
        if not isinstance(pr, list):
            fails.append(f"{w}: prerequisite must be a list (use [] when this problem has no prerequisite)")
            continue
        seen = set()
        for i, e in enumerate(pr):
            ew = f"{w}.prerequisite[{i}]"
            if not isinstance(e, dict):
                fails.append(f"{ew}: each entry must be a mapping with {'/'.join(EDGE_KEYS)}")
                continue
            for k in EDGE_KEYS:
                if not str(e.get(k) or "").strip():
                    fails.append(f"{ew}: missing {k}")
            dep = e.get("problem")
            if dep:
                if dep == oid:
                    fails.append(f"{ew}: problem must not reference itself")
                elif dep not in idx:
                    fails.append(f"{ew}: problem '{dep}' is not an extended_policy id or workflow id in "
                                 "this file — a prerequisite is another SOLVABLE problem, never a base policy")
                if dep in seen:
                    fails.append(f"{ew}: duplicate prerequisite on '{dep}'")
                seen.add(dep)
            kind = e.get("kind")
            if kind and kind not in KINDS:
                fails.append(f"{ew}: kind must be one of {KINDS}")
            # value_input must name a real compute binding of THIS policy
            if kind == "value_input" and okind == "policy":
                gate = str(e.get("gate") or "").strip()
                names = compute_binding_names(node)
                if gate and gate not in names:
                    fails.append(f"{ew}: kind=value_input but gate '{gate}' is not a compute binding of "
                                 f"{oid} (bindings: {names})")
            # policy_source must be quotable from general prose
            src = str(e.get("policy_source") or "").strip()
            if src:
                pool = (rule_pool(node, base_policies) if okind == "policy"
                        else workflow_rule_pool(node, ext, base_policies))
                if not any(_nows(src) in p for p in pool):
                    fails.append(f"{ew}: policy_source is not a verbatim sentence of this problem's own rule "
                                 "or of any base policy it inherits — a prerequisite that is not written into "
                                 "general prose never reaches the agent through the KB, so it is undiscoverable")
            # resolved_by must be the depended-on problem's own action
            rb = str(e.get("resolved_by") or "").strip()
            if rb and dep in idx:
                dkind, dnode = idx[dep]
                want = dnode.get("target_tool") if dkind == "policy" else dep
                if want and rb != want:
                    fails.append(f"{ew}: resolved_by '{rb}' must be the depended-on problem's own action "
                                 f"('{want}')")
                if dkind == "policy" and rb and task_tool_set and rb not in task_tool_set:
                    fails.append(f"{ew}: resolved_by '{rb}' is not a hidden task tool in task_tools.py")
            # no task-authoring narration in general product law
            blob = " ".join(str(e.get(k) or "") for k in ("condition", "policy_source", "effect"))
            hit = [t for t in TASK_VIEW_WORDS if t in blob.lower()]
            if hit:
                fails.append(f"{ew}: prerequisite is general product law and must not narrate a specific "
                             f"task world; remove {hit}")

    # A prerequisite condition is located in the corpus by its own text: the rendering must carry it
    # in the documents of the problem it blocks, and no document may carry two owners' conditions.
    # Two owners sharing one wording therefore cannot both be satisfied — the text would have to live
    # inside each owner's documents at once, and a document belongs to exactly one owner. Containment
    # collides for the same reason, because the lookup is a substring match.
    reported, seen = set(), []
    for oid, dep, e, _okind in edges_of(ext):
        cond = _nows(e.get("condition"))
        if not cond:
            continue
        for oid2, dep2, cond2 in seen:
            if oid2 == oid or (oid, oid2) in reported or (oid2, oid) in reported:
                continue
            if cond == cond2:
                rel = "identical to"
            elif cond in cond2 or cond2 in cond:
                rel = "textually contained in / contains"
            else:
                continue
            reported.add((oid, oid2))
            fails.append(f"prerequisite condition of '{oid}' (blocking '{dep}') is {rel} that of "
                         f"'{oid2}' (blocking '{dep2}'); a condition is located by its text, so two "
                         f"owners cannot each carry the same wording in their own documents — give "
                         f"each owner's condition wording of its own")
        seen.append((oid, dep, cond))
    cyc = find_cycle(edges_of(ext))
    if cyc:
        fails.append("prerequisite graph has a cycle: " + " -> ".join(cyc))


def out_edges(ext):
    """problem id -> [depended-on problem ids]."""
    out = {}
    for oid, _okind, node in owners(ext):
        out[oid] = [e.get("problem") for e in (node.get("prerequisite") or [])
                    if isinstance(e, dict) and e.get("problem")]
    return out


def tree_closure(root, out):
    """Transitive closure of problems reachable from `root` (inclusive)."""
    seen, stack = set(), [root]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(out.get(n, []))
    return seen


def check_task_tree(tid, root, in_scope, ext, fails):
    """Gate one task's problem tree: >=2 prerequisites, >=1 value_input, whole tree in scope."""
    idx = problem_index(ext)
    out = out_edges(ext)
    if root not in idx:
        fails.append(f"prereq {tid}: root_problem '{root}' is not a policy or workflow of this difficulty")
        return
    tree = tree_closure(root, out)
    deps = tree - {root}
    if len(deps) < 2:
        fails.append(f"prereq {tid}: problem tree rooted at '{root}' has {len(deps)} prerequisite "
                     "problem(s); at least 2 are required (chain A->B->C or fan-out A->B, A->C)")
    kinds = [e.get("kind")
             for n in tree
             for e in ((idx.get(n, (None, {}))[1] or {}).get("prerequisite") or [])
             if isinstance(e, dict) and e.get("problem") in tree]
    if kinds and "value_input" not in kinds:
        fails.append(f"prereq {tid}: problem tree rooted at '{root}' has no value_input edge — with only "
                     "state_gate edges the terminal DB is identical whether the prerequisite is solved "
                     "before or after, so the ordering it asserts is unobservable to hash scoring")
    outside = {n for n in tree if n not in in_scope}
    if outside:
        fails.append(f"prereq {tid}: problem(s) {sorted(outside)} are in this task's tree but not in its "
                     "charter_scope — a task claims the whole tree (root plus every prerequisite problem)")
