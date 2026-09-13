"""Shared command-line helpers for difficulty and per-task gate runs."""

import glob
import os


def _task_sort_key(path):
    """Keep task order numeric (0, 1, ..., 10), not lexical (0, 1, 10, 2)."""
    stem = os.path.splitext(os.path.basename(path))[0]
    return (0, int(stem)) if stem.isdigit() else (1, stem)


def task_index(path):
    """Return the numeric task index, or None for a non-standard filename."""
    stem = os.path.splitext(os.path.basename(path))[0]
    return int(stem) if stem.isdigit() else None


def split_task_flag(argv):
    """Return (positional_args, task_selector).

    ``--task N`` and ``--task=N`` are accepted.  Other flags are preserved in
    positional_args so legacy options such as replay's ``--check`` keep their
    existing behavior.
    """
    positional = []
    selector = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--task":
            if i + 1 >= len(argv):
                raise SystemExit("--task requires a task index or tasks/<index>.json")
            selector = argv[i + 1]
            i += 2
            continue
        if arg.startswith("--task="):
            selector = arg.split("=", 1)[1]
            if not selector:
                raise SystemExit("--task requires a task index or tasks/<index>.json")
            i += 1
            continue
        positional.append(arg)
        i += 1
    return positional, selector


def select_task_paths(target, selector=None):
    """List task JSON paths, optionally restricted to one task.

    A selector may be a decimal index (``0``) or a path.  The path form is
    resolved relative to the difficulty directory unless it is absolute.
    """
    all_paths = sorted(glob.glob(os.path.join(target, "tasks", "*.json")), key=_task_sort_key)
    if selector is None:
        return all_paths
    raw = str(selector)
    if raw.isdigit():
        path = os.path.join(target, "tasks", f"{int(raw)}.json")
    else:
        path = raw if os.path.isabs(raw) else os.path.join(target, raw)
    path = os.path.abspath(path)
    if path not in {os.path.abspath(p) for p in all_paths}:
        raise SystemExit(f"task selector {selector!r} does not resolve to a task under {target}/tasks/")
    return [path]


def paths_through_task(target, selector):
    """Return completed task paths through the selected index, for overlap checks."""
    all_paths = select_task_paths(target)
    selected = select_task_paths(target, selector)
    if selector is None or not selected:
        return all_paths
    idx = task_index(selected[0])
    if idx is None:
        return selected
    present = {task_index(p) for p in all_paths if task_index(p) is not None}
    missing = sorted(set(range(idx + 1)) - present)
    if missing:
        raise SystemExit(f"cannot validate task {idx}: earlier task file(s) missing: "
                         + ", ".join(f"tasks/{i}.json" for i in missing))
    return [p for p in all_paths if task_index(p) is not None and task_index(p) <= idx]
