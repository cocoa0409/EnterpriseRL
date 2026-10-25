# plan.md — gap_waiver_cancellations_and_claims (env_0072), M=2  (revision 2, relaunch)

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3 (4 problems), factor_counts [6, 4, 6, 6]
- task 1: prerequisite_problems=1 (2 problems), factor_counts [6, 4]

## Why revision 1 was replaced (symptom -> root cause -> change)
- Rev 1 had the borrower's claim report compute "the balance on the date of loss". The compute is
  evaluated on the world BEFORE the write, and no record carries the date of loss before the claim
  row exists (DSL: no date construction, exact filters only) -> the report's figure is not computable.
- Rev 1's denial -> refund chain needs a paid-off contract (refund mailed is the only non-triggering
  destination); a paid-off contract with an ACTIVE addendum owes a company early-payoff cancellation
  (gap_company_cancellation) that competes with the claim route; a denial for no primary insurance
  also needs no worksheet, so worksheet prerequisites of a denial are not genuine. Dropped.
- Change: both worlds hold a claim already reported on first notice of loss (gap_claim_filed row
  with loss date, loss type and the insurer's settlement figures; addendum claim_open). Every
  problem is a worksheet figure written onto that claim row, computable because the loss date is
  on record. The borrower's own act (blueprint: "supply the primary insurer's settlement documents")
  is the deductible-reimbursement claim made with those documents.

## Base limits (frozen blueprint; routed around, never edited)
1. Trigger rule: gap_claim_decided approved -> contract credit; gap_refund_issued credited_* ->
   contract/deficiency. No tool here writes a decision or a refund at all.
2. The claim row's numeric fields are the only writable computed quantities: balance_at_loss_usd,
   excluded_amounts_usd, deductible_covered_usd, benefit_usd. Six problems over four fields ->
   two pairs are product-scoped: deductible reimbursement and excluded amounts are written by a
   GAP Waiver Premier 150 policy (task 0) and a GAP Waiver Plus 150 policy (task 1) -- the two
   plans that carry a deductible reimbursement -- each with its own product schedule (scoped
   overwrites, sibling tails name each other).
3. Base benefit formula double-counts an uncovered deductible (it is both an excluded amount and
   left out of "+ deductible covered"); the worksheet benefit deducts the insurer's net settlement
   (ACV less deductible) instead -- declared overwrite.
4. Scheduled balance "plus interest accrued to the date of loss": the last scheduled due date
   cannot be constructed in the DSL -> the worksheet balance carries no post-due-date interest
   (declared overwrite).
5. Worksheet writes subject = gap_claim_opened (the addendum held in claim status while the loss is
   reviewed): no base eligibility applies_to it (claim_on_active_addendum is for the filing).
6. trigger: on_request for all six (worked when the borrower asks the claim to be worked), so the
   task-1 world does not light the task-0-only policies.

## Trigger table (every event a tool writes, with base triggers)
| tool | owner | write | base triggers | outside gap? |
|---|---|---|---|---|
| claim_premier_deductible_reimbursement_7815b2b6 | user | update claim row deductible_covered_usd | none (update of a gap_claim_filed row; its only trigger gap:gap_claim_opened is in-category and already fired) | no |
| record_claim_balance_at_loss_15fb7d99 | agent | update claim row balance_at_loss_usd | none | no |
| record_premier_claim_exclusions_258c7293 | agent | update claim row excluded_amounts_usd | none | no |
| record_claim_worksheet_benefit_931d4ebc | agent | update claim row benefit_usd | none | no |
| claim_plus_deductible_reimbursement_49e3d00f | user | update claim row deductible_covered_usd | none | no |
| record_plus_claim_exclusions_41771560 | agent | update claim row excluded_amounts_usd | none | no |
No row of contract / cpi / vsc / deficiency / recovery is ever written.

## Problem trees
- task 0 (Premier 150, Tier 2 contract, collision total loss, servicemember whose SCRA cap ended
  after the loss): customer asks "what will GAP pay on my claim -- work it out and put it on the claim".
  root BEN gap_ext_claim_worksheet_benefit (6)
    <- BAL gap_ext_claim_starting_balance (4)            value_input, state form (balance above 0.00)
    <- EXC gap_ext_premier_excluded_amounts (6)          value_input, action form (excluded total may be 0.00)
         <- DED gap_ext_premier_deductible_reimbursement (6, owner=user) value_input, state form
  order: DED | BAL (commute: different fields of one row, no ids minted) -> EXC -> BEN
- task 1 (Plus 150, Tier 3 contract, theft, servicemember back from deployment):
  customer asks "what part of my balance won't GAP cover -- put it on the claim".
  root EXC_plus gap_ext_plus_excluded_amounts (6) <- DED_plus gap_ext_plus_deductible_reimbursement (4, user)

## Factors (ids never substrings of tool names)
- BAL (4): first-period days (param), installments counted after a due-date change (method),
  SCRA capped schedule adjustment (method), courtesy-extension holdback (param).
- DED Premier (6): proof-on-file deductible (method, multi-source claim+cpi), insurance-history share
  (param, multi-source, cpi), installments unpaid at loss share (param, contract), vesting by
  months from contract date (param), requirement-breach share (param, cpi band), proof channel share (param, cpi).
- DED Plus (4): proof basis, insurance-history share, unpaid-installment share, vesting (Plus values/wording).
- EXC Premier / Plus (6 each): past-due share by days late at loss (param), fee allowance by returned
  payments 12m (param), fee-assessed deferral relief (param), force-placed premium relief by billed
  periods (param), add-on refund basis (method: issued / VSC formula / day-prorated estimate),
  past-due installment amount (method: capped SCRA installment / restored / current).
- BEN (6): term cut (param), credit-tier cut (param, contract), excess method by LTV at signing
  (method), ACV floor by months since contract date (param), late-notice reduction (param),
  unpaid-installment reduction (param).

## Order of work
plan.md -> extended.yaml (base copy + 6 policies) -> task_tools.py -> check_task_tools ->
world generator /tmp/gap_waiver_cancellations_and_claims_0072/gen.py (contract/cpi/vsc ledgers priced
with their own charters) -> tasks/0.json -> per-task gates -> tasks/1.json -> gates -> final gates ->
worklog.md tail line. Delete temp scripts at the end.

## Revision 3 (rework round 2) — factor redesign against audit C1-C8
- Struck (C1, unreal behaviour penalties): every history/unpaid/in-force/requirement/channel share of the
  reimbursements, the courtesy (fee-waived) holdback and fee-waived deferral sentence, partial past-due shares,
  returned-payment fee allowances, placed-premium relief shares, late-notice and unpaid-installment benefit cuts.
- Kept (accepted kinds): first-period days, due-date-change count, SCRA two-/three-stage schedule (both schedules now
  stated to start from the amount financed — C8), covered-LTV cuts by term and tier, excess method, value floor.
- New realistic measurement conventions: days a due-date change added (BAL); recognized deductible by the insurance on
  file (proof / plan requirement / none — one method, C2 closed); add-on part = VSC refund under its own terms vs
  cancelled-before-loss vs day-prorated estimate (C3 closed); past-due installment amount in effect on the due dates;
  past-due count relief and deferral count relief (whole installments only); deferral installment amount in effect on
  the latest extension; placed-premium part net of refunds credited / pending (C5 declared on gap_agg S3);
  floor base (tracking-record valuation); covered-LTV cut by collateral band.
- BLUEPRINT-KNOWN: the deductible reimbursement has one record-driven rule in real GAP addenda; the drawn 6 (Premier) /
  4 (Plus) factors are filled with the product's published deductible-benefit schedule (credit tier, term, collateral
  band, LTV, amount financed) — the only remaining schedule-style factors, confined to the two reimbursement policies.
