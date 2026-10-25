# worklog — protection_plan_claims_and_refunds (env_0080), M=2

## Step 0 — draws
```
{"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 6, 4, 5]}
{"task": 1, "prerequisite_problems": 1, "problems": 2, "factor_counts": [6, 5]}
```

## Step 0 — charter scan (plan.yaml) and structural decisions
- Writable events (claim list): plan_purchase, plan_register_item, plan_file_claim, plan_decide_claim,
  plan_settle_claim, plan_fulfil, plan_cancel, plan_cancel_before_start, plan_refund, plan_charge, plan_lapse.
- Trigger table (base `triggers`): plan_charge (northgate_card -> card), plan_refund (northgate_card -> card),
  plan_settle_claim (reimbursement_egift_card -> gift). All other plan events: none. => every money row my
  tools write is fixed to payment_method_type external_card; no tool writes reimbursement_egift_card.
- owner=user legitimacy (owner_ruling.md): in plan only (a) the holder's cancellation (active->canceled by user)
  with its grouped refund, or (b)/(c) a holder-completed payment (plan purchase / Complete Monthly fee).
- DECISION D0 (thin-charter route, recorded): the Complete Monthly fee is a constant (16.99) and a plan price is a
  band lookup with no prerequisite a plan write can move, so neither can carry 4-6 load-bearing factors in a
  synchronous problem tree; the only owner=user write that carries a real multi-factor computation is the
  holder's cancellation with its refund. Each task therefore roots on a holder cancellation, but of a different
  plan family with a different refund mechanic, claimed as two exclusive policies:
  task 0 = Accident-tier single-item plan (refund keyed on the plan's claim/settlement standing and the corrected
  price); task 1 = Standard-tier single-item plan (refund keyed on paid food-loss claims and the manufacturer
  warranty overlap). Closest established rule: owner_ruling (a) + XF C.16 (sibling policies may retire the same
  base clause, each self-scoped, each naming the other's case). Principle-C risk acknowledged here.
- DECISION D1: service-fee decision with a positive fee must be followed in the same tree by the repair
  authorization (the fee is collected before release, i.e. at the service visit, after authorization), so the
  decision lives in task 0 together with the settlement; task 1's prerequisite is the food-loss payment (Standard
  tiers only carry food loss).
- Cross-difficulty evidence: the order category (order_returns_and_price_adjustments) — covered order line,
  fulfilment program and dates, price adjustments. All seeded order rows priced by order.yaml (external_card
  tender => no cardholder discount, no card rows; large-item program member_benefit_eligible=false => no
  membership interplay).

