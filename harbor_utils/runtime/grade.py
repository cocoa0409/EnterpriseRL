#!/usr/bin/env python3
"""Verifier: score the conversation by the final state of the database.

    expected  = replay(fresh world, the reference actions in expected.json)
    predicted = replay(fresh world, every tool call recorded during the conversation, in order)
    reward    = 1.0 if predicted == expected and the customer ended the call normally else 0.0

``replay`` re-applies the write calls of a trajectory to a fresh copy of the task's database
(reads cannot change state) and hashes the result, so any sequence of calls that makes the
same changes with the same arguments scores the same. "Ended normally" means the customer
simulator closed the call (USER_STOP) or was transferred to a human (USER_TRANSFER); a
conversation that hit a turn or error limit, or never reported an end, scores 0.

reward.json: ``reward`` (the score) and ``reward_db_match`` (the database match alone).
grade.json: the details. A failure of the verifier itself (e.g. an expected hash that the
world no longer reproduces) raises and writes no reward file, so it surfaces as a verifier
error rather than as a 0.
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
from erlbench import replay  # noqa: E402


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

    target = replay(rt.build_engine(episode_cfg), expected["reference_actions"])
    if target != expected["expected_db_hash"]:
        raise RuntimeError(f"the reference actions now reach {target}, "
                           f"expected {expected['expected_db_hash']}")

    calls = _read_calls()
    trajectory = [{"owner": c["owner"], "tool": c["tool"], "arguments": c["arguments"]}
                  for c in calls]
    predicted = replay(rt.build_engine(episode_cfg), trajectory)

    episode = _read_episode()
    report = (episode or {}).get("report") or {}
    termination = report.get("termination") or "NO_EPISODE_END"
    completed_normally = termination in expected["normal_terminations"]
    db_match = predicted == target
    reward = 1.0 if (db_match and completed_normally) else 0.0

    live_hash = (episode or {}).get("live_db_hash")
    details = {
        "task_id": expected["task_id"],
        "reward": reward,
        "db_match": db_match,
        "termination": termination,
        "completed_normally": completed_normally,
        "expected_db_hash": target,
        "predicted_db_hash": predicted,
        # The live database when the call ended. The score replays the recorded calls; the two
        # differ only when a write was refused live but is valid on replay (e.g. calling a
        # discoverable tool without unlocking it first).
        "live_db_hash": live_hash,
        "live_matches_replay": (live_hash == predicted) if live_hash else None,
        "num_tool_calls": len(calls),
        "num_tool_errors": sum(1 for c in calls if c.get("is_error")),
        "episode_report": report,
    }

    VERIFIER_DIR.mkdir(parents=True, exist_ok=True)
    with open(VERIFIER_DIR / "grade.json", "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    with open(VERIFIER_DIR / "reward.json", "w", encoding="utf-8") as f:
        json.dump({"reward": reward, "reward_db_match": 1.0 if db_match else 0.0}, f)

    print(f"reward={reward} db_match={db_match} termination={termination} "
          f"tool_calls={len(calls)} expected={target[:12]} predicted={predicted[:12]}")


if __name__ == "__main__":
    main()