- Worlds: task 0 two unpaid installments at loss, frozen 2026-10-05 (below charge-off), ACV 12,700, VSC refunded within
  30 days of the loss; task 1 second extension, two unpaid at loss, VSC refunded within 30 days (finding 5).

## Adversarial probe table (rework round 2; scratch copies of the task worlds, every policy re-run in tree order)
| probe (record / edge) | rule outcome | result |
|---|---|---|
| earlier withdrawn claim given settlement figures | figures summed on the latest claim's own loss date only | unchanged |
| second claim reported the same day (tie at one activity_date) | rule (round 3): the claim recorded first on the addendum counts, which is the row LATEST keeps | unchanged |
| later rejected proof with lower deductibles | only accepted proofs count | unchanged |
| no accepted proof, tracking record present | recognized deductible = lower of claim deductible and plan borrower maximum | reimbursement rises (tier b) |
| latest accepted proof shows 0.00 for the coverage that paid | proof tier needs a deductible above 0.00 -> claim deductible | tier c |
| no tracking record | claim deductible; value-band share/cut none; floor on book value | consistent |
| service contract cancelled voluntarily before the loss | add-on part 0.00 | consistent |
| service contract still in force, no refund | day-prorated price | consistent |
| cancelled for the loss, refund not yet issued | its own formula = the refund later issued | unchanged (one treatment) |
| no service contract | add-on part 0.00 | consistent |
| latest due-date change took effect after the loss | count on the first payment day, no added days (only the latest change is read; stated in the rule) | consistent |
| SCRA cap ended before the loss / before the oldest unpaid due date / absent | three-stage schedule; blended / scheduled past-due installment; deferral installment by cap on the latest extension date | consistent |
| re-applied cap (applied, ended, applied) | latest-applied with latest-ended mis-pairs; no producible world here (one service period per world) | known DSL limit |
| next due date after the loss / one unpaid 26 days / three unpaid | none treated as past due / none counted (Premier <=30) / all counted | consistent |
| no extensions | deferral part 0.00 | consistent |
| proof accepted, refund not yet credited | latest premium's share from the proof's coverage start (= the refund later credited) | unchanged |
| held_pending_proof_review premium row | never added to the balance, not counted | unchanged |
| partial installment credit above the past-due amount | never below 0.00 | consistent |
| loss on the first payment date (date difference 0) / before it | one installment counted / none (opening principal) | consistent |
| claim deductible 0.00 | reimbursement 0.00; the excluded-total wait applies only to deductibles above 0.00 | consistent |
| month-end day of month | due_day is 1-28 by schema; MONTHS counts whole months with day decrement | n/a |
| boundaries 115 / 130 percent LTV, 12 / 24 months, 30 / 60 / 75 days | inclusive as the rule words them ("up to", "no more than", "fewer than") | checked in compute |

