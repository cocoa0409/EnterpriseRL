# worklog — listing_settings_and_compliance (erl-task-instantiate, M=2)

## Step 0 — difficulty pre-check
- Category `listing`; base charter blueprint/products/listing.yaml; claimed events: listing_pricing_updated,
  listing_fee_change_logged, listing_cancellation_policy_changed, listing_registration_recorded, listing_snoozed,
  listing_unsnoozed, listing_unlisted, listing_relisted, listing_reinstated, listing_removed.
- Base gates on the pricing subjects: listing_evt_fee_settings (eligibility []) and listing_evt_discounts
  (eligibility []) govern listing_pricing_updated; listing_evt_fee_settings governs listing_fee_change_logged.
  So every settings write inherits policy_scope only; no time gate.
- Only the pricing writes carry a number (nightly rate, fees, extra-guest threshold, discounts, minimum stay);
  status transitions, registration and cancellation-policy writes carry no computable value, so every problem
  of every tree is a settings write logged by listing_fee_change_logged.
- Identifier band for this difficulty: phone last-4 and government_id_last4 in 2000-2799.

### draw (scripts/draw_counts.py --tasks 2)
```
{"task": 0, "key": "env_0045_vacation_rental_platform/listing_settings_and_compliance/0", "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 4, 6]}
{"task": 1, "key": "env_0045_vacation_rental_platform/listing_settings_and_compliance/1", "prerequisite_problems": 2, "problems": 3, "factor_counts": [4, 4, 6]}
```

### space budget (principle C)
- task 0 — per-stay fees of one listing: pet-fee ceiling reset (agent, state_due, 4 factors), cleaning-fee
  ceiling reset (agent, state_due, 6 factors), short-stay cleaning fee (customer's own save, on_request, root,
  5 factors). Edges: short-stay <- cleaning reset (value_input: the short-stay fee is a share of the regular
  cleaning fee); short-stay <- pet reset (state_gate: no new per-stay fee while another per-stay fee stands above
  its ceiling).
- task 1 (reserved, disjoint) — per-night pricing of another listing: minimum-stay floor raise (agent, state_due,
  4), extra-guest fee ceiling reset (agent, state_due, 4), Pricing Assist suggested nightly rate (customer's own
  save, on_request, root, 6). Edges: rate <- minimum stay (value_input: cleaning fee spread over the minimum
  stay in the all-in price), rate <- extra-guest reset (value_input: full-party extra-guest charges in the all-in
  price).

### tools (uuid8 drawn one by one with uuid.uuid4().hex[:8])
reset_pet_fee_f8e15273, reset_cleaning_fee_77ae9a3d, save_short_stay_cleaning_fee_f18844b5 (task 0);
raise_minimum_stay_1aeaa300, reset_extra_guest_fee_9609655d, save_nightly_rate_d0fc8a90 (task 1).
- 2026-10-07T01:38:11 task 0 closed: per-task gates all OK (traceability deferred: KB not rendered)
- task 1 closed: per-task gates all OK. Revision: minimum-stay floor's reinstatement factor first counted approved
  safety reinstatements in 24 months; check_compute flagged history as decorative (zeroed COUNTs gave the same
  floor 3 by coincidence) -> redefined on the age of the most recent approved safety reinstatement (<12 months
  2 nights, 12-23 months 1 night); seed change records 2025-07-20 (1->5) and 2026-06-16 (5->2) re-derived; trace,
  seed checks and closure text updated in the same pass; per-task gates re-run green.
- final difficulty-wide gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 44.50, steps mean 15.50, history_rows_max 11, branches_max 47), GROUNDING OK, CACHE-DIFF INFO,
  SCOPE OK. check_traceability -> TRACEABILITY NOT OK only for the six hidden tool names, whose verbatim source is
  the published KB (docs/ not rendered yet); every other argument (18/19 per task) is traced.
- coverage: task 0 = {pet-fee ceiling, cleaning-fee ceiling, short-stay cleaning fee}; task 1 = {minimum-stay
  floor, extra-guest fee ceiling, Pricing Assist rate}; disjoint, all six extended policies covered, no idle tool.

## rework round 2 (audits/policy_task/listing_settings_and_compliance/: _difficulty.md, task_0.md, task_1.md)
- G-1 (RED, mislabelled method factors): pet "guest standing" share -> pet-claim look-back by booking volume
  (6 / 12 / 24 months); cleaning "assessment record" share -> deep-cleaning look-back by guest record (6 after a
  warning or suspension in 12 months / 24 after 6+ all-pass assessments in 24 months / 12); extra-guest "plan
  phase-in" share -> damage look-back by party record (36 / 24 / 12 months); Pricing Assist "assessment
  confidence" share -> expected stay length the cleaning fee is spread over (mean of minimum stay and the
  account's average stay / of minimum stay and a week / minimum stay). Pet gained a pet-damage loss allowance and
  dropped the deductible allowance, which moved to the cleaning policy.
- G-8: cleaning turnover allowance removed; plan phase-in removed.
- G-4: short-stay rule covers an assessment with no completed stays. G-5: short-stay rule states the business link
  for judging per-stay fees together (prerequisite sentence unchanged).
- T0-1 (RED): the suite's property_damage claim moved to 2025-07-15; the short-stay damage addition now reads 24
  months; the suite's minimum-stay floor is 1 (stay 2), so nothing outside the tree is owed.
- T0-6 (RED): 17 quarterly assessments seeded (2022-Q2 ... 2026-Q2); every logged save recomputed as of its
  date (338.00 >= 335.00; 370.00 >= 360.00; 415.00 >= 410.00).
- T0-3: nightly rate 225.00, cleaning 410.00, pet 360.00. T1-2: loft's 2026 safety reinstatement seeded, read by
  customer; loft minimum stay 4 = its floor.
- New gold: task 0 pet 340.00 / cleaning 385.00 / short-stay 333.61; task 1 floor 3 / extra-guest 63.20 / rate
  446.11. A first final run gave history_rows_max 6 (< 8); the clean-record tier of the deep-cleaning look-back
  was set to 24 months (6+ assessments), giving 10 with no value change.
- final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 10,
  branches_max 48, means 46.00 / 15.50), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; TRACEABILITY NOT OK only for
  the six hidden tool names (KB not rendered).
