"""A dependency-light scaffold for synthesizing customer-service agent tasks with
a shared DB, a searchable knowledge base, and discoverable tools.

Public surface:
  from erlbench import tool, ToolContext        # author tools in *_tools.py
  from erlbench import load_scenario, score, validate_scenario
"""

from .determinism import Clock, make_id
from .db import DB
from .tools import ToolContext, tool
from .kb import Document, KnowledgeBase
from .engine import Engine
from .loader import Scenario, load_scenario
from .scoring import replay, score
from .validate import validate_scenario

__all__ = [
    "tool", "ToolContext", "make_id", "Clock",
    "DB", "Document", "KnowledgeBase", "Engine",
    "Scenario", "load_scenario", "replay", "score", "validate_scenario",
]
