"""CLI: run agent <-> user-simulator rollouts over erlbench scenarios and score them.

Load one or more scenario directories, pick tasks, run ``--num-trials`` rollouts per
task concurrently, score each by replaying its collected trajectory against the task's
``evaluation_criteria`` (DB-terminal-state hash match, gated on a normal end of call),
and write ``data/simulations/<save_to>/results.json`` plus a pass@1 summary.

Each scenario's world — its merged DB, its knowledge base, and the KB's BM25 retrieval
index — is loaded and built EXACTLY ONCE (see ``get_world``) and shared across every
task, trial, and repeat reference, so nothing is read from disk or re-indexed twice.

Run it as ``python -m rollout ...`` from the repo root (see ``run.sh``).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

# Make `import erlbench` / `import rollout` resolve when launched oddly.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from erlbench import load_scenario, replay  # noqa: E402
from erlbench.loader import Scenario  # noqa: E402
from erlbench.db import DB  # noqa: E402
from erlbench.determinism import Clock  # noqa: E402
from erlbench.engine import Engine  # noqa: E402
from erlbench.kb import KnowledgeBase  # noqa: E402

from .llm import LLMClient, args_for, DEFAULT_LLM_MAX_TOKENS  # noqa: E402
from .orchestrator import Orchestrator  # noqa: E402
from .prompts import build_agent_prompt, build_user_prompt  # noqa: E402


# --------------------------------------------------------------------------- #
# Scenario "world": one shared DB / KB / toolset spanning EVERY difficulty,
# BUILT ONCE PER SCENARIO AND CACHED (see get_world).
# --------------------------------------------------------------------------- #
# A task rollout runs against the whole scenario, not just its own slice:
#   - tools  : share tools + EVERY difficulty's task tools (merged by the loader)
#   - KB     : EVERY difficulty's documents, with the BM25 retrieval index built ONCE
#   - DB     : the UNION of EVERY task's initial_state (merged here, once)
# Tasks are disjoint by construction (unique uuid seed ids; the validator forbids a
# phone/email/name shared across tasks), so the union is a plain row-wise merge and a
# task's specific-id lookups still resolve only its own rows — the rest are realistic
# distractors on one shared world DB.
#
# The DB / KB / index are the cache: building them (reading the scenario from disk,
# importing its tool modules, merging the DB, indexing the KB) happens EXACTLY ONCE
# per scenario and is then reused by every task and trial. Only the DB is deep-copied
# per rollout, for isolation between concurrent conversations.

class ScenarioWorld:
    def __init__(self, sc: Scenario):
        self.sc = sc
        self.scenario_id = sc.name                      # basename of env/<scenario>/
        self.schema = sc.db_schema
        self.specs = list(sc.specs)                     # union of all difficulties' tools
        self.kb: KnowledgeBase = sc.kb()                # union of all docs (BM25 index built ONCE)
        self.merged_state = merged_initial_state(sc)    # union of all tasks' initial_state (built ONCE)
        self.company = _company_name(sc)
        self.background = (sc.blueprint or {}).get("background")

    def engine_for(self, task: dict) -> Engine:
        ft = task.get("frozen_time")
        if not ft:
            raise ValueError(f"task {task.get('task_index','?')} has no frozen_time")
        # DB.seeded deep-copies, so every engine gets an isolated copy of the union DB,
        # while the KB (and its prebuilt index) and the tool specs are shared read-only.
        # Then overlay THIS task's own initial_state on top: the union merge is row-wise
        # last-win, so a colliding row id from another task could otherwise shadow this
        # task's version — re-asserting it here guarantees the rollout sees its own data.
        db = DB.seeded(self.merged_state).overlay(task.get("initial_state"))
        return Engine(db, Clock.from_stamp(ft),
                      self.kb, self.specs, schema=self.schema)

    def score(self, task: dict, gt_actions: List[dict], agent_actions: List[dict]) -> dict:
        """Replay gold and agent trajectories on the SAME union DB and compare hashes.
        Untouched rows (every other task's) are seeded identically on both sides, so
        they cancel out and the match reduces to this task's own writes — equivalent
        to per-task scoring given the disjointness invariant, but over the shared world."""
        target = replay(self.engine_for(task), gt_actions)
        predicted = replay(self.engine_for(task), agent_actions)
        return {"match": target == predicted,
                "reward": 1.0 if target == predicted else 0.0,
                "target_hash": target, "predicted_hash": predicted}


def merged_initial_state(sc: Scenario) -> dict:
    """Row-wise union of every task's initial_state across all difficulties."""
    merged: dict = {}
    for _, task in sc.all_tasks():
        for table, rows in (task.get("initial_state") or {}).items():
            dst = merged.setdefault(table, {})
            for rid, row in (rows or {}).items():
                dst[rid] = dict(row)
    return merged


# One ScenarioWorld per scenario path, built lazily and cached for the whole run.
_WORLD_CACHE: Dict[str, ScenarioWorld] = {}


def get_world(scenario: str) -> ScenarioWorld:
    """Return the cached ScenarioWorld for a scenario dir, building it on first use only.

    This IS the DB / KB / retrieval-index cache: on the first reference the scenario is
    read from disk, its tool modules imported, its union DB merged, and its BM25 index
    built; every later task, trial, and repeat reference (including across scenarios in
    one run) reuses the same in-memory world with no re-read and no re-index."""
    key = os.path.abspath(scenario)
    world = _WORLD_CACHE.get(key)
    if world is None:
        world = ScenarioWorld(load_scenario(scenario))
        _WORLD_CACHE[key] = world
    return world


# --------------------------------------------------------------------------- #
# Task selection
# --------------------------------------------------------------------------- #

def _flat_tasks(sc: Scenario) -> List[Tuple[str, int, dict]]:
    out = []
    for difficulty in sorted(sc.tasks):
        for task in sc.tasks[difficulty]:
            out.append((difficulty, int(task.get("task_index", 0)), task))
    return out


def select_tasks(sc: Scenario, difficulty: Optional[str], task_ids: Optional[List[str]],
                 num_tasks: Optional[int]) -> List[Tuple[str, int, dict]]:
    flat = _flat_tasks(sc)
    if difficulty and difficulty != "all":
        flat = [t for t in flat if t[0] == difficulty]
    if task_ids:
        wanted = set(task_ids)
        flat = [t for t in flat if f"{t[0]}/{t[1]}" in wanted or str(t[1]) in wanted]
    if num_tasks:
        flat = flat[:num_tasks]
    return flat


def _company_name(sc: Scenario) -> str:
    bp = sc.blueprint or {}
    explicit = (bp.get("company") or "").strip()
    if explicit:
        return explicit
    bg = bp.get("background", "") or ""
    if " is " in bg:
        name = bg.split(" is ", 1)[0].strip()
        if 0 < len(name) <= 60:
            return name
    return bp.get("name", sc.name).replace("_", " ").title()


# --------------------------------------------------------------------------- #
# One rollout unit
# --------------------------------------------------------------------------- #

def _sim_dir(artifacts_root: str, scenario_id: str, difficulty: str, task_index: int,
             trial: int) -> str:
    return os.path.join(artifacts_root, scenario_id,
                        f"task_{difficulty}_{task_index}", f"sim_{trial}")


def _write_artifacts(artifacts_root: str, scenario_id: str, difficulty: str, task_index: int,
                     trial: int, task: dict, result, sr: dict, record: dict) -> str:
    """Write one simulation's full agent/user trajectories to disk, under a
    scenario-tagged subfolder:

        artifacts/<scenario>/task_<difficulty>_<index>/sim_<trial>/
            sim_status.json          # metadata (scenario, reward, termination, hashes, usage)
            transcript.json          # readable event log
            trajectory.json          # the scoring actions ({owner, tool, arguments})
            agent_trajectory.json    # tools offered to the agent + full agent message history
            user_trajectory.json     # tools offered to the user  + full user message history
            llm_debug/<seq>_<call_name>.json   # per-turn request+response — STREAMED live by
                                               # the orchestrator as each call returns, not here

    The llm_debug/ files are already on disk (the orchestrator streams them call by
    call while the rollout runs); this writes the end-of-run summaries. A sim dir
    that has llm_debug/ but no sim_status.json is therefore a rollout still in
    flight (or one that died mid-run).
    """
    sim_dir = _sim_dir(artifacts_root, scenario_id, difficulty, task_index, trial)
    os.makedirs(sim_dir, exist_ok=True)

    def dump(name, obj):
        with open(os.path.join(sim_dir, name), "w") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

    def tool_names(tools):
        return [t.get("function", {}).get("name") for t in (tools or [])]

    dump("sim_status.json", {k: v for k, v in record.items() if k != "artifacts"})
    dump("transcript.json", result.transcript)
    dump("trajectory.json", result.trajectory)
    dump("agent_trajectory.json", {"role": "agent", "tool_names": tool_names(result.agent_tools),
                                   "tools": result.agent_tools, "messages": result.agent_messages})
    dump("user_trajectory.json", {"role": "user", "tool_names": tool_names(result.user_tools),
                                  "tools": result.user_tools, "messages": result.user_messages})
    return sim_dir


def run_one(world: ScenarioWorld, difficulty: str, task_index: int, task: dict, trial: int,
            agent_client: LLMClient, user_client: LLMClient, no_background: bool,
            max_steps: int, max_errors: int, artifacts_root: Optional[str]) -> dict:
    t0 = time.time()
    record = {"scenario": world.scenario_id, "difficulty": difficulty,
              "task_index": task_index, "trial": trial}
    try:
        engine = world.engine_for(task)   # cached union DB (deep-copied) + shared KB/index + tools
        background = None if no_background else world.background
        label = f"{world.scenario_id}/{difficulty}/{task_index} trial={trial}"
        # Streaming debug: the orchestrator writes each LLM call's record into
        # llm_debug/ the moment it returns, so the sim dir is inspectable mid-run.
        debug_dir = (os.path.join(_sim_dir(artifacts_root, world.scenario_id, difficulty,
                                           task_index, trial), "llm_debug")
                     if artifacts_root else None)
        orch = Orchestrator(
            engine=engine, agent_client=agent_client, user_client=user_client,
            agent_system=build_agent_prompt(world.company, background, task.get("frozen_time")),
            user_system=build_user_prompt(task.get("user_scenario", "")),
            max_steps=max_steps, max_errors=max_errors, label=label, debug_dir=debug_dir)
        result = orch.run()

        gt_actions = task.get("evaluation_criteria") or []
        sr = world.score(task, gt_actions, result.trajectory)  # scored on the same union DB
        gated_reward = float(sr["reward"]) if result.completed_normally else 0.0

        record.update({
            "reward": gated_reward,
            "db_match": bool(sr["match"]),
            "db_reward": float(sr["reward"]),
            "termination": result.termination,
            "completed_normally": result.completed_normally,
            "steps": result.steps,
            "errors": result.errors,
            "num_tool_calls": len(result.trajectory),
            "target_hash": sr["target_hash"],
            "predicted_hash": sr["predicted_hash"],
            "usage": result.usage,
            "error_detail": result.error_detail,
            "seconds": round(time.time() - t0, 1),
        })
        if artifacts_root:
            sim_dir = _write_artifacts(artifacts_root, world.scenario_id, difficulty,
                                       task_index, trial, task, result, sr, record)
            record["artifacts"] = os.path.relpath(sim_dir, os.path.dirname(artifacts_root))
    except Exception as e:  # noqa: BLE001 -- one rollout must never kill the batch
        import traceback
        record.update({"reward": 0.0, "db_match": False, "termination": "RUNNER_ERROR",
                       "completed_normally": False, "error_detail": f"{e}",
                       "traceback": traceback.format_exc(), "seconds": round(time.time() - t0, 1)})
    return record


# --------------------------------------------------------------------------- #
# Aggregation + reporting
# --------------------------------------------------------------------------- #

def summarize(records: List[dict]) -> dict:
    n = len(records)

    def mean(key):
        vals = [r.get(key, 0.0) for r in records]
        return (sum(vals) / n) if n else 0.0

    def _rate(rs, pred):
        return round(sum(1 for x in rs if pred(x)) / len(rs), 3) if rs else 0.0

    per_task: dict = {}
    per_scen: dict = {}
    for r in records:
        tkey = f"{r.get('scenario', '?')}/{r['difficulty']}/{r['task_index']}"
        per_task.setdefault(tkey, []).append(r)
        per_scen.setdefault(r.get("scenario", "?"), []).append(r)

    task_pass = {}
    for key, rs in sorted(per_task.items()):
        task_pass[key] = {"pass@1": round(sum(x["reward"] for x in rs) / len(rs), 3),
                          "trials": len(rs),
                          "db_match": _rate(rs, lambda x: x.get("db_match")),
                          "completed": _rate(rs, lambda x: x.get("completed_normally"))}
    scen_pass = {}
    for key, rs in sorted(per_scen.items()):
        scen_pass[key] = {"rollouts": len(rs),
                          "reward_mean": round(sum(x["reward"] for x in rs) / len(rs), 4),
                          "db_match_rate": _rate(rs, lambda x: x.get("db_match")),
                          "completion_rate": _rate(rs, lambda x: x.get("completed_normally"))}
    return {
        "rollouts": n,
        "reward_mean": round(mean("reward"), 4),
        "db_match_rate": round(sum(1 for r in records if r.get("db_match")) / n, 4) if n else 0.0,
        "completion_rate": round(sum(1 for r in records if r.get("completed_normally")) / n, 4) if n else 0.0,
        "avg_steps": round(mean("steps"), 1),
        "per_scenario": scen_pass,
        "per_task": task_pass,
    }


def print_summary(summary: dict, cfg: dict) -> None:
    print("\n" + "=" * 70)
    print(" ROLLOUT SUMMARY")
    print("=" * 70)
    print(f"   scenarios       : {', '.join(cfg['scenarios'])}")
    print(f"   agent / user    : {cfg['agent_llm']}  /  {cfg['user_llm']}")
    print(f"   rollouts        : {summary['rollouts']}  "
          f"(trials={cfg['num_trials']}, max_steps={cfg['max_steps']})")
    print(f"   reward (pass@1) : {summary['reward_mean']:.3f}")
    print(f"   db-match rate   : {summary['db_match_rate']:.3f}")
    print(f"   completion rate : {summary['completion_rate']:.3f}")
    print(f"   avg agent steps : {summary['avg_steps']}")
    if len(summary.get("per_scenario", {})) > 1:
        print("   per scenario:")
        print(f"      {'scenario':40} {'pass@1':>7} {'dbmatch':>8} {'done':>6} {'n':>5}")
        for key, v in summary["per_scenario"].items():
            print(f"      {key:40} {v['reward_mean']:>7} {v['db_match_rate']:>8} "
                  f"{v['completion_rate']:>6} {v['rollouts']:>5}")
    print("   per task:")
    print(f"      {'scenario/task':52} {'pass@1':>7} {'dbmatch':>8} {'done':>6} {'trials':>7}")
    for key, v in summary["per_task"].items():
        print(f"      {key:52} {v['pass@1']:>7} {v['db_match']:>8} {v['completed']:>6} {v['trials']:>7}")
    print("=" * 70)


# --------------------------------------------------------------------------- #
# Live progress
# --------------------------------------------------------------------------- #

class _Progress:
    """Live run progress: one tqdm bar over all tasks with a ``running=N`` postfix
    (tqdm can stack multiple bars via ``position=``, but "currently running" is not a
    monotonic quantity — a postfix on the single completed-tasks bar is sturdier).

    The bar is drawn on /dev/tty, NOT stdout/stderr: run.sh pipes both through
    ``tee`` into the log file, and a carriage-return bar would shred the log. On a
    tty-less environment (cron, CI) the bar silently disables itself — the per-task
    completion lines in the log still carry done/running/pending counts."""

    def __init__(self, total: int):
        self._lock = threading.Lock()
        self.total = total
        self.done = 0
        self.passed = 0
        self.running: set = set()
        self._bar = None
        self._tty = None
        try:
            from tqdm import tqdm
            self._tty = open("/dev/tty", "w")
            self._bar = tqdm(total=total, file=self._tty, desc="tasks", unit="task",
                             dynamic_ncols=True)
        except Exception:  # noqa: BLE001 -- no tqdm or no tty: log lines only
            if self._tty is not None:
                try:
                    self._tty.close()
                except Exception:  # noqa: BLE001
                    pass
                self._tty = None
            self._bar = None

    def _refresh_locked(self) -> None:
        if self._bar is not None:
            self._bar.set_postfix(running=len(self.running), passed=self.passed)

    def start(self, tag: str) -> None:
        with self._lock:
            self.running.add(tag)
            self._refresh_locked()

    def finish(self, tag: str, reward: float) -> None:
        with self._lock:
            self.running.discard(tag)
            self.done += 1
            if reward == 1.0:
                self.passed += 1
            if self._bar is not None:
                self._bar.update(1)
            self._refresh_locked()

    @property
    def running_count(self) -> int:
        with self._lock:
            return len(self.running)

    def close(self) -> None:
        if self._bar is not None:
            self._bar.close()
        if self._tty is not None:
            try:
                self._tty.close()
            except Exception:  # noqa: BLE001
                pass


# --------------------------------------------------------------------------- #
# Client construction
# --------------------------------------------------------------------------- #

def _role_args(model: str, effort: str, temperature: float, max_tokens: int,
               api_base: str, api_key: str, timeout: float, override_json: str) -> dict:
    """Assemble the litellm kwargs for one role. If ``override_json`` is given it is
    used verbatim; otherwise args are derived from the model id via ``args_for``.
    Per-role api_base/api_key/timeout are merged in."""
    if override_json:
        try:
            args = json.loads(override_json)
        except json.JSONDecodeError as e:
            raise SystemExit(f"invalid JSON in llm-args: {override_json!r}: {e}")
    else:
        args = args_for(model, effort, temperature=temperature, max_tokens=max_tokens)
    if api_base:
        args["api_base"] = api_base
    if api_key:
        args["api_key"] = api_key
    if timeout and "timeout" not in args:
        args["timeout"] = timeout
    return args


def build_client(model: str, args: dict, max_attempts: int) -> LLMClient:
    return LLMClient(model=model, args=args, max_attempts=max_attempts)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rollout", description=__doc__)
    p.add_argument("--scenario", default="env/residential_solar_installer",
                   help="path to a single scenario directory (holds blueprint.yaml)")
    p.add_argument("--scenarios", nargs="+", default=None,
                   help="one or more scenario dirs run in ONE process, sharing the world "
                        "cache (overrides --scenario; artifacts are grouped per scenario)")
    p.add_argument("--difficulty", default="all",
                   help="restrict to one difficulty dir, or 'all'")
    p.add_argument("--task-ids", nargs="*", default=None,
                   help="task ids like 'warranty_repair_claims/0' (space separated)")
    p.add_argument("--num-tasks", type=int, default=None,
                   help="run only the first N selected tasks (per scenario)")
    p.add_argument("--num-trials", type=int, default=1)
    p.add_argument("--max-steps", type=int, default=80)
    p.add_argument("--max-errors", type=int, default=10)
    p.add_argument("--max-concurrency", type=int, default=8)

    # Models: litellm ids. A leading `openai/` routes to the OpenAI-compatible proxy;
    # `openai/responses/<m>` targets the Responses API (tools + reasoning effort).
    p.add_argument("--agent-llm", default=os.environ.get("AGENT_LLM", "openai/responses/gpt-5.6-sol"))
    p.add_argument("--user-llm", default=os.environ.get("USER_LLM", "openai/responses/gpt-5.4-mini-construct"))
    # Per-role reasoning effort (used only for gpt/claude ids via args_for).
    p.add_argument("--agent-effort", default=os.environ.get("AGENT_EFFORT", "high"))
    p.add_argument("--user-effort", default=os.environ.get("USER_EFFORT", "medium"))
    # Full llm-args override as a JSON string; empty -> derived from the model id.
    p.add_argument("--agent-llm-args", default=os.environ.get("AGENT_LLM_ARGS", ""))
    p.add_argument("--user-llm-args", default=os.environ.get("USER_LLM_ARGS", ""))
    p.add_argument("--agent-temperature", type=float, default=1.0)
    p.add_argument("--user-temperature", type=float, default=1.0)
    p.add_argument("--agent-max-tokens", type=int, default=DEFAULT_LLM_MAX_TOKENS)
    p.add_argument("--user-max-tokens", type=int, default=DEFAULT_LLM_MAX_TOKENS)
    # Per-role endpoint override; empty -> global OPENAI_API_BASE/KEY that litellm reads.
    p.add_argument("--agent-api-base", default=os.environ.get("AGENT_API_BASE", ""))
    p.add_argument("--agent-api-key", default=os.environ.get("AGENT_API_KEY", ""))
    p.add_argument("--user-api-base", default=os.environ.get("USER_API_BASE", ""))
    p.add_argument("--user-api-key", default=os.environ.get("USER_API_KEY", ""))
    p.add_argument("--request-timeout", type=float, default=0.0,
                   help="per-call timeout seconds passed to litellm (0 = litellm default)")
    p.add_argument("--max-attempts", type=int, default=0,
                   help="LLM retry cap; 0 (default) = retry every generation error forever")

    p.add_argument("--api-base", default=os.environ.get("OPENAI_API_BASE", ""))
    p.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))

    p.add_argument("--save-to", default=None,
                   help="output dir name under data/simulations/ (default: timestamped)")
    p.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "WARNING"),
                   help="root log level (DEBUG/INFO/WARNING/ERROR)")
    p.add_argument("--no-background", action="store_true",
                   help="omit the company background from the agent prompt")
    p.add_argument("--verbose-logs", action="store_true",
                   help="write per-task agent/user trajectories under <save_to>/artifacts/")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_argparser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.WARNING),
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    # litellm reads OPENAI_API_BASE/OPENAI_API_KEY for the `openai/` provider.
    if args.api_base:
        os.environ.setdefault("OPENAI_API_BASE", args.api_base)
    if args.api_key:
        os.environ.setdefault("OPENAI_API_KEY", args.api_key)
    if not (args.api_base or args.agent_api_base) or not (args.api_key or args.agent_api_key):
        raise SystemExit("OPENAI_API_BASE and OPENAI_API_KEY must be set "
                         "(env, --api-base/--api-key, or per-role --*-api-base/--*-api-key).")

    scenarios = args.scenarios or [args.scenario]

    # Build (or fetch from cache) each scenario's world ONCE, then select its tasks.
    # get_world memoizes the DB / KB / retrieval index so a scenario is never re-read
    # or re-indexed, even if it appears more than once in the list.
    units: List[Tuple[ScenarioWorld, str, int, dict, int]] = []
    for scen in scenarios:
        world = get_world(scen)
        picked = select_tasks(world.sc, args.difficulty, args.task_ids, args.num_tasks)
        ncust = sum(len(rows) for rows in world.merged_state.values())
        print(f"  world[{world.scenario_id}]: {len(world.specs)} tools, {len(world.sc.docs)} KB docs, "
              f"union DB {len(world.merged_state)} tables / {ncust} rows, "
              f"{len(picked)} tasks selected")
        if not picked:
            print(f"    WARN: no tasks selected under {scen} "
                  f"(difficulty={args.difficulty}, ids={args.task_ids}) — skipping")
            continue
        for (d, i, t) in picked:
            for trial in range(args.num_trials):
                units.append((world, d, i, t, trial))
    if not units:
        raise SystemExit(f"no tasks selected across scenarios={scenarios} "
                         f"(difficulty={args.difficulty}, ids={args.task_ids})")

    agent_args = _role_args(args.agent_llm, args.agent_effort, args.agent_temperature,
                            args.agent_max_tokens, args.agent_api_base, args.agent_api_key,
                            args.request_timeout, args.agent_llm_args)
    user_args = _role_args(args.user_llm, args.user_effort, args.user_temperature,
                           args.user_max_tokens, args.user_api_base, args.user_api_key,
                           args.request_timeout, args.user_llm_args)
    agent_client = build_client(args.agent_llm, agent_args, args.max_attempts)
    user_client = build_client(args.user_llm, user_args, args.max_attempts)

    def _redact(a):  # keep api_key out of logs / results.json
        return {k: ("<set>" if k == "api_key" else v) for k, v in a.items()}
    print(f"  agent args: {_redact(agent_args)}")
    print(f"  user  args: {_redact(user_args)}")

    save_to = args.save_to or f"rollout_{args.agent_llm.split('/')[-1]}_{time.strftime('%Y%m%d_%H%M%S')}"
    out_dir = os.path.join(_REPO_ROOT, "data", "simulations", save_to)
    os.makedirs(out_dir, exist_ok=True)
    artifacts_root = os.path.join(out_dir, "artifacts") if args.verbose_logs else None
    if artifacts_root:
        os.makedirs(artifacts_root, exist_ok=True)

    print(f"Running {len(units)} rollouts across {len(scenarios)} scenario(s) "
          f"(trials={args.num_trials}) agent={args.agent_llm} user={args.user_llm} "
          f"concurrency={args.max_concurrency} max_attempts={args.max_attempts or 'inf'}")
    print(f"  output={out_dir}" + (f"  artifacts={artifacts_root}" if artifacts_root else ""))

    records: List[dict] = []
    done = 0
    progress = _Progress(len(units))

    def _run_unit(world: ScenarioWorld, d: str, i: int, t: dict, trial: int) -> dict:
        tag = f"{world.scenario_id}/{d}/{i}#{trial}"
        progress.start(tag)
        rec = run_one(world, d, i, t, trial, agent_client, user_client,
                      args.no_background, args.max_steps, args.max_errors, artifacts_root)
        progress.finish(tag, float(rec.get("reward") or 0.0))
        return rec

    with ThreadPoolExecutor(max_workers=max(1, args.max_concurrency)) as pool:
        futs = {
            pool.submit(_run_unit, world, d, i, t, trial): (world.scenario_id, d, i, trial)
            for (world, d, i, t, trial) in units
        }
        for fut in as_completed(futs):
            rec = fut.result()
            records.append(rec)
            done += 1
            running = progress.running_count
            print(f"  [{done}/{len(units)}] {rec.get('scenario')}/{rec['difficulty']}/{rec['task_index']} "
                  f"trial={rec['trial']} -> reward={rec.get('reward')} "
                  f"term={rec.get('termination')} steps={rec.get('steps')} "
                  f"tools={rec.get('num_tool_calls')} ({rec.get('seconds')}s) "
                  f"| running={running} pending={len(units) - done - running}")
    progress.close()

    records.sort(key=lambda r: (r.get("scenario", ""), r["difficulty"], r["task_index"], r["trial"]))
    summary = summarize(records)
    cfg = {
        "scenarios": scenarios, "agent_llm": args.agent_llm, "user_llm": args.user_llm,
        "agent_llm_args": _redact(agent_args), "user_llm_args": _redact(user_args),
        "num_trials": args.num_trials, "max_steps": args.max_steps,
        "max_errors": args.max_errors, "max_attempts": args.max_attempts,
        "verbose_logs": bool(artifacts_root),
    }
    out = {"config": cfg, "summary": summary, "results": records}
    results_path = os.path.join(out_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print_summary(summary, cfg)
    print(f"\nDone. Results: {results_path}")
    if artifacts_root:
        print(f"Per-task trajectories: {artifacts_root}/<scenario>/task_<difficulty>_<index>/sim_<trial>/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
