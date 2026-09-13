#!/usr/bin/env python3
"""One conversation, run inside the task container.

    python3 run_episode.py <config.json>

The agent (the model under test) and the customer simulator — both LLMs, called through
litellm from this process — take turns over the task's own engine: rollout/'s conversation
loop drives a ``runtime.Session``, so every tool call runs here, in-process, and is recorded
for the verifier. Everything the run produces goes to /logs/agent (the trial's agent/).

config.json (written by erl_agent.py): per role (agent, customer) the model, reasoning effort,
temperature, max_tokens, an optional litellm-arguments JSON override and the endpoint;
max_steps, max_errors, max_attempts; the run id and where the agent's system prompt is (the
task's instruction.md). The customer simulator's system prompt is the task's episode.json.
The API keys arrive in a secrets file that is deleted as soon as it is read.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import socket
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK_DIR = Path(os.environ.get("ERL_TASK_DIR") or "/opt/task")
LOGS_DIR = Path(os.environ.get("ERL_LOGS_DIR") or "/logs/agent")
PID_FILE = Path(os.environ.get("ERL_PID_FILE") or "/tmp/erl_agent.pid")
sys.path.insert(0, str(HERE))                      # rollout/
sys.path.insert(0, str(TASK_DIR / "runtime"))      # the task's runtime and engine

import runtime as rt  # noqa: E402
from rollout.llm import LLMClient, LLMError, args_for  # noqa: E402
from rollout.orchestrator import NORMAL_TERMINATIONS, Orchestrator  # noqa: E402

_STOP = threading.Event()


class _Client(LLMClient):
    """LLMClient that gives up at its next call or retry once the run is told to stop
    (SIGTERM, sent when harbor's agent timeout hits): with max_attempts=0 it would otherwise
    retry forever."""

    def chat(self, messages, tools=None, tag=""):
        if _STOP.is_set():
            raise LLMError(f"stopped [{tag}]")
        return super().chat(messages, tools=tools, tag=tag)

    def _backoff(self, attempt: int) -> float:
        if _STOP.is_set():
            raise LLMError("stopped during retry backoff")
        return super()._backoff(attempt)


def _dump(name: str, obj) -> None:
    with open(LOGS_DIR / name, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _read_secrets(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        secrets = json.load(f)
    os.unlink(path)
    return secrets


def _llm_args(role: dict) -> dict:
    """litellm arguments for one role, as rollout.runner builds them: the JSON override
    verbatim, else args_for(model, effort, temperature, max_tokens); then the endpoint."""
    args = (json.loads(role["llm_args"]) if role.get("llm_args") else
            args_for(role["model"], role["effort"], temperature=role["temperature"],
                     max_tokens=role["max_tokens"]))
    args["api_base"] = role["api_base"]
    if role.get("timeout") and "timeout" not in args:
        args["timeout"] = role["timeout"]
    return args


def _usage_by_role(result) -> dict:
    out = {r: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "calls": 0}
           for r in ("agent", "user")}
    for call in (result.llm_calls if result else []):
        usage, role = call["response"].get("usage") or {}, call["speaker"]
        out[role]["calls"] += 1
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            out[role][k] += int(usage.get(k, 0) or 0)
    return out


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    secrets = _read_secrets(cfg["secrets_file"])
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    signal.signal(signal.SIGTERM, lambda *_: _STOP.set())

    episode = rt.load_episode()
    label = f"{episode['task_id']}#{cfg['run_id']}"
    handler = logging.FileHandler(LOGS_DIR / "erl_agent.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    log = logging.getLogger("rollout")
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    roles = cfg["roles"]
    llm_args = {role: _llm_args(roles[role]) for role in ("agent", "user")}
    log.info("%s | agent %s | customer %s | running in %s", label, roles["agent"]["model"],
             roles["user"]["model"], socket.gethostname())

    session = rt.open_session(episode)
    clients = {role: _Client(roles[role]["model"],
                             {**llm_args[role], "api_key": secrets[f"{role}_api_key"]},
                             max_attempts=cfg["max_attempts"])
               for role in ("agent", "user")}
    orch = Orchestrator(
        engine=session, agent_client=clients["agent"], user_client=clients["user"],
        agent_system=Path(cfg["instruction_file"]).read_text(encoding="utf-8"),
        user_system=episode["user_system_prompt"],
        max_steps=cfg["max_steps"], max_errors=cfg["max_errors"], label=label,
        debug_dir=str(LOGS_DIR / "llm_debug"))

    result, error = None, None
    try:
        result = orch.run()
    except BaseException as e:  # noqa: BLE001 -- recorded as the end of the conversation
        error = e
        log.exception("%s | the conversation loop failed", label)

    if result is not None:
        termination = "CANCELLED" if _STOP.is_set() else result.termination
        report = {"termination": termination,
                  "completed_normally": termination in NORMAL_TERMINATIONS,
                  "steps": result.steps, "errors": result.errors, "usage": result.usage,
                  "error_detail": result.error_detail, "num_tool_calls": len(result.trajectory)}
    else:
        report = {"termination": "HARNESS_ERROR", "completed_normally": False,
                  "error_detail": f"{type(error).__name__}: {error}"}
    report["harness"] = {"label": label, "agent_model": roles["agent"]["model"],
                         "user_model": roles["user"]["model"], "max_steps": cfg["max_steps"],
                         "max_errors": cfg["max_errors"], "host": socket.gethostname()}
    if not session.ended:
        session.end(report)

    def names(tools):
        return [t.get("function", {}).get("name") for t in (tools or [])]

    _dump("rollout.json", {**report, "usage_by_role": _usage_by_role(result),
                           "llm_args": llm_args})
    if result is not None:
        _dump("transcript.json", result.transcript)
        _dump("erl_trajectory.json", result.trajectory)
        _dump("agent_trajectory.json", {"role": "agent", "tool_names": names(result.agent_tools),
                                        "tools": result.agent_tools, "messages": result.agent_messages})
        _dump("user_trajectory.json", {"role": "user", "tool_names": names(result.user_tools),
                                       "tools": result.user_tools, "messages": result.user_messages})
        _dump("llm_calls.json", [{"speaker": c["speaker"], "usage": c["response"].get("usage") or {}}
                                 for c in result.llm_calls])
    log.info("%s | ended: %s", label, report["termination"])
    handler.close()
    for dirpath, _dirs, files in os.walk(LOGS_DIR):        # readable/removable by the host user
        os.chmod(dirpath, 0o777)
        for fn in files:
            os.chmod(os.path.join(dirpath, fn), 0o666)
    print(json.dumps({"termination": report["termination"], "steps": report.get("steps"),
                      "tool_calls": report.get("num_tool_calls")}))
    return 0 if error is None else 1


if __name__ == "__main__":
    sys.exit(main())
