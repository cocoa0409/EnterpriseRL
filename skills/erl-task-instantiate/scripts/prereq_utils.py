"""Shared PREREQUISITE helpers for this skill's gates.

A task is a PROBLEM TREE, not a single problem.  Every problem is one `extended_policy`,
resolved by one call of its target_tool; `prerequisite` declares problem->problem
dependencies, and the edges of a difficulty together form the execution graph of its
tasks (a directed acyclic graph).  A task's gold write sequence is a topological order of
the tree rooted at its root problem.  There is no other source of ordering: no workflow,
no step list, no convention.

Edge shape (policy side, general prose — no task-specific facts):
    problem          another extended_policy id in the SAME file
    kind             state_gate | value_input
    gate             <policy>.<eligibility> | <table>.<field> | <compute binding name>
    form             state | action — the form of the prerequisite sentence
    policy_source    the PREREQUISITE SENTENCE: a verbatim sentence of THIS policy's own rule
                     that states outright, with an explicit ordering connective (before /
                     after / only after / only once / until / first ...), that this policy's
                     own result waits on something:
                       state form  (preferred) — it waits on a STATE the records make
                                   visible (a kind of entry standing on an account, a
                                   status, a field, a balance, a date), named in the words
                                   the tables and finders use; the sentence names no action,
                                   no performer and no tool, so the reader must still work
                                   out which problem's write brings that state about;
                       action form (fallback) — it waits on the depended-on ACTION, named in
                                   plain business language; used only where no record-visible
                                   state can carry the dependency, and `fallback_reason`
                                   says why.
                     In either form: no tool name, no policy id, no code token.
    fallback_reason  required when form == action (absent otherwise): why no record-visible
                     state carries this dependency
    condition        the state of the records that must hold at this problem's handling
                     time, in record terms (an authoring / verification field: what the
                     task's unresolved_at_frozen_time falsifies and flips_to_true_by restores)
    resolved_by      the depended-on problem's target_tool
    effect           which gate flips true / which compute binding changes value
"""
import re

KINDS = ("state_gate", "value_input")
FORMS = ("state", "action")
EDGE_KEYS = ("problem", "kind", "gate", "form", "condition", "policy_source", "resolved_by", "effect")
# Authoring-view leakage: `prerequisite` is general product law, never task narration.
TASK_VIEW_WORDS = ("this task", "this problem", "the opening world", "the current world",
                   "this customer currently", "this seed")
# Ordering / timing connectives joining the two sides of a prerequisite sentence. A
# prerequisite sentence MUST carry one: it states outright that this policy's result waits
# on a state (or, as a declared fallback, on an action).
ORDER_CUE = re.compile(r"\b(?:before|after|first|then|until|once|prior\s+to|only\s+after|only\s+once"
                       r"|not\s+until|no\s+earlier\s+than|no\s+sooner\s+than|already|thereafter"
                       r"|subsequently|beforehand|in\s+advance|ahead\s+of|precede[sd]?|preceding)\b", re.I)
# The KB carries the prerequisite sentence verbatim and the KB render gate (erl-kb-doc-render/scripts/check_docs.py) rejects these tokens in prose.
CODE_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+|\b[0-9a-f]{16}\b")
_WORD = re.compile(r"[a-z0-9]+")
_STOP = set("a an the of to and or is are be by for in on at as that this with from its it their any "
            "every each which who has have been was were not no than then when where once so into "
            "under over per such these those shall will would may must can could should".split())


def _nows(s):
    return "".join(str(s or "").split())


def _content_words(text):
    return {w for w in _WORD.findall(str(text or "").lower()) if len(w) > 2 and w not in _STOP}


def problem_index(ext):
    """Map every solvable problem id -> ('policy', node). Every problem is an extended policy."""
    idx = {}
    for ep in ext.get("extended_policies") or []:
        pid = ep.get("id")
        if isinstance(pid, str) and pid:
            idx[pid] = ("policy", ep)
    return idx


