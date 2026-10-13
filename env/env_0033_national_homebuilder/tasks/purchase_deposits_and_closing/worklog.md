# worklog — purchase_deposits_and_closing (erl-task-instantiate, M=2)

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/purchase.yaml,
  db_schema.json, share_tools.py (identity: find_customers -> verify_customer_identity, K=2 credentials).
- Draw (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=1, factor_counts=[5, 4]
  - task 1: prerequisite_problems=1, factor_counts=[6, 4]
- Constraint found: every task needs an owner=user task tool that carries a computed parameter. In this
  charter the buyer-originated numeric writes are (a) the buyer-requested closing extension
  (purchase_closing_extended: "A buyer may move the scheduled closing date later up to
  closing_extension_max times") and (b) a deposit payment the buyer makes (purchase_deposit_posted).
  purchase_cancelled (the lifecycle's by:user transition) carries no numeric field, so it cannot be a
  scored problem. Any purchase_deposit_posted write inherits the base gates additional_deposit_deadline
  and return_cure_window (subject-scoped), so a buyer deposit write is only well-formed inside a
  returned-payment cure window during the additional-deposit window.
- Decision: task 0 = late closing (per diem -> buyer extension, user = the buyer signs the extension
  addendum); task 1 = returned additional deposit at construction start (user = the buyer wires the
  replacement funds). Headroom: task 1 uses deposit/charge events (purchase_deposit_posted) that task 0
  does not touch; task 0 uses purchase_charge_assessed (per diem) + purchase_closing_extended.

## Task 0 — design thesis
- Surface goal: buyer (outside lender after switching away from Calloway Home Mortgage) asks to push her
  missed closing back; her extension request fee is already on the ledger, the addendum awaits her signature.
- Tree: root purchase_ext_buyer_closing_extension (user tool, computes extension_days, 4 factors)
  <- value_input <- purchase_ext_closing_delay_per_diem (agent tool, computes amount, 5 factors).
- Edge sentence (state form, affirmative): the new closing date waits on per diem standing on the ledger
  for the buyer-delay days before the request.

## Task 0 — closed (gates --task 0)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
- per diem expected 1782.00 (baseline 3825.00; factor baselines 3168.00/2178.00/1584.00/1620.00/2227.50);
  extension expected 46 (baseline 14; factor baselines 28/39/39/45); skipping per diem -> 28.
- Fix during gate: helper functions at module top level counted as task tools -> inlined into tool bodies.
- Extension fee for the request is pre-charged in the seed (fee booked when the emailed request was received),
  so no fee write is owed after the buyer signs; per diem period stops the day before that request.

## Task 1 — design thesis (decided after a long search; see decision note)
- No second natural buyer-owned numeric write exists besides the closing extension (taken by task 0), so the
  buyer's own write is the replacement wire for a returned deposit payment (purchase_deposit_posted), which is
  only well-formed inside the return cure window and the additional-deposit window (both base time gates are
  genuinely engaged: construction start 2026-09-28, return notified 2026-10-02, frozen 2026-10-06).
- Tree: root purchase_ext_returned_deposit_replacement (user wire, 6 factors) <- value_input <-
  purchase_ext_returned_payment_fee (agent, state_due, 4 factors). Edge sentence, state form, negated direction:
  replacement funds are not figured until the ledger carries the returned-payment fee for every returned payment.
  Value link: the replacement's repeat-return security tier counts returned-payment fees charged on the agreement.
- Decision note for the orchestrator: the factor ladders of both task-1 computations are Calloway-designed
  refinements (escalating NSF fee, cross-product return surcharge, large-item / method charges; additional
  deposit uplifts by financing, homesite premium class, studio options, occupancy intent; repeat-return security;
  lot premium deposit excess/shortfall carry). Base gives only flat values here; these are declared via overwrite.

## Task 1 — closed (gates --task 1): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK /
COMPUTE OK / GROUNDING OK / SCOPE OK. fee expected 110.00 (baseline 35.00), replacement 25159.60 (baseline 12829.80);
skipping the fee -> 21952.15.

## Final difficulty-wide run
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches=28.50, steps=11.50;
history_rows_max=16, branches_max=31); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK.
TRACEABILITY NOT OK — expected before KB render: the four hidden tool names have no source until docs/ is published.
Authoring scratch (_author/, __pycache__) removed at hand-off.

## Round 2 — rework against audits/policy_task/purchase_deposits_and_closing/{_difficulty,0,1}.md
Base copy untouched (first 978 lines byte-identical to blueprint/products/purchase.yaml); every fix lives in
extended_policies, the task worlds or the GT path.
- F1 / T0-F1 (weekend roll: Saturday and Sunday tiers one method) -> P2 rule, compute and ladder now move a weekend
  date to the nearest weekday: Saturday back to the Friday before, Sunday forward to the Monday after, weekday
  unchanged (three distinct methods). Task 0 takes the Sunday tier; its figures are unchanged. P2 keeps 4 factors.
- F2 / T1-F1 (lot premium squaring: one signed true-up) -> three methods: an excess held is credited but capped at the
  reservation credits applied to the agreement (the rest stays with the non-refundable lot premium deposit); a
  shortfall is added in full; otherwise no adjustment. P4 again has a real method factor. Task 1's adjustment is
  unchanged because the cap equals the excess.
- F3 (P1 grace ladder contradicted "shrink" for low-grace collections) -> the one-request tier is now
  per_diem_grace_days less one day, never below zero, and the separate 1-day parameter is removed, so a request never
  grants more grace than no request. Task 0 (Summit, grace 2) still gets 1 day. Tiers can still coincide where
  per_diem_grace_days is 0 or 1; no task uses those collections.
- F4 (P2 compute dropped "no per diem has been charged") -> the tier-2 test now also requires perdiem_count == 0.
- O1 -> the rule states lot premium deposit owed is zero without a converted reservation; the unstated
  lp_owed >= 0 / > 0 guards were removed.
- O2 -> "an outside-lender deposit stands" is now defined as postings exceeding returns, in both rule and compute.
- O3 -> P3's rule now states the charge is dated the day it is booked; a fee not yet booked is booked when the return
  is next handled. Base trigger text unchanged (frozen).
- O4 -> no change. The base per diem formula/measure is not rule text and cannot be quoted. The end day falls inside
  the declared overwrite clause ("its first and last day"); recorded in task 0's rationale.
- T0-F2 / T1-F2 (opening pre-authorisations) -> both personas' unconditional "happy to post whatever is owed / goes
  with a returned payment" sentences were removed; only the conditional reactions remain. no_user_hint updated.
- T0-O1 -> trigger reworded to "a charge ... for days you were late past your closing date".
- T0-O2 / T1-O1 -> rationales no longer call the single-row studio factors multi-source.
- T0-O3 -> delay-measure figure corrected to 20 days.
- T1-F3 (0.01 half-cent proof figure) -> P4 uplifts are now in tenths of a point (premium 0.3/0.6, studio 0.3/0.6,
  cash 0.3), so no percentage of the contract price leaves a half cent. The seeded additional deposit and its
  return were moved to the new rate, and every task-1 figure was recomputed and re-verified by check_compute.
Gates re-run (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK; TRACEABILITY NOT OK (pre-render, hidden tool names have no KB source yet).
