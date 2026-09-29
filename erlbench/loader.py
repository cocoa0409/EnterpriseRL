"""Load a generated scenario directory into runnable, scorable objects.

Expected layout (produced by the erl-entrance pipeline):

  env/<scenario>/
    blueprint/                         # the scenario constitution
      blueprint.yaml
      db_schema.json
      share_tools.py
      products/<category>.yaml         # per-category product/event strategies
    tasks/<difficulty>/                # one directory per difficulty
      task_tools.py                    # this difficulty's task tools
      <category>.extended.yaml         # the difficulty's strategy charter
      tasks/0.json ... tasks/M-1.json  # the M concrete tasks
    docs/<category>/<KB_DOC_ID>.json   # scenario-level KB corpus (id/title/content)

A legacy layout is still read for older scenarios: blueprint files at the env
root, difficulties directly under the root with tools/task_tools.py +
docs/*.json + 0/task.json per difficulty.

All difficulties' tools and KB documents are merged into one registry and one
corpus (so unrelated documents act as distractors), while each task seeds its own
DB — which is why the difficulties must be designed to be non-intersecting.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

from .db import DB
from .determinism import Clock
from .engine import Engine
from .kb import Document, KnowledgeBase
from .tools import ToolSpec, collect_specs

# make sure `import erlbench...` works inside generated *_tools.py
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MODCOUNT = 0


def _import_module(py_path: str):
    global _MODCOUNT
    _MODCOUNT += 1
    name = f"_gen_tools_{_MODCOUNT}"
    spec = importlib.util.spec_from_file_location(name, py_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_tool_specs(py_path: str, kind: str) -> List[ToolSpec]:
    """Load @tool functions from a module, tagging them share/task by source file."""
    if not os.path.exists(py_path):
        return []
    return collect_specs(_import_module(py_path), kind)


def _looks_like_doc(obj) -> bool:
    return isinstance(obj, dict) and "id" in obj and "content" in obj


def blueprint_dir(root: str) -> str:
    """Where the scenario constitution lives: env/<scenario>/blueprint/ when that
    subdir holds blueprint.yaml (new layout), else the env root (legacy layout)."""
    sub = os.path.join(root, "blueprint")
    if os.path.exists(os.path.join(sub, "blueprint.yaml")):
        return sub
    return root


def _read_target_tools(difficulty_dir: str) -> Dict[str, str]:
    """{extended policy id: target_tool} from the difficulty's <category>.extended.yaml."""
    out: Dict[str, str] = {}
    for fn in sorted(os.listdir(difficulty_dir)):
        if not fn.endswith(".extended.yaml"):
            continue
        with open(os.path.join(difficulty_dir, fn)) as f:
            ext = yaml.safe_load(f) or {}
        for p in ext.get("extended_policies") or []:
            if isinstance(p, dict) and p.get("id"):
                out[p["id"]] = p.get("target_tool")
    return out


def required_order(closure: dict, target_tool: dict) -> List[dict]:
    """The tool pairs a task's ``prerequisite_closure`` imposes, one per edge in edge order:
    an edge ``from -> to`` says the ``from`` problem depends on the ``to`` problem, and each
    problem is resolved by its policy's target tool, so ``{"before": to's tool, "after":
    from's tool}``. ``target_tool`` maps a policy id to its target tool (Scenario.target_tools).
    A policy without a tool, or a ``resolved_by`` that is not the prerequisite's tool, is a
    data error (ValueError). Only the tool names leave this function: what the verifier ships
    says nothing about where the pairs come from."""
    order = []
    for e in (closure or {}).get("edges") or []:
        blocked, prerequisite = e.get("from"), e.get("to")
        after, before = target_tool.get(blocked), target_tool.get(prerequisite)
        if not after or not before:
            missing = blocked if not after else prerequisite
            raise ValueError(f"prerequisite edge {blocked} -> {prerequisite}: policy {missing!r} "
                             f"has no target tool")
        if e.get("resolved_by") and e["resolved_by"] != before:
            raise ValueError(f"prerequisite edge {blocked} -> {prerequisite}: resolved_by "
                             f"{e['resolved_by']!r} is not the target tool of {prerequisite} "
                             f"({before!r})")
        order.append({"before": before, "after": after})
    return order


def _read_tasks(task_dir: str) -> List[dict]:
    """Read a difficulty's numbered task files, in index order. Two layouts:
    <difficulty>/tasks/<idx>.json (current) or <difficulty>/<idx>/task.json (legacy)."""
    tasks = []
    if not os.path.isdir(task_dir):
        return tasks
    flat = os.path.join(task_dir, "tasks")
    if os.path.isdir(flat):
        for fn in sorted(os.listdir(flat)):
            stem, ext = os.path.splitext(fn)
            if not (ext == ".json" and stem.isdigit()):
                continue
            with open(os.path.join(flat, fn)) as f:
                t = json.load(f)
            t.setdefault("task_index", int(stem))
            tasks.append(t)
        tasks.sort(key=lambda t: t["task_index"])
        return tasks
    for idx in sorted(os.listdir(task_dir)):
        p = os.path.join(task_dir, idx, "task.json")
        if not (idx.isdigit() and os.path.exists(p)):
            continue
        with open(p) as f:
            t = json.load(f)
        t.setdefault("task_index", int(idx))
        tasks.append(t)
    return tasks


