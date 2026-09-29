"""Regression checks for scoring: the ground-truth replay and the routed replay of a recorded
conversation agree on the reference; a call the live engine refuses lands nothing on replay
— the routed replay closes what the ground-truth replay would accept; and the tool order a
task's problem tree imposes is checked by first calls, whichever side made them, before
any replay."""

import json
import types
import unittest
from types import SimpleNamespace

from erlbench.db import DB
from erlbench.determinism import Clock
from erlbench.engine import Engine
from erlbench.kb import Document, KnowledgeBase
from erlbench.loader import required_order
from erlbench.scoring import check_order, first_calls, replay, replay_calls, score
from erlbench.tools import collect_specs

SHARE_TOOLS = '''
from erlbench import tool

@tool(owner="agent", rw="read")
def find_orders(ctx, customer_id: str) -> str:
    """Orders of a customer."""
    return str(ctx.find("orders", customer_id=customer_id))

@tool(owner="agent", rw="write")
def note_order(ctx, order_id: str, note: str) -> str:
    """Attach a note to an order."""
    if not ctx.update("orders", order_id, note=note):
        return f"Error: no order {order_id}"
    return "ok"
'''
TASK_TOOLS = '''
from erlbench import tool

@tool(owner="agent", rw="write")
def post_credit(ctx, order_id: str, amount: float) -> str:
    """Book a credit against an order."""
    key = ctx.make_id("cr_", order_id, amount)
    ctx.create("credits", key, id=key, order_id=order_id, amount=amount)
    return key

@tool(owner="user", rw="write")
def confirm_cancellation(ctx, order_id: str) -> str:
    """The customer confirms the cancellation of an order."""
    if not ctx.update("orders", order_id, status="cancelled"):
        return f"Error: no order {order_id}"
    return "cancelled"
'''
SCHEMA = {"orders": ["id", "customer_id", "status", "note"], "credits": ["id", "order_id", "amount"]}
SEED = {"orders": {"o1": {"id": "o1", "customer_id": "c1", "status": "open", "note": ""}}}
DOCS = [Document("d1", "Credits", "post_credit books a credit; confirm_cancellation is the customer's.")]

# The task's evaluation_criteria as authored: bare tool names, no unlock steps.
GROUND_TRUTH = [
    {"owner": "agent", "tool": "find_orders", "arguments": {"customer_id": "c1"}},
    {"owner": "agent", "tool": "note_order", "arguments": {"order_id": "o1", "note": "reviewed"}},
    {"owner": "agent", "tool": "post_credit", "arguments": {"order_id": "o1", "amount": 12.5}},
    {"owner": "user", "tool": "confirm_cancellation", "arguments": {"order_id": "o1"}},
]


def call(owner, tool, **arguments):
    return {"owner": owner, "tool": tool, "arguments": arguments}


def wrapped(side, tool, **arguments):
    return call(side, f"call_{side}_discoverable_tool", tool_name=tool,
                arguments=json.dumps(arguments))


# The same solution as a conversation would issue it, through the routing.
CONVERSATION = [
    call("agent", "KB_search", query="credit"),
    call("agent", "find_orders", customer_id="c1"),
    call("agent", "note_order", order_id="o1", note="reviewed"),
    call("agent", "unlock_agent_discoverable_tool", tool_name="post_credit"),
    wrapped("agent", "post_credit", order_id="o1", amount=12.5),
    call("agent", "unlock_user_discoverable_tool", tool_name="confirm_cancellation"),
    wrapped("user", "confirm_cancellation", order_id="o1"),
]
UNLOCKS = ("unlock_agent_discoverable_tool", "unlock_user_discoverable_tool")

# The task's problem tree: the customer's cancellation (root) depends on the credit having
# been booked — so post_credit (agent) must be called before confirm_cancellation (user).
CLOSURE = {"root_problem": "p_cancel", "edges": [
    {"from": "p_cancel", "to": "p_credit", "kind": "value_input", "resolved_by": "post_credit"}]}
TARGET_TOOLS = {"p_credit": "post_credit", "p_cancel": "confirm_cancellation"}
ORDER = [{"before": "post_credit", "after": "confirm_cancellation"}]


def _specs(source, kind):
    module = types.ModuleType(f"scoring_test_{kind}_tools")
    exec(source, module.__dict__)
    return collect_specs(module, kind)


def fresh_engine():
    specs = _specs(SHARE_TOOLS, "share") + _specs(TASK_TOOLS, "task")
    return Engine(DB.seeded(SEED), Clock.from_stamp("2026-01-01T00:00:00Z"),
                  KnowledgeBase(DOCS), specs, schema=SCHEMA)


