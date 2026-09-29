#!/usr/bin/env python3
"""Verifier: score the conversation by the order of its tool calls and the final state of
the database.

    order_ok  = check_order(required_order, the recorded calls)
    expected  = replay_calls(fresh world, reference_calls)
    predicted = replay_calls(fresh world, the recorded calls)        -- only when order_ok
    reward    = 1.0 if order_ok and predicted == expected and the call ended normally else 0.0

expected.json holds ``required_order`` (pairs of tool names: the first must be called before
the second), ``reference_calls`` (the reference solution as tool calls, the list
solution/oracle_calls.json runs), ``expected_db_hash`` (the hash they reach) and
``normal_terminations``.

The order check looks at the first call of each tool, whichever side made it and whatever its
arguments or outcome; a conversation that fails it scores 0 and is not replayed.
``replay_calls`` re-runs tool calls, verbatim and in order, through the engine's own routing
on a fresh copy of the task's world, so what the live run refused (wrong owner, tool not
unlocked or not handed over, bad arguments) is refused again and changes nothing. "Ended
normally" means the customer closed the call (USER_STOP) or was transferred to a human
(USER_TRANSFER); a conversation that hit a turn or error limit, or never reported an end,
scores 0.

reward.json: ``reward``, ``reward_order`` (the order check alone) and ``reward_db_match``
(the database match; 0 when the order check failed). grade.json: the details. A failure of
the verifier itself raises and writes no reward file, so it surfaces as a verifier error
rather than as a 0.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TESTS_DIR = Path(os.environ.get("ERL_TESTS_DIR") or Path(__file__).resolve().parent)
VERIFIER_DIR = Path(os.environ.get("ERL_VERIFIER_DIR") or "/logs/verifier")
TASK_DIR = Path(os.environ.get("ERL_TASK_DIR") or "/opt/task")
sys.path.insert(0, str(TASK_DIR / "runtime"))

import runtime as rt  # noqa: E402
from erlbench import check_order, replay_calls  # noqa: E402


def _read_calls() -> list:
    path = rt.STATE_DIR / rt.CALLS_FILE
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _read_episode() -> dict | None:
    path = rt.STATE_DIR / rt.EPISODE_FILE
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    with open(TESTS_DIR / "expected.json", encoding="utf-8") as f:
        expected = json.load(f)
    episode_cfg = rt.load_episode()
    if expected["task_id"] != episode_cfg["task_id"]:
        raise RuntimeError(f"tests/ belong to {expected['task_id']}, the environment to "
                           f"{episode_cfg['task_id']}")
    rt.check_integrity(rt.build_engine(episode_cfg), episode_cfg)

    order = expected["required_order"]
    if check_order(order, expected["reference_calls"]):
        raise RuntimeError("the reference calls violate the required order")
    target = replay_calls(rt.build_engine(episode_cfg), expected["reference_calls"])
    if target != expected["expected_db_hash"]:
        raise RuntimeError(f"the reference calls now reach {target}, "
                           f"expected {expected['expected_db_hash']}")

    calls = _read_calls()
    trajectory = [{"owner": c["owner"], "tool": c["tool"], "arguments": c["arguments"]}
                  for c in calls]
    violations = check_order(order, trajectory)
    order_ok = not violations
    predicted = replay_calls(rt.build_engine(episode_cfg), trajectory) if order_ok else None
    db_match = (predicted == target) if order_ok else None

    episode = _read_episode()
    report = (episode or {}).get("report") or {}
    termination = report.get("termination") or "NO_EPISODE_END"
    completed_normally = termination in expected["normal_terminations"]
    reward = 1.0 if (order_ok and db_match and completed_normally) else 0.0

    live_hash = (episode or {}).get("live_db_hash")
    details = {
        "task_id": expected["task_id"],
        "reward": reward,
        "order_ok": order_ok,
        "order_violations": violations,
        "required_order": order,
        "db_match": db_match,
        "termination": termination,
        "completed_normally": completed_normally,
        "expected_db_hash": target,
        "predicted_db_hash": predicted,
        # The live database when the call ended; equal to the replay whenever the world
        # reproduced the session.
        "live_db_hash": live_hash,
        "live_matches_replay": (live_hash == predicted) if (live_hash and predicted) else None,
        "num_tool_calls": len(calls),
        "num_tool_errors": sum(1 for c in calls if c.get("is_error")),
        "episode_report": report,
    }

    VERIFIER_DIR.mkdir(parents=True, exist_ok=True)
    with open(VERIFIER_DIR / "grade.json", "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    with open(VERIFIER_DIR / "reward.json", "w", encoding="utf-8") as f:
        json.dump({"reward": reward, "reward_order": 1.0 if order_ok else 0.0,
                   "reward_db_match": 1.0 if db_match else 0.0}, f)

    print(f"reward={reward} order_ok={order_ok} db_match={db_match} termination={termination} "
          f"tool_calls={len(calls)} expected={target[:12]} "
          f"predicted={(predicted or 'not replayed')[:12]}")


if __name__ == "__main__":
    main()
