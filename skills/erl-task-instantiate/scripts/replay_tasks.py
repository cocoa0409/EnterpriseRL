"""REPLAY gate: determinism + soundness of each task's gold, in the layout
(env/<scenario>/tasks/<difficulty>/). Self-contained: imports the blueprint share
tools + this difficulty's task_tools.py, seeds each task's own initial_state, and:

  - replays the gold WRITES twice -> the two DB hashes must be identical (determinism);
  - replays reads+writes instrumented (a TrackingDB marks every PRE-EXISTING row a
    ctx.find READ matches, or a write mutates) -> no tool may raise or return "Error:";
  - the gold must be non-vacuous -> its write hash differs from the empty-trajectory hash;
  - extracts the DB closure (rows any action reads/writes + rows named in gold args) and
    writes db_closure + db_closure_matches_initial_state back per task. A history-
    reconciliation task MUST read its history via find tools so those rows enter the closure;
  - every initial_state row id is an opaque uuid4 (see UUID4_RE) -> readable ids collide in
    the rollout's cross-task union DB;
  - no dangling foreign key: every non-PK *_id value resolves to a seeded row in its parent
    table (the table whose PK bears that field name).

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/replay_tasks.py env/<scenario>/tasks/<difficulty> [--check] [--task N]
"""
import glob
import importlib.util
import json
import os
import re
import sys
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import select_task_paths, split_task_flag

# Seed row ids must be opaque uuid4: the rollout merges every task's initial_state into
# one union DB (row-wise last-win), so a readable id two tasks both mint collides there.
UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
def pk_fk_map(db_schema):
    """Per table: its primary key (the first 'id' field) and its foreign keys (every later
    'id' field). A FK's parent is resolved by NAME — the table whose PK carries that same
    field name — not from the field's prose, which is free text and unenforceable."""
    ids_of, pk, owner = {}, {}, {}
    for t, fields in (db_schema or {}).items():
        if not isinstance(fields, dict):
            continue
        ids = [f for f, m in fields.items() if isinstance(m, dict) and m.get("type") == "id"]
        if not ids:
            continue
        ids_of[t], pk[t] = ids, ids[0]
        owner[ids[0]] = t
    fk = {t: [(f, owner[f]) for f in ids[1:] if f in owner] for t, ids in ids_of.items()}
    return pk, fk