def live_session(calls):
    """Drive a fresh engine as the conversation loop does; return (engine, outputs)."""
    engine = fresh_engine()
    outputs = [str(engine.call(c["owner"], c["tool"], c["arguments"])) for c in calls]
    return engine, outputs


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.initial = fresh_engine().db.hash()
        self.target = replay(fresh_engine(), GROUND_TRUTH)
        self.assertNotEqual(self.target, self.initial)

    def test_conversation_through_the_routing_reaches_the_ground_truth(self):
        engine, outputs = live_session(CONVERSATION)
        self.assertFalse([o for o in outputs if o.startswith("Error")], outputs)
        self.assertEqual(engine.db.hash(), self.target)
        self.assertEqual(replay_calls(fresh_engine(), CONVERSATION), self.target)
        self.assertEqual(replay_calls(fresh_engine(), []), self.initial)

    def test_refused_calls_land_nothing_on_replay(self):
        # The whole conversation each time, with one rule broken.
        without_unlocks = [c for c in CONVERSATION if c["tool"] not in UNLOCKS]
        agent_runs_the_customers_tool = [
            wrapped("agent", "confirm_cancellation", order_id="o1") if c["owner"] == "user" else c
            for c in CONVERSATION]
        bare_names = [call(c["owner"], c["arguments"]["tool_name"], **json.loads(c["arguments"]["arguments"]))
                      if c["tool"].startswith("call_") else c for c in without_unlocks]
        wrong_owner = [call("user", "note_order", order_id="o1", note="reviewed")
                       if c["tool"] == "note_order" else c for c in CONVERSATION]
        unexpected_parameter = [wrapped("agent", "post_credit", order_id="o1", amount=12.5, extra=1)
                                if c["tool"] == "call_agent_discoverable_tool" else c for c in CONVERSATION]
        accepted_by_ground_truth_replay = (without_unlocks, agent_runs_the_customers_tool,
                                           bare_names, wrong_owner)
        for calls in accepted_by_ground_truth_replay + (unexpected_parameter,):
            with self.subTest(calls=[c["tool"] for c in calls]):
                engine, outputs = live_session(calls)
                self.assertTrue([o for o in outputs if o.startswith("Error")], outputs)
                replayed = replay_calls(fresh_engine(), calls)
                self.assertEqual(replayed, engine.db.hash())   # the replay reproduces the session
                self.assertNotEqual(replayed, self.target)       # and does not score it
        # What the routed replay closes: the ground-truth replay applies these writes anyway.
        for calls in accepted_by_ground_truth_replay:
            self.assertEqual(replay(fresh_engine(), calls), self.target)

    def test_score_routes_the_conversation(self):
        scenario = SimpleNamespace(engine_for=lambda task: fresh_engine())
        self.assertEqual(score(scenario, {}, GROUND_TRUTH, CONVERSATION)["reward"], 1.0)
        without_unlocks = [c for c in CONVERSATION if c["tool"] not in UNLOCKS]
        self.assertEqual(score(scenario, {}, GROUND_TRUTH, without_unlocks)["reward"], 0.0)

    def test_required_order_from_the_problem_tree(self):
        self.assertEqual(required_order(CLOSURE, TARGET_TOOLS), ORDER)
        self.assertEqual(required_order({}, TARGET_TOOLS), [])
        chain = {"edges": [{"from": "p_cancel", "to": "p_credit"}, {"from": "p_credit", "to": "p_note"}]}
        tools = {**TARGET_TOOLS, "p_note": "note_order"}
        self.assertEqual([(o["before"], o["after"]) for o in required_order(chain, tools)],
                         [("post_credit", "confirm_cancellation"), ("note_order", "post_credit")])
        with self.assertRaises(ValueError):          # a policy without a target tool
            required_order(CLOSURE, {"p_cancel": "confirm_cancellation"})
        with self.assertRaises(ValueError):          # resolved_by disagrees with the mapping
            required_order(CLOSURE, {**TARGET_TOOLS, "p_credit": "note_order"})

    def test_check_order_by_first_call_whichever_side(self):
        self.assertEqual(first_calls(CONVERSATION),
                         {"find_orders": 1, "note_order": 2, "post_credit": 4, "confirm_cancellation": 6})
        self.assertEqual(check_order(ORDER, CONVERSATION), [])
        self.assertEqual(check_order(ORDER, []), [])
        # The customer's tool attempted before the agent's prerequisite write.
        customer_first = [CONVERSATION[6]] + CONVERSATION[:6]
        self.assertEqual(check_order(ORDER, customer_first),
                         [{"before": "post_credit", "after": "confirm_cancellation", "before_at": 5, "after_at": 0}])
        # The prerequisite never called at all.
        no_credit = [c for c in CONVERSATION if "post_credit" not in json.dumps(c)]
        self.assertEqual(check_order(ORDER, no_credit)[0]["before_at"], None)
        # The blocked tool never called: nothing to order.
        self.assertEqual(check_order(ORDER, CONVERSATION[:6]), [])
        # An attempt is a call, whoever makes it and however it is refused: the customer's
        # tool by bare name (not directly callable), or issued by the agent (unknown agent tool).
        for attempt in (call("user", "confirm_cancellation", order_id="o1"),
                        wrapped("agent", "confirm_cancellation", order_id="o1")):
            self.assertEqual(len(check_order(ORDER, [attempt] + CONVERSATION)), 1)
        # Handing the tool over is not calling it.
        handed_over_first = [CONVERSATION[5]] + CONVERSATION[:5] + CONVERSATION[6:]
        self.assertEqual(check_order(ORDER, handed_over_first), [])

    def test_score_checks_the_order_before_replaying(self):
        scenario = SimpleNamespace(engine_for=lambda task: fresh_engine())
        ok = score(scenario, {}, GROUND_TRUTH, CONVERSATION, ORDER)
        self.assertEqual((ok["reward"], ok["order_ok"]), (1.0, True))
        customer_first = [CONVERSATION[6]] + CONVERSATION[:6]
        bad = score(scenario, {}, GROUND_TRUTH, customer_first, ORDER)
        self.assertEqual((bad["reward"], bad["order_ok"], bad["predicted_hash"]), (0.0, False, None))
        self.assertEqual(len(bad["order_violations"]), 1)


if __name__ == "__main__":
    unittest.main()
