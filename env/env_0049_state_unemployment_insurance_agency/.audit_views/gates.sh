#!/bin/bash
# usage: gates.sh <difficulty>
cd /home/ubuntu/github/enterprise_rl
DIFF=env/env_0049_state_unemployment_insurance_agency/tasks/$1
for g in check_extended check_task_tools replay_tasks check_solvability check_compute check_grounding check_cache_diff check_cross_fire; do
  out=$(.venv/bin/python skills/erl-task-instantiate/scripts/$g.py "$DIFF" 2>&1); rc=$?
  echo "[$g rc=$rc] $(echo "$out" | grep -E 'OK|FAIL|ERROR|INFO|suite|depth' | tail -3 | tr '\n' ' ')"
done
find $DIFF -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
