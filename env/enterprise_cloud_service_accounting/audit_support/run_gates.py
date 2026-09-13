"""Coordinator gate snapshots. No business-semantic verdict is inferred here."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
root_arg = str(root.relative_to(Path.cwd()))
mode = sys.argv[1]
unit = sys.argv[2] if len(sys.argv) > 2 else 'scenario'
revision = sys.argv[3] if len(sys.argv) > 3 else '1'
python = '.venv/bin/python'
commands = []
if mode == 'blueprint':
    for script in ['check_blueprint', 'check_share_tools']:
        commands.append([python, f'skills/erl-scenario-blueprint/scripts/{script}.py', root_arg])
elif mode == 'source':
    for script in ['check_extended', 'check_task_tools', 'replay_tasks', 'check_solvability',
                   'check_compute', 'check_grounding', 'check_cross_fire']:
        command = [python, f'skills/erl-task-instantiate/scripts/{script}.py', f'{root_arg}/tasks/{unit}']
        if script == 'replay_tasks':
            command.append('--check')
        commands.append(command)
elif mode == 'docs':
    commands.append([python, 'skills/erl-kb-doc-render/scripts/check_docs.py', root_arg, unit])
elif mode == 'traceability':
    commands.append([python, 'skills/erl-task-instantiate/scripts/check_traceability.py', f'{root_arg}/tasks/{unit}'])
else:
    raise SystemExit('Unknown gate mode')

directory = root / 'gate_snapshots' / mode / unit
directory.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
snapshot = directory / f'round_{revision}_{stamp}.txt'
results = []
with snapshot.open('w') as out:
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        block = '$ ' + ' '.join(command) + '\n' + result.stdout + result.stderr
        block += f'EXIT_CODE={result.returncode}\n'
        out.write(block + '\n')
        out.flush()
        print(block, flush=True)
        results.append(result.returncode)
print('SNAPSHOT=' + str(snapshot.relative_to(Path.cwd())))
print('ALL_GATES_GREEN=' + str(all(code == 0 for code in results)))
sys.exit(0 if all(code == 0 for code in results) else 1)
