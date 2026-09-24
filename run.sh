#!/usr/bin/env bash
#
# Run agent <-> user-simulator rollouts over one or more erlbench scenarios and score them.
#
# Built entirely on this repo's own scaffold (erlbench/ + rollout/). The agent's tools are
# only the fixed BASE meta tools (KB_search/grep/unlock/call) plus each scenario's SHARE
# tools; every task tool is hidden and reached through unlock_*_discoverable_tool + call_*.
#
# By default it runs EVERY scenario under env/. Any parameter can be overridden from the
# environment, e.g.:
#   NUM_TRIALS=3 ./run.sh                                          # 3 trials, all scenarios
#   SCENARIOS="env/home_appliance_warranty_provider" ./run.sh     # just one scenario
#   TASK_IDS="service_claim_dispatch/0" ./run.sh                  # a single task
#   AGENT_EFFORT=high ./run.sh                                    # lower the agent reasoning effort
#
# Models are served by AWS Bedrock's OpenAI-compatible `bedrock-mantle` endpoint
# (https://bedrock-mantle.us-west-2.api.aws/openai/v1 — the only mantle Region that
# serves openai.gpt-6-astra), authenticated with a Bedrock API key:
#   AWS_BEARER_TOKEN_BEDROCK   (the Bedrock long-term API key)
# It is exported to litellm as OPENAI_API_KEY, and OPENAI_API_BASE defaults to the
# mantle URL (BEDROCK_API_BASE overrides it). An OPENAI_API_KEY / OPENAI_API_BASE
# already in the environment wins, so the script still works against any other
# OpenAI-compatible endpoint.
# Results land in data/simulations/<SAVE_TO>/results.json; per-task trajectories (with
# --verbose-logs, the default) under data/simulations/<SAVE_TO>/artifacts/<scenario>/.
#
set -euo pipefail

# --- cd to repo root (this script lives at the repo root) ---------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- preflight: endpoint + credentials ----------------------------------------
# Exported (not passed as CLI flags) so the key never shows up in `ps` output.
: "${BEDROCK_API_BASE:=https://bedrock-mantle.us-west-2.api.aws/openai/v1}"
export OPENAI_API_BASE="${OPENAI_API_BASE:-${BEDROCK_API_BASE}}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-${AWS_BEARER_TOKEN_BEDROCK:-}}"
if [[ -z "${OPENAI_API_KEY}" ]]; then
  echo "ERROR: no API key. Export AWS_BEARER_TOKEN_BEDROCK (the Bedrock API key; or source ~/.bashrc) first." >&2
  exit 1
fi

# --- scenario + task selection (override via env) -----------------------------
# Scenarios run in ONE process, sharing the per-scenario world cache (DB/KB/index
# built once each). Precedence:
#   SCENARIOS="env/a env/b"  (explicit list)  >  SCENARIO=env/x  (single)  >
#   DEFAULT: every scenario under env/ (each dir with blueprint/blueprint.yaml,
#   or a root-level blueprint.yaml for legacy scenarios).
: "${ENV_ROOT:=env}"          # where scenarios live
: "${SCENARIO:=}"             # optional single scenario dir (overrides the all-scenarios default)
: "${DIFFICULTY:=all}"                              # a difficulty dir, or "all"
: "${TASK_IDS:=}"                                   # e.g. "service_claim_dispatch/0" (space-separated)
: "${NUM_TASKS:=}"                                  # first N selected tasks (per scenario)

if [[ -z "${SCENARIOS:-}" ]]; then
  if [[ -n "${SCENARIO}" ]]; then
    SCENARIOS="${SCENARIO}"
  else   # default: discover every scenario dir under env/
    SCENARIOS="$(for d in "${ENV_ROOT}"/*/; do [[ -f "${d}blueprint/blueprint.yaml" || -f "${d}blueprint.yaml" ]] && printf '%s ' "${d%/}"; done)"
  fi
fi
if [[ -z "${SCENARIOS// /}" ]]; then
  echo "ERROR: no scenarios found under ${ENV_ROOT}/ (a scenario dir needs blueprint/blueprint.yaml)." >&2
  exit 1
fi

# --- rollout parameters (override via env) ------------------------------------
: "${NUM_TRIALS:=1}"          # rollouts per task -> pass@1 averaged over trials
: "${MAX_STEPS:=200}"          # LLM generations per rollout before MAX_STEPS
: "${MAX_ERRORS:=10}"         # tool errors before MAX_ERRORS
: "${MAX_CONCURRENCY:=1000}"     # concurrent rollouts
# Exported so rollout/llm.py sizes litellm's process-wide httpx pool to match (the
# pool hard-caps in-flight requests; below MAX_CONCURRENCY it throttles everything).
export MAX_CONCURRENCY

