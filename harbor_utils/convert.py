#!/usr/bin/env python3
"""Convert erlbench scenarios (env/<scenario>/) into self-contained Harbor tasks.

    uv run python harbor_utils/convert.py                          # every task of every scenario
    uv run python harbor_utils/convert.py --tasks regional_retail_bank/auto_loan_payment_servicing/0
    uv run python harbor_utils/convert.py --scenarios env/metro_gym_chain --selftest

One erlbench task becomes one Harbor task directory, laid out by what the task IS, not by how
it was produced:

    task.toml, instruction.md          harbor config; the agent's system prompt
    user_simulator.md                  a record of the customer simulator's system prompt
    environment/
      db_schema.json                   table -> fields
      db.json                          the database at the start of the conversation: the
                                       union of every task's initial_state, overlaid with this one's
      knowledge_base/<title>.md        every product's documents, as plain Markdown content
      share_tools.py                   the directly listed tools
      task_tools.py                    all discoverable tools, merged as ordinary Python code
      episode.json                     frozen "now", customer-simulator prompt, integrity hashes
      runtime/                         the engine (erlbench runtime) and runtime.py, which builds
                                       the world and records a conversation over it
      requirements.txt, Dockerfile     the image: the world + the packages the conversation needs
    tests/     grade.py + expected.json      (reference actions, expected DB hash)
    solution/  oracle.py + oracle_calls.json (reference actions as live calls)

task.toml metadata lists every document of charter_scope.extended_policies and labels the
task EASY (<=2), MEDIUM (3), or HARD (>=4) by prerequisite_closure.resolution_order length.

The directory name is ``<scenario>__<difficulty>__<index>__<uuid8>``; the 8 hex digits are a
UUID derived from (scenario, difficulty, index), so re-converting keeps every task's name.

Beside the dataset, ``harbor_erl_agent/`` (``--agent-out``) receives the harness: erl_agent.py
(the Harbor agent) and container/ (run_episode.py + rollout/, the conversation loop), which it
copies into each task container and runs there — both models are called from the container
and every tool runs in that process, on the task's engine. Deliver the two directories
together.

Every task carries its own copy of the whole scenario world, so no task depends on another
(or on this repo). Nothing is hand-written per scenario: everything is derived by code, with
the functions the local rollout uses (``load_scenario``, ``merged_initial_state``,
``_company_name``, ``rollout.prompts``, ``erlbench.scoring.replay``).

The tool files (share_tools.py and the merged task_tools.py) and the erlbench runtime are
shipped without
module docstrings and comments (they describe the authoring pipeline, not the task); function
docstrings stay (a tool's docstring is its description), and each cleaned file is proven
AST-identical to its source minus exactly the removed docstrings.

Conversion refuses to write a task unless

  * the packed world, loaded in a fresh interpreter by the task's own runtime, defines
    exactly the source scenario's tools (names, owners, descriptions, schemas, order), the
    same knowledge-base titles and contents (plus any requested factor hints), schema and
    tool lists. Markdown filenames replace source document ids internally; search results
    show titles, scores and content. Documents are indexed in filename order; where that
    differs from the source's order a warning says so (only equal-score results can reorder);
  * the seeded database survives its JSON round trip bit for bit;
  * the reference actions, executed LIVE through the engine's own routing, succeed call by
    call and reach the reference replay's database hash.

``--selftest`` additionally runs each written task end to end without Docker, with its own
runtime, oracle and verifier — oracle -> 1, an empty conversation -> 0, the reference calls
without a normal end of call -> 0 — and runs the harness's run_episode.py once against a
written task with scripted stand-ins for the two models (no model is called).
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
import tomllib
import uuid
from dataclasses import replace
from pathlib import Path

# Loading a scenario imports its tool modules; never leave bytecode next to them.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RUNTIME = HERE / "runtime"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from erlbench.db import DB  # noqa: E402
from erlbench.determinism import Clock  # noqa: E402
from erlbench.engine import AGENT_BASE, BASE_SCHEMAS, USER_BASE, Engine  # noqa: E402
from erlbench.kb import Document, KnowledgeBase  # noqa: E402
from erlbench.loader import Scenario, load_scenario  # noqa: E402
from erlbench.scoring import replay  # noqa: E402
from rollout.orchestrator import NORMAL_TERMINATIONS  # noqa: E402
from rollout.prompts import build_agent_prompt, build_user_prompt  # noqa: E402
from rollout.runner import _company_name, merged_initial_state  # noqa: E402


def _load_runtime_module(name: str):
    spec = importlib.util.spec_from_file_location(f"_erl_{name}", RUNTIME / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The fingerprint functions the task checks itself against — one implementation.
rt = _load_runtime_module("runtime")

BASE_IMAGE = "python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea"
ORACLE_TERMINATION = "USER_STOP"
TASK_MARKER = 'benchmark = "erlbench"'
# What the conversation needs inside the container: the repo's own runtime dependencies
# (pyproject.toml) — the environment the local rollout runs in, which also covers what litellm
# imports lazily beyond its declared requirements (fastapi, on the Responses API path).

# The erlbench runtime shipped with every task (environment/runtime/): what the tool files and
# the engine need. loader/validate belong to authoring and are not shipped.
LIBRARY_MODULES = {
    "db": "The database: tables of rows keyed by id, with find / insert / update / delete "
          "and a content hash.",
    "determinism": "Deterministic primitives: the frozen clock and content-hash row identifiers.",
    "tools": "The tool API: the @tool decorator, the ToolContext a tool runs with, and tool "
             "schemas introspected from signatures and docstrings.",
    "kb": "The knowledge base: BM25 search (KB_search) and case-insensitive regex search "
          "(grep) over whole documents.",
    "engine": "The engine: the base meta tools and the routing that binds a task's database, "
              "knowledge base and tools.",
    "scoring": "Replay: re-apply the write calls of a trajectory to a fresh database and hash "
               "the result.",
}
LIBRARY_EXPORTS = ("tool", "ToolContext", "make_id", "Clock", "DB", "Document",
                   "KnowledgeBase", "Engine", "replay")
LIBRARY_INIT = f'''"""erlbench runtime: the database, clock, knowledge base, tool API and engine a task's
tools run on."""

from .determinism import Clock, make_id
from .db import DB
from .tools import ToolContext, tool
from .kb import Document, KnowledgeBase
from .engine import Engine
from .scoring import replay

__all__ = {list(LIBRARY_EXPORTS)!r}
'''
# The base meta tools' docstrings ARE their LLM-facing descriptions: always kept.
KEEP_DOCSTRINGS = {f"Engine.{name}" for name in AGENT_BASE + USER_BASE}

# The conversation loop shipped with the harness.
HARNESS_MODULES = {
    "__init__": "The conversation loop between an agent and a customer simulator.",
    "llm": "LLM calls through litellm, retried with capped exponential backoff.",
    "orchestrator": "The half-duplex conversation loop between the agent and the customer "
                    "simulator over one engine.",
    "prompts": "System prompts of the agent and the customer simulator, the agent's greeting, "
               "and the stop tokens that end a call.",
}

SHARE_TOOLS_DOC = ("Tools of {company} listed to their owner — the agent or the customer — and "
                   "called by name.")
TASK_TOOLS_DOC = ("Discoverable tools of {company}\n\nListed to no one: each is named in the "
                  "knowledge base and reached with\nunlock_agent_discoverable_tool / "
                  "unlock_user_discoverable_tool, then\ncall_agent_discoverable_tool / "
                  "call_user_discoverable_tool.")

TASK_NAME_NAMESPACE = uuid.UUID("5d8b5c0e-7a3f-4f4e-9a52-6f0c2b8e1d47")


class ConversionError(RuntimeError):
    pass


# ─────────────────────────────────────────────────────────────────────────────────────────
# Python sources: strip docstrings/comments, proven AST-identical
# ─────────────────────────────────────────────────────────────────────────────────────────

def _is_docstring(stmt) -> bool:
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str))


def _whole_lines(lines: list[str], node) -> bool:
    """The node starts its first line (after indentation) and ends its last one."""
    first, last = lines[node.lineno - 1], lines[node.end_lineno - 1]
    before = first.encode("utf-8")[:node.col_offset].decode("utf-8", "replace")
    after = last.encode("utf-8")[node.end_col_offset:].decode("utf-8", "replace").strip()
    return before.strip() == "" and (after == "" or after.startswith("#"))


def _removals(tree: ast.Module, lines: list[str], strip_all: bool, keep: set[str]) -> list:
    """(parent body, node) pairs to remove: the module docstring; with ``strip_all`` every
    class/function docstring except the qualified names in ``keep`` (and except one that is
    its body's only statement)."""
    out = []
    if tree.body and _is_docstring(tree.body[0]):
        out.append((tree.body, tree.body[0]))

    def visit(body, prefix):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = f"{prefix}{node.name}"
                if (strip_all and len(node.body) > 1 and _is_docstring(node.body[0])
                        and q not in keep):
                    out.append((node.body, node.body[0]))
                visit(node.body, q + ".")
            else:
                for attr in ("body", "orelse", "finalbody"):
                    visit(getattr(node, attr, None) or [], prefix)
                for handler in getattr(node, "handlers", None) or []:
                    visit(handler.body, prefix)

    visit(tree.body, "")
    return [(b, n) for b, n in out if _whole_lines(lines, n)]


def clean_python(src: str, *, module_doc: str | None = None, strip_all_docstrings: bool = False,
                 keep: set[str] = frozenset(), what: str = "source") -> str:
    """``src`` without comments, without its module docstring (replaced by ``module_doc``),
    and — with ``strip_all_docstrings`` — without class/function docstrings outside ``keep``.
    Everything else is kept byte for byte, and the result is checked to be AST-identical to
    the source minus exactly those docstrings."""
    src = src.replace("\r\n", "\n").replace("\r", "\n")
    lines = src.split("\n")
    tree = ast.parse(src)
    removals = _removals(tree, lines, strip_all_docstrings, keep)

    drop, cut, protected = set(), {}, set()
    for _body, node in removals:
        drop.update(range(node.lineno - 1, node.end_lineno))
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            row, col = tok.start
            if lines[row - 1][:col].strip() == "":
                drop.add(row - 1)                 # a comment-only line
            else:
                cut[row - 1] = min(cut.get(row - 1, col), col)
        elif tok.start[0] != tok.end[0]:          # inside a multi-line string: never collapse blanks
            protected.update(range(tok.start[0] - 1, tok.end[0]))

    kept, blank_run = [], 0
    for i, line in enumerate(lines):
        if i in drop:
            continue
        if i in cut:
            line = line[:cut[i]].rstrip()
        if line.strip() == "" and i not in protected:
            blank_run += 1
            if blank_run > 2 or not kept:
                continue
        else:
            blank_run = 0
        kept.append(line)
    while kept and kept[-1].strip() == "":
        kept.pop()
    body = "\n".join(kept) + "\n"
    if module_doc:
        if '"""' in module_doc or "\\" in module_doc:
            raise ConversionError(f"{what}: unsupported characters in the module docstring")
        body = f'"""{module_doc}"""\n\n' + body

    for parent, node in removals:
        parent.remove(node)
    if module_doc:
        tree.body.insert(0, ast.Expr(ast.Constant(module_doc)))
    if ast.dump(ast.parse(body)) != ast.dump(tree):
        raise ConversionError(f"{what}: cleaning changed the code, not only docstrings/comments")
    return body


def _check_imports(tree: ast.Module, what: str) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "erlbench":
            if node.module != "erlbench":
                raise ConversionError(f"{what} imports {node.module}, which tasks do not ship")
            missing = [a.name for a in node.names if a.name not in LIBRARY_EXPORTS]
            if missing:
                raise ConversionError(f"{what} imports {missing} from erlbench, not in the task runtime")


def pack_share_tools(src: str, company: str) -> str:
    _check_imports(ast.parse(src), "share_tools.py")
    return clean_python(src, module_doc=SHARE_TOOLS_DOC.format(company=company), what="share_tools.py")


def pack_task_tools(sc: Scenario, dst: Path, company: str) -> None:
    """Merge UUID-named tools as ordinary Python code, deduplicating identical imports."""
    doc = TASK_TOOLS_DOC.format(company=company if company.endswith(".") else company + ".")
    future_imports, body, seen_imports = [], [], set()
    for difficulty, path in _task_tools_sources(sc):
        src = path.read_text(encoding="utf-8")
        _check_imports(ast.parse(src), f"task tools of {difficulty}")
        cleaned = clean_python(src, what=f"task tools of {difficulty}")
        for node in ast.parse(cleaned).body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                key = ast.dump(node)
                if key in seen_imports:
                    continue
                seen_imports.add(key)
                if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                    future_imports.append(node)
                    continue
            body.append(node)
    merged = ast.Module(body=[ast.Expr(ast.Constant(doc))] + future_imports + body,
                        type_ignores=[])
    code = ast.unparse(merged) + "\n"
    if ast.dump(ast.parse(code)) != ast.dump(merged):
        raise ConversionError(f"{sc.name}: merging changed the tool code")
    _write(dst, code)


def package_library(dst: Path) -> None:
    """The erlbench runtime, cleaned: no module/class/function docstrings except the base
    meta tools' (their descriptions), no comments; code unchanged."""
    dst.mkdir(parents=True, exist_ok=True)
    for name, doc in LIBRARY_MODULES.items():
        src = (REPO / "erlbench" / f"{name}.py").read_text(encoding="utf-8")
        (dst / f"{name}.py").write_text(
            clean_python(src, module_doc=doc, strip_all_docstrings=True, keep=KEEP_DOCSTRINGS,
                         what=f"erlbench/{name}.py"), encoding="utf-8")
    (dst / "__init__.py").write_text(LIBRARY_INIT, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────────────────
# The scenario world, packed once per scenario
# ─────────────────────────────────────────────────────────────────────────────────────────

def _source_signature(sc: Scenario) -> dict:
    probe = Engine(DB(), Clock.from_stamp("1970-01-01"), sc.kb(), list(sc.specs), schema=sc.db_schema)
    sig = {
        "specs": [[s.name, s.owner, s.rw, s.kind, s.description, s.parameters, s.param_types]
                  for s in sc.specs],
        "docs": [[d.id, d.title, d.content] for d in sc.docs],
        "schema": sc.db_schema,
        "tool_lists": {o: probe.tool_list(o) for o in ("agent", "user")},
    }
    return json.loads(json.dumps(sig, ensure_ascii=False))


def _task_tools_sources(sc: Scenario) -> list[tuple[str, Path]]:
    """(difficulty, path) of every difficulty's task_tools.py, in erlbench's load order."""
    root = Path(sc.root)
    tasks_root = root / "tasks"
    if not tasks_root.is_dir():
        raise ConversionError(f"{sc.name}: legacy scenario layout (no tasks/ directory) is not supported")
    parts = []
    for entry in sorted(os.listdir(tasks_root)):
        d = tasks_root / entry
        if not d.is_dir() or entry.startswith(".") or entry == "__pycache__":
            continue
        for rel in ("task_tools.py", "tools/task_tools.py"):
            if (d / rel).exists():
                parts.append((entry, d / rel))
                break
    return parts


def document_filename(d: Document) -> str:
    """Use the title verbatim; reject titles that cannot safely name a Markdown file."""
    name = f"{d.title}.md"
    if (not d.title or any(c in d.title for c in '/\\\0')
            or len(name.encode("utf-8")) > 255):
        raise ConversionError(f"document {d.id!r}: title cannot be used as a filename: {d.title!r}")
    return name


def packed_documents(sc: Scenario, *, factor_hint_in_baseline: bool = False) -> list[Document]:
    """Markdown documents in filename order, using filenames as runtime identifiers.
    Optionally append same-policy factor titles to baseline content."""
    filenames = [document_filename(d).casefold() for d in sc.docs]
    if len(set(filenames)) != len(filenames):
        raise ConversionError(f"{sc.name}: duplicate knowledge-base title filenames")
    docs = [replace(d, id=document_filename(d)) for d in sorted(sc.docs, key=document_filename)]
    if not factor_hint_in_baseline:
        return docs
    factor_titles: dict[str, list[str]] = {}
    for d in docs:
        policy_id = d.meta.get("policy_id")
        if d.meta.get("role") == "factor" and policy_id:
            factor_titles.setdefault(policy_id, []).append(d.title)
    hinted = []
    for d in docs:
        titles = factor_titles.get(d.meta.get("policy_id"), [])
        if d.meta.get("role") == "baseline" and titles:
            d = replace(d, content=d.content + "\n\nSee also:\n" +
                        "\n".join(f"- {title}" for title in titles))
        hinted.append(d)
    return hinted


def harness_requirements() -> str:
    """requirements.txt for the image: the repo's runtime dependencies (pyproject.toml) and
    their whole dependency closure, each pinned to the version installed in this repo's
    environment (the one the local rollout runs), for a reproducible ``pip install --no-deps``."""
    from importlib import metadata
    from packaging.requirements import Requirement

    def canon(name: str) -> str:
        return re.sub(r"[-_.]+", "-", name).lower()

    project = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    pinned, stack = {}, [Requirement(dep).name for dep in project["dependencies"]]
    while stack:
        name = stack.pop()
        if canon(name) in pinned:
            continue
        dist = metadata.distribution(name)
        pinned[canon(name)] = f"{dist.metadata['Name']}=={dist.version}"
        for spec in dist.requires or []:
            req = Requirement(spec)
            if req.marker is None or req.marker.evaluate({"extra": ""}):
                stack.append(req.name)
    lines = sorted(pinned.values(), key=str.lower)
    return ("# Python packages the conversation needs inside the container (its LLM client and\n"
            "# dependencies), pinned; installed with --no-deps.\n" + "\n".join(lines) + "\n")


def pack_world(sc: Scenario, company: str, staged: Path, *,
               factor_hint_in_baseline: bool = False) -> list[Document]:
    """Write the scenario-level part of every task's environment/ into ``staged`` and prove,
    in a fresh interpreter running the packed runtime, that it is the source world with
    any requested factor hints. Return the packed documents in index order."""
    bdir = Path(sc.root) / "blueprint"
    share_src = (bdir / "share_tools.py").read_text(encoding="utf-8") if (bdir / "share_tools.py").exists() else ""
    (staged / "share_tools.py").parent.mkdir(parents=True, exist_ok=True)
    (staged / "share_tools.py").write_text(pack_share_tools(share_src, company), encoding="utf-8")
    pack_task_tools(sc, staged / "task_tools.py", company)
    docs = packed_documents(sc, factor_hint_in_baseline=factor_hint_in_baseline)
    for d in docs:
        _write(staged / "knowledge_base" / document_filename(d), d.content)
    _dump(staged / "db_schema.json", sc.db_schema)
    package_library(staged / "runtime" / "erlbench")
    shutil.copyfile(RUNTIME / "runtime.py", staged / "runtime" / "runtime.py")
    _write(staged / "requirements.txt", harness_requirements())

    proc = subprocess.run([sys.executable, str(staged / "runtime" / "runtime.py"), "--signature"],
                          env={**os.environ, "ERL_TASK_DIR": str(staged), "PYTHONDONTWRITEBYTECODE": "1"},
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise ConversionError(f"{sc.name}: the packed world does not load: {proc.stderr[-3000:]}")
    packed, source = json.loads(proc.stdout), _source_signature(sc)
    source["docs"] = [[d.id, d.title, d.content] for d in docs]     # compared in packed order
    # Tool names have unique UUID suffixes, so the tools compare by name; the order that
    # is visible — share tools in the tool lists — is compared exactly under "tool_lists".
    for sig in (packed, source):
        sig["specs"] = sorted(sig["specs"], key=lambda s: s[0])
    for key in source:
        if packed.get(key) != source[key]:
            raise ConversionError(f"{sc.name}: the packed world's {key} differs from the source scenario")
    if [d.title for d in docs] != [d.title for d in sc.docs]:
        print(f"    WARN {sc.name}: the knowledge base is indexed in title-filename order, not the "
              "source's order (only the order of equal-score search results can differ)")
    return docs


# ─────────────────────────────────────────────────────────────────────────────────────────
# Per task
# ─────────────────────────────────────────────────────────────────────────────────────────

def task_dir_name(scenario: str, difficulty: str, index: int) -> str:
    """``<scenario>__<difficulty>__<index>__<uuid8>`` in [a-z0-9_]. The suffix is a UUID5 of
    the task's identity, so the same task always gets the same name."""
    suffix = uuid.uuid5(TASK_NAME_NAMESPACE, f"{scenario}/{difficulty}/{index}").hex[:8]
    return re.sub(r"[^a-z0-9_]", "_", f"{scenario}__{difficulty}__{index}__{suffix}".lower())


def _remove_stale_dirs(out: Path, scenario: str, difficulty: str, index: int, name: str) -> None:
    """Drop earlier conversions of the same task that sit under another name."""
    for toml_path in out.glob("*/task.toml"):
        tdir = toml_path.parent
        if tdir.name == name:
            continue
        text = toml_path.read_text(encoding="utf-8")
        if TASK_MARKER not in text and "harbor_utils/convert.py" not in text:
            continue
        meta = tomllib.loads(text).get("metadata") or {}
        same = (meta.get("scenario") == scenario
                and (meta.get("category") or meta.get("difficulty")) == difficulty
                and meta.get("task_index") == index)
        if same:
            shutil.rmtree(tdir)
            print(f"    removed {tdir.name} (same task under an earlier name)")


def oracle_plan(reference: list, registry: dict) -> list:
    """The reference actions as the live tool calls an agent/customer would make. Wrapper
    calls and share/base tools pass through; a bare discoverable-tool name becomes its unlock +
    call pair; a call whose tool was never unlocked/handed over gets that unlock first."""
    unlocked = {"agent": set(), "user": set()}
    calls = []

    def add(owner, tool, arguments):
        if tool == "unlock_agent_discoverable_tool":
            unlocked["agent"].add(arguments.get("tool_name"))
        elif tool == "unlock_user_discoverable_tool":
            unlocked["user"].add(arguments.get("tool_name"))
        calls.append({"owner": owner, "tool": tool, "arguments": arguments})

    for a in reference:
        owner = a.get("owner") or "agent"
        tool = a.get("tool") or a.get("name")
        args = a.get("arguments") or {}
        spec = registry.get(tool)
        if tool in ("call_agent_discoverable_tool", "call_user_discoverable_tool"):
            side = "agent" if tool == "call_agent_discoverable_tool" else "user"
            if args.get("tool_name") not in unlocked[side]:
                add("agent", f"unlock_{side}_discoverable_tool", {"tool_name": args.get("tool_name")})
            add(owner, tool, args)
        elif tool in BASE_SCHEMAS or (spec is not None and spec.kind == "share"):
            add(owner, tool, args)
        elif spec is not None and spec.kind == "task":
            side = spec.owner
            if tool not in unlocked[side]:
                add("agent", f"unlock_{side}_discoverable_tool", {"tool_name": tool})
            add(side, f"call_{side}_discoverable_tool",
                {"tool_name": tool, "arguments": json.dumps(args, ensure_ascii=False)})
        else:
            raise ConversionError(f"a reference action uses an unknown tool: {tool!r}")
    return calls


def task_annotations(sc: Scenario, task: dict) -> dict:
    """Task metadata: resolution length and every document of the scoped policies."""
    count = len(task["prerequisite_closure"]["resolution_order"])
    policies = set((task.get("charter_scope") or {}).get("extended_policies") or [])
    return {
        "difficulty": "EASY" if count <= 2 else "MEDIUM" if count == 3 else "HARD",
        "related_knowledge_base_documents": sorted(document_filename(d) for d in sc.docs
                                                   if d.meta.get("policy_id") in policies),
    }


def _toml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def render_task_toml(name: str, meta: dict, opts) -> str:
    keywords = ["erlbench", "customer-service", "user-simulator", meta["scenario"],
                meta["category"], meta["difficulty"]]
    meta_lines = []
    for key, value in meta.items():
        if isinstance(value, list) and value:
            encoded = "[\n" + "".join(f"  {_toml_str(item)},\n" for item in value) + "]"
        else:
            encoded = json.dumps(value, ensure_ascii=False)
        meta_lines.append(f"{key} = {encoded}")
    meta_lines = "\n".join(meta_lines)
    description = (f"Customer-service conversation at {meta['company']}: an agent serves a "
                   "simulated customer with the company's knowledge base and tools. Scored by "
                   "the final state of the database, when the customer ends the call normally.")
    return f"""# An erlbench task: a conversation between an agent and a simulated customer, run inside
# this task's container by the erlbench harness (harbor_erl_agent/, erl_agent:ErlAgent).
schema_version = "1.4"
# The record of the conversation (every tool call, the end-of-call report, the final database)
# is collected into the trial's artifacts.
artifacts = ["/opt/task/state"]

[task]
name = {_toml_str("erlbench/" + name)}
version = "1.0.0"
description = {_toml_str(description)}
keywords = {json.dumps(keywords)}

[metadata]
{meta_lines}

[agent]
timeout_sec = {float(opts.agent_timeout_sec)}

[verifier]
timeout_sec = {float(opts.verifier_timeout_sec)}

[environment]
build_timeout_sec = {float(opts.build_timeout_sec)}
# The conversation calls its models (the agent and the customer simulator) from inside the
# container, so the container needs the network.
network_mode = "public"
"""


DOCKERFILE = f"""\
# The task environment: the world files at /opt/task, its runtime (the engine), and the Python
# packages the conversation needs, which runs in this container.
FROM {BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt /opt/task/requirements.txt
RUN pip install --no-cache-dir --no-deps -r /opt/task/requirements.txt

WORKDIR /opt/task
COPY db_schema.json db.json share_tools.py task_tools.py episode.json /opt/task/
COPY knowledge_base /opt/task/knowledge_base
COPY runtime /opt/task/runtime
# The world must build and match the integrity fingerprints in episode.json.
RUN python3 /opt/task/runtime/runtime.py
"""

TEST_SH = """\
#!/bin/bash
# Score the conversation by the final state of the database (see grade.py). grade.py writes
# /logs/verifier/reward.json; if the verifier itself fails it writes none.
set -uo pipefail
mkdir -p /logs/verifier
python3 /tests/grade.py
"""

SOLVE_SH = """\
#!/bin/bash
# Reference solution: execute the reference actions live through the task's tools, then end
# the call normally.
set -euo pipefail
python3 /solution/oracle.py
"""


def _write(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def _dump(path: Path, obj, indent: int | None = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)


def _prepare_task_dir(tdir: Path, force: bool) -> None:
    if tdir.exists():
        toml_path = tdir / "task.toml"
        text = toml_path.read_text(encoding="utf-8") if toml_path.exists() else ""
        ours = TASK_MARKER in text or "harbor_utils/convert.py" in text
        if not ours and not force:
            raise ConversionError(f"{tdir} exists and is not an erlbench task; pass --force to replace it")
        shutil.rmtree(tdir)
    tdir.mkdir(parents=True)


def convert_task(sc: Scenario, staged: Path, kb: KnowledgeBase, merged: dict, company: str,
                 background, difficulty: str, index: int, task: dict, out: Path, opts) -> dict:
    name = task_dir_name(sc.name, difficulty, index)
    ft = task.get("frozen_time")
    if not ft:
        raise ConversionError(f"{name}: task has no frozen_time")
    reference = task.get("evaluation_criteria") or []
    if not reference:
        raise ConversionError(f"{name}: task has no evaluation_criteria")

    # The rollout's world for this task (rollout.runner.ScenarioWorld.engine_for), with the
    # knowledge base in its packed index order.
    def engine() -> Engine:
        return Engine(DB.seeded(merged).overlay(task.get("initial_state")), Clock.from_stamp(ft),
                      kb, list(sc.specs), schema=sc.db_schema)

    probe = engine()
    tables = probe.db.tables
    initial_hash = probe.db.hash()
    if DB.seeded(json.loads(json.dumps(tables))).hash() != initial_hash:
        raise ConversionError(f"{name}: the seeded database does not survive a JSON round trip")
    target_hash = replay(engine(), reference)
    if target_hash == initial_hash:
        print(f"    WARN {name}: the reference actions make no database change")

    plan = oracle_plan(reference, probe.registry)
    live = engine()
    for i, c in enumerate(plan, 1):
        output = live.call(c["owner"], c["tool"], c["arguments"])
        if str(output).startswith("Error"):
            raise ConversionError(f"{name}: reference call {i} ({c['owner']} {c['tool']}) fails "
                                  f"live: {str(output)[:300]}")
    if live.db.hash() != target_hash:
        raise ConversionError(f"{name}: the reference calls executed live reach {live.db.hash()}, "
                              f"the reference replay {target_hash}")

    tdir = out / name
    _prepare_task_dir(tdir, opts.force)
    _remove_stale_dirs(out, sc.name, difficulty, index, name)

    # environment/: the world and its runtime.
    env = tdir / "environment"
    shutil.copytree(staged, env, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    _dump(env / "db.json", tables)
    user_system_prompt = build_user_prompt(task.get("user_scenario", ""))
    _write(tdir / "user_simulator.md", user_system_prompt)
    _dump(env / "episode.json", {
        "task_id": name, "scenario": sc.name, "category": difficulty, "task_index": index,
        "frozen_time": ft,
        "user_system_prompt": user_system_prompt,
        "integrity": rt.fingerprints(probe),
    })
    _write(env / "Dockerfile", DOCKERFILE)

    # instruction.md: the agent's system prompt, as the rollout builds it.
    (tdir / "instruction.md").write_text(build_agent_prompt(company, background, ft), encoding="utf-8")

    # tests/: uploaded only after the agent has finished.
    (tdir / "tests").mkdir()
    shutil.copyfile(RUNTIME / "grade.py", tdir / "tests" / "grade.py")
    _write(tdir / "tests" / "test.sh", TEST_SH, executable=True)
    _dump(tdir / "tests" / "expected.json", {
        "task_id": name, "frozen_time": ft,
        "reference_actions": [{"owner": a.get("owner") or "agent", "tool": a.get("tool") or a.get("name"),
                               "arguments": a.get("arguments") or {}} for a in reference],
        "expected_db_hash": target_hash, "initial_db_hash": initial_hash,
        "normal_terminations": sorted(NORMAL_TERMINATIONS)})

    # solution/: uploaded only for the reference solution (-a oracle).
    (tdir / "solution").mkdir()
    shutil.copyfile(RUNTIME / "oracle.py", tdir / "solution" / "oracle.py")
    _write(tdir / "solution" / "solve.sh", SOLVE_SH, executable=True)
    _dump(tdir / "solution" / "oracle_calls.json",
          {"task_id": name, "termination": ORACLE_TERMINATION, "calls": plan})

    specs = list(sc.specs)
    meta = {
        "benchmark": "erlbench",
        "author_name": "Joe Ray",
        "author_email": "joe@kultalab.com",
        "copyright": "Copyright (c) Joe Ray. All rights reserved.",
        "scenario": sc.name, "category": difficulty, "task_index": index,
        "company": company, "frozen_time": ft,
        "harness": "erl_agent:ErlAgent",
        "n_agent_tools": len(probe.tool_list("agent")), "n_customer_tools": len(probe.tool_list("user")),
        "n_share_tools": sum(1 for s in specs if s.kind == "share"),
        "n_discoverable_tools": sum(1 for s in specs if s.kind == "task"),
        "n_knowledge_base_documents": len(probe.kb.docs),
        "n_db_rows": sum(len(rows) for rows in tables.values()),
        "n_reference_actions": len(reference),
        **task_annotations(sc, task),
    }
    text = render_task_toml(name, meta, opts)
    tomllib.loads(text)
    _write(tdir / "task.toml", text)
    return {"name": name, "scenario": sc.name, "category": difficulty, "task_index": index}


# ─────────────────────────────────────────────────────────────────────────────────────────
# The harness (harbor_erl_agent/, delivered beside the tasks) and the dataset README
# ─────────────────────────────────────────────────────────────────────────────────────────

def build_agent_dir(dst: Path, force: bool = False) -> None:
    """harbor_erl_agent/: erl_agent.py (the Harbor agent, host side: it launches and waits) and
    container/ — run_episode.py and the conversation loop (rollout/, cleaned like the rest) —
    which erl_agent.py copies into each task container and runs there, plus a README.
    Rewritten on every run; the loop is checked to import in a fresh interpreter."""
    if dst.exists() and any(dst.iterdir()):
        if not (dst / "erl_agent.py").exists() and not force:
            raise ConversionError(f"{dst} exists and is not the erlbench harness; pass --force to replace it")
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "erl_agent.py", dst / "erl_agent.py")
    shutil.copyfile(HERE / "agent" / "run_episode.py", _mkparent(dst / "container" / "run_episode.py"))
    for name, doc in HARNESS_MODULES.items():
        src = (REPO / "rollout" / f"{name}.py").read_text(encoding="utf-8")
        _write(dst / "container" / "rollout" / f"{name}.py",
               clean_python(src, module_doc=doc, strip_all_docstrings=True, what=f"rollout/{name}.py"))
    _write(dst / "README.md", AGENT_README)
    check = "import rollout.orchestrator, rollout.llm, rollout.prompts"
    proc = subprocess.run([sys.executable, "-c", check], cwd=dst / "container",
                          env={**os.environ, "PYTHONPATH": str(dst / "container"),
                               "PYTHONDONTWRITEBYTECODE": "1"},
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise ConversionError(f"the packed conversation loop does not import: {proc.stderr[-2000:]}")


def _mkparent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_dataset_readme(out: Path) -> None:
    # Earlier layouts kept a harness at the dataset root; it lives in harbor_erl_agent/ now.
    for stale in ("erl_agent.py", "erl_harness.zip"):
        (out / stale).unlink(missing_ok=True)
    shutil.rmtree(out / "__pycache__", ignore_errors=True)
    _write(out / "README.md", DATASET_README)


AGENT_README = """\
# harbor_erl_agent — the harness for the erlbench Harbor tasks

The erlbench tasks are conversations: an agent (the model under test) serves a simulated
customer at a fictional company. This directory is the Harbor agent that runs them:

```
erl_agent.py        the Harbor agent (erl_agent:ErlAgent), on the host: it copies container/
                    into the task container, runs the conversation there, waits for it, and
                    reads back its outputs; it calls no model itself
container/          what runs inside the task container:
  run_episode.py    one conversation: the agent and the customer simulator (their models
                    called from the container) over the task's own engine, in one process
  rollout/          the conversation loop (turn-taking, stop tokens, limits, LLM client)
```

One harness runs every task: the tools, the knowledge base and the database are each task's
own, in its container. The container needs the network (it calls the models); the Python
packages the conversation needs are part of every task image.

```bash
# Run from the directory that holds harbor_tasks/ and harbor_erl_agent/; harbor writes each
# job to ./jobs/<timestamp>/. 64 trials at a time, every task attempted twice.

# reference solution (oracle): must score 1.0 on every task
harbor run -p harbor_tasks -a oracle -n 64 -k 2

# rollout: agent openai.gpt-6-astra (reasoning effort max),
#          customer simulator openai.gpt-5.4 (reasoning effort medium), same endpoint
AGENT_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 AGENT_API_KEY=<API key> \\
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \\
    -m openai/responses/openai.gpt-6-astra \\
    --ak user_model=openai/responses/openai.gpt-5.4 \\
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \\
    -n 64 -k 2

# rollout: agent global.anthropic.claude-opus-4-8 (Anthropic Messages API on bedrock-runtime,
#          reasoning effort max), customer simulator openai.gpt-5.4 on its own endpoint
AGENT_API_BASE=https://bedrock-runtime.us-west-2.amazonaws.com/anthropic AGENT_API_KEY=<API key> \\
USER_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 USER_API_KEY=<API key> \\
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \\
    -m anthropic/global.anthropic.claude-opus-4-8 \\
    --ak user_model=openai/responses/openai.gpt-5.4 \\
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \\
    -n 64 -k 2

# a single task: add  -i <task directory name>
```

Harbor imports a custom agent by module name (`-a module:Class`), so this directory goes on
`PYTHONPATH`; `PYTHONDONTWRITEBYTECODE` keeps a `__pycache__/` out of it. Each trial's
conversation runs in its own container, so `-n` scales with the machine's containers and the
model endpoint's quota.

Each model is three things, given at launch — nothing provider-specific:

| | agent | customer simulator |
|---|---|---|
| model `<protocol>/<model id>` | `-m` | `--ak user_model=` |
| base URL of its endpoint | `AGENT_API_BASE` | `USER_API_BASE` (default: the agent's) |
| API key | `AGENT_API_KEY` | `USER_API_KEY` (default: the agent's) |

The protocol is `openai/` for an OpenAI-compatible endpoint (`openai/responses/` for its
Responses API) or `anthropic/` for an Anthropic-compatible one (Messages API); the model id
after it is the one that endpoint expects — Claude Opus 4.8 is `global.anthropic.claude-opus-4-8`
(or `us.` …, an inference profile) on bedrock-runtime, `anthropic.claude-opus-4-8` on
bedrock-mantle. The variables come from the environment harbor is launched with (or
`--ae NAME=value`). The keys reach the run in a file inside the container that it deletes as
soon as it has read it.

Options (`--ak key=value`): `user_model`, `reasoning_effort`, `user_reasoning_effort`,
`temperature`, `user_temperature`, `max_tokens`, `user_max_tokens`, `agent_llm_args` /
`user_llm_args` (litellm keyword arguments as JSON), `request_timeout`, `max_attempts`
(0 = retry forever), `max_steps` (200), `max_errors` (10).

Per trial it writes, under the trial's `agent/`: `transcript.json`, `agent_trajectory.json`,
`user_trajectory.json`, `rollout.json`, per-call `llm_debug/`, `erl_agent.log`, and an ATIF
`trajectory.json`.
"""


DATASET_README = """\
# erlbench — customer-service tasks for Harbor

Author: Joe Ray (joe@kultalab.com). All rights reserved.

Each task is a live customer-service conversation. An **agent** (the model under test)
serves a **simulated customer** (an LLM playing the brief in the task) at a fictional
company, using the company's knowledge base and tools; the task is scored by the **final
state of the company database**.

Each task directory contains the company's tools, knowledge base and database. Tasks are
self-contained and run with the erlbench harness in `harbor_erl_agent/`, beside this
directory.

## Layout of a task

```
instruction.md           the agent's system prompt
user_simulator.md        the customer simulator's system prompt
task.toml                task identity, difficulty, related documents and runtime settings
environment/
  db_schema.json         the database schema (table -> fields)
  db.json                the database at the start of the conversation
  knowledge_base/        Markdown documents (<title>.md) containing only content: policies,
                         procedures, fee tables, the names of the discoverable tools
  share_tools.py         tools listed to their owner (the agent or the customer)
  task_tools.py          discoverable tools named in the knowledge base,
                         reached through unlock_*_discoverable_tool +
                         call_*_discoverable_tool
  episode.json           the frozen "now", the customer simulator's prompt, integrity hashes
  runtime/               the engine (erlbench runtime) and runtime.py, which builds the world
                         and records a conversation over it
  requirements.txt       the Python packages the conversation needs (installed in the image)
tests/                   the verifier (reference actions, expected database hash)
solution/                the reference solution: solve.sh, oracle.py and oracle_calls.json
```

In `task.toml`, `[metadata].related_knowledge_base_documents` lists the documents relevant
to the task, with filenames relative to `environment/knowledge_base/`.
`[metadata].difficulty` is `EASY`, `MEDIUM` or `HARD`; this label also appears in the task
keywords.

## The conversation

The agent sees the base meta tools — `KB_search`, `grep`, `unlock_agent_discoverable_tool`,
`unlock_user_discoverable_tool`, `call_agent_discoverable_tool` — and the agent-owned tools
of `share_tools.py`. The business rules and the names of the discoverable tools are only in
the knowledge base, so the agent must look them up. Some actions only the customer may take:
the agent hands the tool over with `unlock_user_discoverable_tool`, and the customer runs it
with `call_user_discoverable_tool`. The agent opens with a fixed greeting; the two sides
then take turns, each turn either a message to the other side or a tool call. The customer
ends the call with a stop token.

## Run

The whole conversation runs inside the task container: the harness copies it in, and both
models are called from there (the container needs the network). The endpoints and keys are
given in the environment harbor is launched with; the keys reach the run in a file it deletes
as soon as it has read it.

```bash
# Run from the directory that holds harbor_tasks/ and harbor_erl_agent/; harbor writes each
# job to ./jobs/<timestamp>/. 64 trials at a time, every task attempted twice.

# reference solution (oracle): must score 1.0 on every task
harbor run -p harbor_tasks -a oracle -n 64 -k 2

# rollout: agent openai.gpt-6-astra (reasoning effort max),
#          customer simulator openai.gpt-5.4 (reasoning effort medium), same endpoint
AGENT_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 AGENT_API_KEY=<API key> \\
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \\
    -m openai/responses/openai.gpt-6-astra \\
    --ak user_model=openai/responses/openai.gpt-5.4 \\
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \\
    -n 64 -k 2

# rollout: agent global.anthropic.claude-opus-4-8 (Anthropic Messages API on bedrock-runtime,
#          reasoning effort max), customer simulator openai.gpt-5.4 on its own endpoint
AGENT_API_BASE=https://bedrock-runtime.us-west-2.amazonaws.com/anthropic AGENT_API_KEY=<API key> \\
USER_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 USER_API_KEY=<API key> \\
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \\
    -m anthropic/global.anthropic.claude-opus-4-8 \\
    --ak user_model=openai/responses/openai.gpt-5.4 \\
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \\
    -n 64 -k 2

# a single task: add  -i <task directory name>
```

Each model is three things, given at launch: the model `<protocol>/<model id>` — `openai/...`
for an OpenAI-compatible endpoint (`openai/responses/...` for its Responses API) or
`anthropic/...` for an Anthropic-compatible one — and that endpoint's base URL and API key,
`AGENT_API_BASE` / `AGENT_API_KEY` (the customer simulator uses them too unless
`USER_API_BASE` / `USER_API_KEY` are set). Harness options are listed in
`harbor_erl_agent/README.md`.

## Scoring

Every tool call is recorded as it happens. The verifier re-applies the recorded calls and the
reference actions to fresh copies of the database and compares the resulting database
hashes; the reward is 1 when they match **and** the customer ended the call normally
(`USER_STOP`, or `USER_TRANSFER` after a hand-off to a human). `reward.json` has `reward`
and `reward_db_match` (the database match alone).

Each trial keeps: `agent/` — the conversation (`transcript.json`, `agent_trajectory.json`,
`user_trajectory.json`, `rollout.json`, per-call `llm_debug/`, `erl_agent.log`, and an ATIF
`trajectory.json`); `verifier/grade.json` — the scoring details; `artifacts/` — the record of
the conversation (`calls.jsonl`, `episode.json`, `final_db.json`).
"""


# ─────────────────────────────────────────────────────────────────────────────────────────
# Offline self-test (no Docker): the task's own runtime, oracle and verifier
# ─────────────────────────────────────────────────────────────────────────────────────────

_NO_STOP = """
import json, sys
sys.path.insert(0, sys.argv[1])
import runtime as rt
plan = json.load(open(sys.argv[2]))
session = rt.open_session()
for c in plan["calls"]:
    session.call(c["owner"], c["tool"], c["arguments"])
session.end({"termination": "MAX_STEPS"})
"""


def _selftest_case(tdir: Path, case: str) -> dict:
    env_dir = tdir / "environment"
    with tempfile.TemporaryDirectory() as tmp:
        envv = {**os.environ, "ERL_TASK_DIR": str(env_dir), "ERL_STATE_DIR": f"{tmp}/state",
                "ERL_TESTS_DIR": str(tdir / "tests"), "ERL_VERIFIER_DIR": f"{tmp}/verifier",
                "PYTHONDONTWRITEBYTECODE": "1"}
        steps = {"oracle": [sys.executable, str(tdir / "solution" / "oracle.py")],
                 "no_stop": [sys.executable, "-c", _NO_STOP, str(env_dir / "runtime"),
                             str(tdir / "solution" / "oracle_calls.json")]}
        if case in steps:
            proc = subprocess.run(steps[case], env=envv, capture_output=True, text=True)
            if proc.returncode != 0:
                raise ConversionError(f"{case} failed: {proc.stdout[-1500:]}{proc.stderr[-1500:]}")
        proc = subprocess.run([sys.executable, str(tdir / "tests" / "grade.py")],
                              env=envv, capture_output=True, text=True)
        if proc.returncode != 0:
            raise ConversionError(f"grade.py failed: {proc.stdout[-1500:]}{proc.stderr[-1500:]}")
        return json.loads(Path(f"{tmp}/verifier/reward.json").read_text())


def selftest_task(tdir: Path) -> None:
    """oracle -> 1/1; the reference calls without a normal end of call -> 0/1; an empty
    conversation -> 0/0 (0/1 only when the reference changes nothing, already warned)."""
    expected = json.loads((tdir / "tests" / "expected.json").read_text(encoding="utf-8"))
    no_change = expected["expected_db_hash"] == expected["initial_db_hash"]
    want = {"oracle": {"reward": 1.0, "reward_db_match": 1.0},
            "nop": {"reward": 0.0, "reward_db_match": 1.0 if no_change else 0.0},
            "no_stop": {"reward": 0.0, "reward_db_match": 1.0}}
    got = {case: _selftest_case(tdir, case) for case in want}
    if got != want:
        raise ConversionError(f"{tdir.name}: self-test rewards {got} != expected {want}")


# Scripted stand-ins for the two models: the customer opens, the agent searches the knowledge
# base once and answers, the customer ends the call.
_DRY_RUN = """
import runpy, sys
sys.path.insert(0, sys.argv[1])
from rollout import llm
def chat(self, messages, tools=None, tag=""):
    last = messages[-1]
    if " user " in f" {tag} ":
        text = "###STOP###" if len(messages) > 3 else "Hi, I need help with my account."
        return llm.LLMResult(content=text, tool_calls=[], finish_reason="stop",
                             raw_message={"role": "assistant", "content": text})
    if last.get("role") == "tool":
        text = "Thanks - here is what I found."
        return llm.LLMResult(content=text, tool_calls=[], finish_reason="stop",
                             raw_message={"role": "assistant", "content": text})
    call = llm.ToolCall(id="call_1", name="KB_search", arguments={"query": "account"})
    return llm.LLMResult(content="", tool_calls=[call], finish_reason="tool_calls",
                         raw_message={"role": "assistant", "content": "", "tool_calls": [
                             {"id": "call_1", "type": "function",
                              "function": {"name": "KB_search", "arguments": '{"query": "account"}'}}]})
llm.LLMClient.chat = chat
sys.argv = [sys.argv[2], sys.argv[3]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def harness_dry_run(agent_dir: Path, tdir: Path) -> None:
    """Run the harness's container/run_episode.py on a written task, as erl_agent.py would in
    the container, with the two models replaced by scripted stand-ins: the conversation must
    end normally with its tool call recorded, its outputs written, and the verifier must grade
    it (0: nothing was changed)."""
    env_dir, container = tdir / "environment", agent_dir / "container"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "secrets.json").write_text(json.dumps({"agent_api_key": "x", "user_api_key": "x"}))
        shutil.copyfile(tdir / "instruction.md", tmp / "instruction.md")
        role = {"effort": "low", "temperature": 1.0, "max_tokens": 1024, "llm_args": "",
                "api_base": "http://unused.invalid", "timeout": 0}
        (tmp / "config.json").write_text(json.dumps({
            "run_id": "dryrun", "instruction_file": str(tmp / "instruction.md"),
            "secrets_file": str(tmp / "secrets.json"),
            "roles": {"agent": {**role, "model": "openai/responses/stand-in"},
                      "user": {**role, "model": "openai/responses/stand-in"}},
            "max_steps": 20, "max_errors": 10, "max_attempts": 1}))
        envv = {**os.environ, "ERL_TASK_DIR": str(env_dir), "ERL_STATE_DIR": str(tmp / "state"),
                "ERL_LOGS_DIR": str(tmp / "logs"), "ERL_PID_FILE": str(tmp / "pid"),
                "ERL_TESTS_DIR": str(tdir / "tests"), "ERL_VERIFIER_DIR": str(tmp / "verifier"),
                "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run([sys.executable, "-c", _DRY_RUN, str(container),
                               str(container / "run_episode.py"), str(tmp / "config.json")],
                              env=envv, capture_output=True, text=True)
        if proc.returncode != 0:
            raise ConversionError(f"harness dry run failed: {proc.stdout[-1500:]}{proc.stderr[-2500:]}")
        if (tmp / "secrets.json").exists():
            raise ConversionError("harness dry run: the secrets file was not removed")
        missing = [f for f in ("rollout.json", "transcript.json", "agent_trajectory.json",
                               "llm_calls.json", "erl_agent.log") if not (tmp / "logs" / f).exists()]
        if missing:
            raise ConversionError(f"harness dry run: outputs missing: {missing}")
        subprocess.run([sys.executable, str(tdir / "tests" / "grade.py")], env=envv, check=True,
                       capture_output=True, text=True)
        grade = json.loads((tmp / "verifier" / "grade.json").read_text())
        if (grade["termination"], grade["num_tool_calls"], grade["reward"]) != ("USER_STOP", 1, 0.0):
            raise ConversionError(f"harness dry run graded unexpectedly: {grade}")


# ─────────────────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────────────────

def discover_scenarios(env_root: Path) -> list[Path]:
    return [d for d in sorted(env_root.iterdir())
            if d.is_dir() and ((d / "blueprint" / "blueprint.yaml").exists()
                               or (d / "blueprint.yaml").exists())]


def _selected(scenario: str, difficulty: str, index: int, patterns: list[str] | None) -> bool:
    if not patterns:
        return True
    keys = (f"{scenario}/{difficulty}/{index}", f"{difficulty}/{index}",
            task_dir_name(scenario, difficulty, index))
    return any(fnmatch.fnmatch(k, p) for p in patterns for k in keys)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--env-root", default=str(REPO / "env"), help="where scenarios live")
    p.add_argument("--scenarios", nargs="+", default=None,
                   help="scenario dirs (default: every dir under --env-root with a blueprint)")
    p.add_argument("--tasks", nargs="+", default=None,
                   help="task selectors, globs allowed: scenario/difficulty/index, "
                        "difficulty/index, or a task dir name (default: all)")
    p.add_argument("--out", default=str(REPO / "harbor_tasks"), help="output dataset dir")
    p.add_argument("--agent-out", default=str(REPO / "harbor_erl_agent"),
                   help="where the harness goes (delivered beside the dataset)")
    p.add_argument("--no-background", action="store_true",
                   help="omit the company background from the agent prompt (as rollout --no-background)")
    p.add_argument("--factor-hint-in-baseline", action="store_true",
                   help="append a See also list of the same policy's factor document titles to baseline documents")
    p.add_argument("--agent-timeout-sec", type=float, default=3600.0)
    p.add_argument("--verifier-timeout-sec", type=float, default=600.0)
    p.add_argument("--build-timeout-sec", type=float, default=1200.0)
    p.add_argument("--selftest", action="store_true",
                   help="after writing, run each task's oracle + verifier offline, and the harness once with scripted models")
    p.add_argument("--keep-going", action="store_true",
                   help="report a task that fails conversion and continue with the rest")
    p.add_argument("--force", action="store_true",
                   help="replace existing dirs even if they are not erlbench tasks")
    opts = p.parse_args(argv)

    out = Path(opts.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    scenarios = ([Path(s).resolve() for s in opts.scenarios] if opts.scenarios
                 else discover_scenarios(Path(opts.env_root).resolve()))
    if not scenarios:
        raise SystemExit(f"no scenarios under {opts.env_root}")

    agent_out = Path(opts.agent_out).resolve()
    if agent_out == out or out in agent_out.parents:
        raise SystemExit("--agent-out must be outside the dataset dir (every dir there is a task)")
    build_agent_dir(agent_out, force=opts.force)
    print(f"harness -> {agent_out}")

    written, failed = [], []
    for root in scenarios:
        sc = load_scenario(str(root))
        picked = [(d, int(t.get("task_index", 0)), t) for d in sorted(sc.tasks) for t in sc.tasks[d]
                  if _selected(sc.name, d, int(t.get("task_index", 0)), opts.tasks)]
        if not picked:
            continue
        print(f"[{sc.name}] {len(sc.specs)} tools, {len(sc.docs)} knowledge-base documents, "
              f"{sum(len(v) for v in sc.tasks.values())} tasks — converting {len(picked)}")
        merged = merged_initial_state(sc)
        company = _company_name(sc)
        background = None if opts.no_background else (sc.blueprint or {}).get("background")
        with tempfile.TemporaryDirectory() as tmp:
            staged = Path(tmp) / "environment"
            try:
                docs = pack_world(sc, company, staged,
                                  factor_hint_in_baseline=opts.factor_hint_in_baseline)
            except ConversionError as e:
                failed += [(task_dir_name(sc.name, d, i), str(e)) for d, i, _ in picked]
                print(f"  FAIL {sc.name}: {e}")
                if not opts.keep_going:
                    raise
                continue
            kb = KnowledgeBase(docs)
            for d, i, t in picked:
                try:
                    rec = convert_task(sc, staged, kb, merged, company, background, d, i, t, out, opts)
                    if opts.selftest:
                        selftest_task(out / rec["name"])
                    written.append(rec)
                    print(f"  ok  {rec['name']}" + ("  (self-test passed)" if opts.selftest else ""))
                except ConversionError as e:
                    failed.append((task_dir_name(sc.name, d, i), str(e)))
                    print(f"  FAIL {task_dir_name(sc.name, d, i)}: {e}")
                    if not opts.keep_going:
                        raise

    if written:
        write_dataset_readme(out)
        if opts.selftest:
            harness_dry_run(agent_out, out / written[0]["name"])
            print(f"harness dry run passed on {written[0]['name']}")
    print(f"\n{len(written)} task(s) written to {out}" + (f", {len(failed)} failed" if failed else ""))
    for name, err in failed:
        print(f"  FAILED {name}: {err}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
