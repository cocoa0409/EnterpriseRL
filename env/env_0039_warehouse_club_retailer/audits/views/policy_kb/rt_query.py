"""Runtime DB access path for the render-layer (KB) audit of env_0039_warehouse_club_retailer.

Builds the SAME world a rollout sees (rollout.runner: union DB of every task, overlaid with
this task's own initial_state; the full published KB; every share/task tool spec) and routes
calls through Engine.call exactly as the live agent/user would. It never prints initial_state.

Usage (from the repository root):
  .venv/bin/python env/env_0039_warehouse_club_retailer/audits/views/policy_kb/rt_query.py <difficulty> <task_index> --system
  .venv/bin/python .../rt_query.py <difficulty> <task_index> --tools agent|user
  .venv/bin/python .../rt_query.py <difficulty> <task_index> <tool_name> '<json args>'          # one agent-side call
  .venv/bin/python .../rt_query.py <difficulty> <task_index> --seq '<json list of [owner, tool_name, args]>'
      # several calls in ONE engine, so write effects carry forward (owner = "agent" or "user").
      # Base meta tools: KB_search {"query"}, grep {"pattern"}, unlock_agent_discoverable_tool {"tool_name"},
      # call_agent_discoverable_tool {"tool_name","arguments"(JSON string)}, and the user-side equivalents.
Each invocation starts from the task's opening world (frozen_time); nothing persists between invocations.
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from rollout.runner import get_world
from rollout.prompts import build_agent_prompt

SCEN = "env/env_0039_warehouse_club_retailer"


def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    diff, idx = sys.argv[1], int(sys.argv[2])
    world = get_world(SCEN)
    tasks = world.sc.tasks.get(diff) or []
    task = next((t for t in tasks if int(t.get("task_index", -1)) == idx), None)
    if task is None and 0 <= idx < len(tasks):
        task = tasks[idx]
    if task is None:
        print(f"no task {diff}/{idx}"); sys.exit(2)
    eng = world.engine_for(task)
    op = sys.argv[3]
    if op == "--system":
        print(build_agent_prompt(world.company, world.background, task.get("frozen_time")))
        return
    if op == "--tools":
        print(json.dumps(eng.tool_list(sys.argv[4] if len(sys.argv) > 4 else "agent"), indent=2))
        return
    if op == "--seq":
        for owner, name, args in json.loads(sys.argv[4]):
            print(f"### {owner}: {name} {json.dumps(args)}")
            print(eng.call(owner, name, args))
        return
    args = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    print(eng.call("agent", op, args))


if __name__ == "__main__":
    main()
