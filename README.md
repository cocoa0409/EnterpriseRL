# enterprise_rl

A dependency-light scaffold for synthesizing customer-service agent tasks with a
shared DB, a searchable knowledge base, and discoverable tools.

## Layout

| Path        | Purpose                                                                 |
|-------------|-------------------------------------------------------------------------|
| `erlbench/` | The core library: engine, loader, scoring, validation, DB, KB, tools.   |
| `skills/`   | Authoring skills (entrance, scenario-blueprint, task-instantiate, kb-doc-render, task/kb-doc policy audits). |
| `rollout/`  | Live agent ↔ user-simulator rollout runner (scores generated tasks). See `rollout/README.md`. |
| `env/`      | Generated scenarios (one directory per scenario).                       |
| `run.sh`    | Entry point: run + score rollouts over a scenario (see below).          |

## Getting started

This project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync                 # create .venv and install dependencies (+ editable erlbench)
uv run python -c "import erlbench; print(erlbench.__all__)"
```

Public surface:

```python
from erlbench import tool, ToolContext          # author tools in *_tools.py
from erlbench import load_scenario, score, validate_scenario
```

## Rollouts: simulate + score a generated scenario

Once a scenario exists under `env/<scenario>/`, drive it as a live agent ↔
user-simulator conversation and score each task against its `evaluation_criteria`
(DB terminal-state match, gated on a normal end of call). The agent's context holds
only the fixed **base** meta-tools (`KB_search` / `grep` / `unlock_*` / `call_*`)
plus the scenario's **share** tools; every **task** tool is hidden and reached via
`unlock_*_discoverable_tool` + `call_*_discoverable_tool`. It is built entirely on
`erlbench`. A single run can cover multiple scenarios, sharing a per-scenario
DB/KB/retrieval-index cache.

Requires an OpenAI-compatible proxy in the environment (`OPENAI_API_BASE`,
`OPENAI_API_KEY`).

```bash
# All tasks in the default scenario (env/home_appliance_warranty_provider), 1 trial each:
./run.sh

# One task, 3 trials:
TASK_IDS="service_claim_dispatch/0" NUM_TRIALS=3 ./run.sh

# Several scenarios in one run (shares a per-scenario DB/KB/index cache):
SCENARIOS="env/home_appliance_warranty_provider env/regional_pet_insurer" ./run.sh
```

Results land in `data/simulations/<SAVE_TO>/results.json`. Full details, the
base/share/task tool model, and the scoring gate are documented in
[`rollout/README.md`](rollout/README.md).