## Revision 4 (rework round 3) — audit revision_2: C9, C10, R2-O1, R2-O3, O6; C1/C4 blocked
- C9: the value floor is a baseline quantity of the worksheet benefit (default percent of the book value at origination);
  bn_value_floor sets the percent, bn_floor_value the vehicle value it is figured on, each against that baseline.
- C10: every LATEST read states its tie (claims, accepted proofs, due-date changes, cap-applied/ended, extensions:
  latest date, the one recorded first on a tie; premiums: latest billing-period start, never the billing date).
- R2-O1: Premier past-due relief by count only (one: none; two: one; more: all); Plus keeps its 20/60-day limits.
- R2-O3: pending-refund tier only when the proof takes effect inside the latest billing period (then exact); otherwise gross.
- O6: fee part = fees due less late charges on installments due after the date of loss (ledger, by installment due date).
- C1/C4 not closed: see rework_claims_r3.md (option (b) has no numeric borrower write in the frozen gap schema; option (a)
  tops out at five record-driven reimbursement factors for the Premier draw of six). pd/ud unchanged pending a ruling.

## Adversarial probe table, round 3 additions (scratch copies of the task worlds)
| probe (record / edge) | rule outcome | result |
|---|---|---|
| post-loss late charges (task 0 Aug/Sep, task 1 Aug/Sep installments) | subtracted from fees due | fee part drops by those charges |
| late charge on the last installment due before the loss, assessed after the loss | stays in the fee part (its installment fell due before the loss) | consistent |
| contract current at the loss (next due after the loss) / one / three unpaid | the same post-loss installments are located (months from the next due date to today less months to the loss) | consistent |
| post-loss late charge later waived | fees due already exclude it; subtraction floored at 0.00 | known over-subtraction edge, floored |
| due-date change taking effect after the loss | post-loss installments on the old due day within a month of the loss can be misplaced by the month count | known DSL limit (no producible world) |
| no refund credited, proof effective inside the latest billing period | premiums less the latest premium's share from the effective date (= the refund the CPI terms leave due) | tier 2 exact |
| no refund credited, proof effective before the latest billing period | every premium added (stated in the rule) | tier 3 |
| two premiums billed the same day (backdated placement) | latest premium = latest billing-period start; billing date read from that premium | unchanged |
| two accepted proofs reviewed the same day | the one recorded first counts (= XLATEST's kept row) | no producible tie in either world |
| two cap or extension records on one effective date | the one recorded first counts | no producible tie in either world |
| addendum 24+ months in force | floor percent = baseline default | consistent |
| no tracking record | floor on book value at the default or tiered percent | consistent |
| floor below the insurer's ACV | ACV deducted | consistent |
| Premier one / two / three unpaid installments at the loss | none / one / all counted | consistent |


## Revision 5 (rework round 4) — audit revision_3: C1 (8 schedule shares + bn floor default), C4
- Reimbursements rebuilt per the round-3 ruling (see rework_claims_r4.md): pd = policy_at_loss, paying_coverage,
  window_start, window_days (report promptness), duty_extension (company accommodation on recorded duty dates),
  closed_day; ud = policy_at_loss, window_days (kind of loss), duty_extension, closed_day. Declared scoped overwrite of
  the late_documents clause. Reimbursement edges -> action form (a late claim leaves 0.00).
- bn baseline floor: 60 percent of origination book value under 24 months in force, no floor from 24 months.

## Adversarial probe table, round 4 additions (scratch copies of the task worlds)
| probe (record / edge) | rule outcome | result |
|---|---|---|
| accepted proofs exist, none from the settling insurer | proof deductible = plan borrower maximum | consistent |
| no accepted proof at all | claim deductible, up to the plan maximum | consistent |
| newer policy filed before the loss, starting after it (latest accepted proof) | not read: the settling insurer's proof is | tier (a) |
| recorded duty with no end after its start | window stays open | consistent |
| last day Saturday / Sunday / Friday | +2 / +1 / none | consistent |
| unrecovered theft on a Premier claim | window opens when the 30-day wait runs out; comprehensive deductible | consistent |
| Premier claim reported more than 45 days after the loss | 10-day window from the report | consistent |
| claim deductible 0.00 | reimbursement 0.00 | consistent (action-form edge) |
| claim deductible above the plan maximum (task 1) | plan maximum; the rest is the uncovered-deductible part | consistent |
| two accepted proofs from one insurer reviewed the same day | the one recorded first counts | no producible tie |
| re-applied rate cap (applied, ended, applied) | latest applied after latest ended -> no recorded end -> window open | stated by the rule ("no end after that start") |
| addendum in force 24+ months | no floor (baseline and ladder) | consistent |

## Revision 6 (rework round 5) — audit revision_4: C1, C2, C4, C11, C12
- Task 1 re-treed: root Plus excluded total (owner=user, the borrower confirms the amounts that stay owed), capped at
  and waiting on the Plus starting balance (new policy + tool, the starting balance split by plan for disjoint scopes);
  Plus reimbursement and its tool retired; Plus uncovered deductible = deductible above the plan maximum (base basis).
- Task 1 world re-seeded from origination (due-date change 2025-12-10, deductible 750.00, charter-consistent duty/cap).
- Task 0: C11 customer duty end aligned with the rate-cap end; the Premier reimbursement kept as round 4 (not compliant;
  see rework_claims_r5.md for the arithmetic that blocks a real 6- or 4-factor reimbursement in a 4-problem claim tree).

## Adversarial probe table, round 5 additions
| probe (record / edge) | rule outcome | result |
|---|---|---|
| Plus claim with no starting balance recorded | excluded total capped at 0.00 (edge unmet) | skip effect 0.00 |
| starting balance below the itemized total | excluded total = the starting balance | cap binds (probe 1,000.00) |
| Plus deductible at or under the plan maximum | uncovered-deductible part 0.00 | consistent |
| due-date change moving the next due date across a month end | installments counted drop by the skipped due date | factor bears weight (15 vs 16) |
| rate cap ended after the loss | two-stage schedule; capped past-due and deferral installments | consistent |
| duty end vs rate-cap end | cap ends the day after the recorded duty end (contract charter) | both worlds aligned |

## Revision 7 (rework round 6) — audit revision_5 (C11, C13) and the structural ruling
- Task 1: root = Plus worksheet benefit (owner=user, acceptance) <- Plus starting balance (value edge: the benefit's first
  term). Plus excluded total itemized in place; Plus exclusions policy and tool retired. World re-seeded from 2023-11-24
  with contract rows priced by the contract product's published documents (due-date shift 18 <= 20; extensions after
  the seasoning and spacing allowances; Georgia late-charge rate and first-delinquency reductions; Georgia extension
  charge; SCRA cap from the duty start, ends the day after the duty end); DriveSure Gold service contract.
