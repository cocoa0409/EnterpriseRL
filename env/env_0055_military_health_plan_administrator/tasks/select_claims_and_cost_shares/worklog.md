# select_claims_and_cost_shares — difficulty worklog (erl-task-instantiate; rounds 1 and 2)

The "Task 0 — closed", "Task 1 — closed" and weaker-points sections record round 1 as built; their figures and factor
lists are superseded by the "Round 2" section at the end (current figures and factor sets).

## Draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems 2, factor_counts [5, 4, 6]
- task 1: prerequisite_problems 3, factor_counts [6, 5, 5, 5]

## Task 0 — closed
Root `select_ext_inpatient_stay_correction` (post_select_inpatient_stay_a4ca4c06, agent, 6 factors) for a Retiree
Group A beneficiary's psychiatric stay, reversed after a Medical Necessity Reconsideration was decided partially
overturned (authorization approved on appeal for 10 of 14 days). Prerequisites, both value_input and state form:
- `select_ext_professional_line_correction` (post_select_professional_line_96ff63a5, agent, 5 factors): the reversed
  psychiatrist line of the same admission date must carry its corrected adjudication (liability enters the
  catastrophic total).
- `select_ext_card_installment_payment` (pay_select_installment_by_card_fa3a0d38, **user**, 4 factors): the
  plan year's quarterly installments must show no past-due balance (fees count toward the cap).
