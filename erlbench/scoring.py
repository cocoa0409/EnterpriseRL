"""Scoring: replay a ground-truth trajectory and an agent trajectory on the same
seeded DB and compare the resulting database hashes — after checking the
conversation's tool calls against the task's required order.

Two replays, for two kinds of input.

``replay_calls`` — a RECORDED CONVERSATION (untrusted). Every call is re-run
verbatim, in order, through ``Engine.call`` — the same routing the live session
drove — so the replay enforces exactly what the live run enforced: who may call
what, the unlock / hand-over state a discoverable tool needs before it can be
called, JSON argument parsing and argument validation. A call the live run
refused is refused again and lands nothing; the replay reproduces the session,
and its final hash is the session's. Reads run too (they cannot change state; a
read-only ToolContext enforces the rw declaration) and the base tools run too:
an unlock is engine state the later calls depend on.

``replay`` — the GROUND TRUTH (trusted). A task's ``evaluation_criteria`` is the
task's full standard-operation replay in its authored form: bare tool names,
no unlock steps, both read and write actions (reads select the seed rows the
task depends on; writes add the new nodes). For the FINAL-STATE HASH only writes
matter, so this replay applies the write effects directly and skips the rest.
It bypasses the engine's routing on purpose and must never score a recorded
conversation. Read-action fidelity is checked elsewhere: erlbench.validate
replays reads for guard/error detection, and the verification skill replays
them instrumented so every row they touch enters the task's DB closure. A
wrapped call (``call_agent_discoverable_tool`` / ``call_user_discoverable_tool``)
is unwrapped to the underlying task tool.

The ORDER check. A task's required order is a list of tool pairs (``before``,
``after``); ``check_order`` tests a conversation against it by the FIRST call of
each tool, whichever side made it and whatever its arguments or outcome (an
attempt is a call). It runs before the replay: only a conversation in the right
order has its final state compared. Where the pairs come from is the loader's
business (``erlbench.loader.required_order``), not this module's.

Because tools are deterministic, any conversation that performs the same writes
with the same arguments — through the routing, in the required order — reaches
the ground truth's hash.
"""

from __future__ import annotations

import json
from typing import List, Optional, Tuple

from .engine import BASE_SCHEMAS, Engine


def _resolve(action: dict) -> Tuple[Optional[str], dict]:
    """Reduce a trajectory action to (underlying_tool_name, args) or (None, {})."""
    tool = action.get("tool") or action.get("name")
    args = action.get("arguments", {}) or {}
    if not isinstance(args, dict):
        args = {}
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
    return tool, args


def replay(engine: Engine, actions: List[dict], strict: bool = False) -> str:
    """Apply the write effects of a TRUSTED ground truth to the engine's DB; return its hash.

    Bypasses the engine's routing (permissions, unlock state, argument validation):
    only for a task's reference actions, never for a recorded conversation — use
    ``replay_calls`` for that.

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


def replay_calls(engine: Engine, calls: List[dict]) -> str:
    """Re-run a RECORDED CONVERSATION's tool calls on the engine; return its DB hash.

    ``calls`` is the session's record, ``[{owner, tool, arguments}, ...]`` in call order,
    exactly as each call was issued: the wrapper and unlock calls as such, ``arguments`` as
    the dict the caller passed (a wrapped call's inner arguments as the JSON string it gave).
    Every call goes through ``Engine.call`` — the routing the live session used — on a fresh
    engine, so a call refused live (wrong owner, tool not unlocked or not handed over, bad
    or missing arguments) is refused here and changes nothing. An exception propagates: the
    live session would have raised on that call too, so the record does not reproduce.
    """
    for c in calls:
        owner = c.get("owner") or "agent"
        tool = c.get("tool") or c.get("name")
        args = c.get("arguments") or {}
        engine.call(owner, tool, args if isinstance(args, dict) else {})
    return engine.db.hash()


def first_calls(calls: List[dict]) -> dict:
    """The index of each tool's first call in a conversation, by underlying tool name: a
    wrapped call counts for the tool it names whichever side issued it, a bare name for
    itself, the base tools (searches, unlocks) for nothing. Arguments and outcome are not
    looked at — an attempt is a call."""
    first: dict = {}
    for i, c in enumerate(calls):
        tool, _ = _resolve(c)
        if tool and tool not in first:
            first[tool] = i
    return first


def check_order(order: List[dict], calls: List[dict]) -> List[dict]:
    """The constraints of ``order`` that ``calls`` violate: for each (before, after), once
    ``after`` is called at all, ``before`` must have been called first — by either side,
    whatever the arguments or the outcome. A constraint whose ``after`` is never called
    binds nothing. Each violation: ``{"before", "after", "before_at": index or None,
    "after_at": index}``."""
    first = first_calls(calls)
    violations = []
    for o in order:
        after_at = first.get(o["after"])
        if after_at is None:
            continue
        before_at = first.get(o["before"])
        if before_at is None or before_at > after_at:
            violations.append({"before": o["before"], "after": o["after"],
                               "before_at": before_at, "after_at": after_at})
    return violations


def score(scenario, task: dict, gt_actions: List[dict], agent_calls: List[dict],
          order: List[dict] = ()) -> dict:
    """Ground truth (its write effects) against a recorded conversation: the order check
    first, then — only when it passes — the conversation re-run through the routing."""
    target = replay(scenario.engine_for(task), gt_actions)
    violations = check_order(order, agent_calls)
    predicted = None if violations else replay_calls(scenario.engine_for(task), agent_calls)
    match = predicted == target
    return {
        "match": match,
        "reward": 1.0 if match else 0.0,
        "order_ok": not violations,
        "order_violations": violations,
        "target_hash": target,
        "predicted_hash": predicted,
    }