def _read_docs(docs_dir: str) -> List[Document]:
    """Collect every KB document json under docs_dir (recursing into the
    per-category subdirs of the current layout)."""
    docs: List[Document] = []
    if not os.path.isdir(docs_dir):
        return docs
    for dirpath, dirnames, filenames in os.walk(docs_dir):
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(dirpath, fn)) as f:
                obj = json.load(f)
            if _looks_like_doc(obj):
                docs.append(Document(id=obj["id"], title=obj.get("title", obj["id"]),
                                     content=obj["content"],
                                     meta=obj.get("meta") or {}))
    return docs


def _load_task_tools(difficulty_dir: str) -> List[ToolSpec]:
    """A difficulty's task tools: <difficulty>/task_tools.py (current layout),
    falling back to <difficulty>/tools/task_tools.py (legacy)."""
    p = os.path.join(difficulty_dir, "task_tools.py")
    if not os.path.exists(p):
        p = os.path.join(difficulty_dir, "tools", "task_tools.py")
    return load_tool_specs(p, kind="task")


@dataclass
class Scenario:
    root: str
    name: str
    blueprint: dict
    db_schema: dict
    specs: List[ToolSpec]
    docs: List[Document]
    tasks: Dict[str, List[dict]]  # difficulty -> [task, ...]
    # difficulty -> {extended policy id: its target tool}, from <category>.extended.yaml —
    # what turns a task's prerequisite_closure into a tool order (scoring.required_order)
    target_tools: Dict[str, Dict[str, str]] = field(default_factory=dict)
    _kb_cache: Optional[KnowledgeBase] = field(default=None, repr=False, compare=False)

    def kb(self) -> KnowledgeBase:
        # The BM25 index is immutable (docs are fixed; search/grep are pure reads and the
        # unlock state lives on the Engine), so build it once per Scenario and share it
        # across every engine_for() call instead of rebuilding the index per episode.
        if self._kb_cache is None:
            self._kb_cache = KnowledgeBase(list(self.docs))
        return self._kb_cache

    def engine_for(self, task: dict) -> "Engine":
        ft = task.get("frozen_time")
        if not ft:
            raise ValueError(
                f"task '{task.get('task_index', '?')}' has no frozen_time — it is a "
                "required field of task.json; every timestamp in the task reads it"
            )
        clock = Clock.from_stamp(ft)
        db = DB.seeded(task.get("initial_state"))
        return Engine(db, clock, self.kb(), list(self.specs), schema=self.db_schema)

    def all_tasks(self):
        for difficulty, items in self.tasks.items():
            for t in items:
                yield difficulty, t


def load_scenario(root: str) -> Scenario:
    root = os.path.abspath(root)
    name = os.path.basename(root.rstrip("/"))
    bdir = blueprint_dir(root)

    with open(os.path.join(bdir, "blueprint.yaml")) as f:
        blueprint = yaml.safe_load(f) or {}
    db_schema = {}
    ds = os.path.join(bdir, "db_schema.json")
    if os.path.exists(ds):
        with open(ds) as f:
            db_schema = json.load(f)

    specs: List[ToolSpec] = load_tool_specs(os.path.join(bdir, "share_tools.py"), kind="share")
    docs: List[Document] = []
    tasks: Dict[str, List[dict]] = {}
    target_tools: Dict[str, Dict[str, str]] = {}

    tasks_root = os.path.join(root, "tasks")
    if os.path.isdir(tasks_root):
        # current layout: difficulties under tasks/, one KB corpus under docs/
        for entry in sorted(os.listdir(tasks_root)):
            d = os.path.join(tasks_root, entry)
            if not os.path.isdir(d) or entry.startswith(".") or entry == "__pycache__":
                continue
            specs += _load_task_tools(d)
            t = _read_tasks(d)
            if t:
                tasks[entry] = t
                target_tools[entry] = _read_target_tools(d)
        docs = _read_docs(os.path.join(root, "docs"))
    else:
        # legacy layout: difficulty dirs at the env root, each with its own docs/
        for entry in sorted(os.listdir(root)):
            d = os.path.join(root, entry)
            if not os.path.isdir(d):
                continue
            if entry.startswith(".") or entry in ("__pycache__", "blueprint", "docs"):
                continue
            specs += _load_task_tools(d)
            docs += _read_docs(os.path.join(d, "docs"))
            t = _read_tasks(d)
            if t:
                tasks[entry] = t
                target_tools[entry] = _read_target_tools(d)

    return Scenario(root=root, name=name, blueprint=blueprint, db_schema=db_schema,
                    specs=specs, docs=docs, tasks=tasks, target_tools=target_tools)