## Problem trees (draft)
- task 0 (Accident 3-Year laptop, OK): root R0 = Accident cancellation refund (user). Prereqs: BE = billing
  correction refund of the over-banded plan price (VI into R0's kept price), S = repair authorization value
  (VI into R0), D = claim decision service fee (state_gate into S). Factors: R0 6, D 6, S 5, BE 4 (to confirm).
- task 1 (Standard 3-Year refrigerator, TX): root R1 = Standard cancellation refund (user). Prereq FL = food-loss
  payment (VI into R1). Factors: R1 6, FL 5.

## Task 0 — design locked (written to disk)
- DSL limits found: no tuples/subscripts/comprehensions (ladder lists such as price_ladder / service_fee_ladder cannot be
  indexed) -> a billing re-band correction is not computable; third prerequisite switched from BE to the limit-of-liability
  registration G (registration missing on a plan bought by phone after fulfilment).
- Policies (plan.extended.yaml): G plan_ext_limit_of_liability_registration (4 factors, cross-difficulty order),
  D plan_ext_accident_claim_service_fee (6), S plan_ext_repair_authorization_value (6), R0 plan_ext_accident_cancellation_refund (5).
  Factor counts 4/6/6/5 = draw [6,6,4,5] as a multiset.
- Tools (task_tools.py, TASK TOOL CONTRACT OK): register_item_limit_ba116528 (agent), record_claim_decision_cf68f06d (agent),
  authorize_claim_repair_5d8df043 (agent), cancel_accident_plan_cec4ac7d (user, owner_ruling (a)).
- Tree: R0 <- D (value_input, fees owed), R0 <- S (value_input, payout share), S <- D (state_gate, approval), S <- G (value_input,
  registered limit). Order G, D, S, R0 (G and D commute: neither reads the other's rows).
- Scratch evaluation (check_compute DSL): G 2289.97 (baselines 2489.97/2389.97/2059.98/2279.98; all 2349.99);
  D 43.75 (34.00/58.75/33.75/48.75/38.75/53.75; all 49.00); S 676.69 (553.50/526.69/646.69/636.69/656.69/652.19; all 289.00);
  R0 196.67 (260.12/186.17/188.14/187.78/186.67; all 220.08).
- Trigger table for task 0 writes: plan_register_item [], plan_decide_claim [], plan_settle_claim (repair) — trigger only on
  reimbursement_egift_card, not written; plan_refund external_card — trigger only on northgate_card, not written; plan_cancel [].

## Task 0 — closed (per-task gates)
- tasks/0.json written by scratch generator (/tmp/protection_plan_claims_and_refunds_0080/gen0.py); figures after the
  check_compute "history zeroed" red: plan-price credit raised 10 -> 12 so D's history bears weight (repeat step +10 and
  plan-price credit no longer cancel). Final: G 2289.97, D 41.75, S 676.69, R0 198.77 (baselines 2349.99/49.00/289.00/222.08).
- Fixes during gates: empty FK strings -> None (replay dangling FK); factor evidence must come from records -> category
  read from the covered order line (XLATEST, cross-difficulty) and term from MONTHS(coverage dates); intent_source kinds.
- Per-task gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- compute_basis / policy_source verbatim sweep (scratch sweep.py): clean. Factor ids not substrings of tool names.

### Probe table (task 0 reads)
| read | decoy | absent | second record |
|---|---|---|---|
| G XLATEST covered line (amount/qty/promo/card) | docking & household lines on same order: excluded by order_event_id | `or 0/1` -> recorded price, no reduction | n/a (line ids unique) |
| G XSUM price adjustments on line | competitor match -> half share tier | 0 -> no reduction | two drops -> summed |
| G XSUM same-category lines | household line other category excluded | 0 accessories -> 0 | returned accessory not netted (stated: merchandise lines) |
| G CFIELD order program | — | None -> add nothing | first match by order_id (unique) |
| D LATEST claim | denied 2026-01-03 claim older | out of domain (decision needs a claim) | same-day tie: first row kept |
| D COUNT claims 12m | claim 13 months old falls out | 0 -> -1 -> no step | 3 claims -> two-claim step |
| S SUM registrations/settlements | food-loss settlement counts in remaining share (stated) | 0 -> remaining share 0 | — |
| R SUM decisions fee within 1 month | 2026-01-05 denial (fee 0, outside window) | 0 | two decisions -> summed |
| R LATEST submitted cancel request | confirmed/withdrawn excluded by status filter | None -> 0 days | latest kept (rule says most recent) |

### Defining-sentence table (sentence -> binding/factor)
- G: "starts from the covered item price recorded" -> recorded_price (baseline); starting price sentence -> price_paid_basis;
  price adjustments sentence -> adjustment_pass_through; accessory sentences -> accessory_allowance_rule; delivery sentence ->
  delivery_charge_inclusion; assembly sentence -> result.
- D: baseline band sentence -> band_amount/chargeable; category sentence -> starting_fee_method; prompt/repeat/term/late/price
  sentences -> their factors; assembly -> result.
- S: remaining share sentence -> plain; flat charge (baseline) -> flat_charge; repair charge / parts / age / service-call /
  inspection / label sentences -> their factors; assembly -> result.
- R: price kept, coverage/unused days, fees owed (baseline) -> plain; count-start -> coverage_count_start; payout ->
  payout_weighting_rule; fee by months held -> held_months_fee; late handling -> late_handling_addition; denial credit ->
  denial_credit_rule; order of operations -> net_refund/result.

## Task 1 — closed (per-task gates)
- Policies: FL plan_ext_food_loss_payment (5 factors; household allowance reads the order's haul-away fee and program,
  cross-difficulty), R1 plan_ext_standard_cancellation_refund (6 factors; unused share and fee read the covered line's
  manufacturer warranty months, rebate reads its price drop — cross-difficulty; warranty_period_fee multi-source).
- Tools: pay_food_loss_claim_b4f587dd (agent), cancel_standard_plan_ca7b280f (user, owner_ruling (a)).
- Figures: FL 295.54 (baselines 248.74/373.64/264.30/285.54/275.54; all 250.00); R1 72.85 (5.85/263.82/47.85/71.99/63.88/
  87.85; all 176.99); skip FL -> R1 220.62.
- Trigger table for task 1 writes: plan_settle_claim food_loss_payment (trigger only on reimbursement_egift_card -> none);
  plan_refund external_card (trigger only on northgate_card -> none); plan_cancel []; plan_requests no event.
- Owed-write check: no other product's rule makes an order/card/membership write owed at the opening of either task (orders
  fulfilled, adjustments booked, no returns pending); the plan writes owed (registration, decision, food-loss payment) are the
  prerequisite problems themselves.
