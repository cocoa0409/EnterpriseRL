# Worklog — damage_claims_and_protection (category: protect), M=2

## Step 0 — difficulty pre-check (2026-10-07)

Draw (scripts/draw_counts.py --tasks 2):
- task 0: key env_0045_vacation_rental_platform/damage_claims_and_protection/0, prerequisite_problems=1, factor_counts=[6, 6]
- task 1: key env_0045_vacation_rental_platform/damage_claims_and_protection/1, prerequisite_problems=2, factor_counts=[5, 5, 5]

Writable surface of the protect charter (claimed events: guest_payment_requested, reimbursement_paid,
claim_denied, premium_refunded, plan_tier_changed, plan_cancelled):
- numeric writes: protect_guest_payment_requested.amount, protect_reimbursement_paid.amount,
  protect_premium_refunded.amount. Denials, level changes and cancellations carry no number.
- every task problem needs a 4-6 factor computation on a numeric write, and every tree needs an
  owner=user problem. The only computation in the charter rich enough for 4-6 load-bearing,
  record-derived factors is the claim payable of protect_evt_reimbursement (depreciation by item age,
  guest payments, deductible, sublimits, limits, income-loss nights).

DECLARED DEVIATION (for the coordinator): protect_reimbursement_paid declares a trigger into
payout:payout_adjustment_credited (no `when`, always fires). The skill forbids a task tool writing a
row that satisfies a cross-category trigger. The frozen blueprint claims protect_reimbursement_paid
for this difficulty ("books reimbursements"), and no other claimed numeric write can carry the drawn
factor counts. Resolution taken: the settlement tools write the protect ledger row only; the payout
credit is the payout desk's own knock-on (payout charter: "A claim_reimbursement equals the
reimbursement paid on the claim", booked by the host_payouts difficulty). No task tool writes any
payout table. Flagged for the policy audit.

