"""DOCS gate: verify a rendered KB corpus (env/<scenario>/docs/<product>/) against the
render values — agent-facing wording with zero implementation leaks, independent policy
fragments, quantitative coverage (every number rendered at least once), tool fidelity, prerequisite sentences carried verbatim.
Normative semantic bijection is a manual hard gate: this script cannot prove that prose invented
no confirmation/review step.

WHAT IT CHECKS (the mechanically decidable subset of SKILL.md's values):
  structure   id/title/content/meta present; id == doc_<product>_<topic>_<uuid8> and matches
              the filename; unique ids. Length is reported, never used as a pass condition:
              source fidelity outranks manual-like fullness.
  leak        content+title contain NO snake_case code token outside the whitelist
              (task tool names ∪ share tool names ∪ unlock/call meta-tool names), no compute-DSL
              fragments, no 16-hex row ids. This single rule catches table/field/event/param/
              policy-id leakage wholesale (they are all snake_case). Every doc's content must also
              name its product (the display name or the shared prefix of its tier names).
  tools       every task tool has EXACTLY ONE invocation doc (meta.tool), whose role follows the
              product-wide reference split: a target_tool referenced by one policy is merged into
              that hub; shared or non-target tools have a standalone tool doc. Content names the
              tool verbatim plus unlock wording and spells out every parameter by name; user-owned
              tools' docs must say the customer themselves.
  no workflow the charter has no `workflows` key and no doc has role=sop or meta.workflow: every
              problem is an extended policy, and the order of a task's writes is what the
              solver works out from the policies' prerequisite sentences, the depended-on
              rules and the records — never from a rendered route.
  scatter     every extended policy has EXACTLY ONE hub (meta.role=hub, carries empty), but the hub
              MUST NOT expose a factor list, factor count, fragment navigation, or completion cue.
              The computation doc and the factor docs privately claim source compute bindings
              through meta.covers; every binding (including result) is covered by a fragment. The source fixes
              the factor fragments: every declared `factors[].id` of a policy has EXACTLY ONE factor
              doc (meta.factor == the id) whose covers include all of that factor's bindings, no
              factor doc names an undeclared factor, and a cross_difficulty factor's doc names the
              other product by its display name (findable from that product's records). Such a
              policy also has EXACTLY ONE computation doc (role=baseline) covering every
              non-factor binding (result included), carrying every baseline.params key that is the
              policy's own params key, and free
              of any hint that something modifies it (unless-otherwise, adjustments may apply,
              qualifying customers, elsewhere); no doc of the retired meta_rule role; and no factor doc points at,
              overrides or replaces "the standard calculation" — a discrete topology, never a star.
              The SKILL's single-home rule is an authoring ideal this gate does NOT enforce: it caps
              no doc's carries and never fails a second home. It checks only the floor — a policy's
              OWN constants (its params) rendered in that policy's own docs, and every tier
              parameter (variants.<key>) rendered at least once somewhere in the product corpus,
              the docs whose rules read it naming it in business words.
              Whether every tier of a ladder is present and exact in the prose is a MANUAL gate.
  prereq      a prerequisite is carried AS THE SOURCE STATES IT: the edge's PREREQUISITE SENTENCE
              (`policy_source`, a sentence of the blocked policy's own rule stating outright, with
              an ordering connective, what that policy's result waits on — a record-visible state
              in the state form, the depended-on action in business words in the action form)
              appears VERBATIM in a doc of the blocked policy (its hub or one of its fragments) and
              in no doc of any other policy; the depended-on policy's own docs carry its own rule;
              the `resolved_by` tool of an edge must not appear in the blocked policy's docs (a
              tool-name pointer welds two problems into one procedure). The edge's `condition`,
              `fallback_reason` and `resolved_by` are authoring fields. Whether the hop is then
              resolvable from the sentence, the depended-on docs and the records at the source's
              strength — and whether a state-form restatement quietly names the action — is a
              MANUAL gate.
  routed      the controlled scaffolding of a route across problems fails anywhere: step-before-
              step ordering, procedure entry conditions, wrong/correct-reading contrasts, named
              mistakes. Titles may not take the question form or the internal-procedure form
              (task-mirroring titles).
  full span   EVERYTHING in the charter is carried somewhere (splitting must never drop): every BASE
              policy has >=1 doc (meta.policy_id); every extended policy has its hub+fragments;
              every task tool its invocation doc; every parameter_schema key a home. Scattering
              means splitting, never dropping.
  superseded  base and extended are successive versions of one product law and extended wins on
              conflict, each conflict declared clause by clause in extended_policies[].overwrite.
              A superseded clause KEEPS its bearing doc (an override never breaks the bijection)
              but that doc must declare it in meta.superseded_clauses and its prose must carry the
              controlled retirement marker, so withdrawn law can never read as in force. Declaring
              a clause the source does not retire fails too: the KB may not withdraw law on its
              own. At least one home per retired clause. Only the handling clause retires — base
              params VALUES stay valid and stay homed in that same doc, so `coverage` is unchanged.
  coverage    required quantitative keys — every extended policy params key, every variant
              param its compute reads via P('...'), every parameter_schema key, and every
              BASE policy params key whose value is a literal ("=<param>" references excluded:
              their number is already homed under variants.<param>) — each claimed by AT LEAST
              one doc's meta.carries; claimed numeric values spot-checked to
              actually appear in that doc's content (rates accept percent form).

Usage (repo root):
  .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/<scenario> <product> [--docs-dir PATH]
"""
import ast
import glob
import json
import os
import re
import sys

