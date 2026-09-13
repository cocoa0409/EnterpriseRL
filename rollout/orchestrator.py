"""The half-duplex agent <-> user-simulator loop over one erlbench Engine.

One :class:`Orchestrator` drives a single task: it seeds nothing itself (the caller
hands it an ``Engine`` already built for the task via ``scenario.engine_for(task)``),
then alternates turns between the agent LLM and the user-simulator LLM. The agent
opens with a fixed greeting; thereafter each side, on its turn, may either speak a
plain-text message (which is relayed to the other side and passes the floor) or make
a tool call (routed to the Engine, whose string result is fed back to the caller,
keeping the floor). The user simulator ends the call with a stop token.

Every tool call is appended to ``trajectory`` in the exact ``{owner, tool, arguments}``
shape ``erlbench.scoring`` expects — an agent's hidden-tool call is recorded as the
``call_agent_discoverable_tool`` wrapper it really issued, which ``scoring._resolve``
unwraps back to the underlying task tool. So scoring the run is just
``erlbench.score(scenario, task, task["evaluation_criteria"], result.trajectory)``.

Neither side sees the other's tool traffic — only the plain-text messages — exactly
like the two participants in a real support call.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from erlbench.engine import Engine

from .llm import LLMClient, LLMError, ToolCall
from .prompts import AGENT_GREETING, detect_stop

# Terminations that count as a "normal" completion for reward gating.
NORMAL_TERMINATIONS = {"USER_STOP", "USER_TRANSFER"}


@dataclass
class RolloutResult:
    termination: str                       # why the loop ended
    trajectory: List[dict]                 # [{owner, tool, arguments}, ...] for scoring
    transcript: List[dict] = field(default_factory=list)  # human-readable event log
    steps: int = 0                         # LLM generations
    errors: int = 0                        # tool calls that returned "Error: ..."
    usage: Dict[str, int] = field(default_factory=dict)
    error_detail: Optional[str] = None     # populated on LLM_ERROR
    agent_messages: List[dict] = field(default_factory=list)  # final agent history
    user_messages: List[dict] = field(default_factory=list)   # final user history
    agent_tools: List[dict] = field(default_factory=list)     # tool schemas the agent could use
    user_tools: List[dict] = field(default_factory=list)      # tool schemas the user could use
    llm_calls: List[dict] = field(default_factory=list)       # per-turn request+response

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
        self.label = label            # rollout tag prefix: "<scenario>/<difficulty>/<index> trial=<t>"
        # When set, every LLM call's request+response debug record is STREAMED to
        # <debug_dir>/<seq>_<call_name>.json the moment the call returns — so a
        # running (or crashed) rollout can be inspected mid-flight instead of only
        # after it finishes.
        self.debug_dir = debug_dir
        if debug_dir:
            os.makedirs(debug_dir, exist_ok=True)

        # The tool schemas each side is offered every turn (constant across the run:
        # base meta-tools + that side's SHARE tools; TASK tools stay hidden).
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

    # ------------------------------------------------------------------ #
    def _who(self, speaker: str):
        """Return (client, own message list, other message list, tools) for speaker."""
        if speaker == "agent":
            return (self.agent_client, self.agent_msgs, self.user_msgs, self.agent_tools)
        return (self.user_client, self.user_msgs, self.agent_msgs, self.user_tools)

    def _log(self, kind: str, speaker: str, **payload) -> None:
        self.transcript.append({"event": kind, "speaker": speaker, **payload})

    def _account_usage(self, usage: dict) -> None:
        for k in self.usage:
            self.usage[k] += int(usage.get(k, 0) or 0)

    # ------------------------------------------------------------------ #
    def run(self) -> RolloutResult:
        # The agent opens the conversation; the greeting is displayed to the user.
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
                # A tool turn: run every requested call, keep the floor.
                own_msgs.append(result.raw_message)
                self._handle_tool_calls(speaker, result.tool_calls, own_msgs)
                self.empty_streak = 0
                continue

            text = (result.content or "").strip()
            own_msgs.append(result.raw_message)

            if not text:
                # Nothing said and nothing done: guard against a stalled model.
                self.empty_streak += 1
                self._log("empty", speaker)
                if self.empty_streak >= self.max_empty:
                    termination = "EMPTY"
                    break
                # Nudge the same speaker to actually act.
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
            else:  # agent spoke to the user
                other_msgs.append({"role": "user", "content": text})
                self._log("message", speaker, text=text)
                speaker = "user"

        else:
            # loop exited via the while-condition, not a break
            termination = "MAX_ERRORS" if self.errors >= self.max_errors else "MAX_STEPS"

        return self._finish(termination)

    # ------------------------------------------------------------------ #
    def _handle_tool_calls(self, speaker: str, calls: List[ToolCall],
                           own_msgs: List[dict]) -> None:
        owner = speaker  # "agent" | "user"
        for tc in calls:
            name = tc.name
            args = tc.arguments if isinstance(tc.arguments, dict) else {}
            output = self.engine.call(owner, name, args)
            output = "" if output is None else str(output)
            # Record for scoring in the exact shape scoring._resolve consumes.
            self.trajectory.append({"owner": owner, "tool": name, "arguments": args})
            is_error = output.startswith("Error")
            if is_error:
                self.errors += 1
            own_msgs.append({"role": "tool", "tool_call_id": tc.id, "content": output})
            self._log("tool_call", speaker, tool=name, arguments=args,
                      output=output, error=is_error)

    def _record_call(self, speaker: str, client: LLMClient, request_msgs: List[dict],
                     tools: List[dict], result) -> None:
        """Capture one LLM turn (request history + normalized response). The record is
        kept in memory for RolloutResult AND, when ``debug_dir`` is set, streamed to
        disk immediately — a live rollout's llm_debug/ fills up call by call."""
        call_name = "agent_response" if speaker == "agent" else "user_simulator_response"
        call = {
            "seq": len(self.llm_calls) + 1,
            "speaker": speaker,
            "call_name": call_name,
            "request": {
                "model": client.model_id,
                "messages": [dict(m) for m in request_msgs],
                "tools": tools,          # the exact tool schemas offered this turn
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
                pass  # debug streaming must never kill a live rollout

    def _finish(self, termination: str, error_detail: Optional[str] = None) -> RolloutResult:
        return RolloutResult(
            termination=termination, trajectory=list(self.trajectory),
            transcript=list(self.transcript), steps=self.steps, errors=self.errors,
            usage=dict(self.usage), error_detail=error_detail,
            agent_messages=[dict(m) for m in self.agent_msgs],
            user_messages=[dict(m) for m in self.user_msgs],
            agent_tools=self.agent_tools, user_tools=self.user_tools,
            llm_calls=list(self.llm_calls))
