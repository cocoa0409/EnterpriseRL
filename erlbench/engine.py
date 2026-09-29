"""The engine: the SIX FIXED BASE (meta) TOOLS and the routing that binds a
task's DB, knowledge base, and generated tools together.

These implementations are part of the frozen scaffold — generation never touches
them. Generated scenarios only contribute:
  - share tools (share_tools.py, @tool(owner, rw)) -- always listed, directly callable
  - task tools  (tools/task_tools.py, @tool(owner, rw)) -- hidden; unlocked from the KB
  - KB documents ({id,title,content}) that bury the task tools' names

Base tools (all meta):
  agent: KB_search(query)                      -> BM25 over the KB (kb.py)
         grep(pattern)                         -> regex over the KB (kb.py)
         unlock_agent_discoverable_tool(tool_name)
         unlock_user_discoverable_tool(tool_name)              # hand to user
         call_agent_discoverable_tool(tool_name, arguments)
  user:  call_user_discoverable_tool(tool_name, arguments)

Discovery flow:
  agent-owned task tool : unlock_agent_discoverable_tool -> call_agent_discoverable_tool
  user-owned task tool  : (agent) unlock_user_discoverable_tool -> (user) call_user_discoverable_tool

Unlock/give state is engine memory only — a deliberate simplification: the meta
tools write no bookkeeping rows, so the DB hash (and evaluation_criteria) stays
purely business writes and an extra unlock can never flip a correct outcome.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from .db import DB
from .determinism import Clock
from .kb import KnowledgeBase
from .tools import ToolContext, ToolSpec, function_schema

AGENT_BASE = ["KB_search", "grep", "unlock_agent_discoverable_tool",
              "unlock_user_discoverable_tool", "call_agent_discoverable_tool"]
USER_BASE = ["call_user_discoverable_tool"]


def format_tool_for_display(spec: ToolSpec) -> str:
    """Render a discoverable tool's interface for the agent (shown on unlock)."""
    props = spec.parameters.get("properties", {})
    required = set(spec.parameters.get("required", []))
    lines = []
    for p, meta in props.items():
        req = " (required)" if p in required else " (optional)"
        lines.append(f"  - {p}: {meta.get('type', 'string')}{req} - {meta.get('description', '')}")
    params = "\n".join(lines) if lines else "  (no parameters)"
    return f"Tool: {spec.name}\nDescription: {spec.description}\nParameters:\n{params}"


