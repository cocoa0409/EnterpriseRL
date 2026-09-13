"""DOCS gate: verify a rendered KB corpus (env/<scenario>/docs/<product>/) against the
render values — agent-facing wording with zero implementation leaks, independent policy
fragments, single-home quantitative coverage, tool/SOP fidelity. Normative semantic bijection
is a manual hard gate: this script cannot prove that prose invented no confirmation/review step.

WHAT IT CHECKS (the mechanically decidable subset of SKILL.md's values):
  structure   id/title/content/meta present; id == doc_<product>_<topic>_<uuid8> and matches
              the filename; unique ids. Length is reported, never used as a pass condition:
              source fidelity outranks manual-like fullness.
  leak        content+title contain NO snake_case code token outside the whitelist
              (task tool names ∪ share tool names ∪ unlock/call meta-tool names), no compute-DSL
              fragments, no 16-hex row ids. This single rule catches table/field/event/param/
              policy-id leakage wholesale (they are all snake_case).
  tools       every task tool has EXACTLY ONE invocation doc (meta.tool), whose role follows the
              product-wide reference split: a target_tool referenced by one policy is merged into
              that hub; shared or non-target tools have a standalone tool doc. Content names the
              tool verbatim plus unlock wording; user-owned tools' docs must say the customer themselves.
  workflow    every workflow has EXACTLY ONE doc (meta.workflow). It is never a runbook: it must
              not name any of its step tools (tool names live only in their invocation docs)
              and must not number its steps — the order is carried by the reasons, not stated.
  scatter     every extended policy has EXACTLY ONE hub (meta.role=hub, carries empty), but the hub
              MUST NOT expose a factor list, factor count, fragment navigation, or completion cue.
              Independent factor/meta_rule docs privately claim source compute bindings through
              meta.covers; every binding (including result) has exactly one home. There is no
              arbitrary fragment-count floor: only real source semantics may create fragments.
              Carries caps (factor<=2, facet<=6) block fake scattering.
  prereq      a prerequisite is carried by ENTAILMENT (a principle in the blocked problem's docs,
              completed by the depended-on problem's own rules and the facts), never stated. So
              no doc may contain an edge's `condition` or `policy_source` verbatim, nor restate
              one closely in a sentence that also carries a gating/ordering cue; and the
              `resolved_by` tool of an edge must not appear in the blocked problem's docs (a
              cross-problem operational pointer welds two problems into one procedure). Whether
              each hop is really entailed at the source's strength is a MANUAL gate.
  explicit    the controlled scaffolding of a stated dependency or procedure fails anywhere:
              entry conditions, not-yet-hold clauses, precedence labels ending in "first",
              step-before-step, wrong/correct-reading contrasts, named mistakes. Titles may not
              take the question form or the internal-procedure form (task-mirroring titles).
  wording     paraphrase, never copy: no run of SHINGLE words copied from the charter text, and
              no run of SHINGLE words recurring in TEMPLATE_DOCS+ docs (templated phrasing).
              Quoted/backticked spans (exact identifiers, fixed phrases) are excluded.
  full span   EVERYTHING in the charter is carried somewhere (splitting must never drop): every BASE
              policy has >=1 doc (meta.policy_id); every extended policy has its hub+fragments;
              every task tool its invocation doc; every workflow its SOP doc; every
              parameter_schema key a home. Scattering means splitting, never dropping.
  superseded  base and extended are successive versions of one product law and extended wins on
              conflict, each conflict declared clause by clause in extended_policies[].overwrite.
              A superseded clause KEEPS its bearing doc (an override never breaks the bijection)
              but that doc must declare it in meta.superseded_clauses and its prose must carry the
              controlled retirement marker, so withdrawn law can never read as in force. Declaring
              a clause the source does not retire fails too: the KB may not withdraw law on its
              own. Exactly one home per retired clause. Only the handling clause retires — base
              params VALUES stay valid and stay homed in that same doc, so `coverage` is unchanged.
  coverage    required quantitative keys — every extended policy params key, every variant
              param its compute reads via P('...'), every parameter_schema key, and every
              BASE policy params key whose value is a literal ("=<param>" references excluded:
              their number is already homed under variants.<param>) — each claimed by EXACTLY
              ONE doc's meta.carries (single home); claimed numeric values spot-checked to
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
# formal register: policy prose states arithmetic in WORDS (multiplied by / less / total /
# the higher of), never as equation symbols. Unambiguous equation markers only — markdown bold
# (*), unit slashes (USD/month), list dashes and date hyphens are NOT arithmetic and stay legal.
ARITH = ("＝", "×", "÷", "＋", "−", "=", "+")
FACTOR_CARRY_CAP = 2
FACET_CARRY_CAP = 6
# ANTI-PADDING: length must come from each doc's OWN substance. A line (>=25 chars) that
# recurs verbatim in >=4 docs is stamped boilerplate (injected glossaries, per-role template
# sections) — it fakes length and floods BM25 with identical text. Per-doc ratio of such
# lines must stay under the cap, and the corpus mean under a tighter cap.
BOILER_MIN_LINE = 25
BOILER_DOCS = 4
BOILER_DOC_RATIO = 0.25
BOILER_MEAN_RATIO = 0.12

# Hub must remain a policy/tool entry, never a map of the hidden policy fragments. These markers
# are intentionally strict: a hub that tells the agent where else to read recreates a stopping
# condition even without a numbered factor list.
NAV_CUES = (r"see also|for (?:full )?details,? see"
            r"|(?:see|refer to|consult)\b[^.;\n]{0,40}\b(?:docs?|documents?|polic(?:y|ies)|sections?"
            r"|clauses?|annex|appendix|schedule|table|SOP)\b"
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
    (re.compile(r"\bhub\b|satellite doc|factor doc|fragment doc|other fragments", re.I),
     "fragment topology"),
    (re.compile(NAV_CUES, re.I), "reading navigation/completion cue"),
    (re.compile(r"(?:the\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"
                r"\s+factor|factor\s+(?:no\.?\s*)?\d+", re.I), "factor ordinal"),
)

# IMPLICIT CARRIAGE: what the solver must work out — a dependency between problems, the order of
# a procedure, a remedy — is carried by entailment and never stated. These are the unmistakable
# surface forms of a stated dependency or procedure; a match fails whatever the semantics. The
# subtler statements no pattern can catch remain the manual gate's job.
EXPLICIT_FORMS = (
    (re.compile(r"\bentry\s+conditions?\b", re.I), "entry condition"),
    (re.compile(r"\bwhere\s+(?:that|this|it|they)\s+(?:does|do)\s+not\s+(?:yet\s+)?hold", re.I),
     "not-yet-hold gating clause"),
    (re.compile(r"\*\*[^*\n]{0,60}\bfirst\b[.:!]?\s*\*\*", re.I), "precedence label ending in 'first'"),
    (re.compile(r"\bsteps?\s*\d+\s+(?:before|after|precedes?|follows?)\s+steps?\s*\d+", re.I),
     "step-before-step ordering"),
    (re.compile(r"\bbefore\s+(?:running|starting|beginning|carrying\s+out)\s+(?:this|the)\s+"
                r"(?:procedure|process|workflow)", re.I), "procedure entry condition"),
    (re.compile(r"\b(?:wrong|incorrect|mistaken)\s+(?:reading|interpretation)s?\b"
                r"|\bcorrect\s+(?:basis|reading|interpretation)\b|\bmis-?readings?\b"
                r"|\bcommon\s+(?:mistake|error|misunderstanding|misconception)s?\b", re.I),
     "wrong-reading contrast / named mistake"),
)
# A restatement of a prerequisite that also carries one of these cues reads as an instruction.
ORDER_CUE = re.compile(r"\b(?:before|first|prior\s+to|only\s+after|only\s+once|until|not\s+yet"
                       r"|in\s+advance|ahead\s+of|precede[sd]?|preceding)\b", re.I)
NEAR_RESTATE = 0.8        # share of a prerequisite's content words found in one sentence
# Task-mirroring title forms: a question restating a request, or an internal procedure label.
TITLE_FORMS = (
    (re.compile(r"\?\s*$|^\s*how\s+(?:do|does|can|should|to|is|are)\b", re.I), "question form"),
    (re.compile(r"^\s*internal\s*[:\-–—]|\bhandling\s+procedure\b", re.I),
     "internal-procedure form"),
)
STEP_NUMBERING = re.compile(r"\bsteps?\s*(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"
                            r"|\b(?:first|second|third|fourth|fifth|final|last)\s+step\b", re.I)
# PARAPHRASE: a run of SHINGLE words copied from the charter, or recurring in TEMPLATE_DOCS docs,
# is copied/templated wording. Quoted/backticked spans are exact identifiers and fixed phrases
# (tool names, enum values, verbatim argument phrases) and are excluded.
SHINGLE = 10
TEMPLATE_DOCS = 3
WORD = re.compile(r"[a-z0-9]+")
QUOTED = re.compile(r"`[^`]*`|\"[^\"\n]*\"|“[^”\n]*”")
STOP = set("a an the of to and or is are be by for in on at as that this with from its it their any "
           "every each which who has have been was were not no than then when where once so into "
           "under over per such these those shall will would may must can could should".split())


def _words(text):
    return WORD.findall(QUOTED.sub(" ", str(text or "")).lower())


def _shingles(words, n=SHINGLE):
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def _content_words(text):
    return {w for w in WORD.findall(str(text or "").lower()) if len(w) > 2 and w not in STOP}


def _sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", str(text or "")) if s.strip()]


def _charter_texts(node, out):
    """Every natural-language string of the charter long enough to hold a copied run."""
    if isinstance(node, str):
        if len(WORD.findall(node.lower())) >= SHINGLE:
            out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            _charter_texts(v, out)
    elif isinstance(node, list):
        for v in node:
            _charter_texts(v, out)
    return out


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

    eps = {p["id"]: p for p in (charter.get("extended_policies") or [])}
    base_pols = {p["id"]: p for p in (charter.get("policies") or []) if isinstance(p, dict) and p.get("id")}
    base_policies = set(base_pols)
    wfs = {w["id"]: w for w in (charter.get("workflows") or [])}
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

    # required quantitative keys (single-home coverage targets)
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
    # are skipped: their number's single home is already the variants.<param> key above.
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

    # ---- anti-padding: cross-doc verbatim lines are boilerplate, not substance ----------
    line_homes = {}
    doc_lines = {}
    for fn, d in docs:
        lines = set()
        for ln in str(d.get("content", "")).splitlines():
            s = ln.strip().lstrip("-#*0123456789. ").strip()
            if len(s) < BOILER_MIN_LINE:
                continue
            if set(s) <= set("|-:— "):           # markdown table separators are structure
                continue
            lines.add(s)
        doc_lines[fn] = lines
        for s in lines:
            line_homes.setdefault(s, set()).add(fn)
    boiler_lines = {s for s, homes in line_homes.items() if len(homes) >= BOILER_DOCS}
    ratios = []
    for fn, d in docs:
        total = max(1, len(str(d.get("content", ""))))
        b = sum(len(s) for s in doc_lines[fn] if s in boiler_lines)
        r = b / total
        ratios.append(r)
        if r > BOILER_DOC_RATIO:
            fails.append(f"{fn}: {r:.0%} of content is cross-doc boilerplate (verbatim lines shared by "
                         f">={BOILER_DOCS} docs; cap {BOILER_DOC_RATIO:.0%}) — remove repetition; retain "
                         "a shared definition only when the structured source gives it an independent home")
    if ratios:
        mean_r = sum(ratios) / len(ratios)
        if mean_r > BOILER_MEAN_RATIO:
            fails.append(f"corpus boilerplate ratio {mean_r:.0%} > {BOILER_MEAN_RATIO:.0%} — injected "
                         "glossaries/template sections are padding, not source-backed policy substance")

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
        # formal register: arithmetic in words, never equation symbols
        body = str(d.get("content", ""))
        sym = sorted({s for s in ARITH if s in body})
        if sym:
            fails.append(f"{fn}: arithmetic symbols {sym} in prose — state calculations in words "
                         "(multiplied by / less / total / the higher of), never as equations")
        # product self-identification: the corpus is one merged retrieval pool across products;
        # a doc whose CONTENT never names its product is an ambiguity source (the id prefix does
        # not count — content is the policy body the agent reads).
        if name_tokens and not any(t in body for t in name_tokens):
            fails.append(f"{fn}: content never names its product ({'/'.join(sorted(name_tokens))}) — "
                         "in the merged corpus an unnamed late-fee/penalty/discount doc is ambiguous across "
                         "products; state the product's official name in the prose (value 3)")

    # ---- implicit carriage: stated-dependency scaffolding, task-mirroring titles --------
    for fn, d in docs:
        title = str(d.get("title", ""))
        text = title + "\n" + str(d.get("content", ""))
        for rx, label in EXPLICIT_FORMS:
            hit = rx.search(text)
            if hit:
                fails.append(f"{fn}: pre-solved form ({label}) via {hit.group(0)!r} — what the solver must "
                             "work out is carried by definitions and principles, never stated as an instruction")
        for rx, label in TITLE_FORMS:
            if rx.search(title):
                fails.append(f"{fn}: title in {label} ({title[:80]!r}) — a title names the product and a "
                             "general subject, never a request or a procedure for a particular situation")
                break

    # ---- paraphrase: nothing copied from the charter, no templated wording ------------
    charter_sh = set()
    for s in _charter_texts(charter, []):
        charter_sh |= _shingles(_words(s))
    doc_sh = {fn: _shingles(_words(str(d.get("title", "")) + "\n" + str(d.get("content", ""))))
              for fn, d in docs}
    sh_homes = {}
    for fn, sh in doc_sh.items():
        for s in sh:
            sh_homes.setdefault(s, set()).add(fn)
    templated = {s for s, homes in sh_homes.items() if len(homes) >= TEMPLATE_DOCS}
    for fn, _d in docs:
        copied = doc_sh[fn] & charter_sh
        if copied:
            fails.append(f"{fn}: {len(copied)} run(s) of {SHINGLE} words copied from the charter, e.g. "
                         f"{sorted(copied)[0]!r} — paraphrase in the document's own words (exact identifiers "
                         "and fixed phrases go in backticks)")
        shared = doc_sh[fn] & templated
        if shared:
            fails.append(f"{fn}: templated wording — {len(shared)} run(s) of {SHINGLE} words recur in "
                         f">={TEMPLATE_DOCS} docs, e.g. {sorted(shared)[0]!r} — word each document afresh")

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

    # ---- workflow: one implicit document per workflow, never a runbook ------------------
    sops = {}
    for fn, d in docs:
        w = (d.get("meta") or {}).get("workflow")
        if w:
            sops.setdefault(w, []).append((fn, d))
    for wid, wf in wfs.items():
        entries = sops.get(wid, [])
        if len(entries) != 1:
            fails.append(f"workflow {wid}: {len(entries)} workflow docs (need exactly 1)")
            continue
        fn, d = entries[0]
        text = str(d.get("title", "")) + "\n" + str(d.get("content", ""))
        # The course of a workflow is what the solver works out: the document carries purpose,
        # parties and what each part relies on. Naming the step tools, or numbering steps, turns
        # it back into a recipe (tool names stay in their own invocation documents).
        named = sorted({str(s.get("tool")) for s in (wf.get("steps") or [])
                        if s.get("tool") and str(s.get("tool")) in text})
        if named:
            fails.append(f"{fn}: workflow doc names its step tool(s) {named} — tool names belong only to "
                         "their invocation docs; the workflow doc carries purpose and reliance, not a recipe")
        hit = STEP_NUMBERING.search(text)
        if hit:
            fails.append(f"{fn}: workflow doc numbers its steps via {hit.group(0)!r} — the order must follow "
                         "from the stated reasons, never be listed")
    for w in sops:
        if w not in wfs:
            fails.append(f"meta.workflow '{w}' is not a workflow of this product")

    # ---- scatter (non-directory hub + independently discoverable policy fragments) -----
    by_policy = {}
    for fn, d in docs:
        m = d.get("meta") or {}
        pid = m.get("policy_id")
        if pid and m.get("role") in ("hub", "factor", "meta_rule"):
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
                         "independent factor/meta_rule docs")
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

        # No arbitrary factor-count floor. Binding coverage and quantitative single-home checks
        # prove source coverage; forcing extra fragments would reward duplicated or invented prose.

        fragments = [(fn, d) for fn, d in group if d["meta"]["role"] in ("factor", "meta_rule")]
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
            if role2 == "meta_rule" and not covers:
                fails.append(f"{fn2}: meta_rule doc requires at least one source compute binding in meta.covers")
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
                if name in body2:
                    fails.append(f"{fn2}: hidden compute binding {name!r} leaks into title/content")
        for name in binding_names:
            homes = cover_homes.get(name, [])
            if len(homes) != 1:
                fails.append(f"policy {pid}: compute binding '{name}' is covered by {len(homes)} "
                             f"fragment docs {homes} (need exactly 1; completeness stays in private meta)")
        for name, homes in cover_homes.items():
            if name not in binding_names:
                fails.append(f"policy {pid}: meta.covers claims unknown compute binding '{name}' in {homes}")

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
            declared_homes.setdefault((pid, _nows(clause)), []).append(fn)
            if _nows(clause) not in superseded.get(pid, {}):
                fails.append(f"{fn}: meta.superseded_clauses names a clause of '{pid}' that no extended "
                             "policy retires in its overwrite — KB may not withdraw law the source keeps")
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
            elif len(homes) > 1:
                fails.append(f"supersession: the retired clause of '{pid}' is declared by {homes} "
                             "— exactly one home, same as every other bearing relation")

    # ---- prerequisite: carried by entailment, never stated, no cross-problem pointers ---
    prereq_edges = []            # (owner_id, owner_is_workflow, entry)
    for _pid, _p in sorted(eps.items()):
        for _e in (_p.get("prerequisite") or []):
            if isinstance(_e, dict):
                prereq_edges.append((_pid, False, _e))
    for _wid, _wf in sorted(wfs.items()):
        if isinstance(_wf, dict):
            for _e in (_wf.get("prerequisite") or []):
                if isinstance(_e, dict):
                    prereq_edges.append((_wid, True, _e))

    def _docs_of_problem(problem_id, is_workflow):
        key = "workflow" if is_workflow else "policy_id"
        return [(fn, d) for fn, d in docs if (d.get("meta") or {}).get(key) == problem_id]

    sentences = {fn: _sentences(d.get("content")) for fn, d in docs}
    for owner, owner_is_wf, e in prereq_edges:
        own_docs = {fn for fn, _ in _docs_of_problem(owner, owner_is_wf)}
        # The hop is entailed by a principle plus the depended-on rules and the facts; the source's
        # own sentences for it (condition, policy_source) are never written into the prose —
        # neither verbatim nor as a close restatement carrying a gating/ordering cue.
        for field in ("condition", "policy_source"):
            src = str(e.get(field) or "").strip()
            if not src:
                continue
            where = f"prerequisite of '{owner}' ({field} opens {src[:24]!r})"
            norm = _nows(src)
            verbatim = {fn for fn, d in docs if norm in _nows(d.get("content"))}
            for fn in sorted(verbatim):
                fails.append(f"{fn}: states the {where} verbatim — a prerequisite is carried by entailment "
                             "from definitions and principles, never written out")
            cw = _content_words(src)
            if len(cw) < 6:
                continue
            for fn, _d in docs:
                if fn in verbatim:
                    continue
                for sent in sentences[fn]:
                    if len(cw & _content_words(sent)) / len(cw) >= NEAR_RESTATE and ORDER_CUE.search(sent):
                        fails.append(f"{fn}: restates the {where} as an instruction ({sent.strip()[:90]!r}) — "
                                     "state the governing principle in the document's own terms, never the "
                                     "condition or an order")
                        break
        # resolved_by must not leak into the blocked problem's docs as an operational pointer
        rb = str(e.get("resolved_by") or "").strip()
        if rb:
            for fn in own_docs:
                doc = next(d for f, d in docs if f == fn)
                if rb in str(doc.get("content") or "") + str(doc.get("title") or ""):
                    fails.append(f"{fn}: names the prerequisite's resolved_by action {rb!r} inside the "
                                 "docs of the problem it blocks — the source declares a condition, never "
                                 "a cross-problem instruction; the resolving action belongs to the other "
                                 "problem's own doc")
    # ---- coverage: single-home quantitative keys ---------------------------------------
    claims = {}
    for fn, d in docs:
        m = d.get("meta") or {}
        carries = m.get("carries") or []
        role = m.get("role")
        cap = FACTOR_CARRY_CAP if role in ("factor", "meta_rule") else FACET_CARRY_CAP
        if len(carries) > cap:
            fails.append(f"{fn}: carries {len(carries)} keys > cap {cap} for role {role} (fake scattering)")
        for k in carries:
            claims.setdefault(k, []).append((fn, d))
    for k in sorted(required):
        homes = claims.get(k, [])
        if len(homes) == 0:
            fails.append(f"coverage: quantitative key '{k}' claimed by no doc")
        elif len(homes) > 1:
            fails.append(f"coverage: quantitative key '{k}' claimed by {len(homes)} docs "
                         f"({[fn for fn, _ in homes]}) — every number lives in exactly one doc")
        else:
            fn, d = homes[0]
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
    print(f"   required quantitative keys={len(required)}  task_tools={len(task_tools)}  workflows={len(wfs)}")
    if fails:
        print("\n  [FAIL]")
        for f in fails[:60]:
            print("   -", f)
        print("DOCS NOT OK")
        sys.exit(1)
    print("\n  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, one implicit "
          "workflow doc each, non-directory hubs, private compute-binding coverage, single-home quantitative "
          "coverage, no stated prerequisites or scaffolding, no copied or templated wording")
    print("  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every dependency and "
          "order entailed at the source's strength yet stated nowhere")
    print("DOCS OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