- Task 0: unchanged; the world-type change is blocked by the schema (one money write per addendum outside the claim row)
  and by gap_agg_contract_portfolio (no cross-contract combination); see rework_claims_r6.md.

## Adversarial probe table, round 6 additions
| probe (record / edge) | rule outcome | result |
|---|---|---|
| Plus starting balance not recorded | benefit 0.00 (balance term 0) | skip effect 0.00 |
| starting balance higher / lower by 1,000.00 | benefit moves by the same amount (above 0.00) | value edge |
| net settlement above the balance less exclusions | benefit 0.00 | floor at 0.00 |
| contract LTV within the plan's 150 percent | loan-to-value excess 0.00 | base measure |
| due-date change of more than Tier 3's 20 days | not seeded (charter would refuse) | world within limits |
| extension before 12 installments paid / within 12 months of the last | not seeded (seasoning / spacing allowance zero) | world within limits |
| late charge with no late charge in the prior 12 months | 50 percent first-delinquency reduction | priced so in the world |
| service contract refund below the minimum | not issued | Gold refund issued, above the minimum |

## Revision 8 (rework round 7) — coordinator's final ruling on task 0
- Task 0 placement: reimbursement 4, starting balance 6, excluded total 6, worksheet benefit 6. Reimbursement =
  proof of the policy that paid (param), coverage that paid (param), contract allowance by the current CPI plan (param),
  allowance test (method: cap / void / none). Starting balance + placed premiums (param) + account interest (method).
  Value floor on a 36-month line. Task 0 re-seeded from 2024-02-05 with contract rows per the published documents.
  Task 1 untouched.

