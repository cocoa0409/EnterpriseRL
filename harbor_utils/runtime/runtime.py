"""The world of one task, built from the files at the task root, and one conversation over it.

    db_schema.json        table -> fields
    db.json               the database at the start of the conversation
    knowledge_base/       the knowledge base, one document per file (<id>.json:
                          {"id", "title", "content"}), indexed in file-name order
    share_tools.py        tools listed to their owner (the agent or the customer)
    task_tools/*.py       discoverable tools, in several modules: named only in the knowledge
                          base, reached through unlock_*_discoverable_tool +
                          call_*_discoverable_tool
    episode.json          the frozen "now", the customer simulator's system prompt, and the
                          integrity fingerprints of the files above

``open_session`` is how a conversation acts on the world: the conversation loop (agent and
customer simulator) and the reference solution both drive a ``Session`` — the engine's two
tool surfaces, with every call recorded to state/calls.jsonl and the end of the conversation
to state/episode.json. The verifier grades those records on fresh engines from
``build_engine``. One construction for the conversation and for grading.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
TASK_DIR = Path(os.environ.get("ERL_TASK_DIR") or RUNTIME_DIR.parent)
STATE_DIR = Path(os.environ.get("ERL_STATE_DIR") or TASK_DIR / "state")

if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from erlbench import DB, Clock, Document, Engine, KnowledgeBase  # noqa: E402
from erlbench.tools import collect_specs  # noqa: E402

# state/ files written during the conversation and read by the verifier.
CALLS_FILE = "calls.jsonl"        # every tool call, in order: {owner, tool, arguments, output, ...}
EPISODE_FILE = "episode.json"     # the end-of-conversation report (termination, ...)
FINAL_DB_FILE = "final_db.json"   # the live database when the conversation ended


def read_json(name: str):
    # Plain json.load: row order is part of the world (lookups return rows in insertion
    # order), so nothing is re-sorted.
    with open(TASK_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def load_episode() -> dict:
    return read_json("episode.json")


def load_documents() -> list:
    """The knowledge base in index order: the documents of knowledge_base/, by file name."""
    kb_dir = TASK_DIR / "knowledge_base"
    docs = []
    for fn in sorted(os.listdir(kb_dir)):
        if fn.endswith(".json"):
            with open(kb_dir / fn, encoding="utf-8") as f:
                d = json.load(f)
            docs.append(Document(id=d["id"], title=d.get("title", d["id"]), content=d["content"]))
    return docs


def task_tool_modules() -> list:
    """The modules of task_tools/, each loaded as its own module. Tool names are unique across
    them and discoverable tools are resolved by name, so their order does not matter."""
    return sorted(fn[:-3] for fn in os.listdir(TASK_DIR / "task_tools")
                  if fn.endswith(".py") and not fn.startswith("."))


def _import(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_WORLD = None


def world() -> tuple[list, KnowledgeBase, dict]:
    """(tool specs, knowledge base, schema): loaded once per process and shared read-only
    by every engine; only the database is fresh per engine."""
    global _WORLD
    if _WORLD is None:
        specs = collect_specs(_import(TASK_DIR / "share_tools.py", "share_tools"), "share")
        for name in task_tool_modules():
            specs += collect_specs(_import(TASK_DIR / "task_tools" / f"{name}.py",
                                           f"task_tools_{name}"), "task")
        _WORLD = (specs, KnowledgeBase(load_documents()), read_json("db_schema.json"))
    return _WORLD


def build_engine(episode: dict | None = None) -> Engine:
    """A fresh engine over a fresh copy of the task's database."""
    episode = episode or load_episode()
    specs, kb, schema = world()
    return Engine(DB.seeded(read_json("db.json")), Clock.from_stamp(episode["frozen_time"]),
                  kb, list(specs), schema=schema)


