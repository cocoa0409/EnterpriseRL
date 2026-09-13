"""Mechanically construct allowlisted views for the scenario's independent audits."""
import hashlib
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path.cwd()))
from erlbench.engine import BASE_SCHEMAS
from erlbench.loader import load_tool_specs

root = Path(__file__).resolve().parents[1]
mode, difficulty, revision = sys.argv[1:]
blueprint = yaml.safe_load((root / 'blueprint' / 'blueprint.yaml').read_text())
unit = next(d for d in blueprint['difficulties'] if d['name'] == difficulty)
product = unit['claim']['categories'][0]
destination = root / 'audit_inputs' / mode / difficulty / f'round_{revision}'
destination.mkdir(parents=True, exist_ok=True)
hashes = {}

def save(name, value):
    path = destination / name
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()

for path in sorted((root / 'tasks' / difficulty / 'tasks').glob('[0-9]*.json')):
    task = json.loads(path.read_text())
    keys = ['frozen_time', 'user_scenario']
    if mode == 'source':
        keys.append('initial_state')
    save(path.name, {key: task[key] for key in keys})

if mode == 'runtime':
    save('background.json', {'background': blueprint['background']})
    docs = []
    for path in sorted((root / 'docs').glob('*/*.json')):
        obj = json.loads(path.read_text())
        docs.append({key: obj[key] for key in ['title', 'content']})
    save('documents.json', docs)
    specs = load_tool_specs(str(root / 'blueprint' / 'share_tools.py'), 'share')
    save('tool_schemas.json', {
        'base': list(BASE_SCHEMAS.values()),
        'share': [s.openai_schema() for s in specs if s.kind == 'share'],
        'discoverable_interfaces': 'Obtain each task interface through the runtime unlock tool after discovering its name in the KB.',
    })

(destination / 'SHA256SUMS.json').write_text(json.dumps(hashes, indent=2) + '\n')
print(str(destination.relative_to(Path.cwd())))
print(json.dumps(hashes, indent=2))