# --- models (litellm ids) -----------------------------------------------------
# litellm handles provider routing: a leading `openai/` targets the OpenAI-compatible
# endpoint (OPENAI_API_BASE); `openai/responses/<m>` targets its Responses API path.
# The agent MUST use the Responses API: on Bedrock, gpt-6-astra rejects function tools
# together with reasoning_effort on /chat/completions ("To use function tools, use
# /v1/responses").
#   agent: openai.gpt-6-astra  (Bedrock model card: model-card-openai-gpt-6-astra)
#   user : openai.gpt-5.4      (Bedrock model card: model-card-openai-gpt-54)
: "${AGENT_LLM:=openai/responses/openai.gpt-6-astra}"
: "${USER_LLM:=openai/responses/openai.gpt-5.4}"
# Reasoning effort per role, as verified on bedrock-mantle (an unsupported level 400s):
#   openai.gpt-6-astra : low|medium|high|xhigh|max   (no none)
#   openai.gpt-5.4     : none|low|medium|high|xhigh  (no max)
: "${AGENT_EFFORT:=max}"
: "${USER_EFFORT:=medium}"
: "${AGENT_TEMPERATURE:=1.0}"   # kimi requires 1; anthropic too
: "${USER_TEMPERATURE:=1.0}"
: "${AGENT_MAX_TOKENS:=32768}"
: "${USER_MAX_TOKENS:=32768}"

# --- reasoning-effort format construction (built HERE in the shell) -----------
# litellm 1.92 has NO working unified reasoning-effort path for the Responses API: a
# flat top-level `reasoning_effort` is silently DROPPED before the request is sent (even
# a bogus value is accepted). Only the Responses API's NATIVE nested object
# `reasoning={"effort": <level>}` reaches the server (verified on bedrock-mantle: a bogus
# level THERE returns 400 "Supported values are: 'none', 'low', 'medium', 'high', 'xhigh',
# and 'max'"). So we build the per-role llm-args JSON ourselves, choosing the shape by model
# id, and pass it verbatim via --agent-llm-args / --user-llm-args (rollout uses it as-is,
# bypassing args_for; the nested `reasoning` key survives litellm.drop_params and reaches
# completion()):
#   * responses/ routes -> {"reasoning": {"effort": E}}
#   * other routes      -> {"reasoning_effort": E}
#   * empty effort      -> no reasoning key
# Set AGENT_LLM_ARGS / USER_LLM_ARGS in the env to override this and pass raw JSON instead.
_derive_args() {  # $1=model  $2=effort  $3=temperature  $4=max_tokens  -> prints litellm-args JSON
  M="$1" E="$2" T="$3" MT="$4" python3 - <<'PY'
import os, json
m   = os.environ["M"].lower()
eff = os.environ["E"].strip()
args = {"temperature": float(os.environ["T"]), "max_tokens": int(os.environ["MT"])}
if eff:
    if "responses/" in m:
        args["reasoning"] = {"effort": eff}     # Responses API: nested object, honored by the proxy
    else:
        args["reasoning_effort"] = eff          # Chat Completions: flat, honored/translated
print(json.dumps(args, separators=(",", ":")))
PY
}
: "${AGENT_LLM_ARGS:=$(_derive_args "${AGENT_LLM}" "${AGENT_EFFORT}" "${AGENT_TEMPERATURE}" "${AGENT_MAX_TOKENS}")}"
: "${USER_LLM_ARGS:=$(_derive_args "${USER_LLM}" "${USER_EFFORT}" "${USER_TEMPERATURE}" "${USER_MAX_TOKENS}")}"
# Optional PER-ROLE endpoint override; empty -> global OPENAI_API_BASE/KEY (litellm reads them).
: "${AGENT_API_BASE:=}"
: "${AGENT_API_KEY:=}"
: "${USER_API_BASE:=}"
: "${USER_API_KEY:=}"
: "${REQUEST_TIMEOUT:=0}"     # per-call timeout seconds passed to litellm (0 = litellm default)
# LLM retry cap. 0 = retry EVERY generation error forever (a transient proxy/model
# error never kills a rollout). Set a positive integer to bound it.
: "${MAX_ATTEMPTS:=0}"