- Realism notes for the audit (honest): the refund, fee, repair-value and food-loss schedules are company schedules worded as
  the administrator's own (no statute cited); the two cancellation-refund policies are siblings over disjoint plan families
  (D0). Rounding: half up via RND(x+1e-9) on fees/settlements/registration; refunds round down via int(x*100+1e-9)/100;
  no scored figure lies within 1e-6 of a rounding boundary (D 41.74975, S 676.6946, R0 198.7754, R1 72.8557).

## Final gate block (no --task)
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK
- GROUNDING OK
- SCOPE OK
ROUND 1: gates 7/7 green

## REWORK round 2 — plan (audit files 0.md, 1.md, _difficulty.md read in full)
Items: C1-C11, T0-1, T0-2, T0-3, T1-2, T1-3 (+ observations O1-O15 reviewed). Plan per class:
- C1 (all six): every factor sentence states its own action on the figure; one generic order sentence per rule
  ("standard inputs replaced first, then rates, deductions and additions..."), no factor quantity named in it.
- C2 + class sweep: every record selection read by more than one factor or by the baseline becomes a plain binding.
- C3 + class sweep: every method factor gets pairwise-distinct shapes / inputs, no unreachable tier (price_paid_basis on
  unit price vs card discount vs recorded; delivery charge -> parameter share; starting fee / repair charge / spoilage
  allowance middle tier becomes a max() pick; count start middle tier = purchase-date start).
- C4: tie rule stated (first listed on the plan ledger), term length by coverage days, 12-month windows stated as
  "less than 12 whole months before today".
- C5: warranty >= term -> share one. C6: unused days capped at coverage days. C7: refunds capped at the price kept.
- C8: repair authorization books a replacement settlement (and fulfils the plan) where the repair value would exceed the
  replacement threshold; edges reworded "repair or replacement settlement".
- C9: positive-amount guards; cancel tools refund only external-card charges (trigger rule) and confirm an open request.
- C10: denial credit replaced by an approved-claims administration charge. C11: accessory lines restricted to
  general-merchandise return class (no second device); delivery inclusion as a parameter share.
- T0-1: battery claim approved before the opening and awaiting its repair (root edge unmet at frozen_time); repair
  settles that claim; decision now waits on it (state_gate), order G -> S -> D -> R0.
- T0-2: recorded covered item price seeded as the net price paid (charter meaning).
- T0-3 / T1-2: withdrawn cancellation requests seeded as near-misses (status filter excludes them).
- T1-3: delivery-gap credit removed (double count); replaced by a late-handling addition on the seeded open request.

