# rollout — agent ↔ user-simulator rollouts for erlbench scenarios

`erlbench/` can load a generated scenario, bind its DB + knowledge base + tools
into an `Engine`, and score a trajectory by replaying its writes and comparing DB
hashes — but nothing drives two LLMs through the `Engine`. **`rollout/` is that
missing runtime piece.** It runs a live customer-service conversation between an
**agent** LLM and a **user-simulator** LLM over each task, collects every tool call,
and scores the result. It is implemented entirely on top of this repo's own
`erlbench` scaffold.

## The tool model (base / share / task)

The agent's context contains **only two kinds of tools**, plus the fixed base
meta-tools:

- **BASE (meta) tools** — fixed in `erlbench/engine.py`, same for every scenario:
  - agent: `KB_search`, `grep`, `unlock_agent_discoverable_tool`,
    `unlock_user_discoverable_tool`, `call_agent_discoverable_tool`
  - user: `call_user_discoverable_tool`
- **SHARE tools** — from the scenario's `share_tools.py`; always listed and
  directly callable by their owner (e.g. `locate_customer`,
  `verify_customer_identity`, `find_policies`, `transfer_to_human_agent`).
- **TASK tools** — from each difficulty's `tools/task_tools.py`; **hidden** from
  every tool list. Their names live only in the knowledge base. The agent reaches
  one by discovering its name via `KB_search`/`grep`, then:

  ```
  unlock_agent_discoverable_tool(name)      # reveals the tool's parameters
  call_agent_discoverable_tool(name, args)  # actually runs it
  ```

  A **user-run** task tool is handed over by the agent
  (`unlock_user_discoverable_tool`) and executed by the user simulator
  (`call_user_discoverable_tool`).

Neither participant ever sees the other's tool traffic — only plain-text messages
cross between them, like a real support call.

## The shared world (union of all difficulties), built once and cached

Every task rollout runs against the **whole scenario**, not just its own slice:

- **tools** = the fixed base meta-tools + **every** difficulty's task tools (+ share tools)
- **KB** = **every** difficulty's documents (unrelated docs act as distractors)
- **DB** = the **union of every task's `initial_state`** across all difficulties

`ScenarioWorld` (in `runner.py`) builds this once: the loader merges the tools and
the KB corpus, and `rollout` seeds the DB with the row-wise union of every task's
`initial_state`. Tasks are disjoint by construction (unique uuid seed ids; the
validator forbids a phone/email/name shared across tasks), so a task's specific-id
lookups still resolve only its own rows — every other task's rows are realistic
distractors. Scoring replays the gold and agent trajectories on that **same** union
DB: the untouched distractor rows are seeded identically on both sides and cancel
out, so the DB-hash match reduces to the task's own writes.

**Caching.** `get_world(scenario)` memoizes one `ScenarioWorld` per scenario path.
The expensive setup — reading the scenario from disk, importing its tool modules,
merging the union DB, and building the KB's **BM25 retrieval index** — happens
**exactly once** per scenario and is reused by every task, every trial, and (in a
multi-scenario run) every repeat reference. The KB and its prebuilt index are shared
read-only across all rollouts; only the DB is deep-copied per rollout, for isolation
between concurrent conversations.

## Multi-scenario

One invocation can run several scenarios in a single process, sharing the world
cache. Pass a list via `--scenarios` (or `SCENARIOS="env/a env/b"` in `run.sh`).
Each rollout record carries its `scenario`, the summary breaks results down per
scenario, and artifacts are grouped by scenario id (below).

## The loop

1. The agent opens with a fixed greeting (shown to the user).
2. Half-duplex turn-taking: on its turn a side **either** speaks a plain-text
   message (relayed to the other side, passing the floor) **or** makes a tool call
   (routed to the `Engine`, whose string result is fed back, keeping the floor).
3. The user simulator ends the call with `###STOP###` (goal met),
   `###TRANSFER###` (handed to a human), or `###OUT-OF-SCOPE###`. The run also
   ends on `MAX_STEPS` / `MAX_ERRORS`.

## Scoring

Every tool call is recorded in the exact `{owner, tool, arguments}` shape
`erlbench.scoring` consumes (a hidden-tool call is recorded as the
`call_agent_discoverable_tool` wrapper it really issued, which `_resolve` unwraps).
The run's `reward` is the terminal-state DB-hash match between the agent trajectory
and the task's `evaluation_criteria`, **gated on a normal end of call**
(`USER_STOP` / `USER_TRANSFER`) — an aborted or step-capped conversation scores 0.

## Files

| File | Role |
|------|------|
| `llm.py` | LLM calls via **litellm**: provider routing for `openai/` and `openai/responses/` ids, `drop_params`, per-role `api_base/api_key`, plus infinite retry with backoff |
| `prompts.py` | native agent + user-simulator system prompts |
| `orchestrator.py` | the half-duplex loop over one `Engine`; trajectory + termination |
| `runner.py` | CLI: cache + build each scenario's world, select tasks, N trials with concurrency, score, save `results.json`, print per-scenario pass@1 |

## Usage

From the repo root, with an OpenAI-compatible proxy in the environment
(`OPENAI_API_BASE`, `OPENAI_API_KEY`):

