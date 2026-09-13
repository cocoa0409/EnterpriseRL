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
# Requires an OpenAI-compatible proxy in the environment:
#   OPENAI_API_BASE  (e.g. https://openai.app.msh.team/v1)
#   OPENAI_API_KEY
# Results land in data/simulations/<SAVE_TO>/results.json; per-task trajectories (with
# --verbose-logs, the default) under data/simulations/<SAVE_TO>/artifacts/<scenario>/.
#
set -euo pipefail

# --- cd to repo root (this script lives at the repo root) ---------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- preflight: proxy credentials must be in the environment ------------------
for var in OPENAI_API_KEY OPENAI_API_BASE; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set. Export it (or source ~/.bashrc) first." >&2
    exit 1
  fi
done

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
# proxy (OPENAI_API_BASE); `openai/responses/<m>` targets the Responses API path,
# where the proxy allows `tools` together with reasoning effort.
: "${AGENT_LLM:=openai/responses/gpt-5.6-sol}"
: "${USER_LLM:=openai/responses/gpt-5.4-mini-construct}"
# Reasoning effort per role. On the gpt-5.x Responses models this proxy serves, the
# supported levels are: none|minimal|low|medium|high|xhigh|max  (max is the top tier
# on gpt-5.6; xhigh on gpt-5.1-codex-max/5.2).
: "${AGENT_EFFORT:=max}"
: "${USER_EFFORT:=medium}"
: "${AGENT_TEMPERATURE:=1.0}"   # kimi requires 1; anthropic too
: "${USER_TEMPERATURE:=1.0}"
: "${AGENT_MAX_TOKENS:=32768}"
: "${USER_MAX_TOKENS:=32768}"

# --- reasoning-effort format construction (built HERE in the shell) -----------
# litellm 1.92 has NO working unified reasoning-effort path for the Responses API on
# this proxy: a flat top-level `reasoning_effort` is silently IGNORED (the proxy never
# validates or applies it — even a bogus value is accepted). The proxy only honors the
# Responses API's NATIVE nested object `reasoning={"effort": <level>}` (verified: a bogus
# level THERE returns 400 "Supported values are: none, minimal, low, medium, high, xhigh,
# and max"). So we build the per-role llm-args JSON ourselves, choosing the shape by model
# id, and pass it verbatim via --agent-llm-args / --user-llm-args (rollout uses it as-is,
# bypassing args_for; the nested `reasoning` key survives litellm.drop_params and reaches
# completion()):
#   * openai/responses/<gpt|claude|o*>    -> {"reasoning": {"effort": E}}   (nested; honored)
#   * other gpt/claude (chat completions) -> {"reasoning_effort": E}         (flat; honored there)
#   * everything else (e.g. kimi)         -> no reasoning key
# Set AGENT_LLM_ARGS / USER_LLM_ARGS in the env to override this and pass raw JSON instead.
_derive_args() {  # $1=model  $2=effort  $3=temperature  $4=max_tokens  -> prints litellm-args JSON
  M="$1" E="$2" T="$3" MT="$4" python3 - <<'PY'
import os, json
m   = os.environ["M"].lower()
eff = os.environ["E"].strip()
args = {"temperature": float(os.environ["T"]), "max_tokens": int(os.environ["MT"])}
is_reasoning = any(k in m for k in ("gpt", "claude", "/o1", "/o3", "/o4"))
if is_reasoning and eff:
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