## REWORK round 2 — closure record
- C1 (class, all six rules): assembly sentences rewritten generically ("Where several of these apply, the starting X is
  settled first, every amount that comes off or is added is then applied to it, ..."); each factor sentence states its own
  action on the figure. No assembly sentence names a factor quantity.
- C2 (class sweep): incident/filing dates of the decision are plain bindings; every selection read by two factors or by the
  baseline (line amount/units in registration; claim selection in repair; settlements in refunds) is a plain binding; each
  factor's category read is its own binding.
- C3 (class sweep, pairwise table): replacement_price_basis T1 selling price / T2 amount+card discount / T3 recorded price
  (distinct inputs; recorded price now the net price, so T1 and T3 differ on charter-produced worlds); delivery inclusion
  is now a parameter share (delivery_charge_share); starting_fee_method T2 = greater of band and visit charge;
  repair_charge_method T1 = flat charge scaled by registered limit, T2 = greater of flat charge and in-home minimum;
  spoilage_cause_allowance T2 = greater of flat allowance and disposal rate; coverage_count_start T2 = purchase-date start
  (reachable for Accident plans bought before delivery; probe gives a distinct figure).
- C4: tie rule "the one listed first on the plan's ledger" in decision, repair and food loss (probes: same-day ties keep the
  first-listed row); term credit by coverage days (1095/1460) instead of MONTHS; 12-month windows stated as "less than 12
  whole months before today" (probe: a claim dated exactly 12 months before is excluded).
- C5: warranty months >= term_months -> unused share one; denominator term_months (probes at 36 and 48 months: no crash).
- C6: unused days capped at the coverage days so counted (probe: cancellation before the shifted start, used share 0).
- C7: both refunds held to no more than the price kept (probe: plan without claims returns exactly the price kept).
- C8: repair authorization books a replacement at the remaining share and fulfils the plan above the replacement threshold
  of the recorded net price (probe: cheap item -> replacement); edges reworded "repair or replacement settlement".
- C9: positive-amount guards in register/repair/food-loss tools; cancel tools refund only charges paid by external card
  (trigger rule) and confirm the most recent waiting request instead of adding a second one.
- C10: denial credit removed; replaced by claim_administration_charge (approved claims), which also carries the decision's
  value into the refund.
- C11: accessories limited to general-merchandise-class lines of the covered item's category (probe: a second laptop line
  is excluded); delivery charges now a parameter share.
- T0-1: battery claim approved 2026-09-23 and unsettled at the opening; the repair settles it; the refund edge reads
  "approved before today"; decision waits on the repair (state_gate). Order G -> S -> D -> R0. All four edges unmet at the
  opening on seeded rows.
- T0-2: plan covered_item_price_usd seeded as the line's net amount paid before tax.
- T0-3 / T1-2: withdrawn cancellation requests (August / July) seeded; the status filter excludes them (probes).
- T1-3: delivery-gap credit removed; request_waiting_addition reads the seeded waiting website request.
- Observations: O1 (base definitional text) cannot be changed (base frozen) — each extended rule is scoped and explicit;
  O2 docstrings no longer name "approved" claims; O4 food-loss household tier reworded as an installation allowance with
  coherent tiers; O8 failure claim = mechanical failure or power surge; O9 repair baseline now states the remaining share;
  O12 consistent: the October claim's fee is taken from the refund and its repair follows release; O13 kept (company
  schedule, observation); O15 "portable-device rate" no longer called a tier parameter; open-request observation closed by C9.
- Seed/realism: order rows re-priced (sleeve line, amount paid); persona lines updated (battery claim, August/July
  requests, website form); all proofs, traces, closures and rationales regenerated from the scratch evaluation.
- Probe table (scratch /tmp/protection_plan_claims_and_refunds_0080/probes.py): absent covered line, match-only, second
  device, in-store program, card-discount tier, same-day ties (decision, repair, food loss), 12-month boundary, 1095-day
  span, replacement branch, shifted-start cancellation, missing registration, purchase-date start, surge approval, absent
  failure claim, warranty >= term, no warranty bought after, withdrawn-only request, cap — all evaluate, none crashes.
- Full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 2: gates 7/7 green

