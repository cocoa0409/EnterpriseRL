"""The shared database.

A schemaless store: ``{table_name: {row_id: row_dict}}``. The set of tables and
the shape of each row are described by the scenario's ``db_schema.json`` (which
is documentation + light validation, not enforced typing) — this keeps generated
scenarios flexible while the hash below stays reproducible.

The runtime accesses it through five operations — ``find`` and ``fuzzy_find``
(reads; ``fuzzy_find`` compares values after ``normalize`` on both sides),
``insert`` / ``update`` / ``delete`` (writes; ``insert`` is idempotent on the
row id, so replaying the same write twice is a no-op and can never corrupt the
hash) — plus ``hash()`` for scoring.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Dict, List, Optional


def normalize(value) -> str:
    """Canonical form for tolerant matching: casefold, then keep letters and digits
    only. Case, spacing and punctuation vanish, so "Kestrel Grid Networks Inc." and
    "kestrel grid networks inc" compare equal, as do "+86 574 8131 0427" and
    "8657481310427". Applied identically to the stored value and the value looked up;
    nothing looser than whole-string equality after normalisation."""
    return "".join(ch for ch in str(value).casefold() if ch.isalnum())


class DB:
    def __init__(self, tables: Optional[Dict[str, Dict[str, dict]]] = None):
        self.tables: Dict[str, Dict[str, dict]] = tables or {}

    # -- construction ------------------------------------------------------- #
    @classmethod
    def seeded(cls, initial_state: Optional[dict]) -> "DB":
        """Build a fresh DB from a task's ``initial_state`` (may be None)."""
        return cls().overlay(initial_state)

    def overlay(self, initial_state: Optional[dict]) -> "DB":
        """Write ``initial_state`` rows on top of the current tables (row-wise
        last-win, deep-copied) and return self.

        Used to re-assert a task's OWN rows over the shared union DB: if another
        task happens to reuse a row id, the union merge is last-win and could have
        shadowed this task's version, so overlaying the task's initial_state again
        guarantees the rollout sees exactly the rows the task depends on."""
        if initial_state:
            for table, rows in initial_state.items():
                t = self.tables.setdefault(table, {})
                for row_id, row in (rows or {}).items():
                    t[row_id] = deepcopy(row)
        return self

    # -- reads -------------------------------------------------------------- #
    def find(self, table: str, **match) -> List[dict]:
        out = []
        for row in self.tables.get(table, {}).values():
            if all(str(row.get(k)) == str(v) for k, v in match.items()):
                out.append(row)
        return out

    def fuzzy_find(self, table: str, **match) -> List[dict]:
        """Like ``find`` but both sides pass through ``normalize`` first — for criteria
        the caller states in speech (names, phone numbers, emails), never for ids."""
        out = []
        for row in self.tables.get(table, {}).values():
            if all(normalize(row.get(k)) == normalize(v) for k, v in match.items()):
                out.append(row)
        return out

    # -- writes ------------------------------------------------------------- #
    def insert(self, table: str, row_id: str, row: dict) -> bool:
        """Insert a row. Idempotent: returns False (no-op) if the id already exists."""
        t = self.tables.setdefault(table, {})
        if row_id in t:
            return False
        t[row_id] = dict(row)
        return True

    def update(self, table: str, row_id: str, **fields) -> bool:
        t = self.tables.get(table, {})
        if row_id not in t:
            return False
        t[row_id].update(fields)
        return True

    def delete(self, table: str, row_id: str) -> bool:
        """Delete a row. Returns False (no-op) if it does not exist."""
        t = self.tables.get(table, {})
        if row_id not in t:
            return False
        del t[row_id]
        return True

    # -- identity ----------------------------------------------------------- #
    def hash(self) -> str:
        blob = json.dumps(self.tables, sort_keys=True, default=str, ensure_ascii=False)
        return hashlib.sha256(blob.encode()).hexdigest()
