# harbor_utils — erlbench scenarios → Harbor tasks

`convert.py` turns every task under `env/<scenario>/` into a self-contained Harbor task in
`harbor_tasks/`, and writes the harness that runs them to `harbor_erl_agent/` (beside the
dataset, never inside it — deliver the two directories together). Nothing is written by hand
per scenario: every file is derived from the scenario by the code the local rollout uses, so
any scenario the rollout can run converts the same way.

```bash
uv run python harbor_utils/convert.py                  # every task of every scenario -> harbor_tasks/
uv run python harbor_utils/convert.py --selftest       # + offline end-to-end checks
uv run python harbor_utils/convert.py --tasks 'regional_retail_bank/auto_loan_payment_servicing/*'
uv run python harbor_utils/convert.py --scenarios env/metro_gym_chain --out /tmp/gym_tasks
```

Selectors (`--tasks`, globs allowed): `scenario/difficulty/index`, `difficulty/index`, or a
task dir name. Re-running replaces the task dirs it wrote (and earlier names of the same task)
and rewrites `harbor_erl_agent/` and both READMEs.

## How a task runs

Everything runs **inside the task container**; the host only launches it:

```
host: harbor run -a erl_agent:ErlAgent          task container (one per trial)
  ErlAgent.setup: copy container/  ──────────►  /opt/erl_agent/ (run_episode.py, rollout/)
  ErlAgent.run:   docker exec  ──────────────►  python3 run_episode.py
                                                  ├ agent LLM ────────► AWS Bedrock
                                                  ├ customer LLM ─────► AWS Bedrock
                                                  └ runtime.Session: the task's engine,
                                                    in-process; every tool call recorded
                                                    to /opt/task/state/calls.jsonl
  read back /logs/agent (the trial's agent/)  ◄─  transcripts, trajectories, usage
                                                verifier: tests/grade.py grades state/
```

`run_episode.py` runs **the rollout's own `Orchestrator` and `LLMClient`** (`rollout/`,
cleaned copies) over a `runtime.Session` — the engine's two tool surfaces with every call
recorded. Greeting, turn-taking, stop tokens, empty-turn nudges, `max_steps` / `max_errors`,
retries and prompts are those of `run.sh`; the only difference from a local rollout is that
it happens in the container. The container needs the network (it calls the models); the LLM
client and its dependencies are part of every task image (`environment/requirements.txt`,
the exact versions the repo runs, one shared cached layer). Each model's base URL and key are
given at launch (`AGENT_API_*` / `USER_API_*`); the keys reach the run in a file it deletes as
soon as it has read it.

## One task — laid out by what it is, not by how it was made

`<scenario>__<difficulty>__<index>__<uuid8>/` (charset `[a-z0-9_]`; `task.toml` name
`erlbench/<dir>`). The 8 hex digits are a UUID5 of (scenario, difficulty, index): the same
task always gets the same name, across re-runs and output dirs.

```
instruction.md                 the agent's system prompt
task.toml
environment/
  db_schema.json               table -> fields
  db.json                      the database at the start of the conversation
  knowledge_base/<id>.json     the knowledge base, one document per file ({id, title, content})
  share_tools.py               the tools listed to their owner (agent or customer)
  task_tools/task_tools_<uuid8>.py   the discoverable tools of EVERY difficulty, one module each
  episode.json                 frozen "now", the customer simulator's prompt, integrity hashes
  runtime/                     runtime.py (world + Session), erlbench/ (runtime modules only)
  requirements.txt, Dockerfile the image: the world + the packages the conversation needs
tests/      test.sh, grade.py, expected.json (reference actions, expected DB hash)
solution/   solve.sh, oracle.py, oracle_calls.json, design_rationale.json
```

How each file is derived:

| file | from |
|---|---|
| `db.json` | union of **every** task's `initial_state`, overlaid with this task's (`rollout.runner.merged_initial_state` + `DB.overlay`, as `ScenarioWorld.engine_for`) |
| `knowledge_base/` | **every** product's docs (`erlbench.loader`), one file per doc named by its id; `meta` (authoring provenance) dropped. Indexed in file-name order — for all current scenarios identical to the loader's order; a warning is printed if a scenario ever differs (only equal-score result order can change) |
| `share_tools.py` | `blueprint/share_tools.py` without module docstring and comments |
| `task_tools/task_tools_<uuid8>.py` | every difficulty's `task_tools.py`, without module docstring and comments; the 8 hex digits are a UUID5 of (scenario, difficulty), so the name does not reveal the difficulty but is the same in every task and run. Each is loaded as its own module; tool names must be unique across share and task tools (checked), so load order cannot matter. `design_rationale.json` maps each discoverable tool to its file |
| `runtime/erlbench/` | the erlbench runtime modules (`db`, `determinism`, `tools`, `kb`, `engine`, `scoring`) without docstrings/comments — except the base meta tools' docstrings, which are their LLM-facing descriptions; `loader`/`validate` (authoring) are not shipped |
| `requirements.txt` | the repo's runtime dependencies (`pyproject.toml`) and their whole closure, pinned to the repo environment's versions — what the local rollout runs with |
| `instruction.md` / `episode.json` | `rollout.prompts.build_agent_prompt` / `build_user_prompt` |
| `tests/expected.json` | `evaluation_criteria` as `{owner, tool, arguments}` + `replay` hash |
| `solution/oracle_calls.json` | `evaluation_criteria` as live tool calls |
| `solution/design_rationale.json` | the task's structured design, verbatim: `computations`, `prerequisite_closure` → `prerequisite_tree`, `solvability_contract` → `solvability`, `evaluation_criteria` (with objective / necessity / argument tracing) → `reference_solution`, the customer brief; plus `policies` / `workflows` / `discoverable_tools` → the knowledge-base documents (and files) that carry them. The source's free-text `design_rationale` (the authoring worklog) is not shipped |

