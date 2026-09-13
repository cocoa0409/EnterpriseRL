"""Runtime provenance witness using the frozen Engine, including real user-owned calls."""
from pathlib import Path
import copy, importlib.util, json, sys
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from erlbench.tools import collect_specs
from erlbench.db import DB
from erlbench.determinism import Clock
from erlbench.engine import Engine
from erlbench.kb import KnowledgeBase
from erlbench.scoring import replay
D = ROOT / "env/enterprise_cloud_service_accounting/tasks/database_accounting"
B = D.parents[1] / "blueprint"
def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
specs = collect_specs(module(B / "share_tools.py", "r3_share"), "share") + collect_specs(module(D / "task_tools.py", "r3_task"), "task")
task = json.loads((D / "tasks/1.json").read_text())
schema = json.loads((B / "db_schema.json").read_text())
def engine():
    return Engine(DB.seeded(copy.deepcopy(task["initial_state"])), Clock.from_stamp(task["frozen_time"]), KnowledgeBase([]), specs, schema)
e = engine()
rid = task["evaluation_criteria"][10]["arguments"]["arguments"]["request_id"]
opening = copy.deepcopy(e.db.tables["database_events"][rid])
assert opening["source_subtype"] == "request" and opening["quantity"] == 0
calls = []
for i, action in enumerate(task["evaluation_criteria"]):
    before = copy.deepcopy(e.db.tables["database_events"][rid]) if i == 10 else None
    out = e.call(action["owner"], action["tool"], action["arguments"])
    assert not out.startswith("Error:"), (i, out)
    calls.append(dict(step=i, owner=action["owner"], tool=action["tool"], arguments=action["arguments"], receipt=out))
    if i == 3:
        assert rid in out
    if i == 10:
        signed = copy.deepcopy(e.db.tables["database_events"][rid])
        assert before["quantity"] == 0 and before["source_subtype"] == "request"
        assert signed["quantity"] == 1666.4 and signed["source_subtype"] == "correction"
        assert rid in out and "1666.40" in out
        assert signed["external_reference"] == opening["external_reference"]
assert len(e.db.tables["database_events"]) == len(task["initial_state"]["database_events"]) + 1
score_engine = engine()
score_hash = replay(score_engine, task["evaluation_criteria"], strict=True)
assert score_hash == e.db.hash()
result = dict(request_id=rid, prior_query_step=3, genuine_user_step=10, credit_step=12, opening_request=opening, signed_request=signed, calls=calls, engine_hash=e.db.hash(), scoring_hash=score_hash, engine_matches_scoring=True, new_event_count=1, kb_discovery="Deferred: this witness executes the prescribed GT with an empty KB and makes no discovery claim.")
(D / "rework3_runtime_evidence.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k:result[k] for k in ["request_id", "prior_query_step", "genuine_user_step", "engine_hash", "scoring_hash", "engine_matches_scoring", "new_event_count"]}, indent=2))
