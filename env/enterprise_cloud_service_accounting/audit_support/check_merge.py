"""Cross-difficulty identifier and frozen-blueprint acceptance checks."""
import hashlib
import json
import sys
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
blueprint = yaml.safe_load((root / 'blueprint' / 'blueprint.yaml').read_text())
frozen = json.loads((root / 'audit_support' / 'frozen_blueprint_sha256.json').read_text())
errors = []
for filename, expected in frozen.items():
    actual = hashlib.sha256((root / filename).read_bytes()).hexdigest()
    if actual != expected:
        errors.append('Frozen blueprint changed: ' + filename)

bands = json.loads((root / 'audit_support' / 'identifier_bands.json').read_text())
seen = {}
tasks_count = 0
for unit in blueprint['difficulties']:
    difficulty = unit['name']
    paths = sorted((root / 'tasks' / difficulty / 'tasks').glob('[0-9]*.json'))
    if [p.name for p in paths] != ['0.json', '1.json']:
        errors.append(f'{difficulty}: expected 0.json and 1.json')
    for path in paths:
        task = json.loads(path.read_text())
        tasks_count += 1
        customers = task['initial_state'].get('customers', {})
        rows = customers.values() if isinstance(customers, dict) else customers
        for row in rows:
            for field in ['phone', 'identity_document', 'email']:
                value = row.get(field)
                if not value:
                    continue
                previous = seen.setdefault((field, value), difficulty)
                if previous != difficulty:
                    errors.append(f'Duplicate {field} across {previous} and {difficulty}: {value}')
            band = bands[difficulty]
            phone = row.get('phone', '')
            identity = row.get('identity_document', '')
            if not band['phone_first'] <= phone <= band['phone_last']:
                errors.append(f'{difficulty}: customer telephone outside assigned band')
            if not band['identity_suffix_min'] <= identity <= band['identity_suffix_max']:
                errors.append(f'{difficulty}: identity-document suffix outside assigned band')
print(f'Difficulties: {len(blueprint["difficulties"])}; tasks: {tasks_count}; unique business identifiers: {len(seen)}')
for error in errors:
    print('ERROR:', error)
print('MERGE OK' if not errors else 'MERGE NOT OK')
sys.exit(bool(errors))