Problem families (type-level prerequisite edges must keep the two task scopes disjoint):
- a stay can carry several claims (one per damage category). A loss that rides on another claim of
  the same stay — valuables taken in the stay's theft, lost bookings caused by the stay's property
  damage — is a companion claim: the stay bears one deductible, primaries bear equal shares, the
  companion bears what the stay's already-settled claims have not borne. That is the value coupling
  (value_input) and the order (companion waits for its primaries' reimbursements).
- task 0 family: valuables (root, host's own acceptance of the agreed-value settlement) <- theft
  (agent books the reimbursement).
- task 1 family (reserved): income loss (root, host confirms the cancelled bookings and accepts)
  <- property damage (agent), <- pet damage (agent).
Headroom: after task 0 claims {valuables, theft} and two tools, task 1 keeps {income loss,
property, pet} — three unclaimed settlement policies with their own tools and a natural fan-out tree.

## Task 0 — closed (valuables <- theft)

- Policies: protect_ext_theft_settlement (agent, pay_theft_reimbursement_c380c173, state_due, 6 factors),
  protect_ext_valuables_settlement (user, accept_valuables_settlement_01cb0de3, on_request, 6 factors).
- Edge valuables -> theft: value_input on va_stay_settled, state-form sentence "... is fixed only after the
  plan's HostCover ledger shows a reimbursement on that theft claim." Skip theft -> valuables 793.00.
- Gold: theft 656.98 (step 12), valuables 855.50 (step 14). All-baseline: 1705.00 / 2500.00.
- Revisions: r1 inlined the claim lookup (module helper was read as a tool); r2 closure check forces every
  seeded row to be read and the customer finder runs only at step 0 -> removed earlier-stay history,
  replaced theft repeat-loss share with theft documentation share (listing photo count), near-miss moved to
  the 2026-04-01 Superhost demotion; guest row reached through find_stays(customer_id=guest).
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, SCOPE OK.

## Task 1 — design (income loss <- property, <- pet)

Draw: prerequisite_problems=2, factor_counts=[5, 5, 5]. Occupied: theft, valuables policies and tools.
Claimed: protect_ext_property_settlement (agent), protect_ext_pet_damage_settlement (agent),
protect_ext_income_loss_settlement (user, root). Income loss is the companion of the stay's property- and
pet-damage claims (the damage made the home unusable); it bears what the stay's reimbursed claims have not
borne of the deductible. Both edges value_input (negated-direction state sentences). Property and pet
commute (neither reads the other's write).

## Task 1 — closed (income loss <- property, <- pet)

- Policies: protect_ext_property_settlement (agent, pay_property_damage_reimbursement_941cbbf5, 5 factors),
  protect_ext_pet_damage_settlement (agent, pay_pet_damage_reimbursement_a5391300, 5 factors),
  protect_ext_income_loss_settlement (user, accept_income_loss_settlement_ab094655, on_request, 5 factors).
- Gold: property 1554.60 (step 14), pet 586.13 (step 16), income 666.37 (step 18). Skipping either damage
  write -> income 583.03. Pet-before-property order: identical terminal hash and values.
- Per-task gates (--task 1): all OK.

## Difficulty closing

- 5 extended policies, 5 task tools, scopes disjoint (task 0: theft, valuables; task 1: property, pet,
  income loss); every policy recomputed at its GT call; both tasks call one owner=user tool.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 52.50, steps mean 17.00, history_rows_max 15, branches_max 59), GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.
- check_traceability: NOT OK by design until the KB is rendered (task tool names are reachable only from
  the published docs/); re-run after erl-kb-doc-render.
- Open items for the audits: (1) reimbursement rows carry the payout trigger (see Step 0 note);
  (2) owner=user on the valuables and income-loss settlements rests on host acceptance of agreed-value /
  lost-income settlements, while the blueprint summary lists reimbursements among agent actions;
  (3) each settlement policy repeats the program-wide escalation share and guest-payment method with its
  own values; (4) the lost-nights method reads the most recent host-cancellation calendar block only.
- Temporary authoring scripts (_authoring/) and __pycache__ removed from the write domain.

## Round 2 — rework after audits/policy_task/damage_claims_and_protection (2026-10-07)

- F-G1 (RED): the guest-payment ladder had two distinct outcomes. Replaced in all five policies by the
  recovery-sharing method (factor `<cat>_recovery_sharing_method`, effect method): HostCover Premier/Elite/
  Estate make the host whole first (subtract the larger of guest payments and deductible); Standard/Plus
  share proportionally (deductible + payments x (adjusted loss - deductible, floor 0) / adjusted loss);
  Essential credits Roamhaven first (both subtracted; the baseline). Each policy now names its "adjusted
  ... loss" in the order sentence; compute moved *_covered/*_offset before *_net. Overwrite replaced_by
  updated.
- F-G2 (RED): theft documentation share (listing photo count) removed; replaced by the theft repeat-loss
  share (approved theft claims from other stays in 24 months: 1 -> 90, 2+ -> 75). Task 0 world gained the
  spring 2025 stay, its guest (gov id 5144), the 2025 theft claim, request, Standard premium, 565.00
  reimbursement and host fee row; reads now find_stays(host_account_id) plus find_stays per guest.
- O-L3: condition-share rules state the review's one-year rating window covers the stay. O-L4: pet-fee
  share grounded in the pet fee paid (deep-cleaning offset analogue). O-L5: "agreed value" wording removed
  from the valuables rule and tool docstring. O-T0-2: rules say "rounded half up"; no declared figure ties.
- Not changed: O-RC1 (DSL has no date-bound filter; no prior-year rows fall in the ambiguous part-month),
  O-RC2/O-RC3 (equivalent by construction), O-L1 (escalation shares kept: notice timeliness bears on
  recovery; replacing 5 factors is not cheap), O-L2 (accepted by audit), O-T0-1/O-T1-1 (reactive only),
  six-claimed-events observation (no other claimed event carries a number; see Step 0).
- New gold: theft 620.46, valuables 832.20 (skip theft -> 771.40); property 1499.07, pet 555.49,
  income 648.59 (one damage write skipped -> 567.48, both -> 486.37).