## Adversarial probe table, round 7 additions (task 0)
| probe (record / edge) | rule outcome | result |
|---|---|---|
| no proof names the settling insurer, withheld above the allowance | void | 0.00 |
| withheld within the allowance | allowance does not enter | lesser of withheld and proof deductible |
| settling insurer's proof accepted (deductible within the plan) | that proof's deductible; cap tier ties | consistent |
| no tracking record | no allowance; no allowance test | lesser of withheld, proof, plan maximum |
| latest payment covered its interest | accrued interest only | starting balance lower by the carried interest |
| latest payment after the loss | no account interest | consistent |
| no force-placed premium | none added | consistent |
| addendum in force 36+ months | no floor (ladder and baseline) | consistent |
| first extension before 12 installments paid / second within 12 months | not seeded (allowances zero) | world within the docs |

## Revision 9 (rework round 8) — audit revision_7: C1, C3, C4, C14, C15 (task 0 only)
- Reimbursement (4): pd_policy_at_loss (param), pd_paying_coverage (param), pd_deductible_counted (param; the deductible
  the insurer withheld as the settlement shows it, 0.00 when the settlement shows none withheld, the latest accepted
  proof's lower deductible before settlement figures), pd_allowance_test (method; reads the tracking record's borrower
  maximum itself: cap / void / none). pd_contract_allowance removed; the proof-naming count is a plain shared binding
  with its own rule sentence, owned by no factor.
