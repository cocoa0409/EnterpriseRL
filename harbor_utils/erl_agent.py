"""The erlbench harness for Harbor: runs each conversation inside its task container.

    AGENT_API_BASE=<base url> AGENT_API_KEY=<key> [USER_API_BASE=... USER_API_KEY=...] \\
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=harbor_erl_agent harbor run -p harbor_tasks -a erl_agent:ErlAgent \\
        -m <agent model> --ak user_model=<customer model> -n 64 -k 2

A task is a conversation: the agent (the model under test) serves a customer simulator, each
turn a message to the other side or a tool call on the task's engine. The whole conversation
runs inside the task container — ``setup`` copies container/ (run_episode.py and the
conversation loop, rollout/) into it, and ``run`` starts ``run_episode.py`` there with
``environment.exec``. Both models are called from the container, and every tool runs in that
same process on the task's own engine. This class only launches the run, waits for it, and
reads back what it wrote to the trial's agent/ directory; it calls no model itself.

Each of the two models is three things, nothing provider-specific:

  * the model — ``<protocol>/<model id>``: ``openai/...`` for an OpenAI-compatible endpoint
    (``openai/responses/...`` to use its Responses API), ``anthropic/...`` for an
    Anthropic-compatible one (the Messages API);
  * the endpoint's base URL — ``AGENT_API_BASE`` / ``USER_API_BASE``;
  * its API key — ``AGENT_API_KEY`` / ``USER_API_KEY``.

The customer simulator uses the agent's base URL and key unless ``USER_API_*`` are set. They
are read from the environment harbor is launched with (or ``--ae``), and the keys are copied
into the container in a file the run deletes as soon as it has read it. Defaults for the
models: agent ``openai/responses/openai.gpt-6-astra`` (reasoning effort ``max``), customer
simulator ``openai/responses/openai.gpt-5.4`` (``medium``). Every option is an
``--ak key=value``.

The agent's system prompt is the task's instruction.md (harbor's ``instruction``); the
customer simulator's is in the task's episode.json.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import uuid
from pathlib import Path
from typing import override

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trajectories import (
    Agent as AtifAgent,
    FinalMetrics,
    Metrics,
    Observation,
    ObservationResult,
    Step,
    ToolCall as AtifToolCall,
    Trajectory,
)

HARNESS_VERSION = "2.0.0"
DEFAULT_AGENT_MODEL = "openai/responses/openai.gpt-6-astra"
DEFAULT_USER_MODEL = "openai/responses/openai.gpt-5.4"
DEFAULT_MAX_TOKENS = 32 * 1024
ROLE_ENV = {"agent": "AGENT", "user": "USER"}  # <ROLE>_API_BASE / <ROLE>_API_KEY
AGENT_GREETING = "Hi! Thank you for contacting us. How can I help you today?"

CONTAINER_DIR = "/opt/erl_agent"               # where container/ goes inside the task container
SECRETS_FILE = "/tmp/erl_agent_secrets.json"   # deleted by run_episode.py once read
PID_FILE = "/tmp/erl_agent.pid"                # written by run_episode.py; SIGTERM stops the run
_HERE = Path(__file__).resolve().parent


class ErlAgent(BaseAgent):
    """Launches rollout's conversation loop inside the task container and waits for it."""

    SUPPORTS_ATIF = True

    def __init__(
        self,
        logs_dir: Path,
        model_name: str | None = None,
        *args,
        user_model: str | None = None,
        reasoning_effort: str = "max",
        user_reasoning_effort: str = "medium",
        temperature: float | str = 1.0,
        user_temperature: float | str = 1.0,
        max_tokens: int | str = DEFAULT_MAX_TOKENS,
        user_max_tokens: int | str = DEFAULT_MAX_TOKENS,
        agent_llm_args: str | None = None,      # litellm keyword arguments as JSON, used verbatim
        user_llm_args: str | None = None,
        request_timeout: float | str = 0,       # per LLM call; 0 = litellm's default
        max_attempts: int | str = 0,            # LLM retry cap; 0 = retry forever
        max_steps: int | str = 200,
        max_errors: int | str = 10,
        **kwargs,
    ):
        super().__init__(logs_dir, model_name, *args, **kwargs)
        # --ak values arrive as strings.
        self._models = {"agent": model_name or DEFAULT_AGENT_MODEL,
                        "user": user_model or DEFAULT_USER_MODEL}
        self._efforts = {"agent": str(reasoning_effort), "user": str(user_reasoning_effort)}
        self._temps = {"agent": float(temperature), "user": float(user_temperature)}
        self._max_tokens = {"agent": int(max_tokens), "user": int(user_max_tokens)}
        self._args_override = {"agent": agent_llm_args or "", "user": user_llm_args or ""}
        self._request_timeout = float(request_timeout)
        self._max_attempts = int(max_attempts)
        self._max_steps = int(max_steps)
        self._max_errors = int(max_errors)

    @staticmethod
    @override
    def name() -> str:
        return "erlbench"

    @override
    def version(self) -> str | None:
        return HARNESS_VERSION

    # ── configuration ────────────────────────────────────────────────────────────────────

    def _endpoint(self, role: str) -> tuple[str | None, str | None]:
        prefix = ROLE_ENV[role]
        return self._get_env(f"{prefix}_API_BASE"), self._get_env(f"{prefix}_API_KEY")

    def _role_config(self, role: str) -> tuple[dict, str]:
        """(settings, key) for one role: the model, its base URL and key (from the launch
        environment: <ROLE>_API_BASE / <ROLE>_API_KEY; the customer simulator falls back to the
        agent's), and its generation settings. The run turns the settings into litellm
        arguments with rollout.llm.args_for (or uses the JSON override verbatim)."""
        base, key = self._endpoint(role)
        if role == "user":
            agent_base, agent_key = self._endpoint("agent")
            base, key = base or agent_base, key or agent_key
        missing = [f"{ROLE_ENV[role]}_API_{name}" for name, value in (("BASE", base), ("KEY", key))
                   if not value]
        if missing:
            raise ValueError(f"set {' and '.join(missing)} (the {role} model's base URL and API key) "
                             "in the environment harbor is launched with")
        settings = {"model": self._models[role], "effort": self._efforts[role],
                    "temperature": self._temps[role], "max_tokens": self._max_tokens[role],
                    "llm_args": self._args_override[role], "api_base": base,
                    "timeout": self._request_timeout}
        return settings, key

    # ── the run ──────────────────────────────────────────────────────────────────────────

    @override
    async def setup(self, environment: BaseEnvironment) -> None:
        self._roles = {role: self._role_config(role) for role in ("agent", "user")}
        await environment.upload_dir(source_dir=_HERE / "container", target_dir=CONTAINER_DIR)

    async def _upload_json(self, environment: BaseEnvironment, obj, target: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / "f.json"
            local.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
            local.chmod(0o600)
            await environment.upload_file(local, target)

    @override
    async def run(self, instruction: str, environment: BaseEnvironment,
                  context: AgentContext) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / "instruction.md"
            local.write_text(instruction, encoding="utf-8")
            await environment.upload_file(local, f"{CONTAINER_DIR}/instruction.md")
        config = {
            "run_id": uuid.uuid4().hex[:6],
            "instruction_file": f"{CONTAINER_DIR}/instruction.md",
            "secrets_file": SECRETS_FILE,
            "roles": {role: settings for role, (settings, _key) in self._roles.items()},
            "max_steps": self._max_steps, "max_errors": self._max_errors,
            "max_attempts": self._max_attempts,
        }
        await self._upload_json(environment, config, f"{CONTAINER_DIR}/config.json")
        await self._upload_json(environment, {f"{role}_api_key": key
                                              for role, (_args, key) in self._roles.items()},
                                SECRETS_FILE)
        try:
            result = await environment.exec(
                f"python3 {CONTAINER_DIR}/run_episode.py {CONTAINER_DIR}/config.json")
        except asyncio.CancelledError:
            # harbor's agent timeout: stop the run inside the container, which records the
            # end of the conversation before it exits.
            try:
                await asyncio.wait_for(environment.exec(
                    f"kill -TERM $(cat {PID_FILE}) 2>/dev/null; sleep 5", timeout_sec=30), 40)
            except BaseException:  # noqa: BLE001 -- best effort
                pass
            raise
        if result.return_code != 0:
            raise RuntimeError(f"run_episode.py exited with {result.return_code}: "
                               f"{(result.stdout or '')[-2000:]}")

    # ── outputs (read back from the trial's agent/ directory) ────────────────────────────

    @override
    def populate_context_post_run(self, context: AgentContext) -> None:
        path = self.logs_dir / "rollout.json"
        if not path.exists():
            return
        report = json.loads(path.read_text(encoding="utf-8"))
        by_role = report.get("usage_by_role") or {}
        context.n_input_tokens = sum(r.get("prompt_tokens", 0) for r in by_role.values())
        context.n_output_tokens = sum(r.get("completion_tokens", 0) for r in by_role.values())
        context.metadata = {
            "termination": report.get("termination"),
            "completed_normally": report.get("completed_normally"),
            "steps": report.get("steps"), "tool_errors": report.get("errors"),
            "num_tool_calls": report.get("num_tool_calls"),
            "error_detail": report.get("error_detail"),
            "agent_model": self._models["agent"], "user_model": self._models["user"],
            "efforts": self._efforts, "usage_by_role": by_role,
            "ran_in": (report.get("harness") or {}).get("host"),
        }
        try:
            self._write_atif(report)
        except Exception as e:  # noqa: BLE001 -- a viewer file must never fail the trial
            self.logger.debug(f"ATIF trajectory skipped: {type(e).__name__}: {e}")

    def _write_atif(self, report: dict) -> None:
        """The agent's side of the conversation as ATIF, from the run's agent_trajectory.json
        (its exact message history) and llm_calls.json (per-call token usage). Each assistant
        message after the fixed greeting is exactly one agent LLM call, in order."""
        traj_path, calls_path = self.logs_dir / "agent_trajectory.json", self.logs_dir / "llm_calls.json"
        if not traj_path.exists():
            return
        msgs = json.loads(traj_path.read_text(encoding="utf-8"))["messages"]
        agent_calls = [c for c in json.loads(calls_path.read_text(encoding="utf-8"))
                       if c["speaker"] == "agent"] if calls_path.exists() else []
        tools = json.loads(traj_path.read_text(encoding="utf-8")).get("tools")
        steps: list[Step] = []
        k, i = 0, 0
        while i < len(msgs):
            m = msgs[i]
            role, content = m.get("role"), m.get("content") or ""
            if role in ("system", "user"):
                steps.append(Step(step_id=len(steps) + 1, source=role, message=content))
            elif role == "assistant" and i == 1 and content == AGENT_GREETING and not m.get("tool_calls"):
                steps.append(Step(step_id=len(steps) + 1, source="agent", message=content,
                                  llm_call_count=0))
            elif role == "assistant":
                usage = (agent_calls[k] if k < len(agent_calls) else {}).get("usage") or {}
                k += 1
                tool_calls = []
                for tc in m.get("tool_calls") or []:
                    raw = tc.get("function", {}).get("arguments")
                    try:
                        parsed = json.loads(raw) if isinstance(raw, str) and raw.strip() else (raw or {})
                    except json.JSONDecodeError:
                        parsed = {"__raw__": raw}
                    tool_calls.append(AtifToolCall(
                        tool_call_id=tc.get("id") or uuid.uuid4().hex,
                        function_name=tc.get("function", {}).get("name", ""),
                        arguments=parsed if isinstance(parsed, dict) else {"value": parsed}))
                results = []
                while i + 1 < len(msgs) and msgs[i + 1].get("role") == "tool":
                    i += 1
                    results.append(ObservationResult(source_call_id=msgs[i].get("tool_call_id"),
                                                     content=msgs[i].get("content")))
                steps.append(Step(
                    step_id=len(steps) + 1, source="agent", model_name=self._models["agent"],
                    reasoning_effort=self._efforts["agent"], message=content,
                    reasoning_content=m.get("reasoning_content") or None,
                    tool_calls=tool_calls or None,
                    observation=Observation(results=results) if results else None,
                    llm_call_count=1,
                    metrics=Metrics(prompt_tokens=usage.get("prompt_tokens"),
                                    completion_tokens=usage.get("completion_tokens")) if usage else None))
            i += 1
        agent_usage = (report.get("usage_by_role") or {}).get("agent") or {}
        trajectory = Trajectory(
            session_id=(report.get("harness") or {}).get("label"),
            agent=AtifAgent(name=self.name(), version=HARNESS_VERSION,
                            model_name=self._models["agent"], tool_definitions=tools),
            steps=steps,
            notes=f"termination={report.get('termination')}; customer simulator {self._models['user']}",
            final_metrics=FinalMetrics(total_prompt_tokens=agent_usage.get("prompt_tokens"),
                                       total_completion_tokens=agent_usage.get("completion_tokens"),
                                       total_steps=len(steps)),
            extra={"user_model": self._models["user"], "usage_by_role": report.get("usage_by_role"),
                   "termination": report.get("termination")},
        )
        (self.logs_dir / "trajectory.json").write_text(
            json.dumps(trajectory.to_json_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
