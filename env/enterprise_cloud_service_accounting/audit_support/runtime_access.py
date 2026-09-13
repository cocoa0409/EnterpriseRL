"""Tool-shaped access for independent KB audits; never prints hidden task fields.

Run from repository root with the repository Python, passing difficulty, product,
task index, and a JSON request-list file. Calls are replayed in order on a fresh
world, so a longer request list can continue an earlier audited interaction.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from erlbench.db import DB
from erlbench.determinism import Clock
from erlbench.engine import Engine
from erlbench.kb import Document, KnowledgeBase
from erlbench.loader import load_tool_specs

root = Path(__file__).resolve().parents[1]
difficulty, product, index, request_path = sys.argv[1:]
task = json.loads((root / 'tasks' / difficulty / 'tasks' / f'{index}.json').read_text())
schema = json.loads((root / 'blueprint' / 'db_schema.json').read_text())
specs = load_tool_specs(str(root / 'blueprint' / 'share_tools.py'), 'share')
for tools_path in sorted((root / 'tasks').glob('*/task_tools.py')):
    specs += load_tool_specs(str(tools_path), 'task')
docs = []
for path in sorted((root / 'docs').glob('*/*.json')):
    obj = json.loads(path.read_text())
    docs.append(Document(id=obj['id'], title=obj['title'], content=obj['content']))
engine = Engine(DB.seeded(task['initial_state']), Clock.from_stamp(task['frozen_time']),
                KnowledgeBase(docs), specs, schema=schema)
requests = json.loads(Path(request_path).read_text())
for request in requests:
    owner = request.get('owner', 'agent')
    result = engine.call(owner, request['name'], request.get('arguments', {}))
    print(json.dumps({'request': request, 'result': result}, ensure_ascii=False))
