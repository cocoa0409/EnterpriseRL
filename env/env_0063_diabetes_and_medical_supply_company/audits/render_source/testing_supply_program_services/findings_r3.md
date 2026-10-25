# Render-surfaced source findings, round 3 — bgm (testing_supply_program_services)

Source: `bgm.extended.yaml` sha256 832415a5dce2f10291ab07afeeb3f9b964262eba9bfff5b6d09ddf43f458bd69; `task_tools.py` unchanged.

Checks run against the revised source:
- **Verbatim quotes:** every compute_basis quote, prerequisite `policy_source` and baseline.rule is a verbatim substring of its rule.
- **Combination sentences:** each policy's generic combination sentence was read against `result`. That includes:
  - the courtesy reship's order (replace the days, add days, apply the strips a day, multiply, add strips, then round and cap);
  - days are added in the 30-day-block case too;
  - nothing else changes the one-for-one case.
- **Ladders:** R2-1 and R2-A are closed. The four ladders now match their rules.

New findings: none.