Gold: 215.00 / 34.00 / 4532.00. Every factor moves the result (verify run recorded in tasks/0.json
design_rationale and computations[].factor_sensitivity). Cross-difficulty: referral (Inpatient Mental Health
Authorization) in two factors, both multi-source. Method factors: outpatient_cost_share_basis,
card_application_order, stay_countable_fees (multipliers and divisors were relabelled parameter after the
coordinator's note).

Revisions: R1 factor relabelling; R2 frozen_time 2026-10-28 (inside the 10-day effectuation window), noise rows
dropped, reads widened (provider directory, reconsideration) so the closure equals the seed; R3 the customers finder
may run only once, so no second family member can ever be read — the spouse was removed (individual fee) and the
third-quarter excess (which the refund rule would already have returned) became a 4.50 shortfall cured in grace.

Per-task gates (task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
SCOPE OK; CACHE-DIFF INFO (no trap intended). TRACEABILITY not run (KB not yet rendered).

## Coordinator decision (round 1, continued)
The blueprint stays frozen and M=2 is fixed; stopping or M=1 is not an outcome. Route around the thin base inside the
write domain: other claimed event types or reversal reasons, declared overwrites, a customer-owned write distinct in
channel or object, cross-difficulty reads of other categories, and only factors a real program would use (a `method`
factor must change the formula's shape). The earlier blocker analysis is superseded by the task 1 design below.

## Task 1 — closed
Root `select_ext_cap_line_reprocessing` (post_select_cap_reprocessed_line_5ecdf694, agent, 5 factors): a Group B
retiree's cardiology line reversed for catastrophic-cap reprocessing. Prerequisites (all value_input, state form):
- `select_ext_ohi_stay_reprocessing` (post_select_ohi_reprocessed_stay_ac99ca71, agent, 6 factors): the stay reversed
  for other health insurance must carry its reprocessed adjudication (its liability fills the cap); it in turn waits on
- `select_ext_ohi_line_reprocessing` (post_select_ohi_reprocessed_line_2895a639, agent, 5 factors): the outpatient
  line reversed for other health insurance, and on
- `select_ext_bank_draft_payment` (authorize_select_bank_draft_0bb89bb0, **user**, 5 factors): a one-time bank draft
  clearing the past-due monthly installments (monthly installments cannot be paid by single card, so the channel and
  the object differ from task 0's card payment).
Gold: 174.75 / 27.60 / 3721.64 / 80.00. Cross-difficulty: TRICARE Prime enrollment, claim lines and fees (plan-change
carryover into the catastrophic total, point-of-service exclusion, fee placement by coverage start). Declared
overwrites: the authorization gate (a reprocessed line keeps its original authorization finding) and the Prime
exclusion sentences of the family accumulator and catastrophic-cap policies for a Prime-to-Select plan change within the
plan year.

Changes to task 0 made for task 1: its correction policies now pick only appeal_overturned reversals; the plan-year
window formula of all claim policies counts from January 1 of the service date's year to the adjudication date. Task 0
figures unchanged.

Weaker points flagged for audit: the Group A/Group B schedule factors (draft fee schedule, other-insurance deductible
amount) read tier parameters with the Group A schedule restated as policy params; the Prime carryover overwrites a base
exclusion sentence on the strength of TRICARE's calendar-year cap applying across plan changes.

## Round 2 — policy-audit rework (audits/policy_task/select_claims_and_cost_shares: _difficulty.md, 0.md, 1.md)
Blueprint base untouched (select.extended.yaml lines before `extended_policies` are the base copy, regenerated
verbatim). Real-program grounding checked on tricare.mil: enrollment fees stop once the family catastrophic cap is met
for the calendar year (tricare.mil/catcap), and amounts credited toward one plan's cap carry to the new plan when the
family changes plans under the same sponsor during the year (TRICARE catastrophic-cap Q&A); both are written as
declared overwrites. New figures: task 0 215.00 / 29.50 / 5732.00; task 1 243.50 / 27.60 / 4727.89 / 437.50.

Item by item:
- P1 (cap dropped): professional line and OHI line now cut their liability to the room under catastrophic_cap_family,
  with the same family total (claims net of reversals, fees paid oldest first, Prime carryover) the stays use.
- P2/P3 (preventive, DME): every outpatient cost-share ladder has a network-DME tier (network_dme_cost_share_pct) and
  gives network preventive care its network copayment; the deductible ladders exempt network preventive care.
- P4/P7 (family deductible/total): every claim policy is scoped to an enrollee who is the only Select member of the
  sponsor family (the family remainder can then never be the smaller); both worlds are single-member families.
- P5 (window): frozen_time moved to month ends (2026-10-31) so the DSL's month-count window equals the calendar plan
  year on both worlds; T0's appeal/authorization dates moved to 2026-10-23/24 to stay inside effectuation. Residual:
  the DSL offers no date filter other than month counts, so the rule/compute equivalence holds at month-end
  adjudication dates only.
- P6 (draft fee level): the payment conjunct is gone; the fee level is family / individual per base, plus the cap
  fee waiver (declared overwrite of the fee-schedule sentence, also on the card policy).
- F1: padded conjuncts removed (card and draft fee level, draft schedule factor, OHI-line deductible amount).
- F2: card tiers are first-installment proration / quarterly / annual; the draft now serves allotment, EFT and
  recurring-card payers of any frequency (card: check and single-card payers), so its monthly / quarterly / annual /
  proration tiers are all in scope.
- F3: received ladders are clamps on the payments left after earlier charges (oldest first); deductible taken is a
  clamp (exempt or network preventive / remainder / whole amount); other insurance on stays is a clamp; fees counted
  is a clamp with a fees-do-not-count tier; Prime carryover is cap clamp / plan change / nothing; point-of-service
  exclusion, fee placement and application-order ladders were folded into plain bindings. Residual (kept to meet the
  drawn counts, each moves its result): deductible_met (2 policies) and claims_counted (2 policies) are one netting
  formula written as tiers; stay_payable_allowed's no-covered-day tier equals the per-day formula at zero;
  card_due_charges / draft_due_charges are a filter written as tiers; draft_frequency_in_force's first two tiers
  share a formula. The fee charter offers three independent real variations of an installment payment (amount shape,
  fee level with the cap waiver, oldest-first receipt), so card and draft keep 3 sound factors against the bound of 4;
  every claim computation now keeps at least 4 sound factors with a method.
- F4: application-order factors removed; methods are the cost-share basis, installment owed, per-day pricing,
  inpatient basis (per-admission copayment on T1's network stay) and the fee-counting rule (oldest-first placement).
- F5: fee placement factors removed; every fall-through equals its declared baseline.
- F6: Group A constants and the dishonest 150.00 deductible baseline removed.
- F7: carryover tiers are ordered and disjoint (cap clamp, plan change, nothing).
- F8: card and draft baselines are one definite sentence each (whole annual family fee plus any shortfall on the
  earlier charges); verified 425.50 and 1217.76.
- O1: no installment sits past its grace period on either world. O2: payment rows follow oldest-first application.
  O3: payment tools still leave fee_balance_due to the ledger (observation; the balance is no longer the answer).
  O5: billed days read from the stay's reversal. O6: the carryover sentence restates the point-of-service,
  premium-based and balance-billing exclusions. O4, O7, O8, O9 unchanged observations.
- T0-1: the professional-line rule fixes the authorization reference (empty unless the class needs one and the
  authorization covers the line's own provider); gold prior_authorization_id is ""; the seeded original line is
  denied_not_a_covered_benefit; the tool docstring matches.
- T0-2 / T1-1 (stamps): charges are billed ahead (T0 the 2027 first quarter on 2026-10-15, T1 November on 2026-10-15);
  the balances are 79.00 and 77.19 while the past-due payments are 29.50 and 27.60; payment rows carry no coverage
  period (schema) and the payment tools now leave it empty.
- T0-3 / T1-4: see F1-F8; T0-4 / T1-5: see P1-P7.
- T1-2: OHI-line deductible is the tier's own deductible_individual inside a clamp; no Group A baseline.
- T1-3: task 1's OHI line and root are now the psychiatrist's and psychologist's lines of an inpatient mental health
  admission (Red Rock Canyon, authorization approved for 7 of 8 requested days, exhausted), each with an attending
  share read from the referral record (sound, multi-source); the Prime carryover was rebuilt (F7); the OHI stay moved
  to a network facility (per-admission copayment).
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK; TRACEABILITY deferred (KB not rendered).

## Round 3 — policy re-audit revision_2 (N1-N8, P5, F3 remainder)
Figures unchanged: task 0 215.00 / 29.50 / 5732.00; task 1 243.50 / 27.60 / 4727.89 / 437.50.
- N1 closed: both attending-share computes (OHI line, cap line) test the inpatient mental health stay on the line's date
  in the first rung, as the rule states.
- N2 closed: card and draft fee-level ladders read cap reached -> 0; exactly one member enrolled -> individual fee;
  otherwise -> family fee. The baseline (family fee) is now the fall-through; both customers sit on the individual rung.
- N3: the fee-count clamp is labelled parameter on the corrected stay and the OHI stay. Task 0's stay gets a real method
  instead: its inpatient basis (lesser-of / per diem with minimum / percent of allowed / admission copayment, falling
  through to the copayment, 0.00 on Group A), which moves the result because the cut room 1468.00 sits above that
  fall-through. Residual: the cap line keeps the fee-count factor labelled method, because no method can act on it.
  On any world where its prerequisite stay is load-bearing, that stay fills the cap, so the cap line is "reached".
  Every method acting on the liability figured before the cap (cost-share basis, deductible) is then inert. Its
  movers are the other-insurance clamp, the attending share, Select fees, Prime carryover and the stage, all of which
  are amounts.
- F3 closed for stay_payable_allowed: per-day pricing of mental health stays is now a plain rule sentence.
- F3 residual, forced by the draws: deductible_met (professional, OHI line), claims_counted (stay, OHI stay),
  card/draft_due_charges, and N4 draft_frequency_in_force all remain. Each moves its result but is one formula written
  as rungs.
  - Why they remain: the drawn counts are task 0 {4,5,6} and task 1 {6,5,5,5}. Under the frozen base and the DSL, an
    outpatient line has four independent real levers: other insurance, attending share, deductible clamp and the
    cost-share method. An installment payment has three: fee level with the cap waiver, the installment-owed shape and
    oldest-first receipt.
  - So the professional line, OHI line, card and draft need one or two slots beyond what real Select practice
    supplies. Each stay needs one more beyond other insurance, covered days or basis, fees, Prime and stage.
  - Every other lever was checked (cap stage on a non-binding line, network status, which the DSL cannot read from
    the provider record, timely filing, family deductible, which the single-member scope excludes, payment-method
    placement). Each either does not move the result or has duplicate rungs.
- P5 residual (DSL): `within_months` counts months back from NOW, subtracting one when NOW's day is earlier than the
  row's. A prior-December row whose day exceeds NOW's day therefore counts as January of the current year, and the
  DSL has no other date filter to separate it. Exact on both worlds (NOW is the 31st).
- Observations: N5 (resolver follows the elected payment method; both worlds match the declared edges), N6 (fee-waiver
  totals are Select-only; a Prime-inclusive total would not be load-bearing on either world, so the compute gate
  rejects it), N7, N8 and O2/O3/O4/O7/O8/O9 unchanged.
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK; TRACEABILITY deferred.

## Round 3 (continued) — coordinator decision: restructure problems, fix P5 for any frozen date
Analysis done before touching the artifacts. Tree changes that might help:
- A stay in place of the professional line.
- A tier/arrangement fee recalculation (select_fee_charge).
- A fee credit or refund.
- An OHI update.
- Moving the payment between tasks.
- State_gate edges.
- Problems in a different plan year.
- Cross-category reads of prime, premium, appeal, referral and dme.
- Prime unused-fee credit.
- The cap fee waiver (verified real: fees stop once the cap is met).
Findings (each was checked against the DSL in check_compute.py and against the draws in draw_counts.py):
1. The DSL filters event rows only by equality and by `within_months`. `within_months` counts months back from NOW
   and subtracts one when NOW's day is earlier than the row's. Rows dated 1 Jan of NOW's year and rows dated in the
   prior December after NOW's day of month both sit at month-distance m-1. No other primitive can tell them apart:
   - there are no date comparisons, no string building, no subscripts;
   - the eq filter compares str() values;
   - LATEST/MAX take no window.
   So no compute can bound a sum at 1 January exactly for an arbitrary frozen date. Only a scope that keeps every row
   inside the adjudication year would make the window unnecessary (enrollment begun this plan year). The Prime
   carryover still windows Prime claim lines by service date, so that scope would not close P5 either.
2. Draws: task 1 needs four computations of at least 5 sound factors each (with one method).
   - A claim computation's room-side levers (fees, claims, Prime, cap stage) bear weight only when its cap room binds.
   - Once one computation crosses the cap it fills it, so every later claim computation is "reached".
   - A reached computation keeps only amount levers (other insurance, covered days or attending share, fees, Prime,
     stage): no method can move it.
   - A computation adjudicated before the crossing one has a room that does not bind. Its levers then reduce to:
     - outpatient line: other insurance, attending share, deductible clamp, cost-share method (4);
     - stay: covered days, other insurance, inpatient basis (3).
   - A fee payment has fee level (with the cap waiver), period share, installment shape (method) and oldest-first
     receipt (4).
   - Fee charge recalculation and fee credit computations have 3-4 levers. Their inputs (the date a family member
     joined, another enrollment's ledger) sit in other customers' or other holdings' rows that the holding-scoped DSL
     cannot read.
   - So task 1's {6,5,5,5} and task 0's {4,5,6} cannot all be met with real, structurally sound factors. Task 1's
     user-owned payment is capped at 4, and the second claim problem of either tree is capped at 4.
   - Applying unused Prime fees toward Select installments would add a payment lever, but TRICARE states enrollment
     fees are non-refundable in most cases, so it was not adopted as practice.
Decision: the artifacts stay at the round-3 state (all gates green). The proof and the options are reported to the
coordinator rather than inventing factors that real Select practice does not use.

## Round 3 (continued, coordinator decision applied) — problems redesigned, scope device for P5
Supersedes the "Decision" line of the previous section. New figures:
- task 0: professional line 840.00 (TRICARE; liability 200.00), card 11.50, stay 5817.53;
- task 1: OHI line 841.50 (TRICARE; liability 243.50), draft 128.77, OHI stay 4489.57, cap line 542.50.
Problem-tree card (which problem took which count): task 0 stay 6, professional line 5, card 4; task 1 OHI stay 6, cap
line 5, OHI line 5, bank draft 5.
- P5 (scope device, accepted by the coordinator): every claim and fee policy covers only an enrollment that took effect
  in the plan year of the adjudication date. This is stated in the rule and enforced in the compute (scope binding; the
  result is None outside the scope).
  - Select reads sum the enrollment's whole record, and begun charges are found with the exact start <= NOW test, so
    the Select windows are exact for any frozen date within the scope.
  - Task 0 now has Terrence move from Prime to Select on his 2026-03-20 divorce.
  - Residual: Prime claim lines are still windowed by month count (flagged in both rationales).
- New real levers:
  - TRICARE second-payer coordination, a method on every claim computation: the lesser of the primary payment and
    the charge a nonparticipating provider may bill (capped at nonparticipating_balance_billing_limit_pct) less the
    other insurer's payment, with a declared overwrite of the base OHI sentence. Task 0's psychiatrist and task 1's
    psychiatrist and psychologist are nonparticipating, which makes it live.
  - Inpatient basis, a method on the stays, falling through to the admission copayment.
  - Installment owed prorated to the month of the last day of coverage (task 0: Terrence left Select on 2026-10-20).
  - Installment period (12/3/1 months).
  - Charges counted by enrollment standing (ended / active / awaiting activation), a method.
  - Covered days of the task 1 stay, now the Red Rock Canyon mental health stay reprocessed for other insurance.
- Removed:
  - deductible_met and claims_counted (now plain);
  - due_charges (replaced by charges counted by standing);
  - stay_payable_allowed (plain per-day pricing);
  - the OHI clamp on reached or crossing stays (plain).
- Remaining weak factor, flagged in rationale_t1: draft_frequency_in_force. Its first two rungs name the same charged
  frequency. A bank draft has four other independent real levers and task 1 draws at least 5 for every problem.
- Other flagged notes:
  - the Prime-line window;
  - the counted-charges ended/active distinction;
  - the primary payment figured with the adjudicated liability;
  - the task 1 stay's first adjudication paid 8 billed days before the 7-day authorization was applied;
  - the attending share applied to a single session.
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK; TRACEABILITY deferred.

## Round 4 (re-audit revision_3)
Three items closed; every gold figure is unchanged (840.00 / 11.50 / 5817.53; 841.50 / 128.77 / 4489.57 / 542.50).
1. P5, Prime side. The DSL window `within_months = MONTHS(anchor, NOW) % 12 + 1` covers record dates from the day after the
   December date that bears the adjudication date's day of month through the adjudication date. A brute-force check over every
   adjudication date of 2025-2027 found no mismatch. The carryover rule (all four stay/line policies) now states that span
   word for word for the Prime claim lines, the Prime reversals and the Prime installments, with Prime payments applied oldest
   first. Prime fee coverage starts fall on the first of a month, so the span holds exactly the plan year's Prime installments.
   The rule departs from the calendar plan year only by those December days, and no seeded Prime record falls there. This is
   flagged in rationale 8.
   Same class, Select side: the first installment starts on the effective date, not the first of a month, so the DSL day rule
   could shift that one row by a month. A new helper, fee_win, takes it out of each Select fee window and puts it back by
   exact calendar-month arithmetic; a randomized check of 4000 ledgers found no mismatch. It is applied to the card's latest
   installment and after-end charges, and to the draft's charged frequency, latest installment and after-end charges.
2. draft_frequency_in_force removed. The frequency in force is now a plain rule: the frequency installments are charged at
   for the payment date's calendar period, otherwise the elected one. It feeds draft_installment_period (12 / 3 / 1 months,
   fall-through 1). The fifth draft factor is draft_latest_installment, a method with three distinct treatments:
   - an ended enrollment takes the period that contains the last day of coverage;
   - otherwise, where a charge exists for the payment date's period, that period's charges;
   - otherwise the first installment (the fall-through and baseline).
   On the task 1 world it takes the fourth-quarter 148.77; the baseline gives 178.36. The draft keeps 5 factors (3P/2M), and
   every factor still moves.
   The card and draft wording now states its tests exactly as computed: the latest installment, "only one installment begun"
   for first-installment proration, and "ended before the last month of the installment period containing the last day of
   coverage" for exit proration.
3. Seed fix: task 0 Prime point-of-service MRI d86c7fa8-66f0-44d2-b065-0024e6acf7f9 now carries cost_share_amount 450.00
   (300.00 POS deductible + 50% x 300.00), as the Prime charter's formula gives. It is still left out of the carryover, so
   gold does not move. The task 0 evidence, the stay trace and rationale 4 were updated to match.
Sweep: the card/draft related_fee_entry_id bases, the discriminator business meaning, the factor traces and sensitivities,
rationale 5/8/9 (both tasks). No "latest installment whose coverage period has begun", no "ended inside", no "MRI (300.00)"
and no frequency-ladder reference is left outside the revision logs.
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK.

## Round 5 (re-audit revision_4)
Two charter-level items closed. The problem trees, the factor sets and every gold figure are unchanged: 840.00 / 11.50 /
5817.53 and 841.50 / 128.77 / 4489.57 / 542.50. All 36 factor sensitivities and the 7 all-baseline figures match round 4.
1. P5-Prime, by the scope route. The round-4 carryover span is withdrawn.
   - Scope: the five claim policies (professional line, stay, OHI line, OHI stay, cap line) now also require that the
     enrollee hold no TRICARE Prime enrollment, or exactly one that took effect in the plan year of the adjudication date.
     Compute (SCOPE_CLAIM) checks this from XCOUNT of prime_enrollments and CFIELD enrollment_effective_date; the rule states
     it in the scope sentence.
   - Carryover: within the scope every Prime claim line and installment is dated in that calendar plan year, so the
     carryover reads the whole Prime record with no date window. It takes the non-POS cost shares less reversals, plus the
     Prime fees paid toward begun installments (MN(begun, paid), oldest first). This agrees with the base sentence
     "Amounts accumulate to the calendar plan year of the service date"; no overwrite is added.
   - Declarations: the cross-category reads now declare enrollment_effective_date. The Prime window bindings
     (win_*, pr_chg_py_*) were removed from the compute, the compute_basis and the factor bindings.
   - Worlds: both Prime enrollments are now open-season elections effective 2026-01-01 (applications 2025-11-18 and
     2025-11-24, inside the 2025 open season). The first installment is charged with the application, and the December 2025
     Prime installment and its payment are dropped. The carried amounts are unchanged: 371.53 and 882.12.
2. C1. The card's latest installment now follows the bank draft's rule. For an ended enrollment it is the charges of the
   installment period that contains the last day of coverage, no later than that month and the payment date; otherwise it
   is the charges for the payment date's period. Rule and compute (latest_amt) say the same. On the audit's situation (ended
   2026-08-15) both give 0.00, with Q3 49.50 as the latest installment.
Sweep: the Prime enrollment and Prime fee evidence in both tasks; rationale 8 (both tasks) rewritten; revision logs
extended. No "carryover span" or "December 2025" is left outside the revision logs.
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK.

## Round 6 (renderer source report on docs/select)
All four items were checked against select.extended.yaml and all four were real; none is rejected. Every gold figure,
factor sensitivity and all-baseline figure is unchanged. select.extended.yaml bytes changed; task_tools.py bytes did not.
docs/select was rendered from the round-5 yaml and needs re-rendering.
1. Earlier charges (card and draft). The compute subtracted the latest installment from the counted charges even when that
   installment was not among them. The earlier counted charges are now computed and stated as "the counted charges other
   than those of the latest installment":
   - Card: card_counted_charges now decides earlier_c. Ended: charges begun by the end month, less the latest. Active:
     begun charges, less the latest. Otherwise: the first installment, unless it is the latest. The baseline is that
     fall-through, which matches b1.
   - Draft: draft_latest_installment now decides earlier_d. It removes the end-period charges, or the current-period
     charges as far as they are counted, or the first installment if counted, from the counted set.
   - Gold: card 115.50, draft 99.18; left and the results are unchanged.
2. Fee level (card and draft). The waiver is now stated and computed for an individual fee arrangement, where the
   enrollee's own catastrophic total is the family's. The total states the fees_count_toward_catastrophic_cap flag and
   caps fees at the begun installments (MN(begun, paid)). A family arrangement is charged annual_fee_family without the
   waiver test; this is flagged in rationale 8. The ladder is LVL_LADDER (shared).
3. Claim-policy scope. SCOPE_CLAIM now tests the single-member condition: fee_bearing is true and fee_coverage_type is
   individual on the enrollee's own enrollment. The scope sentence states it, which leaves fee-exempt tiers outside the
   five policies.
4. Authorization overwrite. The replacing "auth" sentences of the OHI-line and cap-line policies now name the policy's own
   scope and keep the base clause, and its denial, for every other Select line.
Baseline wording: "times the attending share" is dropped from the professional, OHI-line and cap-line baselines (default
share 1). "met" is removed from the professional and OHI-line baseline lists (the deductible default ignores it). The
unused catastrophic-total sentence is removed from both stays, and its clause from the cap-line baseline (the cap-stage
default is uncapped).
Sweep: fee-level and earlier-charge factor traces, fee-level tier_taken texts, rationale 8 and 9 (both tasks).
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK, TRACEABILITY OK.

## Round 7 (re-audit revision_6)
C3 and O14 are closed, and the enrollment-field class was rechecked binding by binding. Every gold figure, factor
sensitivity and all-baseline figure is unchanged. select.extended.yaml bytes changed; task_tools.py bytes did not.
- C3: the card now uses the frequency in force, not F('payment_frequency'). That is the frequency installments are charged at
  for the payment date's year, quarter or month, otherwise the elected one. It is stated in the card's own frequency rule
  ("freq", now shared with the draft through freq_sentence) and computed by the shared CHARGED_FREQ expression.
  per_c = 12 / 3 / 1 at that frequency. The inherited base sentence "a change of frequency ... takes effect from the next
  installment period" is now honoured by both fee policies.
- O14: both scopes now state and test the fee-bearing flag and the elected method, so a wrong-method payer is out of scope
  (result None):
  - card: fee_bearing true, method card_single or check, frequency in force quarterly or annual;
  - draft: fee_bearing true, method allotment, electronic funds transfer or recurring card.
- Enrollment-field sweep: every F(...) read in the seven computes was listed and matched to its rule sentence.
  - The one remaining gap was "has ended" (computed as any disenrollment date on record, including a future one). Both fee
    policies now define it in a new "end" sentence: a disenrollment date on record before the payment date, and every
    other non-active enrollment is awaiting activation. The compute is ENDED = date present and DAYS(date, NOW) > 0.
  - Already matching their sentences: status, fee_coverage_type, fee_bearing, ohi_on_file, the effective date in the
    scope / plan-change / first-installment reads, and the elected frequency fall-back.
- DSL note: list literals are rejected, so the method tests are written as or-chains.
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK, TRACEABILITY OK.

## Round 8 (re-audit revision_7 + renderer notes)
Every gold figure, factor sensitivity and all-baseline figure is unchanged. select.extended.yaml bytes changed;
task_tools.py bytes did not.
1. C4: the card's and draft's standing is now the lifecycle status, as in the base.
   - ended = disenrolled_voluntary, disenrolled_nonpayment, terminated_ineligible or transferred_out, whatever the payment
     date (each of these events sets the disenrollment date);
   - active = active;
   - awaiting activation = applied;
   - rejected is outside the policy (STANDING_OK in both scopes).
   The "end" sentence states this; ENDED and STANDING_OK compute it. The auditor's reproductions now give base-consistent
   answers:
   - hypo.py: card 11.50 on both 2026-10-20 and 2026-10-21; the C3 rerun stays 44.50;
   - hypo_d.py: draft 29.59 on both 2026-10-31 and 2026-11-01.
2. Prior-authorization overwrite: the declaration is kept, and the replacing sentences now say only what replaces the clause
   for a line that policy reprocesses (payable on the replaced line's authorization finding, carrying its reference). The
   "every other Select line stays under that rule" restatement, which contradicted the declared retirement, is gone. An
   extended overwrite applies to its own policy's writes.
   I also tried dropping the overwrite and limiting the OHI-line and cap-line scopes to classes that need no
   authorization. That fails solvability: authorization_on_file becomes a required gate on every claim write, and a line
   with no authorization cannot bind referral_authorization_id. I reverted it.
3. Fee-exempt tiers: kept by design. A fee-exempt enrollment has fee_coverage_type not_applicable, and the DSL cannot read
   other family members' Select enrollments, so "only Select member of the family" cannot be tested for those tiers. The
   claim policies' scope sentence now says plainly that the fee-exempt (Active Duty Family Member) tiers are outside them.
Sweep: rationale 3, 8 and 9 (task 1) and 8 and 9 (task 0).
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK, TRACEABILITY OK.

## Round 9 (render report, round 3 of docs/select)
The prior-authorization overwrite is kept: without it the base gate would be required on the reprocessed lines, which
breaks SOLVABILITY (round 8). Each replacing ("auth") sentence now names the policy's own scope and keeps the base clause
in force everywhere else:
- OHI-line policy: "For a line this policy reprocesses for other health insurance found retroactively, and only for such a
  line, the authorization finding of the line it replaces stands in place of a fresh authorization test ...; every other
  Select line remains under the base authorization rule."
- Cap-line policy: the same sentence for "a line this policy reprocesses for the catastrophic cap".
So the retirement is visibly limited to the policy's own writes, and the base sentence "A line without one is denied ..."
still refers to a clause in force for every other line.
Every gold figure, factor sensitivity and all-baseline figure is unchanged. select.extended.yaml bytes changed;
task_tools.py bytes did not.
Sweep: rationale 3 and 9 (task 1).
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK, TRACEABILITY OK.

## Round 10 (KB audit source note: payment tools vs fee_balance_due)
The card and bank-draft tools now do what their contracts say. After writing the payment row, each looks up the
enrollment and lowers its recorded fee_balance_due by the amount paid, never below 0.00 (ctx.update in the tool body). The
docstrings say the same: "the enrollment's recorded fee balance (fee_balance_due) falls by the amount paid/drafted, never
below 0.00". Tool names and signatures are unchanged.
After the gold run, fee_balance_due goes from 94.00 to 82.50 (task 0) and from 178.36 to 49.59 (task 1; 49.59 is the January
2027 installment billed ahead). No computation reads fee_balance_due, so every scored value, factor sensitivity and
all-baseline figure is unchanged. The seeded figures hand over no scored value: 94.00 against the card's 11.50, and 178.36
against the draft's 128.77 (178.36 equals only the draft_latest_installment baseline alone).
Sweep: the tools_do_not_block notes (both tasks), a stale "frequency-in-force rung" phrase in task 1's enrollment
evidence, and rationale 9 (both tasks).
Hashes:
- select.extended.yaml unchanged: 7da5f3b38ebc443f5048cfa16c13ace6efdab2dbfb2f60ec26cdccf57199bac1.
- task_tools.py changed from 39e04e8226e647ef906b44ed703be43eabc4c83c1dfdf7b9a6eb86299b0195d3 to
  283e0d0017ca18e68941dd4bbee44f3e9739816a2a3a92800f3b395da3d46571.
Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK, TRACEABILITY OK.
