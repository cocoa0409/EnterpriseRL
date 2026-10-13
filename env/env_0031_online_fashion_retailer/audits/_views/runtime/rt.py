"""Tool-shaped DB access for the KB-layer blind audit (coordinator-built).

Loads the scenario through the frozen runtime and seeds the task's world into an
Engine exactly as a rollout does; the auditor sees only tool outputs, never the
raw initial_state.

Usage (from the repository root):
  .venv/bin/python env/env_0031_online_fashion_retailer/audits/_views/runtime/rt.py \
      <difficulty> <task_index> '<json list of calls>'
  each call: ["agent"|"user", "<tool_name>", {args}]
  Base tools work as at runtime (KB_search, grep, unlock_agent_discoverable_tool,
  call_agent_discoverable_tool, unlock_user_discoverable_tool,
  call_user_discoverable_tool, ...), share finders are called directly.
  All calls in one invocation run against ONE engine, so writes persist within it;
  a new invocation starts again from the task's opening world.
"""
import json, os, sys
sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
sys.path.insert(0, ROOT)
from erlbench.loader import load_scenario  # noqa: E402

def main():
    diff, idx, calls = sys.argv[1], int(sys.argv[2]), json.loads(sys.argv[3])
    sc = load_scenario(os.path.join(ROOT, "env", "env_0031_online_fashion_retailer"))
    tasks = sc.tasks[diff]
    task = tasks[idx]
    eng = sc.engine_for(task)
    for owner, name, args in calls:
        print(f">>> {owner}.{name}({json.dumps(args, ensure_ascii=False)})")
        print(eng.call(owner, name, args))
        print()

if __name__ == "__main__":
    main()