import yaml

# Controlled marker for a base clause an extended policy has superseded. The clause keeps its
# bearing doc, but the prose must carry this word so a retired rule can never read as in force.
SUPERSEDED_MARK = "no longer in force"


def _nows(s):
    """Whitespace-insensitive form for verbatim-clause matching, mirroring the instantiate gate:
    YAML folded scalars inject a space at every fold point, so both sides are normalised the same
    way before comparison and a fold can never turn a faithful quote into a mismatch."""
    return re.sub(r"\s+", "", str(s or ""))


META_TOOLS = {"KB_search", "grep", "unlock_agent_discoverable_tool", "unlock_user_discoverable_tool",
              "call_agent_discoverable_tool", "call_user_discoverable_tool"}
SNAKE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+")
HEX16 = re.compile(r"\b[0-9a-f]{16}\b")
DSL = ("SUM(", "COUNT(", "EXISTS(", "CPARAM(", "CFIELD(", "LATEST(", "ctx.", "make_id",
       "F('", "P('", "K('", "MX(", "MN(", "RND(")

# Hub must remain a policy/tool entry, never a map of the hidden policy fragments. These markers
# are intentionally strict: a hub that tells the agent where else to read recreates a stopping
# condition even without a numbered factor list.
NAV_CUES = (r"see also|for (?:full )?details,? see"
            r"|(?:see|refer to|consult)\b[^.;\n]{0,40}\b(?:another|other|separate|the relevant|the corresponding)"
            r"\s+(?:docs?|documents?|pages?|polic(?:y|ies)|sections?|clauses?)\b"
            r"|read (?:this )?(?:together with|alongside)|continue reading|further reading|read all of")

HUB_DIRECTORY_PATTERNS = (
    (re.compile(r"component factors|contributing factors|factor list|list of factors"
                r"|all (?:the )?factors|the following factors", re.I), "factor inventory"),
    (re.compile(r"(?:consists of|comprises|is (?:made up|composed) of|is (?:divided|broken down) into)"
                r"\s+(?:the following\s+)?(?:factors|components|parts|items|rules|steps|documents)"
                r"|\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
                r"(?:factors|components|parts|rules|documents)\b", re.I), "enumerated decomposition"),
    (re.compile(r"satellite doc|factor doc|fragment doc|other fragments|their own docs", re.I),
     "fragment map"),
    (re.compile(NAV_CUES, re.I), "reading navigation/completion cue"),
)
FRAGMENT_NAV_PATTERNS = (
    (re.compile(r"satellite doc|factor doc|fragment doc|other fragments", re.I),
     "fragment topology"),
    (re.compile(NAV_CUES, re.I), "reading navigation/completion cue"),
    (re.compile(r"(?:the\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"
                r"\s+factor|factor\s+(?:no\.?\s*)?\d+", re.I), "factor ordinal"),
)

# ROUTED CARRIAGE: a dependency is stated exactly as the source states it — one prerequisite
# sentence per edge, on the blocked side — and never as a route through several problems. These
# are the unmistakable surface forms of a rendered route or procedure; a match fails whatever the
# semantics. The subtler routes no pattern can catch remain the manual gate's job.
EXPLICIT_FORMS = (
    (re.compile(r"\bsteps?\s*\d+\s+(?:before|after|precedes?|follows?)\s+steps?\s*\d+", re.I),
     "step-before-step ordering"),
    (re.compile(r"\bbefore\s+(?:running|starting|beginning|carrying\s+out)\s+(?:this|the)\s+"
                r"(?:procedure|process|workflow)", re.I), "procedure entry condition"),
    (re.compile(r"\b(?:wrong|incorrect|mistaken)\s+(?:reading|interpretation)s?\b|\bmis-?readings?\b"
                r"|\bcommon\s+(?:mistake|error|misunderstanding|misconception)s?\b", re.I),
     "wrong-reading contrast / named mistake"),
)
# BASELINE + FACTORS, discrete: the computation document (role=baseline) renders the standard
# method and default values and must be SILENT about anything that modifies it — an agent that
# finds it alone must compute a definite wrong number with no signal. These are the unmistakable
# hints that something else applies; a match in a baseline doc fails whatever the semantics.
BASELINE_HINT_PATTERNS = (
    (re.compile(r"\bunless\s+otherwise\b", re.I), "unless-otherwise hint"),
    (re.compile(r"\b(?:adjustments?|variations?|exceptions?|special\s+(?:rules?|rates?|terms?|treatment))"
                r"\s+(?:may\s+|can\s+|will\s+)?appl(?:y|ies)\b", re.I), "adjustment hint"),
    (re.compile(r"\bmay\s+be\s+(?:adjusted|varied|modified|reduced|increased|halved|doubled|waived)\b", re.I),
     "may-be-adjusted hint"),
    (re.compile(r"\b(?:set\s+out|described|provided|stated|explained|detailed)\s+(?:elsewhere|separately"
                r"|in\s+(?:a|another|other|the\s+relevant)\s+(?:document|page|rule|section|polic(?:y|ies)))", re.I),
     "elsewhere pointer"),
    (re.compile(r"\b(?:certain|some|eligible|qualifying|selected)\s+[a-z][a-z-]*(?:\s+[a-z][a-z-]*)?"
                r"\s+(?:may\s+)?(?:receive|qualify|are\s+entitled|enjoy|get|benefit)\b", re.I),
     "qualifying-parties hint"),
    (re.compile(r"\b(?:the\s+)?(?:standard|default|baseline)\s+(?:calculation|method|rule|treatment|formula)"
                r"\s+(?:applies|is\s+used)\s+(?:unless|except|where\s+no|when\s+no)", re.I), "standard-unless hint"),
)
# A factor doc states only its tiers; pointing at the computation document welds the two.
FACTOR_XREF_PATTERNS = (
    (re.compile(r"\b(?:standard|default|general|usual|normal|ordinary|baseline)\s+(?:calculation|method|rule|treatment"
                r"|formula)\s+(?:described|set\s+out|stated|provided|explained|detailed)\b", re.I),
     "pointer to the computation document"),
    (re.compile(r"\b(?:instead\s+of|in\s+place\s+of|overrid(?:es|ing)|replac(?:es|ing)|supersed(?:es|ing))\s+the\s+"
                r"(?:standard|default|general|usual|normal|ordinary|baseline)\s+(?:calculation|method|rule|treatment"
                r"|formula)\b", re.I), "override wording"),
    (re.compile(r"\b(?:set\s+out|described|stated|provided|explained|detailed|defined)\s+elsewhere\b"
                r"|\bin\s+(?:a|the)\s+separate\s+(?:document|page|rule)\b", re.I), "elsewhere pointer"),
)
# Task-mirroring title forms: a question restating a request, or an internal procedure label.
TITLE_FORMS = (
    (re.compile(r"\?\s*$|^\s*how\s+(?:do|does|can|should|to|is|are)\b", re.I), "question form"),
    (re.compile(r"^\s*internal\s*[:\-–—]|\bhandling\s+procedure\b", re.I),
     "internal-procedure form"),
)