# --- logging / output ---------------------------------------------------------
: "${LOG_LEVEL:=INFO}"        # DEBUG|INFO|WARNING|ERROR  (INFO = one line per LLM call with role/step/model/tokens/latency; retries log at WARNING; set WARNING to quiet)
: "${VERBOSE_LOGS:=1}"        # 1 -> write per-task agent/user trajectories under <save_to>/artifacts/
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
AGENT_TAG="${AGENT_LLM##*/}"
# A timestamp postfix is ALWAYS appended, so the data/ output dir and the log never
# collide across runs — even when SAVE_TO is given explicitly.
SAVE_TO="${SAVE_TO:-${AGENT_TAG}}_${TIMESTAMP}"

mkdir -p logs
LOG_FILE="logs/${SAVE_TO}.log"

# --- assemble optional flags --------------------------------------------------
SEL_ARGS=()
[[ -n "${DIFFICULTY}" ]] && SEL_ARGS+=(--difficulty "${DIFFICULTY}")
[[ -n "${TASK_IDS}" ]]   && SEL_ARGS+=(--task-ids ${TASK_IDS})   # unquoted: split ids
[[ -n "${NUM_TASKS}" ]]  && SEL_ARGS+=(--num-tasks "${NUM_TASKS}")

ARGS=()
[[ -n "${AGENT_LLM_ARGS}" ]] && ARGS+=(--agent-llm-args "${AGENT_LLM_ARGS}")
[[ -n "${USER_LLM_ARGS}" ]]  && ARGS+=(--user-llm-args "${USER_LLM_ARGS}")
[[ -n "${AGENT_API_BASE}" ]] && ARGS+=(--agent-api-base "${AGENT_API_BASE}")
[[ -n "${AGENT_API_KEY}" ]]  && ARGS+=(--agent-api-key "${AGENT_API_KEY}")
[[ -n "${USER_API_BASE}" ]]  && ARGS+=(--user-api-base "${USER_API_BASE}")
[[ -n "${USER_API_KEY}" ]]   && ARGS+=(--user-api-key "${USER_API_KEY}")
[[ "${VERBOSE_LOGS}" == "1" ]] && ARGS+=(--verbose-logs)

# --- pick a python launcher (uv if present, else the project venv) ------------
if command -v uv >/dev/null 2>&1; then
  PY=(uv run python)
elif [[ -x .venv/bin/python ]]; then
  PY=(.venv/bin/python)
else
  PY=(python3)
fi

echo "=================================================================="
echo " enterprise_rl rollout"
echo "   scenarios    : ${SCENARIOS}"
echo "   selection    : difficulty=${DIFFICULTY} tasks=${TASK_IDS:-${NUM_TASKS:-all}}"
echo "   agent        : ${AGENT_LLM}"
echo "     llm_args   : ${AGENT_LLM_ARGS}"
echo "   user         : ${USER_LLM}"
echo "     llm_args   : ${USER_LLM_ARGS}"
echo "   trials       : ${NUM_TRIALS}   max_steps=${MAX_STEPS} max_errors=${MAX_ERRORS}"
echo "   retry        : max_attempts=${MAX_ATTEMPTS} (0 = infinite)  timeout=${REQUEST_TIMEOUT}s"
echo "   concurrency  : ${MAX_CONCURRENCY}"
echo "   save_to      : data/simulations/${SAVE_TO}/results.json"
echo "   log          : ${LOG_FILE}"
echo "=================================================================="

PYTHONUNBUFFERED=1 "${PY[@]}" -u -m rollout \
  --scenarios ${SCENARIOS} \
  --num-trials "${NUM_TRIALS}" \
  --max-steps "${MAX_STEPS}" \
  --max-errors "${MAX_ERRORS}" \
  --max-concurrency "${MAX_CONCURRENCY}" \
  --agent-llm "${AGENT_LLM}" \
  --user-llm "${USER_LLM}" \
  --agent-effort "${AGENT_EFFORT}" \
  --user-effort "${USER_EFFORT}" \
  --agent-max-tokens "${AGENT_MAX_TOKENS}" \
  --user-max-tokens "${USER_MAX_TOKENS}" \
  --request-timeout "${REQUEST_TIMEOUT}" \
  --max-attempts "${MAX_ATTEMPTS}" \
  --log-level "${LOG_LEVEL}" \
  --save-to "${SAVE_TO}" \
  "${SEL_ARGS[@]}" \
  "${ARGS[@]}" \
  2>&1 | tee "${LOG_FILE}"

echo ""
echo "Done. Results: data/simulations/${SAVE_TO}/results.json"