Function docstrings in the tool files are kept verbatim: a tool's docstring **is** its
description. Every cleaned Python file is checked to be AST-identical to its source minus
exactly the removed docstrings, so no code changes.

## The harness: `harbor_erl_agent/`

```
erl_agent.py        the Harbor agent (erl_agent:ErlAgent), from harbor_utils/erl_agent.py
container/          copied into each task container by erl_agent.py
  run_episode.py    one conversation, from harbor_utils/agent/run_episode.py
  rollout/          the conversation loop: __init__, llm, orchestrator, prompts (cleaned)
README.md           how to run
```

## Scoring

Every tool call is appended to `state/calls.jsonl` as it happens; at the end the run records
its termination (`state/episode.json`). `tests/grade.py` computes the rollout's reward:
`replay(reference) == replay(recorded calls)` on fresh copies of the world, gated on
`USER_STOP` / `USER_TRANSFER`. No end record (crash, timeout) → 0. A verifier failure writes
no reward, so harbor shows a verifier error instead of a silent 0.

## Checks

Before writing, per scenario: the packed world, loaded in a fresh interpreter by the task's
own `runtime/runtime.py`, must define exactly the source's tools (names, owners, rw, kinds,
descriptions, schemas, order), knowledge base, schema and both tool lists. Per task: the DB
survives its JSON round trip; the reference actions, executed **live** through the engine's
routing, succeed call by call and reach the reference replay's hash.

In the image: the build fails if the tool / knowledge-base / DB fingerprints differ from
`episode.json`; every `Session` re-checks them; `grade.py` re-checks them and the expected hash.

`--selftest` runs each task without Docker — its real `oracle.py` and `grade.py`: oracle →
1.0; the reference calls without a normal end → 0 (db match 1); an empty conversation → 0 —
and runs `container/run_episode.py` once on a written task with scripted stand-ins for the two
models (no model is called): it must end normally, record its tool call, delete its secrets
file, write its outputs, and be graded.

## Running in Harbor

The generated `harbor_tasks/README.md` and `harbor_erl_agent/README.md` carry the standard
commands (written by `convert.py` on every run — edit them there, in `DATASET_README` /
`AGENT_README`). From the directory that holds both, jobs going to `./jobs/<timestamp>/`:

```bash
harbor run -p harbor_tasks -a oracle -n 64 -k 2              # must be 1.0 everywhere

AGENT_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 AGENT_API_KEY=<API key> \
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \
    -m openai/responses/openai.gpt-6-astra \
    --ak user_model=openai/responses/openai.gpt-5.4 \
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \
    -n 64 -k 2
```

Each model is `<protocol>/<model id>` plus its endpoint's base URL and API key, given at launch:
`-m` + `AGENT_API_BASE` / `AGENT_API_KEY` for the agent, `--ak user_model=` + `USER_API_BASE` /
`USER_API_KEY` for the customer simulator (defaulting to the agent's). The protocol is
`openai/` (OpenAI-compatible; `openai/responses/` for the Responses API) or `anthropic/`
(Anthropic Messages API) — e.g. `-m anthropic/global.anthropic.claude-opus-4-8` with
`AGENT_API_BASE=https://bedrock-runtime.us-west-2.amazonaws.com/anthropic`. The model id is the
endpoint's own: bedrock-runtime takes an inference profile (`global.` / `us.` …),
bedrock-mantle the bare `anthropic.claude-opus-4-8`. Nothing provider-specific, no credentials
read from anywhere else. Harbor imports a custom agent by module name only
(`-a module:Class`), hence `PYTHONPATH`.

## Files

| file | role |
|---|---|
| `convert.py` | the converter (+ `--selftest`) |
| `erl_agent.py` | the Harbor agent (host side: launches, waits, reads back); copied to `harbor_erl_agent/` |
| `agent/run_episode.py` | one conversation inside the task container; copied to `harbor_erl_agent/container/` |
| `runtime/runtime.py` | the world and `Session` — used by the conversation, the oracle, the verifier and the self-test |
| `runtime/grade.py` | the verifier |
| `runtime/oracle.py` | the reference solution |
