"""The half-duplex conversation loop between the agent and the customer simulator over one engine."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .llm import LLMClient, LLMError, ToolCall
from .prompts import AGENT_GREETING, detect_stop

if TYPE_CHECKING:
    from erlbench.engine import Engine

NORMAL_TERMINATIONS = {"USER_STOP", "USER_TRANSFER"}


@dataclass
class RolloutResult:
    termination: str
    trajectory: List[dict]
    transcript: List[dict] = field(default_factory=list)
    steps: int = 0
    errors: int = 0
    usage: Dict[str, int] = field(default_factory=dict)
    error_detail: Optional[str] = None
    agent_messages: List[dict] = field(default_factory=list)
    user_messages: List[dict] = field(default_factory=list)
    agent_tools: List[dict] = field(default_factory=list)
    user_tools: List[dict] = field(default_factory=list)
    llm_calls: List[dict] = field(default_factory=list)

    @property
    def completed_normally(self) -> bool:
        return self.termination in NORMAL_TERMINATIONS


class Orchestrator:
    def __init__(self, engine: Engine, agent_client: LLMClient, user_client: LLMClient,
                 agent_system: str, user_system: str, max_steps: int = 80,
                 max_errors: int = 10, max_empty: int = 3, label: str = "",
                 debug_dir: Optional[str] = None):
        self.engine = engine
        self.agent_client = agent_client
        self.user_client = user_client
        self.max_steps = max_steps
        self.max_errors = max_errors
        self.max_empty = max_empty
        self.label = label
        self.debug_dir = debug_dir
        if debug_dir:
            os.makedirs(debug_dir, exist_ok=True)

        self.agent_tools: List[dict] = engine.tool_list("agent")
        self.user_tools: List[dict] = engine.tool_list("user")

        self.agent_msgs: List[dict] = [{"role": "system", "content": agent_system}]
        self.user_msgs: List[dict] = [{"role": "system", "content": user_system}]
        self.trajectory: List[dict] = []
        self.transcript: List[dict] = []
        self.llm_calls: List[dict] = []
        self.steps = 0
        self.errors = 0
        self.empty_streak = 0
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _who(self, speaker: str):
        if speaker == "agent":
            return (self.agent_client, self.agent_msgs, self.user_msgs, self.agent_tools)
        return (self.user_client, self.user_msgs, self.agent_msgs, self.user_tools)

    def _log(self, kind: str, speaker: str, **payload) -> None:
        self.transcript.append({"event": kind, "speaker": speaker, **payload})

    def _account_usage(self, usage: dict) -> None:
        for k in self.usage:
            self.usage[k] += int(usage.get(k, 0) or 0)

    def run(self) -> RolloutResult:
        self.agent_msgs.append({"role": "assistant", "content": AGENT_GREETING})
        self.user_msgs.append({"role": "user", "content": AGENT_GREETING})
        self._log("message", "agent", text=AGENT_GREETING)

        speaker = "user"
        termination = "MAX_STEPS"

        while self.steps < self.max_steps and self.errors < self.max_errors:
            client, own_msgs, other_msgs, tools = self._who(speaker)
            call_tag = f"{self.label} {speaker} step={self.steps + 1}".strip()
            try:
                result = client.chat(own_msgs, tools=tools, tag=call_tag)
            except LLMError as e:
                termination = "LLM_ERROR"
                self._log("llm_error", speaker, detail=str(e))
                return self._finish(termination, error_detail=str(e))
            self.steps += 1
            self._account_usage(result.usage)
            self._record_call(speaker, client, own_msgs, tools, result)

            if result.has_tool_calls:
                own_msgs.append(result.raw_message)
                self._handle_tool_calls(speaker, result.tool_calls, own_msgs)
                self.empty_streak = 0
                continue

            text = (result.content or "").strip()
            own_msgs.append(result.raw_message)

            if not text:
                self.empty_streak += 1
                self._log("empty", speaker)
                if self.empty_streak >= self.max_empty:
                    termination = "EMPTY"
                    break
                own_msgs.append({"role": "user",
                                 "content": "(Please respond to the customer or take an "
                                            "action.)" if speaker == "agent"
                                            else "(Please continue.)"})
                continue
            self.empty_streak = 0

            if speaker == "user":
                stop = detect_stop(text)
                if stop:
                    termination = stop
                    self._log("stop", speaker, token=text)
                    break
                other_msgs.append({"role": "user", "content": text})
                self._log("message", speaker, text=text)
                speaker = "agent"
            else:
                other_msgs.append({"role": "user", "content": text})
                self._log("message", speaker, text=text)
                speaker = "user"

        else:
            termination = "MAX_ERRORS" if self.errors >= self.max_errors else "MAX_STEPS"

        return self._finish(termination)

    def _handle_tool_calls(self, speaker: str, calls: List[ToolCall],
                           own_msgs: List[dict]) -> None:
        owner = speaker
        for tc in calls:
            name = tc.name
            args = tc.arguments if isinstance(tc.arguments, dict) else {}
            output = self.engine.call(owner, name, args)
            output = "" if output is None else str(output)
            self.trajectory.append({"owner": owner, "tool": name, "arguments": args})
            is_error = output.startswith("Error")
            if is_error:
                self.errors += 1
            own_msgs.append({"role": "tool", "tool_call_id": tc.id, "content": output})
            self._log("tool_call", speaker, tool=name, arguments=args,
                      output=output, error=is_error)

    def _record_call(self, speaker: str, client: LLMClient, request_msgs: List[dict],
                     tools: List[dict], result) -> None:
        call_name = "agent_response" if speaker == "agent" else "user_simulator_response"
        call = {
            "seq": len(self.llm_calls) + 1,
            "speaker": speaker,
            "call_name": call_name,
            "request": {
                "model": client.model_id,
                "messages": [dict(m) for m in request_msgs],
                "tools": tools,
                "tool_choice": "auto" if tools else None,
                "n_tools": len(tools or []),
            },
            "response": {
                "content": result.content,
                "reasoning_content": result.reasoning_content,
                "tool_calls": [
                    {"name": tc.name, "arguments": tc.arguments} for tc in result.tool_calls
                ],
                "finish_reason": result.finish_reason,
                "usage": result.usage,
            },
        }
        self.llm_calls.append(call)
        if self.debug_dir:
            path = os.path.join(self.debug_dir, f"{call['seq']:03d}_{call_name}.json")
            try:
                with open(path, "w") as f:
                    json.dump(call, f, ensure_ascii=False, indent=2)
            except OSError:
                pass

    def _finish(self, termination: str, error_detail: Optional[str] = None) -> RolloutResult:
        return RolloutResult(
            termination=termination, trajectory=list(self.trajectory),
            transcript=list(self.transcript), steps=self.steps, errors=self.errors,
            usage=dict(self.usage), error_detail=error_detail,
            agent_messages=[dict(m) for m in self.agent_msgs],
            user_messages=[dict(m) for m in self.user_msgs],
            agent_tools=self.agent_tools, user_tools=self.user_tools,
            llm_calls=list(self.llm_calls))