def load_yaml(p):
    with open(p) as f:
        return yaml.safe_load(f)


def tool_owners(py_path):
    """{tool_name: owner} for @tool functions in a tools file."""
    out = {}
    if not os.path.exists(py_path):
        return out
    tree = ast.parse(open(py_path).read())
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        for dec in fn.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "tool":
                kw = {k.arg: getattr(k.value, "value", None) for k in dec.keywords}
                out[fn.name] = kw.get("owner", "agent")
    return out


def tool_interfaces(py_path):
    """{tool_name: (arg_names, docstring_snake_tokens)} — an invocation doc must spell out
    every parameter, and may use exactly this tool's own snake tokens (params + enum values)."""
    out = {}
    if not os.path.exists(py_path):
        return out
    tree = ast.parse(open(py_path).read())
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        args = [a.arg for a in fn.args.args if a.arg != "ctx"]
        ds = ast.get_docstring(fn) or ""
        out[fn.name] = (args, set(args) | set(SNAKE.findall(ds)))
    return out


def num_present(content, v):
    """Does numeric value v appear in the prose? ints as digits; rates <1 accept percent form."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return True                       # non-numeric (bool/str) — not spot-checked
    if isinstance(v, bool):
        return True
    if f == int(f) and abs(f) >= 1:
        return str(int(f)) in content
    if 0 < abs(f) < 1:
        pct = f * 100
        forms = [str(f).rstrip("0").rstrip("."), f"{f:g}"]
        if pct == int(pct):
            forms += [str(int(pct))]
        else:
            forms += [f"{pct:g}"]
        return any(s and s in content for s in forms)
    return f"{f:g}" in content or str(v) in content


def main():
    args = sys.argv[1:]
    docs_dir = None
    if "--docs-dir" in args:
        i = args.index("--docs-dir")
        if i + 1 >= len(args):
            raise SystemExit("--docs-dir requires a path")
        docs_dir = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print("usage: check_docs.py env/<scenario> <product> [--docs-dir PATH]")
        sys.exit(2)
    root, product = args[0].rstrip("/"), args[1]
    bdir = os.path.join(root, "blueprint")

    # ---- resolve profile + sources -------------------------------------------------
    ext_hits = glob.glob(os.path.join(root, "tasks", "*", f"{product}.extended.yaml"))
    if len(ext_hits) > 1:
        raise SystemExit(f"multiple extended charters for product '{product}': {sorted(ext_hits)}")
    if ext_hits:
        profile, src = "extended", ext_hits[0]
        charter = load_yaml(src)
        tt_path = os.path.join(os.path.dirname(src), "task_tools.py")
        task_tools = tool_owners(tt_path)
        interfaces = tool_interfaces(tt_path)
    else:
        profile, src = "base", os.path.join(bdir, "products", f"{product}.yaml")
        if not os.path.exists(src):
            raise SystemExit(f"no charter yaml for product '{product}'")
        charter = load_yaml(src)
        task_tools = {}
        interfaces = {}
    share_tools = set(tool_owners(os.path.join(bdir, "share_tools.py")))
    whitelist = set(task_tools) | share_tools | META_TOOLS
    # official display names of every product: a cross-difficulty factor doc must name the product
    # whose records decide its tier, so a reader of those records can find the rule.
    display_names = {}
    for f in glob.glob(os.path.join(bdir, "products", "*.yaml")):
        d0 = load_yaml(f)
        if isinstance(d0, dict) and d0.get("category"):
            display_names[str(d0["category"])] = str(d0.get("display_name") or "").strip()

    eps = {p["id"]: p for p in (charter.get("extended_policies") or [])}
    base_pols = {p["id"]: p for p in (charter.get("policies") or []) if isinstance(p, dict) and p.get("id")}
    base_policies = set(base_pols)
    display_name = str(charter.get("display_name") or "").strip()
    # product self-identification tokens: the official display name, and (if all variants share
    # a family prefix, e.g. a series name) that family name — either names the product in prose.
    name_tokens = {display_name} if display_name else set()
    vnames = [v.get("name", "") for v in (charter.get("variants") or [])]
    if vnames:
        pref = vnames[0]
        for v in vnames[1:]:
            while pref and not v.startswith(pref):
                pref = pref[:-1]
        # strip tier-numbering tail from the common prefix
        pref = re.sub(r"[0-9\s\-\u2013\u2014]+$", "", pref)
        pref = re.sub(r"\s*(?:tier|level|plan|pack|package|edition|series)$", "", pref, flags=re.I)
        if len(pref) >= 3:
            name_tokens.add(pref)
    name_tokens = {t for t in name_tokens if t}
    param_schema_keys = set((charter.get("parameter_schema") or {}).keys())
    variants = {v["name"]: (v.get("parameters") or {}) for v in (charter.get("variants") or [])}

    # required quantitative keys (coverage targets)
    required = {f"variants.{k}" for k in param_schema_keys}
    p_ref = re.compile(r"P\('([^']+)'\)")
    for pid, p in eps.items():
        for k in (p.get("params") or {}):
            required.add(f"{pid}.params.{k}")
        for item in (p.get("compute") or []):
            (_, expr), = item.items()
            for m in p_ref.findall(str(expr)):
                required.add(f"variants.{m}")
    # base policies' own LITERAL constants are quantitative homes too — without them a
    # base-policy number copied into two docs slips through. "=<param>" reference values
    # are skipped: their number is already required under the variants.<param> key above.
    for pid, p in base_pols.items():
        for k, v in (p.get("params") or {}).items():
            if isinstance(v, str) and v.startswith("="):
                continue
            required.add(f"{pid}.params.{k}")

    # ---- load docs -------------------------------------------------------------------
    ddir = docs_dir.rstrip("/") if docs_dir else os.path.join(root, "docs", product)
    paths = sorted(glob.glob(os.path.join(ddir, "*.json")))
    if not paths:
        raise SystemExit(f"no docs under {ddir}")
    docs, fails = [], []
    if "workflows" in charter:
        fails.append("charter carries a `workflows` key — this pipeline has no workflow problems; every problem is an "
                     "extended policy and the order of a task's writes is derived, never rendered")
    seen_ids = set()
    for pth in paths:
        fn = os.path.basename(pth)
        try:
            d = json.load(open(pth))
        except Exception as e:  # noqa: BLE001
            fails.append(f"{fn}: unreadable json ({e})"); continue
        for fld in ("id", "title", "content", "meta"):
            if not d.get(fld):
                fails.append(f"{fn}: missing field '{fld}'")
        did = str(d.get("id", ""))
        stem = fn[:-5]
        if did != f"doc_{product}_{stem}":
            fails.append(f"{fn}: id '{did}' != 'doc_{product}_{stem}' (id must match filename)")
        if did in seen_ids:
            fails.append(f"{fn}: duplicate id {did}")
        seen_ids.add(did)
        docs.append((fn, d))

    # ---- leak + register --------------------------------------------------------------
    for fn, d in docs:
        text = str(d.get("title", "")) + "\n" + str(d.get("content", ""))
        # an invocation doc may additionally use ITS OWN tool's parameter/enum tokens
        own = (d.get("meta") or {}).get("tool")
        allowed = whitelist | (interfaces.get(own, (None, set()))[1] if own else set())
        bad = sorted({t for t in SNAKE.findall(text) if t not in allowed})
        if bad:
            fails.append(f"{fn}: implementation leak — snake_case tokens outside tool whitelist: {bad[:6]}")
        if HEX16.search(text):
            fails.append(f"{fn}: implementation leak — 16-hex row id in prose")
        hit = [s for s in DSL if s in text]
        if hit:
            fails.append(f"{fn}: implementation leak — compute-DSL fragment {hit}")
        body = str(d.get("content", ""))
        # product self-identification: the corpus is one merged retrieval pool across products;
        # a doc whose CONTENT never names its product is an ambiguity source (the id prefix does
        # not count — content is the policy body the agent reads).
        if name_tokens and not any(t in body for t in name_tokens):
            fails.append(f"{fn}: content never names its product ({'/'.join(sorted(name_tokens))}) — "
                         "in the merged corpus an unnamed late-fee/penalty/discount doc is ambiguous across "
                         "products; state the product's official name in the prose (value 3)")

    # ---- routed carriage: route/procedure scaffolding, task-mirroring titles --------------
    for fn, d in docs:
        title = str(d.get("title", ""))
        text = title + "\n" + str(d.get("content", ""))
        for rx, label in EXPLICIT_FORMS:
            hit = rx.search(text)
            if hit:
                fails.append(f"{fn}: routed form ({label}) via {hit.group(0)!r} — a dependency is carried by the "
                             "source's prerequisite sentence on the blocked side, never as a route or a procedure")
        for rx, label in TITLE_FORMS:
            if rx.search(title):
                fails.append(f"{fn}: title in {label} ({title[:80]!r}) — a title names the product and a "
                             "general subject, never a request or a procedure for a particular situation")
                break

    # ---- tools -----------------------------------------------------------------------
    inv = {}
    for fn, d in docs:
        t = (d.get("meta") or {}).get("tool")
        if t:
            inv.setdefault(t, []).append((fn, d))
    for pid, policy in sorted(eps.items()):
        target = policy.get("target_tool")
        if target and target not in task_tools:
            fails.append(f"policy {pid}: target_tool {target!r} is absent from this product's task_tools.py")
    for t, owner in sorted(task_tools.items()):
        entries = inv.get(t, [])
        if len(entries) != 1:
            fails.append(f"tool {t}: {len(entries)} invocation docs (need exactly 1)")
            continue
        fn, d = entries[0]
        meta = d.get("meta") or {}
        target_policies = sorted(pid for pid, p in eps.items() if p.get("target_tool") == t)
        if len(target_policies) == 1:
            expected_pid = target_policies[0]
            if meta.get("role") != "hub" or meta.get("policy_id") != expected_pid:
                fails.append(f"{fn}: tool {t} is target_tool of exactly one policy ({expected_pid}); "
                             "its invocation must be merged into that policy's hub")
        elif meta.get("role") != "tool":
            kind = "shared target_tool" if target_policies else "non-target tool"
            fails.append(f"{fn}: {kind} {t} must have a standalone role=tool invocation doc "
                         f"(target policies={target_policies})")
        c = str(d["content"])
        if t not in c:
            fails.append(f"{fn}: invocation doc never names its tool {t} verbatim")
        if "unlock" not in c.lower():
            fails.append(f"{fn}: invocation doc for hidden tool {t} lacks unlock wording")
        if owner == "user" and not re.search(r"customer (?:themselves|in person|personally)", c, re.I):
            fails.append(f"{fn}: user-owned tool {t} doc lacks 'the customer themselves' (hand-over) wording")
        # parameter completeness: the invocation doc spells out EVERY parameter by name
        args = interfaces.get(t, ([], set()))[0]
        missing_args = [a for a in args if a not in c]
        if missing_args:
            fails.append(f"{fn}: invocation doc for {t} misses parameter(s) {missing_args} — spell out "
                         "every parameter (name, meaning, format, enum candidates)")
    for t in inv:
        if t not in task_tools:
            fails.append(f"meta.tool '{t}' is not a task tool of this product")

    # ---- no workflow documents: order is derived by the solver, never rendered -----------
    for fn, d in docs:
        m = d.get("meta") or {}
        if m.get("role") == "sop" or m.get("workflow"):
            fails.append(f"{fn}: role=sop / meta.workflow — there are no workflow documents; every problem is an "
                         "extended policy and the order of writes is what the solver derives")
        if m.get("role") == "meta_rule":
            fails.append(f"{fn}: role=meta_rule is retired — the assembly of the result belongs to the computation "
                         "document (role=baseline) and every other fragment renders one declared factor")

    # ---- scatter (non-directory hub + independently discoverable policy fragments) -----
    by_policy = {}
    for fn, d in docs:
        m = d.get("meta") or {}
        pid = m.get("policy_id")
        if pid and m.get("role") in ("hub", "factor", "baseline"):
            by_policy.setdefault(pid, []).append((fn, d))
    for pid, p in eps.items():
        group = by_policy.get(pid, [])
        hubs = [(fn, d) for fn, d in group if d["meta"]["role"] == "hub"]
        fsats = [(fn, d) for fn, d in group if d["meta"]["role"] == "factor"]
        if len(hubs) != 1:
            fails.append(f"policy {pid}: {len(hubs)} hub docs (need exactly 1)")
            continue
        hfn, hd = hubs[0]
        if hd["meta"].get("carries"):
            fails.append(f"{hfn}: hub carries quantitative keys {hd['meta']['carries']} — hub must be "
                         "purely qualitative (numbers live in independent policy fragments)")
        if "factors" in hd["meta"]:
            fails.append(f"{hfn}: hub meta.factors is forbidden — factor completeness is private gate "
                         "state, never an agent-visible or hub-attached directory")
        if "covers" in hd["meta"]:
            fails.append(f"{hfn}: hub meta.covers is forbidden — compute coverage belongs only to "
                         "the computation doc and the factor docs")
        if hd["meta"].get("tool") and hd["meta"]["tool"] != p.get("target_tool"):
            fails.append(f"{hfn}: hub meta.tool != policy target_tool")

        hub_text = str(hd.get("title", "")) + "\n" + str(hd.get("content", ""))
        for rx, label in HUB_DIRECTORY_PATTERNS:
            hit = rx.search(hub_text)
            if hit:
                fails.append(f"{hfn}: hub exposes a {label} via {hit.group(0)!r} — keep only the policy/"
                             "tool entry; do not tell the agent what else exists or when reading is complete")

        # A factor's hidden name is private authoring state. Repeating it in the hub creates the exact
        # directory the scattering is designed to remove.
        sat_names = []
        for fn2, d2 in fsats:
            nm = d2["meta"].get("factor")
            if not isinstance(nm, str) or not nm.strip():
                fails.append(f"{fn2}: factor doc requires a non-empty hidden meta.factor name")
            else:
                sat_names.append(nm.strip())
        dup = {n for n in sat_names if sat_names.count(n) > 1}
        if dup:
            fails.append(f"policy {pid}: duplicate hidden meta.factor names: {sorted(dup)}")
        for name in sorted(set(sat_names), key=len, reverse=True):
            if name in hub_text:
                fails.append(f"{hfn}: hub repeats hidden factor name {name!r} — this directly reconnects "
                             "the policy entry to a discoverable fragment")

        # No arbitrary factor-count floor. Binding coverage and quantitative coverage checks
        # prove source coverage; forcing extra fragments would reward duplicated or invented prose.

        fragments = [(fn, d) for fn, d in group if d["meta"]["role"] in ("factor", "baseline")]
        binding_names = []
        for item in (p.get("compute") or []):
            if not isinstance(item, dict) or len(item) != 1:
                continue
            binding_names.append(str(next(iter(item))))
        if len(binding_names) != len(set(binding_names)):
            fails.append(f"policy {pid}: source compute has duplicate binding names")
        cover_homes = {}
        for fn2, d2 in fragments:
            role2 = d2["meta"].get("role")
            covers = d2["meta"].get("covers")
            if not isinstance(covers, list) or not all(isinstance(x, str) and x.strip() for x in covers):
                fails.append(f"{fn2}: {role2} doc requires meta.covers as a list of source compute bindings")
                continue
            if len(covers) != len(set(covers)):
                fails.append(f"{fn2}: duplicate binding names in meta.covers")
            body2 = str(d2.get("title", "")) + "\n" + str(d2.get("content", ""))
            for rx, label in FRAGMENT_NAV_PATTERNS:
                hit = rx.search(body2)
                if hit:
                    fails.append(f"{fn2}: independent {role2} doc exposes {label} via {hit.group(0)!r} — "
                                 "state only this document's business rule, with no reading map")
            for name in covers:
                cover_homes.setdefault(name, []).append(fn2)
                # only a code-shaped binding name (snake_case or numbered) can leak; a plain-word binding
                # such as `balance` or `discount` is ordinary business vocabulary and is never a leak
                code_shaped = "_" in name or any(ch.isdigit() for ch in name)
                if code_shaped and re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", body2):
                    fails.append(f"{fn2}: hidden compute binding {name!r} leaks into title/content")
        for name in binding_names:
            homes = cover_homes.get(name, [])
            if not homes:
                fails.append(f"policy {pid}: compute binding '{name}' is covered by no fragment doc "
                             "(every binding needs a home; completeness stays in private meta)")
        for name, homes in cover_homes.items():
            if name not in binding_names:
                fails.append(f"policy {pid}: meta.covers claims unknown compute binding '{name}' in {homes}")

        # ---- declared factors: one fragment per factor, carrying all of its bindings ----------
        declared = [f for f in (p.get("factors") or []) if isinstance(f, dict) and f.get("id")]
        if not declared:
            fails.append(f"policy {pid}: the charter declares no factors for this policy — an extended policy renders as "
                         "hub + computation doc + one doc per declared factor; re-instantiate the charter first")
        if declared:
            declared_ids = {str(f["id"]) for f in declared}
            # ---- the computation document: exactly one, silent, covering every non-factor binding ----
            bases = [(fn2, d2) for fn2, d2 in group if d2["meta"]["role"] == "baseline"]
            if len(bases) != 1:
                fails.append(f"policy {pid}: {len(bases)} computation docs (role=baseline; need exactly 1 rendering "
                             "baseline.rule — the standard method and default values every factor falls back to)")
            factor_bindings = set()
            for f in declared:
                factor_bindings |= {str(b) for b in (f.get("bindings") or [])}
            if bases:
                bfn, bd = bases[0]
                cov_b = {str(x) for x in (bd["meta"].get("covers") or [])}
                expected_b = set(binding_names) - factor_bindings
                if not expected_b <= cov_b:
                    fails.append(f"{bfn}: computation doc covers {sorted(cov_b)} but must cover every binding that "
                                 f"belongs to no factor {sorted(expected_b)} (result included)")
                btext = str(bd.get("title", "")) + "\n" + str(bd.get("content", ""))
                for rx, label in BASELINE_HINT_PATTERNS:
                    hit = rx.search(btext)
                    if hit:
                        fails.append(f"{bfn}: computation doc carries a {label} via {hit.group(0)!r} — the baseline is "
                                     "silent about anything that modifies it; an agent that finds it alone must "
                                     "compute a definite wrong number with no signal")
                bcar = set(bd["meta"].get("carries") or [])
                for k in ((p.get("baseline") or {}).get("params") or []):
                    if k not in (p.get("params") or {}):
                        continue      # a tier parameter: its figure lives in the facet table; this doc only names it
                    key = f"{pid}.params.{k}"
                    if key not in bcar:
                        fails.append(f"{bfn}: computation doc does not carry default key '{key}' named in "
                                     "baseline.params — a policy's own defaults are homed in the computation document")
            for fn2, d2 in fsats:
                ftext = str(d2.get("title", "")) + "\n" + str(d2.get("content", ""))
                for rx, label in FACTOR_XREF_PATTERNS:
                    hit = rx.search(ftext)
                    if hit:
                        fails.append(f"{fn2}: factor doc carries a {label} via {hit.group(0)!r} — a factor states its "
                                     "tiers and never names, overrides or points at the computation document")
            for f in declared:
                fid = str(f["id"])
                homes_f = [(fn2, d2) for fn2, d2 in fsats if str(d2["meta"].get("factor") or "") == fid]
                if len(homes_f) != 1:
                    fails.append(f"policy {pid}: declared factor '{fid}' has {len(homes_f)} factor docs (need exactly 1 "
                                 "whose meta.factor is the source factor id — a factor is rendered as one fragment "
                                 "carrying its whole ladder)")
                    continue
                fn2, d2 = homes_f[0]
                cov = {str(x) for x in (d2["meta"].get("covers") or [])}
                fb = {str(b) for b in (f.get("bindings") or [])}
                if fb - cov:
                    fails.append(f"{fn2}: factor doc for '{fid}' does not cover its own bindings {sorted(fb - cov)} "
                                 "— meta.covers must include every binding of the declared factor")
                xd = f.get("cross_difficulty")
                if xd:
                    other = display_names.get(str(xd))
                    if other and other not in str(d2.get("content", "")):
                        fails.append(f"{fn2}: cross-difficulty factor '{fid}' decides its tier from '{xd}' records but "
                                     f"never names that product ({other!r}) — a reader of those records must be able "
                                     "to find the rule (value 2)")
            for fn2, d2 in fsats:
                nm = str(d2["meta"].get("factor") or "")
                if nm and nm not in declared_ids:
                    fails.append(f"{fn2}: meta.factor '{nm}' is not a declared factor of {pid} — under a charter that "
                                 "declares factors, every factor doc renders exactly one of them (the assembly of the "
                                 "result and the defaults belong to the computation document, role=baseline)")

    # ---- full span: every BASE policy carried by >=1 doc (splitting must never drop) ----
    base_covered = {str(pid) for pid in ((d.get("meta") or {}).get("policy_id")
                    for _, d in docs if (d.get("meta") or {}).get("role") == "policy") if pid}
    for pid in sorted(base_policies):
        if pid not in base_covered:
            fails.append(f"full span: base policy '{pid}' has no doc (meta.role=policy, meta.policy_id={pid}) "
                         "— scattering means splitting, never dropping")
    for pid in sorted(base_covered - base_policies):
        fails.append(f"meta.policy_id '{pid}' (role=policy) is not a base policy of this product")

    # ---- supersession: base clauses an extended policy declares it overrides ------------
    # base and extended are successive versions of the same product law; where they conflict
    # extended wins, and every conflict is declared clause by clause in extended.overwrite.
    # A superseded clause KEEPS its bearing doc — an override never breaks the bijection — but
    # that doc must present it as retired, so no careful reader can ever apply withdrawn law.
    # Only the handling clause is retired: the base params VALUES stay valid and stay homed here.
    superseded = {}            # base policy id -> {normalized clause: verbatim clause}
    for ep in eps.values():
        for entry in (ep.get("overwrite") or []):
            if not isinstance(entry, dict):
                continue
            bpid, clause = entry.get("base_policy"), str(entry.get("superseded_clause") or "").strip()
            if bpid and clause:
                superseded.setdefault(str(bpid), {})[_nows(clause)] = clause
    declared_homes = {}        # (base policy id, normalized clause) -> [filenames]
    for fn, d in docs:
        m = d.get("meta") or {}
        if m.get("role") != "policy":
            continue
        pid, raw = str(m.get("policy_id") or ""), m.get("superseded_clauses") or []
        if raw and not isinstance(raw, list):
            fails.append(f"{fn}: meta.superseded_clauses must be a list of the base clauses this doc "
                         "presents as retired")
            continue
        for clause in raw:
            cn = _nows(clause)
            # a registered clause matches a retired clause when either contains the other (both are
            # verbatim substrings of the same base rule; a folded scalar may split them differently)
            matched = [norm for norm in superseded.get(pid, {}) if cn and (cn == norm or cn in norm or norm in cn)]
            if not matched:
                fails.append(f"{fn}: meta.superseded_clauses names a clause of '{pid}' that no extended "
                             "policy retires in its overwrite — KB may not withdraw law the source keeps")
                continue
            for norm in matched:
                declared_homes.setdefault((pid, norm), []).append(fn)
        if raw and SUPERSEDED_MARK not in str(d.get("content") or ""):
            fails.append(f"{fn}: declares superseded clauses but its content never says "
                         f"{SUPERSEDED_MARK!r} — a retired clause must read as retired, never as in force")
    for pid, clauses in sorted(superseded.items()):
        for norm, verbatim in sorted(clauses.items()):
            homes = declared_homes.get((pid, norm), [])
            if not homes:
                fails.append(f"supersession: a clause of base policy '{pid}' is retired by an extended "
                             f"policy, but no role=policy doc declares it in meta.superseded_clauses "
                             f"(clause opens {verbatim[:24]!r}) — the KB would still teach withdrawn law")

    # ---- prerequisite: the prerequisite sentence carried verbatim, once, on the blocked side;
    #      no tool-name pointers into the blocked side -----------------------------------------
    prereq_edges = []            # (owner policy id, entry)
    for _pid, _p in sorted(eps.items()):
        for _e in (_p.get("prerequisite") or []):
            if isinstance(_e, dict):
                prereq_edges.append((_pid, _e))

    def _docs_of_policy(pid):
        return [(fn, d) for fn, d in docs if (d.get("meta") or {}).get("policy_id") == pid]

    for owner, e in prereq_edges:
        own_docs = {fn for fn, _ in _docs_of_policy(owner)}
        dep = str(e.get("problem") or "").strip()
        src = str(e.get("policy_source") or "").strip()
        if src:
            norm = _nows(src)
            label = f"the prerequisite sentence of '{owner}' (opens {src[:24]!r})"
            homes = sorted(fn for fn, d in docs if norm in _nows(d.get("content")))
            own_homes = [fn for fn in homes if fn in own_docs]
            foreign = [fn for fn in homes if fn not in own_docs]
            if not own_homes:
                fails.append(f"prerequisite of '{owner}' on '{dep}': {label} is carried verbatim by no doc of that "
                             "policy — the blocked policy's hub or one of its fragments must carry it word for word, "
                             "ordering connective and form intact")
            for fn in foreign:
                fails.append(f"{fn}: carries {label} verbatim although it is not a doc of that policy — a second home "
                             "outside the blocked side welds two problems together (the depended-on policy's docs "
                             "state only its own rule and never say who waits on it)")
        # resolved_by must not leak into the blocked problem's docs as a tool-name pointer
        rb = str(e.get("resolved_by") or "").strip()
        if rb:
            for fn in sorted(own_docs):
                doc = next(d for f, d in docs if f == fn)
                if rb in str(doc.get("content") or "") + str(doc.get("title") or ""):
                    fails.append(f"{fn}: names the prerequisite's resolved_by tool {rb!r} inside the "
                                 "docs of the problem it blocks — the tool belongs to the other problem's own doc; "
                                 "the blocked side states its prerequisite sentence and nothing that routes it")
    # ---- coverage: every quantitative key rendered at least once; a policy's own constants in its own docs
    claims = {}
    for fn, d in docs:
        m = d.get("meta") or {}
        for k in (m.get("carries") or []):
            claims.setdefault(k, []).append((fn, d))
    for k in sorted(required):
        homes = claims.get(k, [])
        if not homes:
            fails.append(f"coverage: quantitative key '{k}' rendered by no doc")
            continue
        if ".params." in k:
            own_pid = k.partition(".params.")[0]
            if own_pid in eps:
                own_fns = {fn for fn, _ in _docs_of_policy(own_pid)}
                if not any(fn in own_fns for fn, _ in homes):
                    fails.append(f"coverage: '{k}' is this policy's own constant but none of that policy's docs "
                                 f"carries it ({[fn for fn, _ in homes]}) — a policy's own numbers are rendered in "
                                 "that policy's documents")
        for fn, d in homes:
            c = str(d["content"])
            if k.startswith("variants."):
                pk = k.split(".", 1)[1]
                vals = [params.get(pk) for params in variants.values() if pk in params]
                missing = [v for v in vals if not num_present(c, v)]
                if missing:
                    fails.append(f"{fn}: claims '{k}' but per-tier value(s) {missing[:4]} absent from content "
                                 "(the facet table must cover every tier)")
            else:
                pid, _, key = k.partition(".params.")
                src_pol = eps.get(pid) or base_pols.get(pid) or {}
                v = (src_pol.get("params") or {}).get(key)
                if not num_present(c, v):
                    fails.append(f"{fn}: claims '{k}' (={v}) but the value is absent from content")
    for k in claims:
        if k not in required:
            fails.append(f"coverage: claimed key '{k}' is not a required quantitative key (typo?)")

    # ---- report ------------------------------------------------------------------------
    n_role = {}
    for _, d in docs:
        r = (d.get("meta") or {}).get("role", "?")
        n_role[r] = n_role.get(r, 0) + 1
    lengths = [len(str(d.get("content", ""))) for _, d in docs]
    length_note = (f" content[min/mean/max]={min(lengths)}/{sum(lengths)/len(lengths):.0f}/{max(lengths)}"
                   if lengths else "")
    print(f"🔎 DOCS gate  product={product} profile={profile} docs={len(docs)} roles={n_role}{length_note}")
    print(f"   required quantitative keys={len(required)}  task_tools={len(task_tools)}  prerequisite edges={len(prereq_edges)}")
    if fails:
        print("\n  [FAIL]")
        for f in fails[:60]:
            print("   -", f)
        print("DOCS NOT OK")
        sys.exit(1)
    print("\n  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, "
          "non-directory hubs, private compute-binding coverage, quantitative coverage, every "
          "prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding")
    print("  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable "
          "at the source's strength from the prerequisite sentence, the depended-on docs and the records, "
          "no state-form sentence restated as an action, and no route stated beyond the sentences")
    print("DOCS OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
