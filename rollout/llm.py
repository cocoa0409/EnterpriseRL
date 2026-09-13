"""LLM calls via litellm — a single client library that fronts every provider.

litellm is a public library; using it (instead of a hand-rolled HTTP client) is what
lets a model id like ``openai/responses/gpt-5.6-sol`` work unchanged. It gives us, for
free, what raw HTTP could not:

  - **provider routing** for the ``openai/`` / ``openai/responses/`` / ``anthropic/`` …
    prefixes: it picks the right API, converts messages/tools to that provider's
    format, and normalizes the response back. Swapping models is just an id change.
  - **``drop_params=True``**: params a model rejects are dropped automatically —
    e.g. Kimi refusing ``temperature`` — so no per-model special-casing is needed.
  - **per-call ``api_base`` / ``api_key``** so one role can point at a different proxy.

On top of litellm we keep one small behavior: **infinite retry on any generation
error** (429 rate limits especially) with capped exponential backoff, so an
oversubscribed shared proxy never kills a run. Bound it with ``max_attempts``.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Use litellm's bundled price map instead of fetching it from GitHub on first call
# (that fetch can time out on locked-down networks and only powers cost accounting,
# which this rollout does not use). Must be set before importing litellm.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

import litellm
from litellm import completion

logger = logging.getLogger("rollout.llm")

# litellm global setup.
litellm.drop_params = True            # drop params a model rejects (e.g. kimi temperature)
litellm.suppress_debug_info = True    # no "Give Feedback / Get Help" banners
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# Size litellm's process-wide httpx pool to the run's concurrency: the pool hard-caps
# in-flight requests, so it must be >= MAX_CONCURRENCY or it throttles everything.
try:  # httpx is a litellm dependency; guard just in case.
    import httpx

    _max_conn = max(int(os.environ.get("MAX_CONCURRENCY", "16")), 16) * 2
    litellm.client_session = httpx.Client(
        limits=httpx.Limits(max_keepalive_connections=_max_conn, max_connections=_max_conn))
except Exception:  # noqa: BLE001
    pass

DEFAULT_LLM_MAX_TOKENS = 32 * 1024


def args_for(model: str, effort: str, temperature: float = 1.0,
             max_tokens: int = DEFAULT_LLM_MAX_TOKENS) -> dict:
    """Pick llm-args by model id: gpt/claude models take a reasoning effort; everything
    else (e.g. kimi) takes only ``temperature`` + ``max_tokens``. ``drop_params`` cleans up
    any residual mismatch, so this only needs to be approximately right.

    For ``openai/responses/*`` litellm DROPS a flat ``reasoning_effort``; only the nested
    ``reasoning={"effort": ...}`` object reaches the server, so that shape is used there
    (mirrors ``_derive_args`` in run.sh, which normally passes these via --*-llm-args)."""
    m = model.lower()
    args = {"temperature": temperature, "max_tokens": max_tokens}
    if ("gpt" in m or "claude" in m) and effort:
        if "responses/" in m:
            args["reasoning"] = {"effort": effort}
        else:
            args["reasoning_effort"] = effort
    return args


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResult:
    content: Optional[str]
    tool_calls: List[ToolCall]
    finish_reason: Optional[str]
    raw_message: dict                    # assistant turn (litellm shape) for history replay
    usage: dict = field(default_factory=dict)
    reasoning_content: Optional[str] = None

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMError(RuntimeError):
    pass


def _is_http_429(e: BaseException) -> bool:
    """Best-effort 429 detection across litellm's exception shapes."""
    if getattr(e, "status_code", None) == 429:
        return True
    if type(e).__name__ == "RateLimitError":
        return True
    s = str(e).lower()
    return ("too many requests" in s or "rate_limit" in s or "rate limit" in s
            or "ratelimiterror" in s or " 429" in s or "429 " in s)


class LLMClient:
    def __init__(self, model: str, args: Optional[dict] = None, max_attempts: int = 0,
                 num_retries: int = 0, retry_min_wait: float = 1.0,
                 retry_max_wait: float = 60.0):
        self.model = model
        self.model_id = model            # kept for parity with earlier code / display
        self.args = dict(args or {})     # temperature / reasoning_effort / max_tokens / api_base / api_key / timeout
        self.max_attempts = max_attempts  # <= 0 -> retry forever
        # This client's own loop is the retry mechanism, so litellm's inner retry is
        # off by default (num_retries=0) — it also avoids litellm importing tenacity.
        self.num_retries = num_retries
        self.retry_min_wait = retry_min_wait
        self.retry_max_wait = retry_max_wait

    # ------------------------------------------------------------------ #
    def _backoff(self, attempt: int) -> float:
        return min(self.retry_max_wait, self.retry_min_wait * (2 ** min(attempt - 1, 6)))

    def chat(self, messages: List[dict], tools: Optional[List[dict]] = None,
             tag: str = "") -> LLMResult:
        """One completion via litellm, retried forever (unless ``max_attempts`` is set)
        on any generation error.

        ``tag`` is a short human label for the call (scenario/difficulty/task/trial/role/
        step) that is included in every log line, so each LLM call — success, retry, or
        failure — is attributable to its exact rollout in the live log stream."""
        tool_choice = "auto" if tools else None
        who = tag or "-"
        attempt = 0
        while True:
            attempt += 1
            try:
                t0 = time.time()
                resp = completion(model=self.model, messages=messages,
                                  tools=tools or None, tool_choice=tool_choice,
                                  num_retries=self.num_retries, **self.args)
                res = self._parse(resp)
                dt = time.time() - t0
                u = res.usage or {}
                act = (f"{len(res.tool_calls)} tool_call(s)[{','.join(tc.name for tc in res.tool_calls)}]"
                       if res.tool_calls else "message")
                logger.info("[llm] %s | model=%s | -> %s | tokens p=%s c=%s t=%s | %.1fs%s | finish=%s",
                            who, self.model, act,
                            u.get("prompt_tokens", 0), u.get("completion_tokens", 0),
                            u.get("total_tokens", 0), dt,
                            "" if attempt == 1 else f" | attempt={attempt}", res.finish_reason)
                return res
            except Exception as e:  # noqa: BLE001 -- retry on anything transient
                if self.max_attempts and attempt >= self.max_attempts:
                    raise LLMError(f"chat failed after {attempt} attempts [{who}]: {e}")
                delay = self._backoff(attempt)
                errkind = "HTTP 429" if _is_http_429(e) else type(e).__name__
                logger.warning("[llm] %s | model=%s | attempt %d failed (%s): %s — retrying in %.1fs",
                               who, self.model, attempt, errkind, str(e), delay)
                time.sleep(delay)

    @staticmethod
    def _parse(resp: Any) -> LLMResult:
        choice = resp.choices[0]
        msg = choice.message
        content = getattr(msg, "content", None)
        reasoning = getattr(msg, "reasoning_content", None)
        raw_tcs = getattr(msg, "tool_calls", None) or []

        tool_calls: List[ToolCall] = []
        for tc in raw_tcs:
            raw_args = tc.function.arguments or "{}"
            if isinstance(raw_args, str):
                try:
                    parsed = json.loads(raw_args) if raw_args.strip() else {}
                except json.JSONDecodeError:
                    parsed = {"__raw__": raw_args}
            elif isinstance(raw_args, dict):
                parsed = raw_args
            else:
                parsed = {}
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=parsed or {}))

        # Rebuild the assistant turn in litellm's message shape for history replay.
        raw_message: Dict[str, Any] = {"role": "assistant", "content": content or ""}
        if raw_tcs:
            raw_message["tool_calls"] = [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in raw_tcs]
        if reasoning:
            raw_message["reasoning_content"] = reasoning
        # The model's reasoning, carried back verbatim with the turn so it persists across
        # tool calls: Anthropic's signed thinking blocks, and the Responses API's reasoning
        # items (id + encrypted content), which litellm turns back into input items.
        for key in ("thinking_blocks", "reasoning_items"):
            items = getattr(msg, key, None)
            if items:
                raw_message[key] = [dict(b) for b in items]

        usage: Dict[str, int] = {}
        u = getattr(resp, "usage", None)
        if u is not None:
            usage = {"prompt_tokens": int(getattr(u, "prompt_tokens", 0) or 0),
                     "completion_tokens": int(getattr(u, "completion_tokens", 0) or 0),
                     "total_tokens": int(getattr(u, "total_tokens", 0) or 0)}
        return LLMResult(content=content, tool_calls=tool_calls,
                         finish_reason=getattr(choice, "finish_reason", None),
                         raw_message=raw_message, usage=usage, reasoning_content=reasoning)