def _find_repo_root(start):
    p = os.path.abspath(start)
    while p != "/":
        if os.path.isdir(os.path.join(p, "erlbench")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def _find_scenario_root(start):
    p = os.path.abspath(start)
    while p != "/":
        if os.path.isdir(os.path.join(p, "blueprint")):
            return p
        p = os.path.dirname(p)
    raise SystemExit(f"cannot find scenario root (blueprint/) above {start}")


def _import(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TrackingDB:
    """DB surface used by ToolContext + touch tracking of PRE-EXISTING rows."""

    def __init__(self, tables, preexisting):
        self.tables = tables
        self._pre = preexisting
        self.touched = set()

    def _mark(self, table, rid):
        if (table, rid) in self._pre:
            self.touched.add((table, rid))

    def find(self, table, **match):
        out = []
        for rid, row in self.tables.get(table, {}).items():
            if all(str(row.get(k)) == str(v) for k, v in match.items()):
                self._mark(table, rid)
                out.append(row)
        return out

    def insert(self, table, row_id, row):
        if row_id in self.tables.get(table, {}):
            self._mark(table, row_id)
            return False
        self.tables.setdefault(table, {})[row_id] = row
        return True

    def update(self, table, row_id, **fields):
        if row_id in self.tables.get(table, {}):
            self._mark(table, row_id)
            self.tables[table][row_id].update(fields)
            return True
        return False

    def delete(self, table, row_id):
        if row_id in self.tables.get(table, {}):
            self._mark(table, row_id)
            del self.tables[table][row_id]
            return True
        return False


def main():
    pos, task_selector = split_task_flag(sys.argv[1:])
    argv = [a for a in pos if a != "--check"]
    write_back = "--check" not in sys.argv
    if not argv:
        print("usage: replay_tasks.py env/<scenario>/tasks/<difficulty> [--check] [--task N]")
        sys.exit(2)
    target = argv[0].rstrip("/")
    sys.path.insert(0, _find_repo_root(target))
    from erlbench.tools import collect_specs, ToolContext
    from erlbench.db import DB
    from erlbench.determinism import Clock
    from erlbench.scoring import _resolve

    scen = _find_scenario_root(target)
    bp = os.path.join(scen, "blueprint")
    db_schema = json.load(open(os.path.join(bp, "db_schema.json")))
    FK = pk_fk_map(db_schema)[1]

    specs = {}
    for s in collect_specs(_import(os.path.join(bp, "share_tools.py"), "_share_bp"), "share"):
        specs[s.name] = s
    tt = os.path.join(target, "task_tools.py")
    if os.path.exists(tt):
        for s in collect_specs(_import(tt, "_task_tools"), "task"):
            specs[s.name] = s

    def replay_writes(initial, clock, actions):
        db = DB.seeded(initial)
        for a in actions:
            tool, args = _resolve(a)
            if not tool:
                continue
            spec = specs.get(tool)
            if spec is None or spec.rw != "write":
                continue
            try:
                spec.func(ToolContext(db, clock, db_schema, writable=True), **spec.coerce(args))
            except Exception:  # noqa: BLE001
                pass
        return db.hash()

    def arg_ref_rows(actions, tables):
        idx = {}
        for t, rows in tables.items():
            for rid in rows:
                idx.setdefault(rid, set()).add(t)
        refs = set()

        def scan(v):
            if isinstance(v, str):
                for t in idx.get(v, ()):
                    refs.add((t, v))
            elif isinstance(v, dict):
                for x in v.values():
                    scan(x)
            elif isinstance(v, list):
                for x in v:
                    scan(x)
        for a in actions:
            _, args = _resolve(a)
            scan(args)
        return refs

    def instrumented(initial, clock, actions):
        tables = {t: {rid: deepcopy(r) for rid, r in rows.items()} for t, rows in (initial or {}).items()}
        pre = {(t, rid) for t, rows in tables.items() for rid in rows}
        db = TrackingDB(tables, pre)
        errs = []
        for i, a in enumerate(actions):
            tool, args = _resolve(a)
            if not tool:
                continue
            spec = specs.get(tool)
            if spec is None:
                continue
            ctx = ToolContext(db, clock, db_schema, writable=(spec.rw == "write"))
            try:
                out = str(spec.func(ctx, **spec.coerce(args)))
            except Exception as e:  # noqa: BLE001
                errs.append(f"action #{i} ({tool}) raised: {e}"); out = ""
            if out.startswith("Error"):
                errs.append(f"action #{i} ({tool}) returned soft error: {out[:120]}")
        return db.touched, pre, errs

    task_paths = select_task_paths(target, task_selector)
    if not task_paths:
        raise SystemExit(f"no task json under {target}/tasks/")

    mode_label = f", selected_task={task_selector}" if task_selector is not None else ""
    print(f"🔎 REPLAY gate  ({len(task_paths)} tasks{mode_label})")
    print(f"{'task':28} {'acts':>4} {'det':>4} {'nonvac':>7} {'errs':>4} {'clos':>5} {'init':>5} {'match':>6}")
    fails, mismatched = [], []
    for tp in task_paths:
        tid = os.path.basename(tp)
        task = json.loads(open(tp).read())
        actions = task.get("evaluation_criteria") or []
        ft = task.get("frozen_time")
        if not ft:
            fails.append(f"{tid}: missing frozen_time"); continue
        clock = Clock.from_stamp(ft)
        initial = task.get("initial_state") or {}

        # row ids must be opaque uuid4 (see UUID4_RE) — report per table, capped
        bad_ids = {}
        for tbl, rows in initial.items():
            if not isinstance(rows, dict):
                continue
            off = [rid for rid in rows if not UUID4_RE.match(str(rid))]
            if off:
                bad_ids[tbl] = off
        if bad_ids:
            n = sum(len(v) for v in bad_ids.values())
            shown = "; ".join(f"{t}: {v[:3]}" for t, v in sorted(bad_ids.items())[:3])
            fails.append(f"{tid}: {n} initial_state row id(s) not uuid4 ({shown}) — "
                         "mint every seed row id with str(uuid.uuid4())")

        # no dangling parent: every FK value must exist as a row id in its parent table
        seeded_pks = {t: set(rows) for t, rows in initial.items() if isinstance(rows, dict)}
        dangling = []
        for tbl, rows in initial.items():
            if not isinstance(rows, dict):
                continue
            for fld, parent in FK.get(tbl, []):
                for rid, row in rows.items():
                    val = (row or {}).get(fld)
                    if val is None:
                        continue
                    if val not in seeded_pks.get(parent, ()):
                        dangling.append(f"{tbl}.{fld}={val} (no such row in {parent})")
        if dangling:
            fails.append(f"{tid}: {len(dangling)} dangling foreign key(s): {dangling[:3]} — "
                         f"seed the parent row too; an agent that follows the reference finds nothing")

        h1 = replay_writes(initial, clock, actions)
        h2 = replay_writes(initial, clock, actions)
        det = (h1 == h2)
        empty = DB.seeded(initial).hash()
        nonvac = (h1 != empty)
        touched, pre, errs = instrumented(initial, clock, actions)
        pre_tables = {t: {rid: 1 for (t2, rid) in pre if t2 == t} for t in {t for t, _ in pre}}
        closure = touched | arg_ref_rows(actions, pre_tables)
        init_rows = set(pre)
        extra = closure - init_rows
        missing = init_rows - closure
        match = (not extra) and (not missing)
        if not det:
            fails.append(f"{tid}: non-deterministic gold (hash differs across replays)")
        if not nonvac:
            fails.append(f"{tid}: gold produced no DB change (do-nothing agent would tie)")
        for e in errs:
            fails.append(f"{tid}: {e}")
        if extra:
            fails.append(f"{tid}: closure references rows outside initial_state: {sorted(extra)[:5]}")
        if not match:
            mismatched.append(tid + (f" (missing {len(missing)})" if missing else ""))
        print(f"{tid:28} {len(actions):>4} {str(det):>4} {str(nonvac):>7} {len(errs):>4} "
              f"{len(closure):>5} {len(init_rows):>5} {str(match):>6}")

        if write_back:
            sub = {}
            for t, rid in closure:
                if t in initial and rid in initial[t]:
                    sub.setdefault(t, {})[rid] = deepcopy(initial[t][rid])
            raw = json.loads(open(tp).read())
            raw.pop("db_closure", None); raw.pop("db_closure_matches_initial_state", None)
            rebuilt = {}
            for k, v in raw.items():
                rebuilt[k] = v
                if k == "initial_state":
                    rebuilt["db_closure"] = sub
                    rebuilt["db_closure_matches_initial_state"] = match
            open(tp, "w").write(json.dumps(rebuilt, ensure_ascii=False, indent=4) + "\n")

    if mismatched:
        print("  MISMATCH (set initial_state := db_closure, drop noise rows, re-run): " + ", ".join(mismatched[:20]))
    ok = not fails and not mismatched
    if fails:
        print("\n  [FAIL]")
        for f in fails[:40]:
            print("   -", f)
    print("REPLAY OK" if ok else "REPLAY NOT OK")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