def owners(ext):
    """Yield (owner_id, owner_kind, owner_node) for everything that may declare prerequisites."""
    for ep in ext.get("extended_policies") or []:
        yield ep.get("id", "?"), "policy", ep


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


def validate_declarations(ext, task_tool_set, fails):
    """Policy-side validation of every `prerequisite` block, including the prerequisite sentence."""
    idx = problem_index(ext)
    task_tool_set = set(task_tool_set or ())
    for oid, okind, node in owners(ext):
        w = f"{okind} {oid}"
        rule = str(node.get("rule") or "")
        rule_norm = _nows(rule)
        own_tool = str(node.get("target_tool") or "").strip()
        # A rule names no code name: no other problem's tool, no other problem's id.
        for tn in sorted(task_tool_set):
            if tn != own_tool and tn in rule:
                fails.append(f"{w}: rule names task tool '{tn}' of another problem — a prerequisite sentence names "
                             "the state it waits on, or as a fallback the action in business words, never a tool")
        for pid2 in sorted(idx):
            if pid2 != oid and pid2 in rule:
                fails.append(f"{w}: rule names another problem's id '{pid2}'")
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
                    fails.append(f"{ew}: problem '{dep}' is not an extended_policy id in this file — a "
                                 "prerequisite is another SOLVABLE problem, never a base policy")
                if dep in seen:
                    fails.append(f"{ew}: duplicate prerequisite on '{dep}'")
                seen.add(dep)
            kind = e.get("kind")
            if kind and kind not in KINDS:
                fails.append(f"{ew}: kind must be one of {KINDS}")
            # value_input must name a real compute binding of THIS policy
            if kind == "value_input":
                gate = str(e.get("gate") or "").strip()
                names = compute_binding_names(node)
                if gate and gate not in names:
                    fails.append(f"{ew}: kind=value_input but gate '{gate}' is not a compute binding of "
                                 f"{oid} (bindings: {names})")
            # ---- the form: state (preferred) or action (declared fallback) ----
            form = str(e.get("form") or "").strip()
            reason = str(e.get("fallback_reason") or "").strip()
            if form and form not in FORMS:
                fails.append(f"{ew}: form must be one of {FORMS} — state: the sentence waits on a record-visible "
                             "state; action: it waits on the depended-on action named in business words")
            if form == "action" and not reason:
                fails.append(f"{ew}: form=action without fallback_reason — the action form is a fallback; say why "
                             "no record-visible state can carry this dependency")
            if form == "state" and reason:
                fails.append(f"{ew}: form=state carries a fallback_reason — a state-form sentence needs none; "
                             "remove it or declare form: action")
            # ---- the prerequisite sentence ----
            src = str(e.get("policy_source") or "").strip()
            src_norm = _nows(src)
            if src:
                if src_norm not in rule_norm:
                    fails.append(f"{ew}: policy_source is not a verbatim sentence of this policy's OWN rule — the "
                                 "prerequisite sentence lives in the rule of the problem it blocks, never in a base "
                                 "rule and never only in this field")
                if not ORDER_CUE.search(src):
                    fails.append(f"{ew}: policy_source carries no ordering connective (before / after / only after / "
                                 "only once / until / first ...) — a prerequisite sentence states outright that this "
                                 "policy's result waits on a state (or, as a fallback, on an action)")
                if dep and dep in src:
                    fails.append(f"{ew}: policy_source names the depended-on problem's id '{dep}' — name the state it "
                                 "waits on, or the action in business words, never a code name")
                for tn in sorted(task_tool_set):
                    if tn in src:
                        fails.append(f"{ew}: policy_source names the tool '{tn}' — a prerequisite sentence names no tool")
                bad = sorted(set(CODE_TOKEN.findall(src)))
                if bad:
                    fails.append(f"{ew}: policy_source carries code token(s) {bad[:4]} — the KB carries this sentence "
                                 "verbatim and its leak gate rejects them; reword in the rule and here")
                if len(_content_words(src)) < 4:
                    fails.append(f"{ew}: policy_source is too thin to state what this policy's result waits on")
                if dep in idx:
                    dep_rule_norm = _nows(idx[dep][1].get("rule"))
                    if dep_rule_norm and src_norm in dep_rule_norm:
                        fails.append(f"{ew}: the depended-on policy '{dep}' restates this prerequisite sentence in its "
                                     "own rule — each side states only its own rule; the depended-on side never says "
                                     "who waits on it")
            # resolved_by must be the depended-on problem's own action
            rb = str(e.get("resolved_by") or "").strip()
            if rb and dep in idx:
                _dkind, dnode = idx[dep]
                want = dnode.get("target_tool")
                if want and rb != want:
                    fails.append(f"{ew}: resolved_by '{rb}' must be the depended-on problem's own action "
                                 f"('{want}')")
                if task_tool_set and rb not in task_tool_set:
                    fails.append(f"{ew}: resolved_by '{rb}' is not a hidden task tool in task_tools.py")
            # no task-authoring narration in general product law
            blob = " ".join(str(e.get(k) or "") for k in ("condition", "policy_source", "effect", "fallback_reason"))
            hit = [t for t in TASK_VIEW_WORDS if t in blob.lower()]
            if hit:
                fails.append(f"{ew}: prerequisite is general product law and must not narrate a specific "
                             f"task world; remove {hit}")

    # A prerequisite sentence is located in the corpus by its own text and carried by the documents
    # of the problem it blocks; two owners sharing one wording could not both be satisfied.
    reported, seen = set(), []
    for oid, dep, e, _okind in edges_of(ext):
        src = _nows(e.get("policy_source"))
        if not src:
            continue
        for oid2, dep2, src2 in seen:
            if oid2 == oid or (oid, oid2) in reported or (oid2, oid) in reported:
                continue
            if src == src2:
                rel = "identical to"
            elif src in src2 or src2 in src:
                rel = "textually contained in / contains"
            else:
                continue
            reported.add((oid, oid2))
            fails.append(f"prerequisite sentence of '{oid}' (waiting on '{dep}') is {rel} that of '{oid2}' "
                         f"(waiting on '{dep2}'); a prerequisite sentence is located by its text and homed in its "
                         "own policy's documents, so two policies cannot share one wording")
        seen.append((oid, dep, src))
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
    """Gate one task's problem tree: >=3 prerequisite problems, >=2 value_input edges, whole tree in scope."""
    idx = problem_index(ext)
    out = out_edges(ext)
    if root not in idx:
        fails.append(f"prereq {tid}: root_problem '{root}' is not an extended policy of this difficulty")
        return
    tree = tree_closure(root, out)
    deps = tree - {root}
    if len(deps) < 3:
        fails.append(f"prereq {tid}: problem tree rooted at '{root}' has {len(deps)} prerequisite "
                     "problem(s); at least 3 are required, the root not counted (any acyclic shape: chain, "
                     "fan-out, diamond or a mix)")
    kinds = [e.get("kind")
             for n in tree
             for e in ((idx.get(n, (None, {}))[1] or {}).get("prerequisite") or [])
             if isinstance(e, dict) and e.get("problem") in tree]
    n_vi = kinds.count("value_input")
    if kinds and n_vi < 2:
        fails.append(f"prereq {tid}: problem tree rooted at '{root}' has {n_vi} value_input edge(s); at least 2 "
                     "are required — state_gate edges alone leave the terminal DB identical whichever order "
                     "the writes take, so ordering is unobservable to hash scoring, and a single value_input "
                     "edge hangs the whole calculation test on one number")
    outside = {n for n in tree if n not in in_scope}
    if outside:
        fails.append(f"prereq {tid}: problem(s) {sorted(outside)} are in this task's tree but not in its "
                     "charter_scope — a task claims the whole tree (root plus every prerequisite problem)")
