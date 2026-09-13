"""Determinism primitives.

Every generated tool must be a pure function of its arguments and the seed DB.
The only two sources of non-determinism in a customer-service simulation are the
clock and generated identifiers; both are pinned here.

  - The clock is frozen to a fixed timestamp chosen when the scenario is built.
    Tools must read the time via ``ctx.now()`` (slice ``ctx.now()[:10]`` for the
    date part) and never call the real clock.
  - Identifiers are content hashes: ``make_id(prefix, *parts)`` returns the same
    id for the same parts, so a ground-truth replay and any correct agent write
    the byte-identical row. Numbers are normalized (floats to 2 decimals) so that
    ``100`` and ``100.0`` can never diverge into two different ids.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


def normalize(value) -> str:
    """Canonical string form of a scalar for use inside an id seed.

    ALL numbers (int or float alike) are pinned to ``f"{v:.2f}"`` — the same
    convention the format spec applies to both types, so the same value always
    produces the same seed no matter which numeric type a caller passed
    (an LLM sending 50 vs 50.0, or a task author writing either in JSON).
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    if value is None:
        return ""
    return str(value)


def make_id(prefix: str, *parts, length: int = 12) -> str:
    """Deterministic id: ``prefix + sha256(prefix:part1:part2:...)[:length]``.

    The prefix is part of the seed so two tables can never collide. Pass the
    minimal set of arguments that make the row unique for its purpose.
    """
    seed = ":".join([prefix, *(normalize(p) for p in parts)])
    return f"{prefix}{hashlib.sha256(seed.encode()).hexdigest()[:length]}"


@dataclass
class Clock:
    """A frozen clock: the task's frozen_time string, verbatim."""

    stamp: str  # e.g. "2025-11-14 03:40:00 EST" (starts with YYYY-MM-DD)

    @classmethod
    def from_stamp(cls, stamp: str) -> "Clock":
        return cls(stamp=stamp)

    def now(self) -> str:
        return self.stamp

