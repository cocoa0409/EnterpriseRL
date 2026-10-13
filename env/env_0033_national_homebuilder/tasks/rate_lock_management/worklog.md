# worklog — rate_lock_management (erl-task-instantiate, M=2)

## Step 0 — difficulty pre-check
- draw_counts --tasks 2:
  task0 prerequisite_problems=3 factor_counts=[6,6,6,4]; task1 prerequisite_problems=2 factor_counts=[6,6,5]
- Constraint found: no rate sheet exists in the schema (no record of today's par rate), so any write that must
  price at "the current offered rate" (float-down, worse-of relock in general, program change re-price, new lock
  request par) cannot be computed from visible records. Claimable computations are therefore: upfront fee,
  confirmation locked rate (par on record), loan-amount decrease (never re-prices), extension, extension charge,
  builder-delay waiver, relock fee (with the builder-delay rate protection keeping the expired rate).
- Coherent trees:
  task0 (4 problems) = builder-delay lapse: relock -> extension (customer's own) -> extension charge -> builder-delay waiver (root)
  task1 (3 problems) = request stage: loan-amount resize to the LTV limit -> upfront fee payment (customer's own) -> confirmation (root)
- Owner decision: blueprint summary lists the agent as recorder of fee payments and extensions and only
  withdrawal as the buyer's own; withdrawal carries no multi-factor computation, so the customer-own writes are
  the upfront fee payment ("The buyer pays the upfront lock fee", event meaning) and the extension the buyer
  elects on their own lock. Recorded as a deliberate deviation for the orchestrator.

## Task 0 — progress
- Tree (chain): relock (lock_ext_builder_delay_relock, agent) -> extension days (lock_ext_extension_days, customer's own)
  -> extension charge (lock_ext_extension_charge, agent) -> builder-delay waiver (lock_ext_builder_delay_waiver, ROOT).
  Factor counts: relock 6, extension days 6, extension charge 6, waiver 4 (= draw [6,6,6,4]).
- Edges: days<-relock state_gate (status locked again after expiry); charge<-days value_input (new_increments);
  waiver<-charge value_input (charge_amount). 2 value_input >= max(3-1,1).
- Tools written + TASK TOOL CONTRACT OK: relock_expired_lock_fa041ac0, extend_rate_lock_f01da2c0 (user),
  assess_extension_charge_dd0de570, waive_builder_delay_charge_8eed57d4.
- World: Nathaniel Osei, second home MT-0418 Mesquite Trails (Meadow), 120-Day Extended Lock expired 2026-09-25
  (expired_date 09-26), builder slip 56 days, buyer closing extension +7, frozen 2026-10-13.
- Task 0 gates (per-task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  Fix log: helper function in task_tools.py was seen as an undiscoverable tool -> inlined; relock history floor failed
  (only LATEST read) -> the missing-reminder test now reads COUNT of expiry reminders.
- Task 0 figures: relock fee 1415.78, extension days 30 (2 increments), extension charge 1061.82 (LCK-CHG-4515), waiver 1005.07.

## Task 1 — design (request stage)
- Draw: prerequisite_problems=2, factor_counts=[6,6,5]. Tree: loan resize (lock_ext_loan_resize, agent, 5 factors)
  -> upfront fee payment (lock_ext_upfront_fee, customer's own, 6) -> confirmation locked rate (lock_ext_lock_confirmation, ROOT, 6).
  Edges: fee<-resize value_input (fee_loan), confirmation<-fee value_input (buyer_paid_fee). 2 value_input >= 1.
- World: Rosa Quintanilla, Cedar Hollow CH-0462 Heritage, 270-Day Build Lock requested 2026-09-30 at 90% of the
  pre-amendment price 533,490; plan-change amendment 2026-10-01 lowered the contract price to 518,490, so the loan on
  the request exceeds the resized loan limit. Frozen 2026-10-05 (last business day for the fee).
- Task 1 figures: resized loan 442,835 (ltv 85.41), upfront fee share paid 2,490.95 (CHM-RCPT-44397), locked rate 6.537 through 2027-07-02.
- Task 1 gates (per-task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Revision: final COMPUTE failed "suite history_rows_max=6 < 8" -> waiver factor 4 changed from purchase deposit standing to
  lock-ledger fee-standing goodwill, task 0 upfront fee seeded as two ach payments (500.00 + 443.85); figures unchanged.
- Final suite: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (history_rows_max=9, branches_max=76,
  means branches=68.50 steps=15.00) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK; TRACEABILITY NOT OK only because the 7 hidden
  tool names (unlock arguments) have no published KB yet — rerun after docs are rendered.
- Temporary authoring scripts lived in /tmp (removed); __pycache__ removed from the write domain.

## Round 2 — audit rework (audits/policy_task/rate_lock_management/{_difficulty,0,1}.md)
Items: F1/T0-1, F2/T0-2/T1-1, F3/T0-3/T1-2, T0-4, T0-5, T0-6/T1-3, observations O1-O9, T0-O1..O5, T1-O1..O3. Closure log below.
- F1 / T0-1 (undeclared override): lock_extensions added to lock_ext_builder_delay_waiver.base_policy_refs and its waiver sentence
  ("When the extension is needed ... is waived under lock_builder_delay_waiver.") named in overwrite, replaced by the extended waiver
  sentence; rule adds "Calloway bears only the part of an extension charge that the builder delay caused ..." (also squares with the
  purchase charter's "caused by a builder delay", O8). Base text untouched.
- F2 / T0-2 / T1-1 (mislabelled method): reminder multiplier = 0.5 + reminder lead / (2 x expiry_notice_days_before) on the late tier;
  slip cushion = one day per slip_week_days (14) of slip on the long tier; step-up = 1 + relock_fee charges counted (relocked) or
  1 + prior_increment_step x prior increments; builder fee share = 1 - min(half the rate_buydown_credit / floored fee, cap).
  Each method ladder now has a tier that computes a record-dependent quantity.
- F3 / T0-3 / T1-2 (indefinite baselines): rule + baseline.rule state "the expiry reminder multiplier starts at one", "the step-up
  multiplier starts at one", "The builder share starts at one and the lapse rate starts at one.", "the buyer's fee share starts at one".
- T0-4 (stamp agrees with tier): relock LTV tier break moved from 85 to 88 and the seeded lock ltv_pct set to 86.31 (request-time figure
  against a price with design options, declared stale in seed_consistency); the stamp now gives the fall-through, the rule's quotient
  (90%) the add-on — a real near-miss.
- T0-5 (near-miss wording): rationale names the stale ltv_pct and the closed Larkspur agreement as the excluded records.
- T0-6 / T1-3 (tie rounding): every half-up RND adds 1e-7 before rounding (and the floor in the resize), so ties round up; sensitivity
  figures now 1887.71 (relock reminder baseline) and 6.563 (term premium baseline), matching the rule.
- O1: homeowner credit reads a warranty coverage only when its purchase_id differs from the lock's agreement.
- O2/O3: docstrings drop "afterwards", before/after wording and the "fee booked separately" hint.
- O4: all seven tool suffixes redrawn, one uuid4 call each: relock 4b9eda82, extend 1be9088d, assess 644b0045, waive 21040a50,
  resize 60b17697, pay 77612280, confirm 760b1890 (renamed in charter, tools and tasks).
- O5: E1 sentence now "... includes the relock that returned it to locked." O6: E5 sentence now "... the buyer's payment of the upfront
  lock fee due from the buyer, after the buyer's fee share." O7/O9: no change (base sentences ground no edge; plan-change add-on kept,
  re-disclosure work on an amended contract). O8: see F1.
- T0-O2: persona now dates the reminder "around September 19". T0-O1/O3/O5, T1-O1/O2: no change needed (recorded). T1-O3: deposit share
  and deposit count rules say transferred reservation funds count as deposits.
- Effects: task 0 relock fee and terminal charges_due changed (factor 6 now method-figured); other scored values unchanged; task 1
  fee-sensitivity figures for two factors changed with the new share method. All texts, tracing and closure fields regenerated.
- Round 2 gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK /
  CACHE-DIFF INFO; TRACEABILITY NOT OK only on the 7 hidden tool names (KB not yet published).

## Round 3 — revision_2 items (N1/T0-7, N2/T1-5, T1-6, O4-r2, O10, O11, T0-O6, T1-O4)
- N1 / T0-7: removed the waiver-rule sentence "Calloway bears only the part of an extension charge that the builder delay caused ..."; the
  formula sentence (declared as replacement of the base lock_extensions waiver sentence, F1 stays closed) is the sole amount sentence.
- N2 / T1-5: builder fee share middle tier is now "a rate_buydown_credit granted and no closing_cost_credit" (conjunction); a
  closing-cost-only agreement reaches the fall-through by its condition, so no tier selects the fall-through value for part of its condition.
- T1-O4: both_credits_cap 0.5 -> 0.6, so the record-dependent part (half the buydown over the floored fee) sets the share on this world.
  Task 1 upfront fee and three of its sensitivity figures moved; the locked rate is unchanged (paid share stays in the same tier).
- T1-6: skip-resize figure recomputed under the reworked share and replaced in prerequisite_closure.edge_load_bearing and rationale
  sections 4 and 10; flips_to_true_by receipt and paid share updated.
- O4-r2: confirmation tool suffix 760b1890 -> 90ad719f (fresh uuid4 call), renamed in charter, tools and task 1 (this log keeps the
  old name only as history).
- O10: missing_reminder_mult 0.5 -> 0.4 (never equals the late tier's 0.5 floor). O11: relocked step-up = 1 + relock_fee charges +
  prior_increment_step x prior increments (varies with the record). Task 0 scored values unchanged.
- T0-O6: the stale ltv_pct is described only as a stored figure that disagrees with the loan over the contract price; the unsupported
  "price with design options" origin is removed from rationale, factor_trace, tracing and seed_consistency.
- Round 3 gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK /
  CACHE-DIFF INFO; TRACEABILITY NOT OK only on the 7 hidden tool names (no published KB yet).

## Round 4 — validate_scenario "forbidden 'from datetime'"
- task_tools.py: removed `from datetime import date, timedelta`; extend_rate_lock_1be9088d now adds the extension days to the
  YYYY-MM-DD expiration with inline integer civil-date arithmetic (days-from-civil / civil-from-days), checked against datetime on
  20,000 random dates/offsets with 0 mismatches. No name, owner, rw, signature or docstring changed.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / TRACEABILITY OK /
  CACHE-DIFF INFO / SCOPE OK; validate_scenario VALID.
- Replay note: db_closure content equals initial_state in both tasks (unchanged); its key order is written from a Python set and
  differs run to run even with no code change (three back-to-back replays gave three different file hashes), so file bytes differ
  only in that ordering; evaluation_criteria is not written by replay.