def tool_fingerprint(engine: Engine) -> str:
    """sha256 of both sides' tool lists (names, descriptions, parameter schemas, order)."""
    blob = json.dumps({"agent": engine.tool_list("agent"), "user": engine.tool_list("user")},
                      sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def kb_fingerprint(engine: Engine) -> str:
    """sha256 of the knowledge base in index order (ids, titles, contents)."""
    blob = json.dumps([[d.id, d.title, d.content] for d in engine.kb.docs], ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def fingerprints(engine: Engine) -> dict:
    return {"tools": tool_fingerprint(engine), "knowledge_base": kb_fingerprint(engine),
            "db": engine.db.hash()}


def check_integrity(engine: Engine, episode: dict) -> None:
    """Refuse a world whose tools, knowledge base or database differ from the fingerprints
    recorded in episode.json."""
    expected = episode.get("integrity") or {}
    bad = {k: (expected.get(k), v) for k, v in fingerprints(engine).items() if expected.get(k) != v}
    if bad:
        raise RuntimeError(f"the task files do not match their integrity fingerprints: {bad}")


def _write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class Session:
    """One conversation's hold on the world: the engine's two tool surfaces — ``tool_list``
    and ``call``, what the conversation loop drives — with every call appended to
    state/calls.jsonl as {owner, tool, arguments, output, ...} before its result is returned,
    and ``end`` recording how the conversation ended. After ``end`` every tool is locked."""

    def __init__(self, engine: Engine, episode: dict):
        self.engine, self.episode = engine, episode
        self.seq, self.ended = 0, False
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self._calls = STATE_DIR / CALLS_FILE
        self._calls.write_text("", encoding="utf-8")

    def tool_list(self, owner: str) -> list:
        return self.engine.tool_list(owner)

    def call(self, owner: str, name: str, arguments: dict | None = None) -> str:
        if self.ended:
            raise RuntimeError("the conversation has ended; tools are locked")
        args = arguments if isinstance(arguments, dict) else {}
        recorded = json.loads(json.dumps(args))
        output = self.engine.call(owner, name, args)
        output = "" if output is None else str(output)
        self.seq += 1
        line = {"seq": self.seq, "owner": owner, "tool": name, "arguments": recorded,
                "output": output, "is_error": output.startswith("Error"), "ts": time.time()}
        with open(self._calls, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return output

    def end(self, report: dict) -> dict:
        if self.ended:
            raise RuntimeError("the conversation has already ended")
        self.ended = True
        live_hash = self.engine.db.hash()
        _write_json(STATE_DIR / FINAL_DB_FILE, self.engine.db.tables)
        record = {"report": report, "num_calls": self.seq, "live_db_hash": live_hash,
                  "ended_at": time.time()}
        _write_json(STATE_DIR / EPISODE_FILE, record)
        return {"num_calls": self.seq, "live_db_hash": live_hash}


def open_session(episode: dict | None = None) -> Session:
    """A fresh world for one conversation, checked against its integrity fingerprints."""
    episode = episode or load_episode()
    engine = build_engine(episode)
    check_integrity(engine, episode)
    return Session(engine, episode)


def world_signature() -> dict:
    """Everything the tool files and the knowledge base define, in order — what an agent and
    a customer can see and call."""
    specs, kb, schema = world()
    probe = Engine(DB(), Clock.from_stamp("1970-01-01"), kb, list(specs), schema=schema)
    return {
        "specs": [[s.name, s.owner, s.rw, s.kind, s.description, s.parameters, s.param_types]
                  for s in specs],
        "docs": [[d.id, d.title, d.content] for d in kb.docs],
        "schema": schema,
        "tool_lists": {o: probe.tool_list(o) for o in ("agent", "user")},
    }


def selfcheck() -> None:
    episode = load_episode()
    engine = build_engine(episode)
    check_integrity(engine, episode)
    print(f"world OK: {episode['task_id']} | {len(engine.registry)} tools, "
          f"{len(engine.kb.docs)} knowledge-base documents, "
          f"{sum(len(r) for r in engine.db.tables.values())} database rows")


if __name__ == "__main__":
    if sys.argv[1:] == ["--signature"]:
        json.dump(world_signature(), sys.stdout, ensure_ascii=False)
    else:
        selfcheck()