- Starting balance: bl_placed_premiums is now a method with three formulas (net of refunds credited / net of the latest
  premium's prorated share from an accepted proof's effective date / gross); baseline adds the premiums gross.
  bl_account_interest replaced by bl_payment_interest (method): per-diem from the latest payment to the loss at the rate
  in force / split at a rate-cap change between them / none. The carried unpaid interest tier is gone. Interest accrues
  on the principal in place over the period: principal balance plus the service-contract refund credited for the total
  loss after the loss.
- Excluded total, worksheet benefit, task 1: unchanged. World unchanged (no re-seed).

## Adversarial probe table, round 8 additions (task 0)
| probe (record / edge) | rule outcome | result |
|---|---|---|
| settling insurer's proof accepted | that proof; withheld above the borrower maximum -> cap | consistent |
| no proof names the settling insurer, withheld above the borrower maximum | void | 0.00 |
| settlement figures absent (ACV 0.00) | deductible counted = latest accepted proof's lower | lower than gold |
| settlement shows no deductible withheld | deductible counted 0.00 | 0.00 |
| withheld within the borrower maximum | allowance does not enter | withheld figure |
| no tracking record | no borrower maximum; no test | lesser of counted, proof and plan maximum |
| comprehensive loss | comprehensive deductible | lower |
| no premium refund, accepted proof inside the latest premium's billing period | prorated pending share netted | equals the refund the CPI terms leave due |
| no premium refund, no qualifying proof | gross premiums | baseline value |
| cap ended between the latest payment and the loss | split rate | higher interest |
| cap applied between the latest payment and the loss | split rate | consistent |
| latest payment after the loss | none | baseline value |
| service contract not cancelled for the total loss | principal as recorded | lower interest |

