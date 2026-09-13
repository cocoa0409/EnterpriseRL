"""Live agent <-> user-simulator rollout for erlbench scenarios.

This package is the missing runtime piece: `erlbench/` can load a scenario, bind
its DB + KB + tools into an `Engine`, and score a trajectory by replaying its
writes and comparing DB hashes — but nothing drives two LLMs through the Engine.
`rollout/` supplies exactly that:

  - `llm.LLMClient`      : LLM calls via litellm.
  - `prompts`            : native agent + user-simulator system prompts.
  - `orchestrator`       : the half-duplex agent<->user loop over one Engine.
  - `runner`             : the CLI (load scenarios, N trials, concurrency, score).

The loop is a half-duplex customer-service simulation: the agent opens, the two
sides take turns, tool calls are routed to the environment, the user simulator ends
the call with a STOP token, and the reward is the DB terminal-state match. It is
implemented entirely on top of `erlbench`.
"""

from .llm import LLMClient, LLMResult
from .orchestrator import Orchestrator, RolloutResult

__all__ = ["LLMClient", "LLMResult", "Orchestrator", "RolloutResult"]
