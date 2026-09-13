# harbor_erl_agent — the harness for the erlbench Harbor tasks

The erlbench tasks are conversations: an agent (the model under test) serves a simulated
customer at a fictional company. This directory is the Harbor agent that runs them:

```
erl_agent.py        the Harbor agent (erl_agent:ErlAgent), on the host: it copies container/
                    into the task container, runs the conversation there, waits for it, and
                    reads back its outputs; it calls no model itself
container/          what runs inside the task container:
  run_episode.py    one conversation: the agent and the customer simulator (their models
                    called from the container) over the task's own engine, in one process
  rollout/          the conversation loop (turn-taking, stop tokens, limits, LLM client)
```

One harness runs every task: the tools, the knowledge base and the database are each task's
own, in its container. The container needs the network (it calls the models); the Python
packages the conversation needs are part of every task image.

```bash
# Run from the directory that holds harbor_tasks/ and harbor_erl_agent/; harbor writes each
# job to ./jobs/<timestamp>/. 64 trials at a time, every task attempted twice.

# reference solution (oracle): must score 1.0 on every task
harbor run -p harbor_tasks -a oracle -n 64 -k 2

# rollout: agent openai.gpt-6-astra (reasoning effort max),
#          customer simulator openai.gpt-5.4 (reasoning effort medium), same endpoint
AGENT_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 AGENT_API_KEY=<API key> \
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \
    -m openai/responses/openai.gpt-6-astra \
    --ak user_model=openai/responses/openai.gpt-5.4 \
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \
    -n 64 -k 2

# rollout: agent global.anthropic.claude-opus-4-8 (Anthropic Messages API on bedrock-runtime,
#          reasoning effort max), customer simulator openai.gpt-5.4 on its own endpoint
AGENT_API_BASE=https://bedrock-runtime.us-west-2.amazonaws.com/anthropic AGENT_API_KEY=<API key> \
USER_API_BASE=https://bedrock-mantle.us-west-2.api.aws/openai/v1 USER_API_KEY=<API key> \
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \
    -m anthropic/global.anthropic.claude-opus-4-8 \
    --ak user_model=openai/responses/openai.gpt-5.4 \
    --ak reasoning_effort=max --ak user_reasoning_effort=medium \
    -n 64 -k 2

# a single task: add  -i <task directory name>
```

Harbor imports a custom agent by module name (`-a module:Class`), so this directory goes on
`PYTHONPATH`; `PYTHONDONTWRITEBYTECODE` keeps a `__pycache__/` out of it. Each trial's
conversation runs in its own container, so `-n` scales with the machine's containers and the
model endpoint's quota.

Each model is three things, given at launch — nothing provider-specific:

| | agent | customer simulator |
|---|---|---|
| model `<protocol>/<model id>` | `-m` | `--ak user_model=` |
| base URL of its endpoint | `AGENT_API_BASE` | `USER_API_BASE` (default: the agent's) |
| API key | `AGENT_API_KEY` | `USER_API_KEY` (default: the agent's) |

The protocol is `openai/` for an OpenAI-compatible endpoint (`openai/responses/` for its
Responses API) or `anthropic/` for an Anthropic-compatible one (Messages API); the model id
after it is the one that endpoint expects — Claude Opus 4.8 is `global.anthropic.claude-opus-4-8`
(or `us.` …, an inference profile) on bedrock-runtime, `anthropic.claude-opus-4-8` on
bedrock-mantle. The variables come from the environment harbor is launched with (or
`--ae NAME=value`). The keys reach the run in a file inside the container that it deletes as
soon as it has read it.

Options (`--ak key=value`): `user_model`, `reasoning_effort`, `user_reasoning_effort`,
`temperature`, `user_temperature`, `max_tokens`, `user_max_tokens`, `agent_llm_args` /
`user_llm_args` (litellm keyword arguments as JSON), `request_timeout`, `max_attempts`
(0 = retry forever), `max_steps` (200), `max_errors` (10).

Per trial it writes, under the trial's `agent/`: `transcript.json`, `agent_trajectory.json`,
`user_trajectory.json`, `rollout.json`, per-call `llm_debug/`, `erl_agent.log`, and an ATIF
`trajectory.json`.