## Revision 10 (rework round 9) — audit revision_8: C1, C4 on the reimbursement (task 0 only)
- Deductible counted = the deductible the primary insurer actually deducted (the claim's deductible withheld), up to
  the plan maximum; a deductible not withheld is never reimbursed. pd_deductible_counted and its proof fall-through
  are removed.
- Declarations check (only ever lowers the withheld figure): standard = the latest accepted proof of the policy on
  file on the tracking record, lower of its two deductibles.
- Four factors: pd_policy_at_loss (param: settling insurer / any insurer when no policy on file / insurer of the
  policy on file), pd_proof_standing (param, new: the settling insurer's latest proof rejected for a deductible above
  the allowance -> its declarations count whatever the result / rejected otherwise -> none read / accepted only, else
  the policy on file's), pd_paying_coverage (param), pd_allowance_test (method, unchanged). No re-seed.
- Why the declarations check stays in the standard: every honest deductible term is a ceiling on one figure, so with
  a bare "withheld up to the plan maximum" standard only the single tightest ceiling can move the result; the
  factors bear weight because their standards (policy on file, accepted only, lower deductible) differ from what
  the records show for the policy that paid.

## Adversarial probe table, round 9 additions (task 0)
| probe (record / edge) | rule outcome | result |
|---|---|---|
| settling insurer's proof accepted | accepted standing; withheld above the borrower maximum -> cap | consistent |
| settling insurer's proof rejected for another reason | no declarations read | withheld up to plan max, then cap |
| no proof names the settling insurer | policy on file's declarations; void (never put before the company) | 0.00 |
| no proof names it and no policy on file | any insurer's latest proof; void | 0.00 |
| withheld within the borrower maximum | allowance does not enter | withheld figure |
| nothing withheld | nothing reimbursed | 0.00 |
| no tracking record | no declarations, no allowance | withheld up to plan maximum |
| comprehensive loss | comprehensive deductible declared | lower |

## Revision 11 (rework round 10) — render-source scan render_r1.md: S1, S2, S3, docstring note
- S1: the Premier and Plus worksheet benefits each declare the base LTV-excess clause overwritten, each tail naming the
  other plan's own excess and leaving the 120-150 plans on the base proportion.
- S2: payment interest when a cap starts, ends, or both inside the period from the latest payment to the loss: each
  day at the rate in force on it (cap days = overlap of [cap start, cap end) with [payment, loss)).
- S3 / month-end: one whole-months definition sentence in every policy that counts months (bl, ep, bn, bp, pb); the
  post-loss late-charge window stated exactly as computed (ep, pb).
- task_tools.py docstrings: "rounded to the cent" (the body's round()); names, signatures and parameters unchanged.
- No figure changed; tasks/0.json and tasks/1.json unchanged.

| probe (record / edge) | rule outcome | result |
|---|---|---|
| cap applied and ended between the latest payment and the loss | cap rate on the days in between, APR on the rest | consistent |
| cap applied in the period, ending after the loss | split at the start | equals the round-8 split |
| cap ended in the period | split at the end | equals the round-8 split |

## Revision 12 (rework round 11) — KB audit kb_round1 source items S1, S2 and observation P1
- S1: no change to rows. gap_claim_withdrawn is a status transition of gap_addenda (claim_open -> active) that writes
  no activity row; the March claim's withdrawal returned the addendum to active and the 2026-08-19 claim opened the
  present claim_open. The seed-consistency check now says so.
- S2 (task 0 re-seed, CPI only): the policy on file (Buckeye, expired 2026-09-18) lapsed with no acceptable
  replacement -> tracking record lapse_notice, lapse_date 2026-09-18; first lapse notice 2026-09-21 (5-day period).
  Second notice not due before 2026-10-06, placement not before 2026-10-21 (after the frozen date). No figure reads
  the status or the notice; values and traces unchanged.
- P1: pd_proof_standing now decides only which review results count (any / none / accepted only); the plain sentence
  combining insurer and standing (with the policy-on-file fallback) is stated once outside the factors;
  pd_policy_at_loss and pd_allowance_test each own their count of proofs naming the settling insurer.
- Bounded pass over every cross-category seeded row of both worlds against docs/contract, docs/cpi, docs/vsc (no
  recovery or deficiency rows are seeded): only S2 needed a change.

## Revision 13 (rework round 12) — KB revision_2: K1 / S3 on the Premier deductible reimbursement
- Route (b): the insurer choice and the review-standing choice are one factor, pd_policy_at_loss, whose tiers are
  complete selections: the settling insurer's latest proof when accepted or rejected only for its deductible / no
  declarations when rejected otherwise / the policy on file's latest accepted proof (standard). The round-11
  combination sentence and pd_proof_standing are gone; no rule sentence combines factor outputs.
- Freed slot: pd_policy_disclosure (method, record-backed on when the latest proof naming the settling insurer was
  reviewed): reviewed on or before the date of loss -> not barred / only after -> never more than the borrower maximum /
  no such proof -> nothing reimbursed. It acts against the standard bar (new baseline sentence): a withheld deductible
  above the plan's borrower maximum is not reimbursed. Own reads only.
- pd_allowance_test (method, own reads): rejected for its deductible -> never more than the borrower maximum; accepted ->
  never more than the higher of that proof's deductibles; otherwise no bound. Its void tier moved to the disclosure
  method (no duplicate).
- Deductible counted stays the deductible the insurer actually withheld, up to the plan maximum; never a deductible not
  withheld. Gold unchanged; ep/bn unchanged.

| probe (record / edge) | outcome | result |
|---|---|---|
| settling insurer's proof accepted | its declarations; bound at the accepted deductibles | consistent |
| settling insurer's proof rejected for another reason | no declarations | withheld up to plan max, then bounds |
| settling insurer's proof reviewed after the loss | not void; never more than the borrower maximum | consistent |
| no proof names the settling insurer, withheld above the borrower maximum | nothing reimbursed | 0.00 |
| withheld within the borrower maximum | no bound, no bar | withheld figure |
| nothing withheld | nothing reimbursed | 0.00 |
| no tracking record | no declarations, no bound, no bar | withheld up to plan maximum |
| comprehensive loss | comprehensive deductible declared | lower |

## Revision 14 (rework round 13) — audit revision_12: C14, C4 on the Premier deductible reimbursement
- Baseline softened: the deductible the insurer actually withheld, up to the plan maximum, bounded by the one declared
  deductible of the declarations read (standard: the latest accepted proof, lower of its two deductibles). The
  round-12 bar ("above the borrower maximum is not reimbursed") is gone.
- Selectors: pd_policy_at_loss (merged declarations selection) and pd_paying_coverage. Methods, own reads:
  pd_allowance_test (withheld vs borrower maximum, by whether a proof names the settling insurer: cap / void / none)
  and pd_policy_disclosure (review date of the latest proof naming the settling insurer vs the date of loss: no bound /
  never more than the borrower maximum / never more than the policy on file's lower deductible). The borrower maximum
  is a plain binding stated once.
- Task 0 gold unchanged; every factor moves the result alone. Pair probes (one factor at baseline, another toggled):
  every ordered pair has a world where the toggled factor matters; no factor is inert through a single other factor's
  tier. With all three others at baseline, pd_policy_disclosure's standard (policy on file) coincides with the
  declarations standard (latest accepted proof) on every open tracking record, and pd_paying_coverage is masked by it
  there; both bear weight as soon as any one other factor leaves its baseline.

| probe | outcome | result |
|---|---|---|
| settling insurer's proof accepted | its declarations; cap at the borrower maximum | consistent |
| settling insurer's proof rejected for another reason | no declarations | allowance cap only |
| settling insurer's proof reviewed after the loss | never more than the borrower maximum | consistent |
| no proof names the settling insurer, withheld above the borrower maximum | void | 0.00 |
| withheld within the borrower maximum | no allowance bound | withheld figure |
| nothing withheld | — | 0.00 |
| no tracking record | no declarations, no bounds | withheld up to plan maximum |

## Revision 15 (rework round 14) — audit revision_13: C14, C4 on the Premier deductible reimbursement
- pd_policy_disclosure removed. New pd_loss_schedule (parameter, record-backed on the claim's own loss type): the
  Harborline GAP Waiver Premier 150 deductible reimbursement schedule caps the baseline directly: collision total loss
  -> the plan's deductible_reimbursement_max_usd; unrecovered theft -> 500.00 (theft_reimbursement_max_usd);
  comprehensive total loss or no loss type -> 250.00 (comprehensive_reimbursement_max_usd) = the standard.
- Baseline: the deductible actually withheld, up to the reimbursement maximum (standard 250.00), never more than the
  declared deductible of the declarations read (standard: latest accepted proof, lower of its two deductibles).
- No re-seed; task 0 gold unchanged.

### T1 / T2 acceptance table (reimbursement factors)
T1 = task 0 world, the factor's baseline alone (others at their task tiers); T2 = the stated producible world variant
of task 0, the other three factors at baseline, the factor at its taken tier vs its baseline.

| factor | T1 (task 0) | T2 probe world | T2 taken vs baseline |
|---|---|---|---|
| pd_policy_at_loss | moves (gold vs its baseline) | the Keystone Prairie proof shows comprehensive 100.00 (collision 1,000.00, still rejected for its deductible) | moves |
| pd_paying_coverage | moves | the latest accepted Buckeye proof shows collision 200.00 / comprehensive 100.00 (within Plan B's 500.00) | moves |
| pd_allowance_test | moves | no proof names Keystone Prairie (the policy was never put before the company) | moves (void) |
| pd_loss_schedule | moves | the latest accepted Buckeye proof shows 500.00 / 500.00 (exactly Plan B's 500.00, accepted) | moves |