## REWORK round 3 — plan (audit revision_2 sections of _difficulty.md, 0.md, 1.md read in full)
Items: R2-C3, R2-C11, N1, N2, N3, T0-R2-1 (+ O16-O20). Verified each finding on the scratch evaluator before changing:
- R2-C3 confirmed (replacement_price_basis tiers all return the pre-discount unit price on charter-produced lines;
  coverage_count_start T2 formula is 0 on T3's domain). Fix: registration basis T2 = the lowered Northgate price of a
  price drop (new input); competitor matches move to their own parameter factor; coverage_count_start T2 limited to a
  delivery wait of more than the short-wait days, so T3 covers short gaps where the T2 formula differs.
- R2-C11 confirmed (mixer/blender, fridge/range probes). Fix: accessories only for a covered device whose own return
  class is not general merchandise; accessory amount and delivery fees divided among the order's device lines of the
  covered category, so each is counted once per order across plans.
- N1 confirmed. Fix: same-incident failure claims — an approved one counts first, then a manufacturer-warranty denial.
- N2 confirmed. Fix: the decision gate and the refund's settlement edge are keyed on "carries a settlement" (any kind).
- N3 confirmed. Fix: no-lemon clause applied in the repair rule and compute (settlement rows now carry the claim type),
  no overwrite needed; the base clause is followed.
- T0-R2-1 confirmed (second path repairs the October claim). Fix: the repair rule authorizes no repair on the day of the
  approval, and the cancellation rule states outright that a claim approved on the cancellation date keeps its fee in the
  claim service fees still owed and is repaired after the cancellation under the repair rule.

## REWORK round 3 — closure record
- R2-C3: replacement_price_basis T1 unit price before promotions / T2 the lowered Northgate price of a price-drop
  adjustment (input adjusted_unit_price_usd) / T3 recorded net price — pairwise distinguishing inputs: promo line (T1 vs
  T3: unit price above net), drop line without promo (T2 vs T3: lowered price below net; T2 vs T1 formula: unit price =
  net there). Competitor matches are a separate parameter factor (local whole / online half / none), so no price base is
  mixed (O18). coverage_count_start T2 requires a delivery wait of more than the delivery-wait days; on T3's domain with a
  short wait the T2 formula gives a different count (probe: three-day wait -> T3 figure, sixteen-day wait -> T2 figure).
  starting_fee_method visit charge set below the top band so "the greater of" can pick either (O19).
- R2-C11: covered device lines = same-category lines of the covered line's return class; accessories count only for a
  non-general-merchandise covered line; accessory allowance and delivery share divided by the device lines, so each is
  counted once per order across plans (probes: mixer with blender -> no accessory, fee split in two; refrigerator with
  range -> delivery fee split in two).
- N1: same-incident failure claims — any approved one first (greater-of tier), else a manufacturer-warranty denial
  (rate tier), else nothing; both claim types read (probe: denied mechanical + approved surge -> approved tier).
- N2: the decision gate and the Accident refund's settlement edge now read "carries a settlement" (any settlement row);
  task 1's seeded October decisions are consistent with it (the June food claim carries its food-loss payment).
- N3: the repair rule applies the base no-lemon clause (repairs of the same claim type on the line at no_lemon_repairs ->
  replacement at the remaining share); settlement rows now carry the claim type (tools copy it; seeded food-loss
  settlement carries food_spoilage). No overwrite needed — the base clause is followed (probe: three battery repairs ->
  replacement).
- T0-R2-1: repair rule "A claim is not authorized on the day of its approval" (compute gives no value on an approval dated
  today; the tool rejects a zero amount); cancellation rule states outright that a claim approved on the cancellation date
  stays covered, its fee is among the fees still owed taken from the refund, and its repair follows the cancellation
  (probe: authorizing after the October decision gives no value). The service fee is charged only on accidental damage,
  a base service-fee claim type. Persona gains a passive line for the post-cancellation repair. Real-administrator check:
  claims for incidents inside the term are honored after cancellation; the outstanding deductible is netted from the refund.
- O16-O20: O18/O19 closed above; O20 closed (persona no longer volunteers the sleeve); O16/O17 noted (placement wording;
  installation allowance kept as a company schedule).
- Stale-text sweep over tasks/0.json, tasks/1.json and the charter: no round-2 figure or wording remains.
- Full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 3: gates 7/7 green

## REWORK round 4 — closure record (audit revision_3: both tasks PASS; charter items R3-C11, N5)
- R3-C11 verified by probe, closed by one record-composition sentence in plan_ext_limit_of_liability_registration
  ("The order's line composition is read once and used throughout: ..."), the only policy that reads accessories or
  delivery shares. Merchandise lines = every line of the covered order whatever its category; device lines = lines in
  the covered category with the covered line's return class; accessory lines = general-merchandise lines of the
  category, counted only when the covered line is not general merchandise and every such line is priced below the
  lowest min_item_price_usd of the single-item tiers (no line that could carry a plan of its own is ever an accessory).
  Delivery fees are shared across all merchandise lines of the order. Probes: a coverable keyboard on the laptop's
  order -> no accessory; refrigerator + sofa on one large-item order -> the fee is split across both. Task 0's
  accessory is reseeded as a charging cable priced below the lowest plan price (order amount paid re-priced).
  Single-factor bindings moved into their factor (XF A.3).
- N5 verified by probe, closed: the decision gate is scoped to "every claim approved on the plan before today carries a
  settlement", so a second same-day decision is never blocked; the claim decided (and every fee read) is "the latest
  claim filed on the plan that does not yet carry a decision", the decision tool marking the claim itself with its
  decision (seeded decided claims carry theirs). Probe: two undecided claims -> both decided in the call, each fee keyed
  on its own claim. The same-day repair bar stays (closes T0-R2-1 and is no longer combined with the gate).
- O21-O23: O21 noted (resolved_by names the resolver of the engaged tree); O22 noted (returned lines are still lines of
  the order); O23 noted (company processing rule).
- Task 0 figures regenerated (registration, repair and refund move; decision unchanged); task 1 unchanged. Stale-text
  sweep over both task files and the charter: clean.
- Full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 4: gates 7/7 green

## REWORK round 5 — closure record (audit revision_4: both tasks PASS; charter item N6, observation O24)
- N6 verified by probe (unit price vs net price), closed in plan_ext_limit_of_liability_registration: the accessory test
  now compares each general-merchandise line's line amount, the net price paid for the line before tax (the price the
  plan-eligibility rule uses), in rule and compute (XMAX over amount_usd). Probes on a scratch copy: a promotion that
  takes the cable's net amount below the lowest plan price -> counted as an accessory; a cable whose net amount is at or
  above it -> no accessories; absent accessory -> nothing; coverable keyboard present -> none. Task 0 figures unchanged.
