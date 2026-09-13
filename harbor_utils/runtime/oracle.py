#!/usr/bin/env python3
"""Reference solution: the task's reference actions, executed live.

``oracle_calls.json`` lists the reference solution as tool calls, each by its owner (the agent
or the customer), through the same ``Session`` the conversation loop drives — permissions and
unlock/call steps included, every call recorded. Every call must succeed; then the
conversation is closed as a normal end of call, and the verifier must score 1.0.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK_DIR = Path(os.environ.get("ERL_TASK_DIR") or "/opt/task")
sys.path.insert(0, str(TASK_DIR / "runtime"))

import runtime as rt  # noqa: E402


def main() -> None:
    with open(HERE / "oracle_calls.json", encoding="utf-8") as f:
        plan = json.load(f)
    session = rt.open_session()
    for owner in ("agent", "user"):
        print(f"{owner} tools: {len(session.tool_list(owner))}")
    for i, call in enumerate(plan["calls"], 1):
        output = session.call(call["owner"], call["tool"], call["arguments"])
        print(f"[{i}/{len(plan['calls'])}] {call['owner']} {call['tool']} -> {output[:160]!r}")
        if output.startswith("Error"):
            raise SystemExit(f"reference call {i} ({call['owner']} {call['tool']}) failed: {output}")
    end = session.end({"termination": plan["termination"], "completed_normally": True,
                       "harness": {"name": "oracle", "reference_calls": len(plan["calls"])}})
    print(f"conversation closed: {end}")


if __name__ == "__main__":
    sys.exit(main())
