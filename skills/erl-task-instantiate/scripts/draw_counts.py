"""Draw each task's counts by code: the size of its problem tree and the number of factors of
each of its computations.

Told to draw a count "uniformly at random", the instantiating agent does not draw: it settles on
the floor (measured on two generated scenarios: every tree at exactly the minimum number of
prerequisite problems, 79 of 80 computations at exactly the minimum number of factors). So the
draw is made here, by `random.randint`, and the gates recompute it:

    prerequisite_problems = random.randint(MIN_PREREQ_PROBLEMS, MAX_PREREQ_PROBLEMS)   # one draw per task
    factor_counts = [random.randint(MIN_FACTORS_PER_COMP, MAX_FACTORS_PER_COMP)
                     for _ in range(prerequisite_problems + 1)]                         # one draw per problem of the tree

The generator is seeded from "<scenario>/<difficulty>/<task index>" (sha256): <scenario> is the name
of the directory holding blueprint/ (found by walking up from the target, exactly as the gates locate
the scenario root), <difficulty> is the target directory's own name. The script opens no file, so the
same difficulty gives the same numbers from any path under its scenario, for anyone, on any re-run;
it refuses a target with no blueprint/ ancestor rather than silently keying on another name. The
printed `key` is the proof: it reads <scenario>/<difficulty>/<task index>. So the draw is uniform
over tasks and scenarios and recomputable by the gates without any recorded field: check_extended and check_solvability require the tree to have exactly
`prerequisite_problems` prerequisite problems, and check_compute requires the factor counts of the
task's computations, as a multiset, to equal `factor_counts` (which problem takes which count is the
author's choice). The draw cannot be re-rolled — the same task always draws the same numbers — and
is never adjusted to a design; the design is adjusted to the draw.

Usage (repo root):
  .venv/bin/python skills/erl-task-instantiate/scripts/draw_counts.py env/<scenario>/tasks/<difficulty> --task N
  .venv/bin/python skills/erl-task-instantiate/scripts/draw_counts.py env/<scenario>/tasks/<difficulty> --tasks M   # tasks 0..M-1
"""
import hashlib
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_utils import split_task_flag
from prereq_utils import MAX_PREREQ_PROBLEMS, MIN_PREREQ_PROBLEMS

MIN_FACTORS_PER_COMP = 4   # every computed value rests on 4 to 6 declared, load-bearing factors ...
MAX_FACTORS_PER_COMP = 6   # ... exactly the count draw_for_task draws for that problem (check_compute recomputes it)


def scenario_root(start):
    """The nearest ancestor holding blueprint/ — the scenario directory — as the gates locate it."""
    path = os.path.abspath(str(start).rstrip("/"))
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, "blueprint")):
            return path
        path = os.path.dirname(path)
    raise SystemExit(f"cannot find the scenario root (a directory holding blueprint/) above {start}: run against "
                     "env/<scenario>/tasks/<difficulty>")


def draw_key(target, task_index):
    """'<scenario>/<difficulty>/<task index>': the scenario directory's name, the target directory's own
    name and the task index — the same from any path under the scenario."""
    diff = os.path.abspath(str(target).rstrip("/"))
    return f"{os.path.basename(scenario_root(diff))}/{os.path.basename(diff)}/{int(task_index)}"


def draw_for_task(target, task_index):
    """The counts drawn for one task: prerequisite problems (root not counted), problems (root included)
    and one factor count per problem, in draw order."""
    key = draw_key(target, task_index)
    rng = random.Random(int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big"))
    n_prereq = rng.randint(MIN_PREREQ_PROBLEMS, MAX_PREREQ_PROBLEMS)
    factor_counts = [rng.randint(MIN_FACTORS_PER_COMP, MAX_FACTORS_PER_COMP) for _ in range(n_prereq + 1)]
    return {"task": int(task_index), "key": key, "prerequisite_problems": n_prereq,
            "problems": n_prereq + 1, "factor_counts": factor_counts}


def main():
    argv = sys.argv[1:]
    n_tasks = None
    rest = []
    i = 0
    while i < len(argv):
        if argv[i] == "--tasks" and i + 1 < len(argv):
            n_tasks = argv[i + 1]; i += 2; continue
        if argv[i].startswith("--tasks="):
            n_tasks = argv[i].split("=", 1)[1]; i += 1; continue
        rest.append(argv[i]); i += 1
    pos, selector = split_task_flag(rest)
    if len(pos) != 1 or (selector is None and n_tasks is None):
        print("usage: draw_counts.py env/<scenario>/tasks/<difficulty> (--task N | --tasks M)")
        sys.exit(2)
    target = pos[0].rstrip("/")
    if selector is not None:
        m = re.match(r"\d+", os.path.basename(str(selector)))   # 0 | tasks/0.json | 0.masked.json
        if not m:
            raise SystemExit(f"--task expects a task index, got {selector!r}")
        indices = [int(m.group(0))]
    else:
        if not str(n_tasks).isdigit() or int(n_tasks) < 1:
            raise SystemExit(f"--tasks expects a positive task count, got {n_tasks!r}")
        indices = list(range(int(n_tasks)))
    for idx in indices:
        print(json.dumps(draw_for_task(target, idx)))


if __name__ == "__main__":
    main()