- O24: kept on purpose and now stated with its reason in the rule (a coverable general-merchandise line may have been
  bought for its own sake, so the order then counts no accessories at all). O25 noted (delivery share over all lines,
  no double count).
- Task texts reworded to the net-line-amount test; stale-text sweep clean.
- Full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 — seed-only (policy_kb revision_2 src2, src3; src1 BLUEPRINT-KNOWN, no action)
- Charter and tools untouched (sha256 verified before and after).
- Bounded exhaustive pass over every seeded row of another product in both worlds: all order rows (lines, promotions,
  fees, haul-away, competitor match / price drop windows and amounts, amount paid) already match the published order
  docs as of their dates (the KB re-judge confirms); neither customer holds membership, card, gift, market or trade rows.
- Own-product history re-priced with the published plan rules as of each row's date (scratch evaluation on the world as
  it stood on that date):
  - src2 closed: task 1 June food-loss payment re-priced as of 2026-06-19 (limit raised by the registered limit, whole
    share, disposal, reporting and installation allowances); remaining limit on the plan holding updated.
  - src3 closed: task 1 January registration re-priced as of 2026-01-24 (promotion start, large-item delivery and
    haul-away share; the later price drop excluded).
  - Task 0 history checked: the January denial and the September battery approval carry no service fee under the
    published fee rule as of their dates; the plan charges match their price bands. No change.
- Gold moves in task 1: the Standard cancellation refund (via the claims deduction); the food-loss payment is unchanged.
  Task 0 gold unchanged. Task 1 traces, sensitivities, closure, seed checks and rationale recomputed; persona has no
  amounts; stale-text sweep clean.
- Full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK
  (TRACEABILITY OK also run).
REWORK round 6: gates 7/7 green
