"""Scoring: replay a ground-truth trajectory and an agent trajectory on the same
seeded DB and compare the resulting database hashes.

A ground truth is the task's full standard-operation replay and contains BOTH
read and write actions (reads select the seed rows the task depends on; writes
add the new nodes). For the FINAL-STATE HASH only writes matter: reads cannot
touch state (the rw declaration is enforced statically by the validator and at
runtime by a read-only ToolContext), so this replay skips them and the DB
end-state is exactly the effect of the write calls. Read-action fidelity is
checked elsewhere: erlbench.validate replays reads for guard/error detection,
and the verification skill replays them instrumented so every row they touch
enters the task's DB closure. A wrapped call
(``call_agent_discoverable_tool`` / ``call_user_discoverable_tool``) is unwrapped
to the underlying task tool. Because tools are deterministic, any agent path that
performs the same writes with the same arguments reaches the same hash.
"""

from __future__ import annotations

import json
from typing import List, Optional, Tuple

from .engine import BASE_SCHEMAS, Engine


def _resolve(action: dict) -> Tuple[Optional[str], dict]:
    """Reduce a trajectory action to (underlying_tool_name, args) or (None, {})."""
    tool = action.get("tool") or action.get("name")
    args = action.get("arguments", {}) or {}
    if tool in ("call_agent_discoverable_tool", "call_user_discoverable_tool"):
        inner = args.get("tool_name")
        inner_args = args.get("arguments", {})
        if isinstance(inner_args, str):
            try:
                inner_args = json.loads(inner_args) if inner_args else {}
            except json.JSONDecodeError:
                inner_args = {}
        return inner, (inner_args or {})
    if tool in BASE_SCHEMAS:  # KB_search / grep / unlock_* -> no write
        return None, {}
    return tool, (args if isinstance(args, dict) else {})


def replay(engine: Engine, actions: List[dict], strict: bool = False) -> str:
    """Execute the effects of a trajectory on the engine's DB; return its hash.

    strict=False (default): a call that raises is skipped (it made no state change
    live, so it makes none here). strict=True: exceptions propagate — used to
    validate that a ground-truth trajectory is clean.
    """
    for a in actions:
        tool, args = _resolve(a)
        if not tool:
            continue
        spec = engine.registry.get(tool)
        if spec is None or spec.rw != "write":  # reads are stateless by enforcement
            continue
        try:
            spec.func(engine._ctx(), **spec.coerce(args))
        except Exception:  # noqa: BLE001
            if strict:
                raise
    return engine.db.hash()


def score(scenario, task: dict, gt_actions: List[dict], agent_actions: List[dict]) -> dict:
    target = replay(scenario.engine_for(task), gt_actions)
    predicted = replay(scenario.engine_for(task), agent_actions)
    return {
        "match": target == predicted,
        "reward": 1.0 if target == predicted else 0.0,
        "target_hash": target,
        "predicted_hash": predicted,
    }