```bash
# All tasks in the default scenario, 1 trial each:
./run.sh

# Several scenarios in one run:
SCENARIOS="env/home_appliance_warranty_provider env/regional_pet_insurer" ./run.sh

# One task, 3 trials:
TASK_IDS="service_claim_dispatch/0" NUM_TRIALS=3 ./run.sh
```

Or call the CLI directly:

```bash
uv run python -m rollout --scenarios env/home_appliance_warranty_provider \
  --task-ids service_claim_dispatch/0 --num-trials 1 --verbose-logs
```

Results land in `data/simulations/<SAVE_TO>/results.json` (config + summary +
per-rollout metadata — kept lean, no message dumps). With `--verbose-logs` (the
`run.sh` default), the full per-task **agent and user trajectories** are written
under `artifacts/`, grouped by scenario id:

```
data/simulations/<SAVE_TO>/
  results.json                                  # config + summary (overall + per scenario) + per-rollout metadata
  artifacts/
    <scenario>/                                 # e.g. home_appliance_warranty_provider
      task_<difficulty>_<index>/
        sim_<trial>/
          sim_status.json                       # scenario, reward, db_match, termination, hashes, usage
          transcript.json                       # readable conversation + tool-call event log
          trajectory.json                       # the scored {owner,tool,arguments} actions
          agent_trajectory.json                 # full agent message history
          user_trajectory.json                  # full user-simulator message history
          llm_debug/
            001_user_simulator_response.json    # each turn: request messages + normalized response
            002_agent_response.json             # STREAMED live, call by call, while the rollout runs
            ...
```

`llm_debug/` is written **live**: the orchestrator flushes each call's record the
moment it returns, so a running rollout can be inspected mid-flight. The summary
files (`sim_status.json` etc.) land at the end — a sim dir with `llm_debug/` but no
`sim_status.json` is a rollout still in progress (or one that died mid-run). A tqdm
progress bar (completed tasks + `running=N` postfix) is drawn on the terminal's
/dev/tty so it never pollutes the tee'd log; each completion line in the log also
carries `running=`/`pending=` counts.

### Models, config, and retries (via litellm)

LLM calls go through **litellm**, so a model id works unchanged and no HTTP is
hand-rolled. Every knob is an env var in `run.sh` mapped to a CLI flag:

| env (run.sh) | CLI | meaning |
|---|---|---|
| `SCENARIOS` / `SCENARIO` | `--scenarios` / `--scenario` | one or more scenario dirs (space-separated); run in one process sharing the world cache |
| `AGENT_LLM` / `USER_LLM` | `--agent-llm` / `--user-llm` | litellm ids. `openai/…` → OpenAI-compatible proxy; `openai/responses/…` → Responses API. Defaults: agent `openai/responses/gpt-5.6-sol`, user `openai/responses/gpt-5.4-mini-construct` |
| `AGENT_EFFORT` / `USER_EFFORT` | `--agent-effort` / `--user-effort` | reasoning effort: `none\|minimal\|low\|medium\|high\|xhigh\|max` (model-dependent; `max` is the gpt-5.6 top tier) |
| `AGENT_MAX_TOKENS` / `USER_MAX_TOKENS` | `--*-max-tokens` | output cap (default 32768) |
| `AGENT_LLM_ARGS` / `USER_LLM_ARGS` | `--*-llm-args` | full litellm-kwargs JSON override; empty → built by `run.sh` from the model id (see below) |
| `AGENT_API_BASE`/`AGENT_API_KEY`, `USER_API_BASE`/`USER_API_KEY` | `--*-api-base` / `--*-api-key` | per-role endpoint override; empty → global `OPENAI_API_BASE`/`OPENAI_API_KEY` |
| `MAX_ATTEMPTS` | `--max-attempts` | LLM retry cap; `0` (default) = retry forever |
| `REQUEST_TIMEOUT` | `--request-timeout` | per-call timeout passed to litellm (`0` = its default) |
| `MAX_CONCURRENCY` | `--max-concurrency` | concurrent rollouts; also sizes litellm's httpx pool |

**Reasoning effort is formatted in `run.sh`, per model id.** litellm does not
translate a flat `reasoning_effort` into the Responses API's nested `reasoning.effort`
for `openai/responses/*` on this proxy — a flat value there is silently ignored. So
`run.sh` builds the per-role llm-args JSON itself (`_derive_args`) and passes it via
`--*-llm-args`:

- `openai/responses/<gpt|claude|o*>` → `{"reasoning": {"effort": E}}` (nested; honored)
- other gpt/claude (chat completions) → `{"reasoning_effort": E}` (flat)
- everything else (e.g. kimi) → no reasoning key

`temperature` defaults to 1.0 (kimi and Anthropic thinking both require it), and
`litellm.drop_params=True` silently drops any param a model still rejects.

One behavior sits on top of litellm: **every generation error is retried, by
default forever**, with capped exponential backoff — 429, 5xx, timeout, connection
drop, malformed response — so an oversubscribed shared proxy never kills a run.
Bound it with `MAX_ATTEMPTS`. Each LLM call also logs one INFO line tagged with its
`scenario/difficulty/task trial role step`, model, token usage, and latency.