class Engine:
    """One running task: a seeded DB + the KB + every generated tool, with the
    six base tools bound on top. Permissions and the unlock flow are enforced
    here — for live runs and, through the same ``call``, for the replay of a
    recorded conversation (scoring.replay_calls); only the ground-truth replay of
    a trusted reference bypasses it (scoring.replay)."""

    def __init__(self, db: DB, clock: Clock, kb: KnowledgeBase, specs: List[ToolSpec],
                 schema: dict | None = None):
        self.db = db
        self.clock = clock
        self.kb = kb
        self.schema = schema or {}
        self.registry: Dict[str, ToolSpec] = {s.name: s for s in specs}
        self.unlocked_agent: set = set()
        self.given_user: set = set()

    # -- helpers ------------------------------------------------------------ #
    def _ctx(self, writable: bool = True) -> ToolContext:
        return ToolContext(self.db, self.clock, self.schema, writable=writable)

    def _run(self, spec: ToolSpec, arguments: dict) -> str:
        try:
            ctx = self._ctx(writable=(spec.rw == "write"))
            return str(spec.func(ctx, **spec.coerce(arguments or {})))
        except Exception as e:  # noqa: BLE001  -- soft error, never crash a run
            return f"Error: {spec.name} failed: {e}"

    def _get(self, name: str, owner: str, kind: str) -> Optional[ToolSpec]:
        s = self.registry.get(name)
        if s and s.owner == owner and s.kind == kind:
            return s
        return None

    @staticmethod
    def _parse_json_args(arguments) -> tuple[Optional[dict], Optional[str]]:
        if isinstance(arguments, dict):
            return arguments, None
        try:
            return (json.loads(arguments) if arguments else {}), None
        except json.JSONDecodeError as e:
            return None, f"Error: Invalid JSON in arguments: {e}"

    @staticmethod
    def _validate_args(spec: ToolSpec, args: dict) -> Optional[str]:
        props = spec.parameters.get("properties", {})
        for p in spec.parameters.get("required", []):
            if p not in args:
                return f"Error: Missing required parameter: {p}"
        for a in args:
            if a not in props:
                return f"Error: Unexpected parameter: {a}"
        return None

    # -- LLM-facing tool lists ---------------------------------------------- #
    def tool_list(self, owner: str) -> List[dict]:
        base = AGENT_BASE if owner == "agent" else USER_BASE
        schemas = [BASE_SCHEMAS[n] for n in base]
        for s in self.registry.values():
            if s.owner == owner and s.kind == "share":
                schemas.append(s.openai_schema())
        return schemas

    # -- live call routing --------------------------------------------------- #
    def call(self, owner: str, name: str, arguments: Optional[dict] = None) -> str:
        """Route one tool call from ``owner`` ("agent"|"user")."""
        args = arguments or {}
        if name in BASE_SCHEMAS:
            allowed = AGENT_BASE if owner == "agent" else USER_BASE
            if name not in allowed:
                return f"Error: '{name}' is not available to the {owner}."
            try:
                return getattr(self, name)(**args)
            except TypeError as e:
                return f"Error: Invalid arguments: {e}"
        spec = self.registry.get(name)
        if spec is None:
            return f"Error: unknown tool '{name}'."
        if spec.kind != "share":
            return f"Error: '{name}' is not directly callable; it must be unlocked first."
        if spec.owner != owner:
            return f"Error: '{name}' is not available to the {owner}."
        return self._run(spec, args)

    # ===================================================================== #
    # The six fixed base tools
    # ===================================================================== #

    def KB_search(self, query: str) -> str:
        """Search the knowledge base for relevant documents.

        Args:
            query: The search query to find relevant documents
        """
        return self.kb.search(query)

    def grep(self, pattern: str) -> str:
        """Search for a regex pattern in all knowledge base documents. Returns
        documents ranked by number of matches, with full content.

        Args:
            pattern: The regex pattern to search for (e.g., 'refund.*order', 'fee|charge')
        """
        return self.kb.grep(pattern)

    def unlock_agent_discoverable_tool(self, tool_name: str) -> str:
        """Unlock an agent discoverable tool that was found in the knowledge base.
        Use this when the knowledge base indicates that you have access to a
        specialized internal tool. After unlocking, you can use the tool by
        calling `call_agent_discoverable_tool` with the tool name and required
        arguments.

        Args:
            tool_name: The exact tool name found in the knowledge base
        """
        spec = self._get(tool_name, owner="agent", kind="task")
        if spec is None:
            return f"Error: Unknown agent tool '{tool_name}'. This tool is not available."
        self.unlocked_agent.add(tool_name)
        return (
            f"Tool unlocked: {tool_name}\n\n"
            f"{format_tool_for_display(spec)}\n\n"
            f"You can now use this tool by calling `call_agent_discoverable_tool` with "
            f"tool_name='{tool_name}' and the required arguments."
        )

    def unlock_user_discoverable_tool(self, tool_name: str) -> str:
        """Pass a tool to the user so they can execute it themselves. Use this
        when the knowledge base indicates that the user should perform an action
        themselves. This reveals the tool's interface; the user will then be able
        to call `call_user_discoverable_tool` with the tool name and the required
        arguments.

        Args:
            tool_name: The exact user tool name found in the knowledge base
        """
        spec = self._get(tool_name, owner="user", kind="task")
        if spec is None:
            return f"Error: Unknown discoverable tool '{tool_name}'."
        self.given_user.add(tool_name)
        return (
            f"Tool given to user: {tool_name}\n\n"
            f"{format_tool_for_display(spec)}\n\n"
            f"The user can now execute this action by calling `call_user_discoverable_tool` "
            f"with tool_name='{tool_name}' and the required arguments. Tell the user, in your "
            f"reply, the exact tool name and the exact argument values to use."
        )

    def call_agent_discoverable_tool(self, tool_name: str, arguments: str = "{}") -> str:
        """Call an agent discoverable tool that you have previously unlocked.
        Use this after unlocking a tool with `unlock_agent_discoverable_tool`.
        The knowledge base will tell you which tool to use and what arguments
        to provide.

        Args:
            tool_name: The name of the agent discoverable tool to call
            arguments: JSON string of arguments for the tool (e.g., '{"user_id": "abc123"}')
        """
        spec = self._get(tool_name, owner="agent", kind="task")
        if spec is None:
            return f"Error: Unknown agent tool '{tool_name}'. This tool is not available."
        if tool_name not in self.unlocked_agent:
            return (
                f"Error: Tool '{tool_name}' has not been unlocked. You must first use "
                f"`unlock_agent_discoverable_tool` to unlock this tool before calling it."
            )
        args, err = self._parse_json_args(arguments)
        if err:
            return err
        err = self._validate_args(spec, args)
        if err:
            return err
        return self._run(spec, args)

    def call_user_discoverable_tool(self, tool_name: str, arguments: str = "{}") -> str:
        """Call a tool that was given to you by the agent. Use this when the
        agent has instructed you to perform an action using a discoverable
        tool. The agent will have told you the tool name and arguments.

        Args:
            tool_name: The name of the discoverable tool to call
            arguments: JSON string of arguments for the tool (e.g., '{"order_id": "o1"}')
        """
        spec = self._get(tool_name, owner="user", kind="task")
        if spec is None:
            return f"Error: Unknown discoverable tool '{tool_name}'."
        if tool_name not in self.given_user:
            return (
                f"Error: Tool '{tool_name}' has not been given to you by the agent yet. "
                f"The agent must make it available first."
            )
        args, err = self._parse_json_args(arguments)
        if err:
            return err
        err = self._validate_args(spec, args)
        if err:
            return err
        return self._run(spec, args)


# The base tools' OpenAI schemas are introspected from the six methods above —
# the same signature+docstring path every generated tool goes through. One
# source of truth: the implementation; no hand-written schema anywhere.
BASE_SCHEMAS = {name: function_schema(getattr(Engine, name))
                for name in AGENT_BASE + USER_BASE}
