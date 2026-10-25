# worklog — payment_plan_servicing (category plan), env_0073_regional_hospital_system, M=2

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/plan.yaml (+ encounter/assist charters for cross-product pricing), db_schema.json, share_tools.py, audits/render_source/XF_recipe.md (27 points; applied to every policy/row).
- Claimable events: plan_created, plan_balance_enrolled, plan_balance_reduced, plan_terms_modified, plan_signed, plan_reaged, plan_reinstated, plan_cancelled_by_patient.
- Event-trigger check (XF 23): plan_installment_paid triggers encounter:encounter_payment_posted -> no task tool writes it. Every event my tools write (plan_balance_enrolled, plan_balance_reduced, plan_terms_modified, plan_signed) has triggers: [].
- Base automatic clauses to respect while seeding: signature deadline lapse (14/21 days), missed after grace -> past_due, default at missed_installments_to_default, FAP-pending pause, ECA protection while active, plan statement lead 21 days, reductions mirror encounter adjustments same date, payment application OLDEST_SERVICE_START_DATE_FIRST.
- DSL constraints noted (check_compute): SUM/COUNT scoped to plan_id; XSUM/XCOUNT customer-scoped; LATEST keeps first row in file order on same-date ties; MONTHS = whole months (day2<day1 -> minus 1), due days are 1/15 so no month-end ambiguity; min/max in an assembly kill factor sensitivity -> assemblies are additive/multiplicative.
- Owner doctrine: patient's own acts = signing the agreement (plan_signed) and patient-requested changes to their own installment (plan_patient_changes, an instruction over their own plan); agent = enroll/reduce/recompute.
- Identifier band 33: phones 92055503xx, MRN RB33xxxxxx, ssn4 3100-3999, surnames I-L, payment refs PMT-33xxxxx, emails <initial>33...

## Draw (scripts/draw_counts.py --tasks 2)
{"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [5, 5, 5, 4]}
{"task": 1, "prerequisite_problems": 1, "problems": 2, "factor_counts": [5, 5]}

## Scope plan (headroom, principle C)
- task 0 (4 problems): active Riverbend Hardship Payment Plan. root = patient lowers own installment to the lowest allowed (user, plan_terms_modified via plan_patient_changes); prereqs = installment recompute after an add-on (agent, plan_add_on_balances), the add-on of a newly billed month of an enrolled therapy series (agent, plan_eligible_balances), withdrawal of an enrolled account placed on a charge-dispute hold (agent, plan_balance_reduction).
- task 1 (2 problems): pending_signature Riverbend Extended Payment Plan. root = patient signs and authorizes the down payment (user, plan_signed / plan_signature_and_activation + plan_tier_and_installment down payment); prereq = re-figure of the unsigned offer's installment after an enrolled balance fell (agent, plan_tier_and_installment).
- Disjoint: task 0 claims plan_add_on_balances / plan_eligible_balances / plan_balance_reduction / plan_patient_changes cores; task 1 claims plan_tier_and_installment / plan_signature_and_activation cores. Re-age/reinstatement/cancel stay base-only (no extended policy).

## Scope decision (revised before any asset was written)
- Plan-category quantities a tool can carry: money = monthly_payment_usd, down_payment_usd, plan_transactions.amount (enroll / reduce pass-through); integer = term_months.
  Pass-through amounts (add-on, reduction) carry no natural multi-factor rule, so they are NOT claimed.
- Rich contexts: installment after add-ons (plan_add_on_balances), patient-requested lowest installment (plan_patient_changes),
  re-age schedule (plan_reage_and_reinstatement), FAP-pending pause (plan_missed_payment_and_default, 501(r) interplay),
  unsigned-offer installment re-figure (plan_tier_and_installment), down payment at signing (plan_signature_and_activation + plan_tier_and_installment).
- task 0 (4 problems, factors {5,5,5,4}): past_due Riverbend Hardship Payment Plan, patient's FA application open (pending BadgerCare Plus screening),
  two monthly therapy add-ons auto-enrolled since the last recompute.
  root  = patient sets the lowest installment allowed (owner=user, plan_terms_modified)
  edges = root -> installment recompute (value_input: reference installment)
          recompute -> re-age (value_input: schedule length)    recompute -> FAP pause (value_input: schedule length)
- task 1 (2 problems, factors {5,5}): pending_signature Riverbend Extended Payment Plan whose enrolled balance fell after the offer.
  root = patient signs + authorizes the down payment (owner=user, plan_signed); prereq = offer installment re-figure (value_input: installment floor of the down payment).

## Task 0 design (scratch evaluator: /tmp/payment_plan_servicing_0073/pol_t0.py, chain0.py; uses check_compute's own sandbox)
- World: Riverbend Long-Term Payment Plan (Teresa Lindqvist), offered 2025-04-21 (ED + inpatient self-pay balances 10,953.00, 10% down 1,095.30,
  20 installments of 492.89), monthly physical-therapy series add-ons (Aug month enrolled 2025-09-09 with recompute -> 405.20 x 26;
  Sep month 2025-10-05 and Oct month 2025-11-05 auto-enrolled, NOT recomputed), installment 2025-09-15 unpaid (+120.00 partial 2025-10-20),
  2025-10-15 and 2025-11-15 unpaid; system counted 2 missed (past_due). Open FAP case received 2025-10-02 (submitted, FPL 187.6,
  BadgerCare referral 2025-10-24, no determination notice). frozen 2025-11-20.
- Problems / edges: P_PAUSE (h, term) and P_REAGE (c, term) commute; P_RECALC (a0) value_input on both (term);
  P_LOWER (b, user) value_input on P_RECALC (remaining schedule as last computed = balance / recomputed installment, rounded up).
- Evaluator run: GOLD h=32 c=37 a0=263.65 b=223.85; skip h -> a0 304.21 b 252.43; skip c -> a0 296.61 b 252.43; skip a0 -> b 320.66.
  Every factor's single baseline substitution moves its result (PAUSE 31/31/31/31/31 vs 32; REAGE 38/35/36/36 vs 37;
  RECALC 359.52/282.48/269.64/269.64/269.64 vs 263.65; LOWER 263.65/263.65/252.43/232.63/219.71 vs 223.85).
- Revision log: (1) b first drafted as max(pct x ref, max-term floor): the max-term floor binds in any realistic world, so b ignored the
  recompute and the edge was decorative -> b re-specified as "lengthening allowance over the remaining schedule as last computed" (binding branch reads the recomputed installment).
  (2) re-age cap dropped (never binding) -> card/no-autopay cushion. (3) original term 24 -> 20 so the recompute stays under the 60 cap (edges load-bearing).

## Task 0 per-task gates (2026-10-20T11:15:26Z)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    CACHE-DIFF INFO (optional; no correctness gate)
    SCOPE OK
- fixes during gating: replay closure required reading hospital-account activity (find_encounter_transactions added, steps shift +1); re-age history floor coincidence (no-autopay cushion 2 -> 3).

## Task 1 design
- World: pending Riverbend Extended Payment Plan offer (Marcus Jankowski) offered 2025-10-06 on surgery 2,680.00 + imaging 1,341.00 = 4,021.00, 18 installments of 201.05, down 402.10, ACH, first due 2025-12-01;
  duplicate supply line credited 2025-10-09 (correction 110.00, plan reduction same day); patient portal payment 150.00 on 2025-10-10; open FAP case (pending_documents) FPL 249.6, referral 2025-10-07. frozen 2025-10-14.
- Tree: root plan_ext_signing_down_payment (owner=user) <- plan_ext_offer_refigure (value_input via the first-installment part). Re-figure 161.54, down payment 182.09; skipping the re-figure gives 221.60.
- Factor sensitivity: re-figure 166.08/153.04/185.77/168.88/168.88 vs 161.54 (all-baseline 201.05); signing 377.64/187.59/20.55/332.09/207.09 vs 182.09 (all-baseline 402.10).

## Method tiers — all-pairs table (C14), every method factor
- pause_exclusion (re-age): A min(missed, months(next due, receipt)+1) | B 0 | C missed. Input missed 2, next due 2025-09-15, receipt 2025-10-02 -> 1 / 0 / 2. A-B: A adds receipt input+min; A-C: A adds operation; B-C: constant vs data.
- window_reach (pause): A months(first due, handling)+1 | B months(first due, documents due) | C months(first due, handling). Input handling 2025-11-20, documents due 2025-11-05 -> 6 / 4 / 5.
- paid_installments (recompute): A entries - entries for next-due installment | B floor(total paid / installment) | C entries. Input 4 entries incl. 120.00 partial, total 1,598.67, installment 300.00 -> 3 / 5 / 4.
- application_due_dates (lowest): A months to handling - months to receipt | B months to documents due - months to receipt | C 0. Input handling 2025-11-20, documents due 2025-12-20, receipt 2025-10-02 -> 2 / 3 / 0.
- offer_balance_basis / signing_balance_basis: A enrolled - held account's enrolment | B enrolled - reductions | C enrolled. Input 4,021.00, held 1,341.00, reductions 110.00 -> 2,680.00 / 3,911.00 / 4,021.00.
- prior_payment_credit (signing): A credit_after_share x latest card payment | B credit_recent_share x it | C 0. Input 150.00 after vs 10 days before the offer -> 150.00 / 75.00 / 0.

## Probe table (scratch copies of each handling-time world; /tmp/payment_plan_servicing_0073/gen/probes.py)
| policy | probe | gold world | probed world |
|---|---|---|---|
| plan_ext_reage_schedule | decoy: second case, denied, FPL 120, older | 31 | 31 |
| plan_ext_reage_schedule | absent: no assistance case at all | 31 | 30 |
| plan_ext_reage_schedule | next_due_date empty (paid-off shape) | 31 | 29 |
| plan_ext_assistance_pause | decoy: second case, denied, FPL 120, older | 37 | 37 |
| plan_ext_assistance_pause | absent: no assistance case at all | 37 | 31 |
| plan_ext_assistance_pause | next_due_date empty (paid-off shape) | 37 | 37 |
| plan_ext_addon_recompute | decoy: second case, denied, FPL 120, older | 263.65 | 263.65 |
| plan_ext_addon_recompute | absent: no assistance case at all | 263.65 | 359.52 |
| plan_ext_addon_recompute | next_due_date empty (paid-off shape) | 263.65 | 263.65 |
| plan_ext_lowest_installment | decoy: second case, denied, FPL 120, older | 215.71 | 215.71 |
| plan_ext_lowest_installment | absent: no assistance case at all | 215.71 | 263.65 |
| plan_ext_lowest_installment | next_due_date empty (paid-off shape) | 215.71 | 215.71 |
| plan_ext_assistance_pause | decoy: referral notice on a different (denied) case | 37 | 36 |
| plan_ext_reage_schedule | decoy: referral notice on a different (denied) case | 31 | 30 |
| plan_ext_assistance_pause | decoy: add-on entry 13 months old (outside window) | 37 | 37 |
| plan_ext_addon_recompute | decoy: add-on entry 13 months old (outside window) | 263.65 | 263.65 |
| plan_ext_addon_recompute | tie: second add-on same latest date (recorded later) | 263.65 | 263.65 |
| plan_ext_lowest_installment | zero installment on plan (division guard) | 215.71 | 0.0 |
| plan_ext_addon_recompute | zero installment on plan (division guard) | 263.65 | 263.65 |
| plan_ext_reage_schedule | decoy: extra payment entry for a different due date | 31 | 31 |
| plan_ext_assistance_pause | pending_documents case past documents due (window tier B) | 37 | 35 |
| plan_ext_offer_refigure | decoy: second case, withdrawn, FPL 150 | 161.54 | 161.54 |
| plan_ext_offer_refigure | absent: no assistance case | 161.54 | 176.0 |
| plan_ext_offer_refigure | decoy: charge-dispute hold on an account NOT enrolled (listed first) | 161.54 | 161.54 |
| plan_ext_offer_refigure | tier: enrolled imaging account on charge-dispute hold | 161.54 | 110.7 |
| plan_ext_signing_down_payment | decoy: second case, withdrawn, FPL 150 | 182.09 | 182.09 |
| plan_ext_signing_down_payment | absent: no assistance case | 182.09 | 377.64 |
| plan_ext_signing_down_payment | decoy: charge-dispute hold on an account NOT enrolled (listed first) | 182.09 | 182.09 |
| plan_ext_signing_down_payment | tier: enrolled imaging account on charge-dispute hold | 182.09 | 120.54 |
| plan_ext_signing_down_payment | decoy: older, larger phone-card payment (2025-09-20) | 182.09 | 182.09 |
| plan_ext_signing_down_payment | absent: no card payment at all | 182.09 | 332.09 |
| plan_ext_signing_down_payment | ACH -> CARD on the offer | 182.09 | 207.09 |
Reading: decoy rows (denied/withdrawn second case, referral on another case, out-of-window add-on, entry for another due date, older/larger card payment, unenrolled held account) never change the result; absent case / no card payment / empty next due date / zero installment evaluate without error to the rule's stated fall-backs. One first-match read (charge-dispute hold) is now stated in the rule ('the first of the patient's accounts listed on such a hold').

## Task 1 per-task gates
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK

## XF recipe sweep (all 27 points, both tasks)
- A1/A2 (scripted): no factor binding reads another factor's binding; shared reads (open case, receipt, enrolled total, plan fields) are plain bindings; assembly only in plain bindings/result.
- A3/A4: each rule has one generic assembly sentence fixing order where it matters (counts/limits first, additions after; share first, credits after); quantities used by one factor live in that factor's bindings; baselines silent about factors.
- A5: no "as policy X figures it"; cross-policy waits are prerequisite sentences (one state form, three action forms with fallback reasons).
- B6: None/absent/zero/empty-date edges guarded and stated (no open case; empty next due date; zero installment; remaining < 1 counts as one; lengthened/longest >= 1; down payment never below zero).
- B7: tie rules stated (latest add-on: first recorded; latest card payment: portal over phone on a shared date, first recorded within a channel).
- B8: whole-month convention stated in the shared open-application paragraph (month complete when the later day number reaches the earlier; due days 1/15).
- B9: referral/determination counts filtered by the open case id; add-on counts exclude creation-date entries and use the same twelve-whole-month window on both terms.
- B10: rounding sentences match RND placement (installments, shares, credits, candidates half-up to the cent; schedule counts whole numbers).
- B11 (scripted): every compute_basis quote is a verbatim substring of its rule. B12/B13: rule words map to real fields; ladders gap-free with boundaries named by params.
- C14: all-pairs tables above. D15-D17: each overwrite retires exactly the conflicting base sentence(s), replaced_by names its own scope; no rule defers to a retired clause.
- E18-E24: task_tools.py imports only erlbench; frozen_time 'YYYY-MM-DD HH:MM:SS CST/CDT'; no factor id is a substring of a tool name; docstrings carry formats, not example values; one enum per field; events written (plan_terms_modified, plan_reaged, plan_signed) all have triggers []; schema meanings respected (amounts positive, term positive integer).
- F25-F27: encounter rows priced by the encounter charter (uninsured discount by class, correction = credit x (1 - discount), statements every 30 days within the summary count, every plan installment mirrored oldest account first, ED account closed at zero); assistance FPL on the 2025 HHS guideline (3 persons 26,650; 2 persons 21,150) with tier-correct documents/notices/deadlines; add-on window and statement look-backs inside seeded history.

## Manual values gates
- Length/breadth: T0 surface goal (lowest payment) -> recompute (waits on re-age and pause) -> lowest; parallel inputs: assistance screening (5 policies), BadgerCare referral/determination, plan ledger (balance, add-ons, partial, drafts), hospital-account type. T1: sign -> re-figure; inputs: case screening, reduction, holds, account types, latest card payment, first-due gap, autopay. Both trees end in an owner=user write the patient must sign personally (installment change; agreement).
- Persona boundary: both personas state the goal, identity on request, and passive answers only; no prerequisite named; no extra ask; arc ends at the last gold action (new payment set / plan active).
- Chronology: every volunteered fact (payment plan offer received; hours cut; wants lowest payment) is consistent with initial_state; facts that only gold produces are never stated in advance.
- Base eligibility/time: only plan_signed has a time gate (signature deadline 14 days from 2025-10-06, inclusive, last day 2025-10-20; handling day 8). Re-age prose conditions hold (re-age count 0 < 2; 4 installments paid >= 3).
- Authority/object: status, missed count, case status/FPL, holds and payments are read from system rows; the plan is the only plan of each patient; reductions and enrollments carry encounter ids.
- Reachability: one frozen_time per task; no waits; all must-ask answers present in the persona.
- Prerequisite sentences: four-point test passed (connectives 'only after' x2, 'not ... until' x2; business states/actions; no tool/id/code tokens; exact scope). State form used where a record-visible state singles out the write (re-age); action form elsewhere with reasons.
- Rule/compute equivalence: reverse sweep done per policy (every window, filter, branch, cap and rounding sentence claimed by a binding).
- Factor honesty: every factor's baseline is the computation document's default; every method tier changes formula shape (table above).
- Draft recomputation from visible context: reproduces gold in both tasks (see each task's rationale item 11).

## Honest realism note (for the audit)
- Grounded in the charter / real practice: assistance-screened servicing values taken from the Hardship / Assistance-Linked tiers, the 501(r)-style pause while an application is open, the BadgerCare Plus screening extension, paused installments excluded from a re-age, partial-payment and paid-installment counting, payment-application reality (card vs ACH drafts), unsigned offers re-figured on reductions, down payment credited with payments made after the offer, first-installment collection when the first due date is far off.
- Riverbend-specific schedules with no external source (the plan charter is thin on plan-side money rules): the pause bridge installments (balance band, add-on frequency, household size), the re-age cushions, the recompute band/class installments, the lowering allowance and draw holdback, the offer band/class installments and the ACH signing credit. They are coherent, record-derived and load-bearing, but an auditor may judge some of them invented; they are the first candidates for rework.

## Final gate block (difficulty-wide, 2026-10-20T11:22:01Z)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
    (check_traceability runs after the KB is rendered; check_cache_diff is informational)
- Scratch authoring scripts and data in /tmp/payment_plan_servicing_0073/ removed after this run.

INSTANTIATE round 1: gates 7/7 green

# REWORK round 2
- Read in full: audits/policy_task/payment_plan_servicing/_difficulty.md, 0.md, 1.md (revision_1: task0=RED task1=RED charter=C1..C12; T0-1..3, T1-1..2; observations O1..O9).
- Plan: close every finding by class (all overwrites, every ladder on every plan tier in scope, every read site, every assembly sentence), replace the self-flagged invented levers with
  charter/501(r)-grounded ones, re-seed task 0 so counters equal what the in-force rules produce, re-run probes + pairwise method table, sweep proof text, re-run gates.

## REWORK round 2 — item-by-item response (item -> what changed -> where)
Resumed after an account cut: the round-2 header above was the only round-2 write before the cut; everything below was redone from that breakpoint. Draw unchanged (task 0: 3 prerequisites, factor counts [5,5,5,4] -> re-age 5, pause 5, recompute 5, lowering 4; task 1: 1 prerequisite, [5,5] -> re-figure 5, signing 5). Gold now: task 0 re-age term 27, pause term 31, recompute 74.98, lowering 62.00; task 1 re-figure 74.73 over 48, signing down payment 109.13.
- C1 (undeclared departure, re-figure down payment) -> plan_ext_offer_refigure now overwrites the base sentence "The down payment is down_payment_pct of the enrolled total, rounded half-up to the cent, due at signing." for unsigned-offer re-figures only; its replaced_by restates the creation rule and names the signing rule's share as the down payment collected at signing; the signing overwrite of the same sentence names the re-figure's deduction (sibling exclusion both ways). Class sweep: every extended rule was diffed against every base sentence it touches; one more undeclared departure was found and declared: signing's screening hold vs base plan_signature_and_activation "Any down payment is paid at signing." (new overwrite). Re-figure also declares the term, installment and reduction sentences. Where: plan.extended.yaml overwrite[] of plan_ext_offer_refigure (4), plan_ext_signing_down_payment (2).
- C2 (replaced_by deferring to the retired clause; 7 members) -> every replaced_by (now 9 across 6 policies) restates the still-in-force base content for the out-of-scope case and names its own scope; none says "stays under the base ... rule". Pause: "until a pause is booked they stay paused for up to fap_pending_pause_days" and "are not counted as missed"; recompute names the offer re-figure for unsigned offers; lowering names due-day change/skip/cancellation as staying under the patient-change terms (sentences not retired); re-figure x4 restate the creation-time down payment/term/installment and the signed-plan reduction treatment; signing x2 restate the offer-time down payment and "pays any down payment at signing" for other signings. Where: overwrite[].replaced_by of all six policies (verbatim in each rule, checked by the build script).
- C3 (window tier rule != compute) -> pause window rewritten: tiers keyed on case status and documents due date only (pending_documents with documents due date on/after the handling date; submitted; otherwise); rule words and compute test the same fields; probe rows "documents due date already passed", "documents due date empty", "case submitted" confirm. Where: plan_ext_assistance_pause rule/compute.window/factors.pause_window.
- C4 (care_class first-match vs rule) -> the class factor was removed from the re-figure; the remaining first-match reads were re-worded to say exactly what is read: re-figure/signing balance "when the first of the patient's accounts listed on a charge-dispute billing hold is an account enrolled on the offer"; recompute care installments read the exact encounter_id of the latest add-on entry (no first-match by variant) with the tie rule stated. Probes: decoy hold on a non-enrolled account listed first, same-day add-on tie.
- C5 (negative month count / future-dated counts in application_due_dates) -> the lowering's waiting installments count only due dates that have already come (end = earlier of handling date and documents due date), clamp the receipt position at one month before the first due date and never go below zero; the framing says "have already come". The pause window, which does take in installments still to fall due by the documents due date, now says so in its own words ("also takes in the installments that will fall due by then"). Probes: receipt before first due date (negative months), receipt in the future, documents due passed/empty.
- C6 (empty "read below" boilerplate; baseline naming factor inputs) -> the open-application sentence now states only the definition (and the receipt date only in the three policies that read it); no sentence promises reads the policy does not make; the pause baseline no longer names FPL, household size, notices or documents. Where: OPEN_S/OPEN_S2 in each rule; baseline.rule of every policy.
- C7 (assembly sentences naming factor quantities) -> one generic sentence in every policy: "The adjustments set out below are applied to the standard figure in a fixed order: values that replace a standard input come first, installments that are added or taken away come next, and any limit comes last."
- C8 (re-figure vs recompute on an unsigned offer with an add-on) -> scopes made disjoint by record state: the re-figure rule covers offers in pending_signature "an add-on enrolled on the offer included" and "a signed plan is never re-figured under this rule"; the recompute covers signed plans (active or past_due) and says "an offer not yet signed is never recomputed under this rule"; the recompute's replaced_by names the re-figure for unsigned offers.
- C9 (pause window tiers differing by +1) -> new window method: data-selected end date (documents due date) vs elapsed-time count (days/30, floor) vs due-date positions to the handling date; all-pairs table below.
- C10 (prior_payment_credit multiplier-only "method") -> removed. The post-offer payment is now a parameter factor whose tiers are the account's enrolled amount, the payment itself, or nothing (no multiplier tiers, no half credit).
- C11 (collisions/inversions on other plan tiers) -> every ladder whose fall-through is a tier parameter is scoped rung by rung ("only on tiers whose <param> is shorter/higher"), so no in-scope rung equals the fall-through and no applicant gets a harsher figure than a non-applicant on any of the six tiers; table below.
- C12 (unreal levers: ACH gap credit, half credit, plus the coordinator's list: pause bridges, re-age cushions, lowering allowance, draw holdback, offer band terms) -> all removed. Replaced by: BadgerCare Plus screening days and case-completion days on the pause period (assist charter parameters), assistance-linked terms (Hardship/Assistance-Linked max terms 60/48, skip allowances 3/2, minimum payments 10/20, requested-installment shares 50/75), a term schedule by balance as a ceiling (60 at 10,000+, 48 at 3,000+), add-on recompute rules (frequency extension 12/6, latest add-on care), partial-payment treatment, a Medicaid-pending hold of the down payment, crediting of a post-offer payment, a payment-record ceiling for re-ages.
- T0-1 (seeded missed count not what the in-force rules give) -> task 0 re-seeded (Extended plan, see dossier): missed_installments 1 = the 2025-08-15 installment that passed its 15 grace days before the 2025-09-10 receipt; 2025-09-15 and 2025-10-15 fall due within the base 60-day pause and are not counted; 2025-11-15 is inside its grace days at 2025-11-20. No pause/re-age/recompute was booked before the call; installment and term are the offer's. seed_consistency rows state this.
- T0-2 (pause without a passing method; < 4 sound factors) -> pause has 5 factors with a passing method; re-age 5, recompute 5, lowering 4; every factor bites (check_compute sensitivity, table in computations[]).
- T0-3 (why_false said 2025-12-15 "fell due") -> rewritten: "the installments due 2025-09-15, 2025-10-15 and 2025-11-15 have fallen due since receipt and the 2025-12-15 installment falls due within the pause window that runs to the documents due date". All proof/trace/necessity text of both tasks regenerated from the computed values.
- T1-1 (two clauses fix the deducted down payment) -> closed by C1 (declared overwrite) and by the signing using the same share and balance ladders as the re-figure deduction; only one reading remains.
- T1-2 (signing resting on C10/C12 ladders) -> signing factors are now signing share, signing balance (method), screening hold, post-offer payment credit, installments collected at signing; 5 sound factors, all biting.
- Observations: O1 re-age leaves next_due_date -> on the new world the re-age moves no whole installment (the 52.24 remainder stays due on 2025-08-15), so next_due_date unchanged is what the rule says; O2 "once" removed from the recompute docstring; O3 the lowering's hop is still tested against the recompute rule (no recompute date is recorded; action-form edge kept with its fallback reason); O4 method borderlines replaced (see table); O5 weak ladders removed (household, draw) or kept and argued (care class); O7 the overpayment tier now compares the numbered payments' total with their count times the installment (the down-payment entry no longer meets it).
- Tool change: refigure_plan_offer_04613189 now also writes term_months (the re-figure books the term it uses; otherwise an offer would show 24 installments of a 48-installment figure); docstring example value removed (XF E21). Recompute docstring reworded.

## C11 — every scoped ladder on all six plan tiers (Short-Term / Standard / Extended / Long-Term / Assistance-Linked / Hardship)
Fall-through first, then the in-scope rung values; "-" = rung out of scope on that tier (falls through). Monotone means applicant/lower-FPL/larger-need never gets less.
| ladder (policies) | fall-through by tier | rung 1 | rung 2 | monotone, no rung == fall-through |
|---|---|---|---|---|
| screening ceiling / screening term / lowered term limit (pause, re-age, recompute, lowering, re-figure) | 6/12/24/36/48/60 | <=200% FPL: 60/60/60/60/60/- | (200,400]: 48/48/48/48/-/- | yes on all six |
| balance ceiling / balance term (pause, re-age, re-figure) | 6/12/24/36/48/60 | ledger >= 10,000: 60/60/60/60/60/- | >= 3,000: 48/48/48/48/-/- | yes |
| payment-record ceiling (re-age) | 6/12/24/36/48/60 | >= 3 entries: 60 x5/- | 1-2 entries: 48 x4/-/- | yes |
| deferrals (re-age) | 0 | <=200%: 3/3/3/3/3/- (skip 0/0/1/1/2/3) | (200,400]: 2/2/2/2/-/- | yes (3 >= 2 >= 0) |
| add-on frequency extension (recompute) | 0/0/6/6/12/12 | >= 3 add-ons: 12/12/12/12/-/- | exactly 2: 6/6/-/-/-/- | yes |
| recompute / lowering / offer floor | 25/50/75/100/20/10 | <=200%: 10/10/10/10/10/- | (200,400]: 20/20/20/20/-/- (Hardship stays 10) | yes (an applicant's floor never higher) |
| lowering share | 100/100/100/100/75/50 | <=200%: 50 x5/- | (200,400]: 75/75/75/75/-/- (Hardship stays 50) | yes |
| deducted down share / signing share | 0/0/10/10/0/0 | <=200%: -/-/0/0/-/- | (200,400]: -/-/5/5/-/- | yes (applicants never pay more) |
| Medicaid screening days, case-completion days (pause) | +0 on tier fap_pending_pause_days 60/60/60/60/90/90 | +45 / +30 | +30 / +30 | additive, never negative |
| screening hold (signing) | 0 | <=200%: 100% | (200,400]: 50% | yes |

## C14 — all-pairs method-tier table (distinguishing input per pair)
| factor | tiers | A vs B | A vs C | B vs C |
|---|---|---|---|---|
| pause_window | A: due-date positions to the documents due date; B: floor(elapsed days receipt->handling / 30); C: due-date positions to the handling date | A adds a data-selected end date and due-day positions, B a day count with floor; distinguishing input: due day of month (moves A, not B) | A's end is a data-selected record date (documents_due_date, may lie after the handling date) vs the clock; distinguishing input: documents_due_date | B floor-divides a day span from receipt, C counts positions from the start position (next due/receipt); distinguishing input: first_due_date |
| moved_installments | A: floor((missed x installment - partial payments) / installment); B: whole months next due -> receipt + 1; C: recorded missed count | amount division with floor vs calendar count; input: partial payment sum | adds the partial-payment sum and the installment; input: partial sum | adds receipt date and next due date; input: application_date |
| installments_paid_count (recompute) | A: entries numbered >= 1 less the entries numbered as the next-due installment; B: floor(numbered total / installment); C: entries numbered >= 1 | count arithmetic vs amount division with floor; input: payment amounts | adds a data-selected second count (entries matching the next-due installment number); input: next_due_date | adds the amounts and the installment; input: payment amounts |
| waiting_installments (lowering) | A: positions after receipt to MN(handling, documents due), clamped; B: floor(elapsed days / 30); C: none | position count with min/clamp vs day floor; input: due day | A is non-zero across its domain once a due date has come; input: application_date | B non-zero after 30 days; input: receipt-to-handling span |
| refigure_balance / signing_balance | A: enrolled total less the enrolled amount of the first held account; B: enrolled total less reductions; C: enrolled total | A adds a cross-category selection (billing_hold_reason picks the account) that B lacks; B adds the reductions aggregate; input: encounter hold | adds the encounter-selected subtraction; input: billing_hold_reason | adds the reductions aggregate; input: plan_balance_reduced rows |

## Probe table — decoy / absent / None / zero / negative-month / future-date cases (scratch copies of each handling-time world)
| T0 probe | results (gold: reage=27, pause=31, recompute=74.98, lowest=62.0) |
|---|---|
| gold world | reage=27, pause=31, recompute=74.98, lowest=62.0 |
| decoy approved case (FPL 120) listed first | reage=27, pause=31, recompute=74.98, lowest=62.0 |
| decoy submitted case of another customer | reage=27, pause=31, recompute=74.98, lowest=62.0 |
| second open case submitted (FPL 320) listed last -> submitted taken first | reage=26, pause=29, recompute=74.98, lowest=73.27 |
| decoy referral notice on a denied case | reage=27, pause=31, recompute=74.98, lowest=62.0 |
| BadgerCare determination received on the open case | reage=27, pause=31, recompute=74.98, lowest=62.0 |
| determination only REQUESTED (not received) | reage=27, pause=31, recompute=74.98, lowest=62.0 |
| absent assistance case | reage=24, pause=27, recompute=153.52, lowest=74.98 |
| case FPL missing (None) | reage=24, pause=27, recompute=153.52, lowest=74.98 |
| case FPL 250 (partial band) | reage=26, pause=31, recompute=74.98, lowest=73.27 |
| case FPL 450 (above bands) | reage=24, pause=27, recompute=153.52, lowest=74.98 |
| case submitted instead of pending_documents | reage=27, pause=29, recompute=74.98, lowest=63.22 |
| documents due date already passed (2025-11-10) | reage=27, pause=30, recompute=74.98, lowest=63.22 |
| documents due date empty | reage=27, pause=30, recompute=74.98, lowest=62.0 |
| receipt before the first due date (2025-02-20; negative months) | reage=27, pause=31, recompute=74.98, lowest=57.57 |
| receipt in the future (2025-12-01) | reage=27, pause=28, recompute=74.98, lowest=65.8 |
| plan next_due_date empty | reage=28, pause=31, recompute=76.76, lowest=62.0 |
| no partial entry (deleted) | reage=28, pause=31, recompute=74.98, lowest=62.24 |
| installment 0.00 | reage=28, pause=31, recompute=74.98, lowest=0.0 |
| add-on tie: inpatient add-on on 2025-11-05 listed before the therapy one | recompute=76.76 |
| no add-on entries (only offer-date enrollments) | recompute=94.82, lowest=59.02 |
| skip_count 3 (deferrals used up) | reage=24 |
| T1 probe | results (gold: refigure=74.73, signing=109.13) |
|---|---|
| gold world | offer_refigure=74.73, signing_down_payment=109.13 |
| decoy charge-dispute hold on a non-enrolled account listed first | offer_refigure=74.73, signing_down_payment=109.13 |
| surgery account (enrolled) on a charge-dispute hold | offer_refigure=23.87, signing_down_payment=74.73 |
| absent assistance case | offer_refigure=141.6, signing_down_payment=392.33 |
| decoy denied case FPL 150 listed first | offer_refigure=74.73, signing_down_payment=109.13 |
| FPL 180 (low-income band) | offer_refigure=78.67, signing_down_payment=74.73 |
| determination received | offer_refigure=74.73, signing_down_payment=203.53 |
| no reduction booked | offer_refigure=76.91, signing_down_payment=111.88 |
| offer term 18 (patient asked a shorter term) | offer_refigure=199.29, signing_down_payment=109.13 |
| payment before the offer date only | offer_refigure=74.73, signing_down_payment=169.13 |
| later payment on a non-enrolled account | offer_refigure=74.73, signing_down_payment=169.13 |
| payment of the whole MRI enrolled amount | offer_refigure=74.73, signing_down_payment=74.73 |
| same-day tie: second payment 25.00 on 2025-10-10 listed after | offer_refigure=74.73, signing_down_payment=109.13 |
| first due date 70 days out (2025-12-23) | offer_refigure=74.73, signing_down_payment=183.86 |
| first due date 30 days out (2025-11-13) | offer_refigure=74.73, signing_down_payment=34.4 |
| first due date empty | offer_refigure=74.73, signing_down_payment=34.4 |
Reading: decoys (other customer's case, approved/denied case listed first, referral on a denied case, hold on a non-enrolled account listed first, payment on a non-enrolled account, payment before the offer) never move a result; absent case or missing FPL falls to the standard figures without error; negative months (receipt before the first due date) clamp at one position before the first due date; a future receipt or documents due date counts only what the rule words say; installment 0.00 and empty first/next due dates evaluate without error (0.00 is unreachable: every tier floor is at least 10.00); same-day ties keep the first listed row, as the rules state.

## XF recipe re-application (all points, all six policies)
- A1-A4: mechanical scan (no factor binding reads another factor's binding, transitively) passes; shared selections (open application, receipt date, ledger balance in the lowering) are plain bindings stated once; one generic assembly sentence with the order in generic words; every convention a single factor uses (month counting) is stated inside that factor's own sentence; baselines are self-sufficient and name no factor input.
- A5: no rule defines a quantity "as another policy figures it"; cross-policy waits are the three prerequisite sentences (two action-form with fallback reasons, one state-form).
- B6-B13: probe table above; tie rules stated (LATEST/XLATEST keep the first listed row); month-end convention stated; XCOUNT filters carry the case id, notice type, document type and RECEIVED status the rules name; rounding sentences match RND placement (re-figure deduction and installment, signing share and the part left after the hold, recompute, lowering); compute_basis quotes verified verbatim by the build script; ladders stated with their figures and re-checked on all six tiers.
- C14: table above.
- D15-D17: overwrites listed under C1/C2; no rule defers to a clause its own overwrite retires.
- E18-E24: task_tools has no datetime/random/uuid imports; frozen_time format kept; no factor id is a substring of a tool name (scanned); no example values in docstrings; one value per argument; tools write only plan_terms_modified / plan_reaged / plan_signed fields, none of which triggers another category.
- F25-F27: task 0's encounter rows are priced with the encounter charter (ED 45%, imaging 55%, therapy 45% uninsured discounts at final bill; first statements only before enrollment; plan installments posted to the enrolled accounts); assist rows follow the assist charter (documents due date 30 days after the missing-information notice, referral before the screening deadline, FPL 187.6 for 50,000 and a household of 3 against the 2025 HHS 26,650); task 1's imaging account re-priced (2,680.00 gross, 55% discount 1,474.00, 1,206.00 enrolled, 60.00 portal payment after the offer). No statute is cited; Riverbend's schedules are worded as Riverbend's own.

## Honest realism note (round 2)
Strongest levers: assistance-linked terms read from the Hardship/Assistance-Linked tier parameters, the pause lengthened by the assist charter's BadgerCare Plus screening deadline and missing-information/determination periods, term ceilings by balance, add-on recompute rules, partial-payment treatment, crediting a post-offer payment, a hold of the down payment while Medicaid screening is pending. Weaker, kept and argued: the payment-record ceiling (re-age stretch only after three or more installments paid — the usual re-age qualifying-payment test, not a tenure ladder), the latest add-on care installments (3 for a recurring therapy series, 2 for an acute stay), installments collected at signing when the first due date is far off (gap 45/60 days), the case-completion days ladder whose two non-zero tiers are both 30 days (two distinct assist parameters that happen to be equal), the pause window's elapsed-time tier for submitted cases, and the lowering's waiting installments, which lengthen the lowered schedule for due dates that came while the application waited even though the pause also moved them to the end. These are the first candidates if an auditor rejects any.

## Stale-text sweep (round 2)
plan.extended.yaml and both task files (outside initial_state/db_closure) were scanned for every round-1 figure and lever name (bridge, cushion, holdback, allowance installments, ACH credit, half credit, band/class installments, 405.20, 263.65, 215.71, 161.54, 182.09, 4,021.00, 3,911.00, term 18, "fell due", "read below", "base ... rule"); remaining hits are only current figures. All factor traces, tracing strings, necessity lines, seed checks, why_false/flips_to_true_by and edge_load_bearing texts were regenerated from the computed values.

## Round-2 final gate block (difficulty-wide, 2026-10-20T20:51:17Z)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
    (check_cache_diff informational: CACHE-DIFF INFO; check_traceability runs after the KB is rendered)
- Scratch authoring scripts and data in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 2: gates 7/7 green

# REWORK round 3
- Read in full: audits/policy_task/payment_plan_servicing/_difficulty.md, 0.md, 1.md (revision_2: task0=RED task1=RED charter=R2-C1..R2-C7; T0-R2-1..3, T1-R2-1..2; observations R2-O1..O4). Round-2 authoring scripts had been removed, so the edits were made by loading plan.extended.yaml and the task files, patching the named fields and re-dumping (base text re-verified verbatim; every compute_basis/baseline/replaced_by/policy_source re-checked verbatim in its rule).
- Gold moves: none. Task 0 stays re-age 27 / pause 31 / recompute 74.98 / lowering 62.00; task 1 stays re-figure 74.73 over 48 / signing 109.13. The only figure that moved is the re-figure's all-baseline fallback, 145.72 -> 145.73 (now half-up, as the rule says).

## Item-by-item (item -> change -> where)
- R2-C1 / T0-R2-2 (case_completion_days tiers 1 and 2 both 30) -> re-cut on the time the case still needs: pending_documents -> days from the handling date to the documents due date (0 once passed) + determination_days; submitted -> determination_days; none -> 0. Tier 1 differs from tier 2 whenever the documents due date lies ahead (task 0: 28 + 30 = 58 vs 30). New own binding dc_docs_due. Pause allowance on task 0 becomes int((60 + 45 + 58)/30) = 5, paused still MN(window 4, 5) = 4; baselines (medicaid -> int(118/30) = 3, completion -> int(105/30) = 3) still bite. Class sweep for dead/duplicate tiers on every ladder: medicaid 45/30/0 distinct; deferrals, floors, shares, ceilings, terms distinct on reachable tiers (record ceiling tier 2 live on Short-Term/Standard; balance ceiling tier 2 live on Extended/Long-Term; add-on extension tier 2 live on Standard; installments-at-signing tier 1 live when signing early in an Extended/Assistance-Linked/Hardship signature window, first due set from the deadline: gap up to 69/81 days); post-offer credit tiers distinct.
- R2-C2 / T1-R2-1 (screening_hold tier 1 dead) -> re-cut where a signing share exists: referral unanswered and FPL at or below hold_fpl_near 300 -> hold_near 50%; above 300 and at or below 400 -> hold_far 25%; else 0. Task 1 (FPL 249.6) keeps 50%.
- R2-C3 / T0-R2-1 (re-age records active/0 missed while a remainder stays due past grace) -> the partial-payment tier now closes the unpaid part of less than one installment into the plan balance for the final installment, and the re-age declares a scoped overwrite of base "An installment not paid in full by grace_days calendar days after its due date is missed and the plan becomes past_due; a partial payment does not cure a missed installment." whose replaced_by restates the base rule for every case and names its own scope (only a re-age under this rule closes such a remainder). Task 0 texts (trace, business effect, dossier) say so; the world needs no row change (the closed 52.24 is already in plan_balance). Re-age docstring no longer says the missed installments are always moved.
- R2-C4 (generic order vs compute floor position) -> every policy's order sentence now states the exact compute order without naming a factor: pause (days and window, then allowance and addition, then longest paused schedule, never shorter last); re-age (moved and added installments, then longest re-aged schedule, never shorter last); recompute (replacements and added installments, then longest schedule, then paid and missed taken away with at least one installment, floor last on the divided figure); lowering (additions, then term-limit schedule, then the three figures compared and held to the current installment); re-figure (balance and deduction, shorter term, floor last); signing (share of the balance, held/credited amounts taken away with the zero floor, installments added last). Probe: payment 150.00 > share left 94.40 -> 74.73 (floor before the installment).
- R2-C5 (re-figure replaced_by dropping the floor-schedule clause) -> creation clause restated in full ("when that floor applies the schedule has as many installments as the floor needs; in every case the final installment absorbs the remainder") and the in-scope re-figure says the offer is booked with as many installments as the offer floor needs when it applies. Sweep of all 11 overwrites (pause 1, re-age 2, recompute 1, lowering 1, re-figure 4, signing 2): every still-in-force part of each retired clause is restated for its out-of-scope case or replaced in scope.
- R2-C6 (submitted pause window, two readings) -> one reading: one per full 30 days from receipt to handling, never more than the considered installments fallen due by the handling date (so a paid installment is never paused). Compute MN(floor(days/30), positions to handling - start). Pairwise: B vs A (data-selected documents date end, month positions) and B vs C (adds the day count and the min) still distinct; distinguishing inputs as in the round-2 table.
- R2-C7 / T0-R2-3 (therapy bill dates) -> September and October therapy liabilities and uninsured discounts re-posted 2025-10-05 and 2025-11-05 (bill_hold_days 5 after each service month); every seeded encounter row re-checked against the encounter charter: the imaging final bill moved 2025-03-06 -> 2025-03-07 (bill_hold_days 4) with its liability and discount; ED 02-15 -> 02-19 (4), therapy August -> 09-05 (5), task 1 surgery 09-03 -> 09-08 (5) and imaging 09-19 -> 09-23 (4) correct; discounts 45% ED/therapy, 55% imaging, 50% surgery; payments applied oldest service start first; statements only before enrollment. Seed checks re-worded.
- T1-R2-2 (RND ties) -> every RND in compute now rounds ties up (RND(x + 0.000001, 2); all amounts are non-negative), matching every rule's "rounded half-up to the cent"; the re-figure all-baseline figure is 145.73 in computations[].
- O2 leftover -> ordering words removed from docstrings ("once the pause/re-age is booked" -> "with the pause/re-age booked"; "after balances have been added" -> "that has had balances added").
- Observations carried: R2-O1 (record ceiling tier 2 unreachable on Extended/Long-Term, live elsewhere), R2-O2 (pause/re-age caps commute on task 0, general case noted), R2-O4 (deferrals not counted in skip_count), re-age leaves next_due_date (tool field set unchanged).

## Round-3 probe table (touched reads)
| probe (round 3, touched reads) | result |
|---|---|
| pause: gold (term 27 before the pause) | 31 |
| pause: documents due date passed (2025-11-10): completion days = determination only | 30 |
| pause: documents due date empty | 30 |
| pause: decoy approved case with documents due 2026-03-01 listed first | 31 |
| pause: absent case | 27 |
| pause: submitted, receipt 2025-09-10 (71 days -> 2; considered fallen due 3) | 29 |
| pause: submitted, receipt 2025-06-01 with next due 2025-08-15 (elapsed 5, considered fallen due 4: paid ones never paused) | 31 |
| pause: submitted, receipt 2025-11-19 (0 days) | 27 |
| signing: gold | 109.13 |
| signing: FPL 320 (hold_far 25%) | 156.33 |
| signing: FPL 180 (share 0; hold irrelevant) | 74.73 |
| signing: FPL 450 (no hold, tier share 10%) | 392.33 |
| signing: FPL None | 392.33 |
| signing: payment 150.00 > share left 94.40 (zero floor before the installment) | 74.73 |
| refigure all-baseline tie 3,497.40/24 = 145.725 | 145.73 |
Untouched reads keep their round-2 probe rows (their bindings did not change); every touched read is re-probed above.

## Round-3 final gate block (difficulty-wide, 2026-10-20T22:58:47Z)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 3: gates 7/7 green

# REWORK round 4
- Read in full: audits/policy_task/payment_plan_servicing/_difficulty.md, 0.md, 1.md (revision_3: task0=RED task1=RED charter=R3-C1,R3-C2,R3-C3; T0-R3-1, T0-R3-2, T1-R3-1; observation R3-O1). Edits patched into plan.extended.yaml / task_tools.py / tasks/*.json in place (base text and every quoted sentence re-verified verbatim).
- Gold moves: none. Task 0 re-age 27 / pause 31 / recompute 74.98 / lowering 62.00; task 1 re-figure 74.73 over 48 / signing 109.13. Task 0's re-age write gains one argument (next_due_date 2025-09-15); terminal state now carries that next due date.

## Item-by-item (item -> change -> where)
- R3-C1 / T0-R3-2 (mislabelled effect) -> label sweep of all 29 factors against C14: a factor is a method when a tier computes its outcome by a different formula or from inputs other tiers do not read. Relabelled: case_completion_days (pause; tier 1 adds a date span) -> method; post_offer_payment_credit (signing; tiers credit different record amounts) -> method. Reshaped: reage_deferrals now only selects a value (3 / 2 / 0); the skips already used are netted in a plain binding `deferred = MX(0, deferrals - skip_count)`, so its tiers no longer compute. Unchanged and honest: ceilings, terms, floors, shares, hold, add-on extension, care installments, medicaid days (value selection, fall-through a tier parameter or record value); installments_at_signing (constant multiples of one installment). Floors per computation after relabel: pause 3 param + 2 method; re-age 4 + 1; recompute 4 + 1; lowering 3 + 1; re-figure 4 + 1; signing 3 + 2. C14 pairs for the two new methods: case_completion A (date span + determination days) vs B (determination days: tariff parameter only) vs C (nothing; A and B never 0 across their domains); credit A (enrolled amount of the paid account) vs B (the payment's amount) vs C (nothing) — each pair adds an input.
- R3-C2 / T0-R3-1 (two readings of the paid count after the re-age) -> the re-age now books next_due_date as the base plan_reaged event defines ("A re-age settles every missed installment the plan records, so the plan's next due date moves forward one month, on the plan's due day, for each missed installment the plan recorded." — in the standard sentence); task 0: 2025-08-15 -> 2025-09-15. Tool contract: reage_payment_plan_e7c586c0 gains next_due_date (fixed-format date, YYYY-MM-DD; no example value, no ordering word). The recompute's paid-count partial tier is re-keyed on the record alone: "the installment payment entries numbered as the highest installment number among the entries total less than the current installment" (task 0: #4 totals 75.00 < 127.24 -> 3 paid), so it reads 3 whether the next due date is 2025-08-15 or 2025-09-15 (probe rows below); its month-count clause, no longer used, was removed. The pause's start position is unchanged (MX(3, 3) = 3 after the re-age, MX(3, 2) = 3 before), so re-age and pause still commute (31 either order).
- R3-C3 / T1-R3-1 (signing order sentence names factor quantities) -> "the signing share of the signing balance is taken first, amounts taken away from it come next with the figure never falling below zero, and amounts added to it come last." Sweep of the other five order sentences: each names only baseline-defined quantities (pause period/window/allowance, longest schedules, extended/lengthened/term-limit schedules, re-figure balance and deducted share, term used, floors) and generic classes of adjustment; unchanged.
- R3-O1 (hold tier 2 reachable only after an FPL recompute) -> hold bands moved onto the FPL bands where assist sends BadgerCare Plus referrals: 50% at or below 250% (hold_fpl_near), 25% above 250% and at or below 300% (hold_fpl_far). Task 1 (249.6%) keeps 50%.
- Stale-text sweep: task traces, tracing strings, business effects, why_false/flips and dossiers re-worded for the relabels, the next due date and the hold bands; round-3 history lines marked where superseded.

## Round-4 probe table (touched reads)
| probe (round 4, touched reads) | result |
|---|---|
| recompute: gold (next due 2025-09-15 after the re-age) | 74.98 |
| recompute: same world with next due left at 2025-08-15 (pre-re-age record) | 74.98 |
| recompute: next due date empty | 74.98 |
| recompute: partial entry #4 removed (no partial) | 74.98 |
| recompute: decoy: a second entry #4 of 60.00 completes installment 4 (135.00 >= 127.24) | 78.63 |
| recompute: decoy: partial on an older number only (#2 split), #3 full | 76.76 |
| recompute: overpayment: #4 entry 300.00 | 78.63 |
| recompute: only the down payment entry (#0) recorded | 70.09 |
| signing: gold (FPL 249.6 -> hold_near 50%) | 109.13 |
| signing: FPL 280 (hold_far 25%) | 156.33 |
| signing: FPL 320 (no hold) | 203.53 |
| signing: determination received (no hold) | 203.53 |

## Round-4 final gate block (difficulty-wide, 2026-10-21T02:07:48Z)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 4: gates 7/7 green

# REWORK round 5
- Read in full: audits/render_source/payment_plan_servicing/render_r1.md (renderer scan-first STOP on plan_ext_offer_refigure; note on the pause start position). Policy revision_4 was PASS/CLEAN; edits are minimal and patched in place (base text and every quoted sentence re-verified verbatim).
- Gold moves: none. Task 0 re-age 27 (next due 2025-09-15) / pause 31 / recompute 74.98 / lowering 62.00; task 1 re-figure 74.73 booked over 48 / signing 109.13.

## Item-by-item (item -> change -> where)
- R5-1 (render_r1 blocking: re-figure books two different term_months when the offer floor binds) -> one booking stated in every place it appears and computed: standard sentence "the offer is then booked with that installment and the term used, except that when the offer floor applies it is booked with as many installments as that floor needs, the financed amount divided by the offer floor and rounded up to a whole installment"; the installment overwrite's replaced_by carries the same clause with the same rounding (and still restates the creation-time floor schedule for out-of-scope plans); the term overwrite's replaced_by now says the offer is "figured over the term this rule uses and booked with the term this rule books". New compute binding term_booked = ceil(financed / offer floor) when RND(financed / term used) is below the floor, else the term used; the tool's term_months argument is described as the number of installments the re-figured offer is booked with. Task 1: floor 20.00 does not bind, booked term 48 (tracing updated). Class sweep of all 11 replaced_by texts and every baseline sentence for a written field stated two ways or stated with no binding: the re-age's next_due_date is stated once (standard sentence) and traced as the tool argument; recompute and lowering write only the installment; pause and re-age write term_months from result; signing writes down_payment_usd from result — no other member.
- R5-2 (render_r1 note: pause start position with no next due date) -> the compute already bounds both branches at minus one (MX(-1, ...) wraps the conditional); the rule now says so in words: "a receipt date before the first due date counting as one month before it so that no installment is counted before the first due date". Probe row below (no next due date, receipt 2025-02-01: start position -1, window counts from the first due date). The case is also outside the policy's practical scope (only paid-off or cancelled plans lack a next due date).

## Round-5 probe table (including floor-binding offers)
| probe (round 5) | result |
|---|---|
| re-figure: gold (floor 20.00 not binding) | installment 74.73, term used 48, booked term 48 |
| re-figure: no open application (floor 75.00, term 24 -> 145.73) | installment 141.6, term used 24, booked term 24 |
| re-figure: floor binds: surgery account on a charge-dispute hold, case closed (1,206.00 basis -> 1,085.40 financed over 24 = 45.23 < 75.00) | installment 75.0, term used 24, booked term 15 |
| re-figure: applicant floor 20.00 with the surgery account on hold, FPL 249.6 (1,145.70 / 48 = 23.87 > 20.00, not binding) | installment 23.87, term used 48, booked term 48 |
| re-figure: floor binds exactly at a whole count: reduction raised so the financed amount is 900.00 with no open case | installment 75.0, term used 24, booked term 12 |
| pause: gold opening world (receipt after the first due date) | start position 3, window 4, paused 4, term 28 |
| pause: no next due date, receipt 2025-02-01 (more than a month before the first due date 2025-05-15) | start position -1, window 8, paused 5, term 29 |
| pause: next due 2025-08-15, receipt 2025-02-01 | start position 2, window 5, paused 5, term 29 |

## Round-5 final gate block (difficulty-wide, 2026-10-21T05:34:52Z)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Stale-text sweep: task 1 term tracing and dossier updated; no other text referred to the booking.
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 5: gates 7/7 green

# REWORK round 6
- Read in full: audits/render_source/payment_plan_servicing/render_r1.md (round-5, closed) and render_r2.md (second renderer scan-first STOP: signing order, re-age `deferred`, pause start position). Policy revision_5 was PASS/CLEAN; minimal in-place edits; replay run only with --check.
- Gold moves: none (task 0: 27 / 31 / 74.98 / 62.00; task 1: 74.73 over 48 / 109.13).

## Item-by-item (item -> change -> where)
- R6-1 (signing: hold-before-credit order fixed only inside the credit sentence; share_left a plain binding carrying the hold factor's text) -> the order sentence now fixes it by adjustment kind: "the signing share of the signing balance is taken first, a percentage held back is taken off it next and the part left is rounded half-up to the cent, an amount credited is taken away after that with the figure never falling below zero, and amounts added to it come last." The credit sentence no longer says "left after any hold"; the hold sentence no longer carries the rounding of the part left; the plain binding share_left is removed and its arithmetic sits in `result` (compute_basis = the order sentence): RND(MX(0, RND(share_due x (100 - hold) / 100) - credit) + installments).
- R6-2 (re-age: `deferred` a plain binding with only the deferral factor's text) -> `deferred` is now one of reage_deferrals' bindings (df_fpl, deferrals, deferred); the deferral sentence states "less the skips already used on the plan (skip_count) but never fewer than none".
- R6-3 (pause: no-next-due-date branch of start_idx without the minus-one floor) -> written with the floor on both branches explicitly: (MX(-1, MX(months to receipt, months to next due - 1)) if next due else MX(-1, months to receipt)) if receipt else 0. (The previous expression already wrapped both branches — MX(-1, A if c else B) — but the explicit form removes the misreading.)
- Class sweeps over all six policies: (a) plain bindings whose only source text is one factor's sentence — scanned every non-factor binding's compute_basis against factor sentences: only share_left and deferred were members (both fixed); the rest quote the open-application definition or a baseline sentence. (b) factor sentences naming another factor's effect or quantity — fixed "left after any hold" (signing credit), "longer again" (pause completion days), "allows as well" (pause and re-age balance ceilings), "allows too" (re-age record ceiling), "Such an offer also" (re-figure balance term, now restates "An offer that carries the tier's max_term_months"). (c) rule-stated floors/clamps missing in a compute branch — pause start position (fixed); lowering waiting count (minus-one and zero floors in its only month branch), pause window branches (MX(0, ..) / MN with MX(0, ..)), recompute and lowering MX(1, ..), signing MX(0, ..), deferrals MX(0, ..) all present.

## Round-6 probe table (touched reads)
| probe (round 6, touched reads) | result |
|---|---|
| signing: gold | share 188.8, hold 50.0%, credit 60.0, result 109.13 |
| signing: credit 150.00 above the held share (zero floor before the installment) | share 188.8, hold 50.0%, credit 150.0, result 74.73 |
| signing: no referral hold (determination received): credit taken from the whole share | share 188.8, hold 0%, credit 60.0, result 203.53 |
| signing: half-cent part left (share 188.81 -> 94.405 rounds up) | share 188.81, hold 50.0%, credit 60.0, result 109.14 |
| re-age: gold (skip_count 0) | deferrals 3, deferred 3, term 27 |
| re-age: skip_count 1 | deferrals 3, deferred 2, term 26 |
| re-age: skip_count 4 (more than the allowance: never fewer than none) | deferrals 3, deferred 0, term 24 |
| re-age: absent case | deferrals 0, deferred 0, term 24 |
| pause: gold opening world | start position 3, window 4, paused 4 |
| pause: no next due date, receipt 2025-03-20 (two months before the first due date) | start position -1, window 8, paused 5 |
| pause: next due 2025-08-15, receipt 2025-03-20 | start position 2, window 5, paused 5 |

## Round-6 final gate block (difficulty-wide, 2026-10-21T19:16:55Z; replay with --check)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Stale-text sweep: task 1 signing trace/tracing and dossier updated; no task text quoted the removed phrases.
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 6: gates 7/7 green

# REWORK round 7
- Read in full: audits/policy_task/payment_plan_servicing/_difficulty.md, 0.md, 1.md through revision_6 (VERDICT revision_6: task0=RED task1=PASS charter=R6-C1; observation R6-O1). Minimal in-place edits to plan.extended.yaml only; tasks/0.json and tasks/1.json byte-identical (sha256 344635286eee / 2a711ba9efef before and after); replay run only with --check.
- Gold moves: none (task 0: re-age 27 with next due 2025-09-15 / pause 31 / recompute 74.98 / lowering 62.00; task 1: re-figure 74.73 booked over 48 / signing 109.13).

## Item-by-item (item -> change -> where)
- R6-C1 / T0-R6-1 (lowering's plain `receipt` used only by waiting_installments, XF A4) -> `receipt` is now a binding of waiting_installments (receipt, aw_status, aw_docs_due, waited); its defining words moved into that factor's sentence ("... for the time the open application has been waiting since its receipt date, which is that case's application date: ..."), and the lowering's open-application sentence no longer defines a receipt date (now the shared definition without it, as in the recompute, re-figure and signing). Same shape as the re-age (mv_receipt inside moved_installments); the pause keeps receipt as a baseline input (its start position and standard window read it).
- R6-O1 (re-figure term_used kept an unstated one-installment floor) -> dropped: term_used = MN(screening term, balance term), exactly "the term used is the shorter of the terms allowed"; both terms are the offer's term_months or 48/60, never below one (probe: an offer of term 1 gives term used 1).
- Mechanical sweep (all six policies) for plain bindings not read by the baseline/result chain (result traced with every factor at its baseline): only the shared open-application selections (case_submitted, case_pending, open_case — each consumed by two or more factors, XF A2) and the re-figure's term_booked (a baseline quantity the standard sentence states and the tool books as term_months, not part of the installment) remain; no plain binding is consumed by a single factor any more.

## Round-7 probe table (touched reads)
| probe (round 7, touched reads) | result |
|---|---|
| lowering: gold handling state | receipt 2025-09-10, waiting 3, result 62.0 |
| lowering: absent case | receipt None, waiting 0, result 74.98 |
| lowering: decoy approved case listed first | receipt 2025-09-10, waiting 3, result 62.0 |
| lowering: receipt 2025-03-01 before the first due date | receipt 2025-03-01, waiting 7, result 57.57 |
| lowering: submitted case (elapsed-time count) | receipt 2025-09-10, waiting 2, result 63.22 |
| re-figure: gold | term used 48, booked 48, installment 74.73 |
| re-figure: offer term 1 (smallest term an offer can carry) | term used 1, booked 1, installment 3587.2 |

## Round-7 final gate block (difficulty-wide, 2026-10-21T19:37:27Z; replay with --check)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Stale-text sweep: no task or worklog text quoted the moved receipt words or the dropped floor; task files unchanged.
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 7: gates 7/7 green

# REWORK round 8
- Read in full: audits/policy_task/payment_plan_servicing/_difficulty.md, 0.md, 1.md through revision_7 (VERDICT revision_7: task0=RED task1=PASS charter=R7-C1). Edit in plan.extended.yaml only; tasks/0.json and tasks/1.json byte-identical (sha256 344635286eee / 2a711ba9efef); replay run only with --check.
- Gold moves: none (task 0: re-age 27 with next due 2025-09-15 / pause 31 / recompute 74.98 / lowering 62.00; task 1: re-figure 74.73 booked over 48 / signing 109.13).

## Item-by-item
- R7-C1 / T0-R7-1 (re-age: the shared open-application sentence defined the receipt date, read only by moved_installments) -> the re-age's shared sentence is now the definition without the receipt clause ("... a submitted case being taken first."), and the moved-installments sentence defines it where it is read: "when there are no such entries and the open application was received after the plan's next due date (its receipt date being that case's application date), ...".

## Exhaustive definition sweep (all six policies)
Rules applied: a quantity read by exactly one factor is defined in that factor's own sentence; a quantity the baseline reads is defined in the baseline (rule); shared selections read by two or more factors are defined once in the shared sentence. Readers are traced through plain bindings, including each factor's standard (baseline) expression.

### A. Every compute binding: where it is defined, who reads it (generated mechanically from plan.extended.yaml)
| policy | binding | owner | defined in | read by |
|---|---|---|---|---|
| assistance_pause | case_submitted | plain | baseline | baseline,baseline (standard window),case_completion_days,medicaid_screening_days,pause_window,paused_screening_ceiling |
| assistance_pause | case_pending | plain | baseline | baseline,baseline (standard window),case_completion_days,medicaid_screening_days,pause_window,paused_screening_ceiling |
| assistance_pause | open_case | plain | baseline | baseline,baseline (standard window),case_completion_days,medicaid_screening_days,pause_window,paused_screening_ceiling |
| assistance_pause | receipt | plain | baseline | baseline,baseline (standard window),pause_window |
| assistance_pause | start_idx | plain | baseline | baseline (standard window),pause_window |
| assistance_pause | md_refs | medicaid_screening_days | factor:medicaid_screening_days | medicaid_screening_days |
| assistance_pause | md_dets | medicaid_screening_days | factor:medicaid_screening_days | medicaid_screening_days |
| assistance_pause | md_days | medicaid_screening_days | factor:medicaid_screening_days | baseline |
| assistance_pause | dc_status | case_completion_days | factor:case_completion_days | case_completion_days |
| assistance_pause | dc_docs_due | case_completion_days | factor:case_completion_days | case_completion_days |
| assistance_pause | dc_days | case_completion_days | factor:case_completion_days | baseline |
| assistance_pause | allowance | plain | baseline | baseline |
| assistance_pause | win_status | pause_window | factor:pause_window | pause_window |
| assistance_pause | win_docs_due | pause_window | factor:pause_window | pause_window |
| assistance_pause | window | pause_window | factor:pause_window | baseline |
| assistance_pause | paused | plain | baseline | baseline |
| assistance_pause | cf_fpl | paused_screening_ceiling | factor:paused_screening_ceiling | paused_screening_ceiling |
| assistance_pause | cf_cap | paused_screening_ceiling | factor:paused_screening_ceiling | baseline |
| assistance_pause | cb_bal | paused_balance_ceiling | factor:paused_balance_ceiling | paused_balance_ceiling |
| assistance_pause | cb_cap | paused_balance_ceiling | factor:paused_balance_ceiling | baseline |
| reage_schedule | case_submitted | plain | shared:A financial assistance application of th | moved_installments,reage_deferrals,reaged_screening_ceiling |
| reage_schedule | case_pending | plain | shared:A financial assistance application of th | moved_installments,reage_deferrals,reaged_screening_ceiling |
| reage_schedule | open_case | plain | shared:A financial assistance application of th | moved_installments,reage_deferrals,reaged_screening_ceiling |
| reage_schedule | mv_no | moved_installments | factor:moved_installments | moved_installments |
| reage_schedule | mv_part_n | moved_installments | factor:moved_installments | moved_installments |
| reage_schedule | mv_part_sum | moved_installments | factor:moved_installments | moved_installments |
| reage_schedule | mv_receipt | moved_installments | factor:moved_installments | moved_installments |
| reage_schedule | moved | moved_installments | factor:moved_installments | baseline |
| reage_schedule | df_fpl | reage_deferrals | factor:reage_deferrals | reage_deferrals |
| reage_schedule | deferrals | reage_deferrals | factor:reage_deferrals | reage_deferrals |
| reage_schedule | cf_fpl | reaged_screening_ceiling | factor:reaged_screening_ceiling | reaged_screening_ceiling |
| reage_schedule | cf_cap | reaged_screening_ceiling | factor:reaged_screening_ceiling | baseline |
| reage_schedule | cb_bal | reaged_balance_ceiling | factor:reaged_balance_ceiling | reaged_balance_ceiling |
| reage_schedule | cb_cap | reaged_balance_ceiling | factor:reaged_balance_ceiling | baseline |
| reage_schedule | ch_paid | reaged_record_ceiling | factor:reaged_record_ceiling | reaged_record_ceiling |
| reage_schedule | ch_cap | reaged_record_ceiling | factor:reaged_record_ceiling | baseline |
| reage_schedule | deferred | reage_deferrals | factor:reage_deferrals | baseline |
| addon_recompute | case_submitted | plain | shared:A financial assistance application of th | recompute_floor,recomputed_screening_ceiling |
| addon_recompute | case_pending | plain | shared:A financial assistance application of th | recompute_floor,recomputed_screening_ceiling |
| addon_recompute | open_case | plain | shared:A financial assistance application of th | recompute_floor,recomputed_screening_ceiling |
| addon_recompute | sched_now | plain | baseline | baseline |
| addon_recompute | missed_now | plain | baseline | baseline |
| addon_recompute | cf_fpl | recomputed_screening_ceiling | factor:recomputed_screening_ceiling | recomputed_screening_ceiling |
| addon_recompute | cf_cap | recomputed_screening_ceiling | factor:recomputed_screening_ceiling | baseline |
| addon_recompute | ex_n | addon_frequency_extension | factor:addon_frequency_extension | addon_frequency_extension |
| addon_recompute | ext | addon_frequency_extension | factor:addon_frequency_extension | baseline |
| addon_recompute | cl_date | latest_addon_care | factor:latest_addon_care | latest_addon_care |
| addon_recompute | cl_enc | latest_addon_care | factor:latest_addon_care | latest_addon_care |
| addon_recompute | cl_var | latest_addon_care | factor:latest_addon_care | latest_addon_care |
| addon_recompute | cls | latest_addon_care | factor:latest_addon_care | baseline |
| addon_recompute | pd_no | installments_paid_count | factor:installments_paid_count | installments_paid_count |
| addon_recompute | pd_part_sum | installments_paid_count | factor:installments_paid_count | installments_paid_count |
| addon_recompute | pd_part_n | installments_paid_count | factor:installments_paid_count | installments_paid_count |
| addon_recompute | pd_all | installments_paid_count | factor:installments_paid_count | baseline (standard paid),installments_paid_count |
| addon_recompute | pd_total | installments_paid_count | factor:installments_paid_count | installments_paid_count |
| addon_recompute | paid | installments_paid_count | factor:installments_paid_count | baseline |
| addon_recompute | fl_fpl | recompute_floor | factor:recompute_floor | recompute_floor |
| addon_recompute | floor | recompute_floor | factor:recompute_floor | baseline |
| addon_recompute | remaining | plain | baseline | baseline |
| lowest_installment | case_submitted | plain | shared:A financial assistance application of th | lowered_term_limit,lowering_floor,lowering_share,waiting_installments |
| lowest_installment | case_pending | plain | shared:A financial assistance application of th | lowered_term_limit,lowering_floor,lowering_share,waiting_installments |
| lowest_installment | open_case | plain | shared:A financial assistance application of th | lowered_term_limit,lowering_floor,lowering_share,waiting_installments |
| lowest_installment | receipt | waiting_installments | factor:waiting_installments | waiting_installments |
| lowest_installment | lo_bal | plain | baseline | baseline |
| lowest_installment | remaining_now | plain | baseline | baseline |
| lowest_installment | ls_fpl | lowering_share | factor:lowering_share | lowering_share |
| lowest_installment | share | lowering_share | factor:lowering_share | baseline |
| lowest_installment | lf_fpl | lowering_floor | factor:lowering_floor | lowering_floor |
| lowest_installment | lfloor | lowering_floor | factor:lowering_floor | baseline |
| lowest_installment | lt_fpl | lowered_term_limit | factor:lowered_term_limit | lowered_term_limit |
| lowest_installment | limit | lowered_term_limit | factor:lowered_term_limit | baseline |
| lowest_installment | aw_status | waiting_installments | factor:waiting_installments | waiting_installments |
| lowest_installment | aw_docs_due | waiting_installments | factor:waiting_installments | waiting_installments |
| lowest_installment | waited | waiting_installments | factor:waiting_installments | baseline |
| lowest_installment | paid_entries | plain | baseline | baseline |
| lowest_installment | lengthened | plain | baseline | baseline |
| lowest_installment | longest | plain | baseline | baseline |
| offer_refigure | case_submitted | plain | shared:A financial assistance application of th | deducted_down_share,offer_floor,offer_screening_term |
| offer_refigure | case_pending | plain | shared:A financial assistance application of th | deducted_down_share,offer_floor,offer_screening_term |
| offer_refigure | open_case | plain | shared:A financial assistance application of th | deducted_down_share,offer_floor,offer_screening_term |
| offer_refigure | rf_bh | refigure_balance | factor:refigure_balance | refigure_balance |
| offer_refigure | rf_bhe | refigure_balance | factor:refigure_balance | refigure_balance |
| offer_refigure | rf_br | refigure_balance | factor:refigure_balance | refigure_balance |
| offer_refigure | rf_bt | refigure_balance | factor:refigure_balance | baseline (standard rf_basis),refigure_balance |
| offer_refigure | rf_basis | refigure_balance | factor:refigure_balance | baseline,baseline (booked term) |
| offer_refigure | dd_fpl | deducted_down_share | factor:deducted_down_share | deducted_down_share |
| offer_refigure | dd_pct | deducted_down_share | factor:deducted_down_share | baseline,baseline (booked term) |
| offer_refigure | tf_fpl | offer_screening_term | factor:offer_screening_term | offer_screening_term |
| offer_refigure | tf_term | offer_screening_term | factor:offer_screening_term | baseline,baseline (booked term) |
| offer_refigure | tb_bal | offer_balance_term | factor:offer_balance_term | offer_balance_term |
| offer_refigure | tb_term | offer_balance_term | factor:offer_balance_term | baseline,baseline (booked term) |
| offer_refigure | of_fpl | offer_floor | factor:offer_floor | offer_floor |
| offer_refigure | ofloor | offer_floor | factor:offer_floor | baseline,baseline (booked term) |
| offer_refigure | financed | plain | baseline | baseline,baseline (booked term) |
| offer_refigure | term_used | plain | baseline | baseline,baseline (booked term) |
| offer_refigure | term_booked | plain | baseline | baseline (booked term) |
| signing_down_payment | case_submitted | plain | shared:A financial assistance application of th | screening_hold,signing_share |
| signing_down_payment | case_pending | plain | shared:A financial assistance application of th | screening_hold,signing_share |
| signing_down_payment | open_case | plain | shared:A financial assistance application of th | screening_hold,signing_share |
| signing_down_payment | sg_fpl | signing_share | factor:signing_share | signing_share |
| signing_down_payment | sg_pct | signing_share | factor:signing_share | baseline |
| signing_down_payment | sb_bh | signing_balance | factor:signing_balance | signing_balance |
| signing_down_payment | sb_bhe | signing_balance | factor:signing_balance | signing_balance |
| signing_down_payment | sb_br | signing_balance | factor:signing_balance | signing_balance |
| signing_down_payment | sb_bt | signing_balance | factor:signing_balance | baseline (standard sb_basis),signing_balance |
| signing_down_payment | sb_basis | signing_balance | factor:signing_balance | baseline |
| signing_down_payment | hd_refs | screening_hold | factor:screening_hold | screening_hold |
| signing_down_payment | hd_dets | screening_hold | factor:screening_hold | screening_hold |
| signing_down_payment | hd_fpl | screening_hold | factor:screening_hold | screening_hold |
| signing_down_payment | hold_pct | screening_hold | factor:screening_hold | baseline |
| signing_down_payment | cr_date | post_offer_payment_credit | factor:post_offer_payment_credit | post_offer_payment_credit |
| signing_down_payment | cr_enc | post_offer_payment_credit | factor:post_offer_payment_credit | post_offer_payment_credit |
| signing_down_payment | cr_amt | post_offer_payment_credit | factor:post_offer_payment_credit | post_offer_payment_credit |
| signing_down_payment | cr_enrolled | post_offer_payment_credit | factor:post_offer_payment_credit | post_offer_payment_credit |
| signing_down_payment | credit | post_offer_payment_credit | factor:post_offer_payment_credit | baseline |
| signing_down_payment | first_gap | installments_at_signing | factor:installments_at_signing | installments_at_signing |
| signing_down_payment | first_part | installments_at_signing | factor:installments_at_signing | baseline |
| signing_down_payment | share_due | plain | baseline | baseline |

Result: no flag — every factor binding is defined in its own factor's sentence; every plain binding is either a shared selection read by two or more factors or a baseline quantity defined in the baseline sentences (pause receipt and start position are read by the standard window and the baseline chain; re-figure term_booked is the baseline's booked term).

### B. Every defined term in rule text: the sentence that carries the defining words, and its owner
| defined term | policy | sentence that defines it | sentence owner |
|---|---|---|---|
| open application (case status, submitted first) | assistance_pause | A financial assistance application of the patient is open wh... | baseline |
| open application (case status, submitted first) | reage_schedule | A financial assistance application of the patient is open wh... | shared (case_submitted,case_pending,open_case) |
| open application (case status, submitted first) | addon_recompute | A financial assistance application of the patient is open wh... | shared (case_submitted,case_pending,open_case) |
| open application (case status, submitted first) | lowest_installment | A financial assistance application of the patient is open wh... | shared (case_submitted,case_pending,open_case) |
| open application (case status, submitted first) | offer_refigure | A financial assistance application of the patient is open wh... | shared (case_submitted,case_pending,open_case) |
| open application (case status, submitted first) | signing_down_payment | A financial assistance application of the patient is open wh... | shared (case_submitted,case_pending,open_case) |
| receipt date = application date | assistance_pause | A financial assistance application of the patient is open wh... | baseline |
| receipt date = application date | reage_schedule | The installments moved follow what has been paid toward them... | factor moved_installments |
| receipt date = application date | lowest_installment | The lengthened schedule also takes in installments for the t... | factor waiting_installments |
| whole-month counting convention | assistance_pause | Whole months between two dates are counted the calendar way:... | baseline |
| whole-month counting convention | assistance_pause | The pause window follows the open case's status: for a case ... | factor pause_window |
| whole-month counting convention | reage_schedule | The installments moved follow what has been paid toward them... | factor moved_installments |
| whole-month counting convention | addon_recompute | The extension follows how often care has been added to the p... | factor addon_frequency_extension |
| whole-month counting convention | lowest_installment | The lengthened schedule also takes in installments for the t... | factor waiting_installments |
| plan/offer ledger balance | assistance_pause | The longest paused schedule may run past the tier's max_term... | factor paused_balance_ceiling |
| plan/offer ledger balance | reage_schedule | The longest re-aged schedule may run past the tier's max_ter... | factor reaged_balance_ceiling |
| plan/offer ledger balance | lowest_installment | As standard, the lowest installment a patient may set is the... | baseline |
| plan/offer ledger balance | offer_refigure | The re-figure balance follows what has happened to the enrol... | factor refigure_balance |
| plan/offer ledger balance | offer_refigure | An offer that carries the tier's max_term_months runs only a... | factor offer_balance_term |
| plan/offer ledger balance | signing_down_payment | The signing balance follows what has happened to the enrolle... | factor signing_balance |
| add-on enrollment entry | addon_recompute | The extension follows how often care has been added to the p... | factor addon_frequency_extension |
| add-on enrollment entry | addon_recompute | The extended schedule also gains installments for the care t... | factor latest_addon_care |
| installment payment entries numbered 1 or more | reage_schedule | The longest re-aged schedule may run past the tier's max_ter... | factor reaged_record_ceiling |
| installment payment entries numbered 1 or more | addon_recompute | As standard, the remaining schedule is the plan's current nu... | baseline |
| installment payment entries numbered 1 or more | addon_recompute | The installments already paid are counted by how they were p... | factor installments_paid_count |
| installment payment entries numbered 1 or more | lowest_installment | The longest schedule the change may reach is the smaller of ... | baseline |
| number of the installment due on the next due date | reage_schedule | The installments moved follow what has been paid toward them... | factor moved_installments |
| BadgerCare referral unanswered | assistance_pause | While BadgerCare Plus is screening the patient the pause per... | factor medicaid_screening_days |
| BadgerCare referral unanswered | signing_down_payment | While BadgerCare Plus is screening the patient, part of the ... | factor screening_hold |
| remaining schedule as last computed | lowest_installment | The longest schedule the change may reach is the smaller of ... | baseline |
| considered installments | assistance_pause | Due dates fall on the plan's due day each month from the fir... | baseline |

Result: the receipt date is defined in the pause baseline (read by the baseline), in the re-age moved-installments sentence and in the lowering waiting sentence (each its only reader); the month-counting convention is stated by the pause baseline and by each factor that counts months (pause window, moved installments, add-on frequency extension, waiting installments); ledger balances, add-on entries, numbered entries and the BadgerCare referral state are defined in each sentence that reads them (baseline or factor). No defining clause of a single-factor quantity sits outside that factor.

## Round-8 final gate block (difficulty-wide, 2026-10-21T20:17:37Z; replay with --check)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Stale-text sweep: no task or worklog text quoted the moved receipt clause; task files unchanged.
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 8: gates 7/7 green

# REWORK round 9 (seed only)
- Read in full: audits/policy_kb/payment_plan_servicing/_difficulty.md, 0.md, 1.md (revision_2: task0=PASS task1=PASS kb=CLEAN src=S1,S2), and the published assist and encounter docs the items cite (docs/assist: application completeness and documents, required documents by tier, BadgerCare Plus screening, missing-information notice contract and due date; encounter bill hold, discounts, statement cycle). audits/runtime_context/ not read.
- plan.extended.yaml and task_tools.py byte-identical (503da59afb88 / 3b987caeb498); tasks/1.json byte-identical (2a711ba9efef); tasks/0.json re-seeded (initial_state and db_closure edited identically; replay run only with --check).
- Gold moves: none. Task 0 keeps the state its rules read (case pending_documents since a 2025-11-18 notice, documents due 2025-12-18, BadgerCare Plus referral of 2025-10-10 unanswered, receipt 2025-09-10): re-age 27 / next due 2025-09-15, pause 31, recompute 74.98, lowering 62.00. Task 1: 74.73 over 48 / 109.13.

## Item-by-item
- S1 (task 0 assist history not producible: the case was complete on 2025-10-08, so the 2025-11-18 pay-stub request and notice could not be issued) -> re-seeded to an assist-producible history with the same final case state: pay stubs and proof of residency uploaded with the 2025-09-10 portal application (both RECEIVED 09-10); pay stubs ACCEPTED 09-15; BadgerCare Plus referral 10-10; proof of residency REJECTED 2025-11-17; missing-information notice 2025-11-18 requesting proof of residency (the first REQUESTED entry of that type; proof of income not requested since pay stubs were accepted), moving the case to pending_documents with documents due 2025-11-18 + 30 = 2025-12-18. Removed: the 09-15 residency request and notice and the 10-06/10-08 residency receipt and acceptance (rows 7415496c and f6757628 reused with new dates/statuses, 143021a6 now requests PROOF_OF_RESIDENCY, dbae375f and 35c178ae dropped). The persona line ("they have asked you for more paperwork since") matches the 2025-11-18 request. Task text swept: the case-documents read objective and the dossier now describe this history; no scored figure rested on the removed rows' dates.
- S2 (task 0 ED account lacked its cycle-2 summary statement of 2025-03-26) -> added SUMMARY_STATEMENT cycle 2 on 2025-03-26 (first statement 02-24 + 30 days; the plan offered 03-24 was unsigned until 03-27, so the balance was still on standard statements), as task 1 treats its unsigned offer (cycle 2 on 10-12). No plan computation reads statements.

## Bounded exhaustive pass — every other-category row in both worlds
### Encounter rows (generated against the encounter charter's bill hold days, uninsured discounts and 30-day statement cycle, the plan's signing and enrollment dates and each account's ledger)
| world / account | row | rule test | result |
|---|---|---|---|
| 0 Emergency Department V 8ab336e5 | final bill 2025-02-19 4860.00; discount 2187.00 | charges 4860.00; bill_hold_days 4 -> 2025-02-19; 45.0% | ok |
| 0 Emergency Department V 8ab336e5 | statement cycle 1 2025-02-24 | 30-day cycle; stops once enrolled on a signed plan (2025-03-27) | ok |
| 0 Emergency Department V 8ab336e5 | statement cycle 2 2025-03-26 | 30-day cycle; stops once enrolled on a signed plan (2025-03-27) | ok |
| 0 Emergency Department V 8ab336e5 | next statement would be 2025-04-25 | enrolled 2025-03-24, plan signed 2025-03-27, frozen 2025-11-20 | ok (none owed) |
| 0 Emergency Department V 8ab336e5 | payment_posted 2025-03-27 339.30 PAYMENT_PLAN_INSTALLMENT | equals the plan's installment-paid row of the same date and amount; applied oldest service start first (ED) | ok |
| 0 Emergency Department V 8ab336e5 | payment_posted 2025-05-15 127.24 PAYMENT_PLAN_INSTALLMENT | equals the plan's installment-paid row of the same date and amount; applied oldest service start first (ED) | ok |
| 0 Emergency Department V 8ab336e5 | payment_posted 2025-06-15 127.24 PAYMENT_PLAN_INSTALLMENT | equals the plan's installment-paid row of the same date and amount; applied oldest service start first (ED) | ok |
| 0 Emergency Department V 8ab336e5 | payment_posted 2025-07-15 127.24 PAYMENT_PLAN_INSTALLMENT | equals the plan's installment-paid row of the same date and amount; applied oldest service start first (ED) | ok |
| 0 Emergency Department V 8ab336e5 | payment_posted 2025-08-25 75.00 PAYMENT_PLAN_INSTALLMENT | equals the plan's installment-paid row of the same date and amount; applied oldest service start first (ED) | ok |
| 0 Emergency Department V 8ab336e5 | account balance 1876.98, status patient_due, first statement 2025-02-24, final bill 2025-02-19 | ledger 1876.98; first statement row 2025-02-24 | ok |
| 0 Outpatient Diagnostic  0a1a27bc | final bill 2025-03-07 1600.00; discount 880.00 | charges 1600.00; bill_hold_days 4 -> 2025-03-07; 55.0% | ok |
| 0 Outpatient Diagnostic  0a1a27bc | statement cycle 1 2025-03-11 | 30-day cycle; stops once enrolled on a signed plan (2025-03-27) | ok |
| 0 Outpatient Diagnostic  0a1a27bc | next statement would be 2025-04-10 | enrolled 2025-03-24, plan signed 2025-03-27, frozen 2025-11-20 | ok (none owed) |
| 0 Outpatient Diagnostic  0a1a27bc | account balance 720.00, status patient_due, first statement 2025-03-11, final bill 2025-03-07 | ledger 720.00; first statement row 2025-03-11 | ok |
| 0 Recurring Outpatient T bfb52d4d | final bill 2025-09-05 380.00; discount 171.00 | charges 380.00; bill_hold_days 5 -> 2025-09-05; 45.0% | ok |
| 0 Recurring Outpatient T bfb52d4d | final bill 2025-10-05 380.00; discount 171.00 | charges 380.00; bill_hold_days 5 -> 2025-10-05; 45.0% | ok |
| 0 Recurring Outpatient T bfb52d4d | final bill 2025-11-05 380.00; discount 171.00 | charges 380.00; bill_hold_days 5 -> 2025-11-05; 45.0% | ok |
| 0 Recurring Outpatient T bfb52d4d | statement cycle 1 2025-09-08 | 30-day cycle; stops once enrolled on a signed plan (2025-03-27) | ok |
| 0 Recurring Outpatient T bfb52d4d | next statement would be 2025-10-08 | enrolled 2025-09-09, plan signed 2025-03-27, frozen 2025-11-20 | ok (none owed) |
| 0 Recurring Outpatient T bfb52d4d | account balance 627.00, status patient_due, first statement 2025-09-08, final bill 2025-11-05 | ledger 627.00; first statement row 2025-09-08 | ok |
| 1 Outpatient Surgery Acc a3ce437a | final bill 2025-09-08 5360.00; discount 2680.00 | charges 5360.00; bill_hold_days 5 -> 2025-09-08; 50.0% | ok |
| 1 Outpatient Surgery Acc a3ce437a | statement cycle 1 2025-09-12 | 30-day cycle; stops once enrolled on a signed plan (None) | ok |
| 1 Outpatient Surgery Acc a3ce437a | statement cycle 2 2025-10-12 | 30-day cycle; stops once enrolled on a signed plan (None) | ok |
| 1 Outpatient Surgery Acc a3ce437a | next statement would be 2025-11-11 | enrolled 2025-10-06, plan signed None, frozen 2025-10-14 | ok (none owed) |
| 1 Outpatient Surgery Acc a3ce437a | charge_credited 2025-10-09 220.00 DUPLICATE_CHARGE | inquiry 8d1e7860 (2025-10-08) on the duplicated line; credited, inquiry RESOLVED_CREDITED | ok |
| 1 Outpatient Surgery Acc a3ce437a | adjustment_posted 2025-10-09 110.00 CHARGE_CORRECTION_ADJUSTMENT | 220.00 x (1 - 50% uninsured discount); plan reduction of the same amount and date | ok |
| 1 Outpatient Surgery Acc a3ce437a | account balance 2570.00, status patient_due, first statement 2025-09-12, final bill 2025-09-08 | ledger 2570.00; first statement row 2025-09-12 | ok |
| 1 Outpatient Diagnostic  6dbef1c6 | final bill 2025-09-23 2680.00; discount 1474.00 | charges 2680.00; bill_hold_days 4 -> 2025-09-23; 55.0% | ok |
| 1 Outpatient Diagnostic  6dbef1c6 | statement cycle 1 2025-09-26 | 30-day cycle; stops once enrolled on a signed plan (None) | ok |
| 1 Outpatient Diagnostic  6dbef1c6 | next statement would be 2025-10-26 | enrolled 2025-10-06, plan signed None, frozen 2025-10-14 | ok (none owed) |
| 1 Outpatient Diagnostic  6dbef1c6 | payment_posted 2025-10-10 60.00 PORTAL_CARD | designated payment on the MRI account (below card maximum); after the offer date | ok |
| 1 Outpatient Diagnostic  6dbef1c6 | account balance 1146.00, status patient_due, first statement 2025-09-26, final bill 2025-09-23 | ledger 1146.00; first statement row 2025-09-26 | ok |

### Assistance rows (against the published assist docs as of each posting date)
| world / row | row | rule test (published assist docs) | result |
|---|---|---|---|
| 0 case 4a312d59 | portal application 2025-09-10; household 3, income 50,000.00, FPL 187.6 -> Riverbend Full Charity Care (0-200% FPL) | channel allowed on every tier; 50,000 / 26,650 (2025 HHS, household 3) = 187.6%; inside the 240-day application period of every account's first statement (02-24, 03-11, 09-08) | ok |
| 0 6c8a47d0 | PAY_STUBS_LAST_90_DAYS RECEIVED 2025-09-10 | uploaded with the application; one entry per status (7.3) | ok |
| 0 7415496c (re-seeded) | PROOF_OF_RESIDENCY RECEIVED 2025-09-10 | uploaded with the application; Full Charity requires proof of income and proof of residency | ok |
| 0 2b104531 | PAY_STUBS_LAST_90_DAYS ACCEPTED 2025-09-15 | proof of income satisfied by any accepted proof-of-income document | ok |
| 0 00453238 | MEDICAID_SCREENING_REFERRAL 2025-10-10 | Full Charity requires BadgerCare Plus screening before approval; determination notice due within 45 days (2025-11-24), none received by 2025-11-20 | ok |
| 0 f6757628 (re-seeded) | PROOF_OF_RESIDENCY REJECTED 2025-11-17 | one REJECTED entry for the type (7.3); the application is incomplete again (no residency accepted) | ok |
| 0 143021a6 (re-seeded) | PROOF_OF_RESIDENCY REQUESTED 2025-11-18 | notice contract: residency REQUESTED when no proof of residency has been accepted; income NOT_REQUESTED (pay stubs accepted); first REQUESTED entry of the type (7.3) | ok |
| 0 46f78010 | MISSING_INFORMATION_NOTICE 2025-11-18 (English) | 7.2: an incomplete application receives the notice; case moves to pending_documents; due = notice date + 30 response days = 2025-12-18 (case fields status pending_documents, documents_due_date 2025-12-18) | ok |
| 0 removed rows | the 2025-09-15 residency request + notice and the 2025-10-06/10-08 residency receipt/acceptance | they made the case complete on 2025-10-08, which left the 2025-11-18 request unproducible (S1) | removed |
| 1 case dd3dc30d | mail application 2025-10-02; household 2, income 52,800.00, FPL 249.6 -> 80% Charity Discount (201-250% FPL) | 52,800 / 21,150 = 249.6%; inside the application period | ok |
| 1 FEDERAL_TAX_RETURN RECEIVED 10-02, ACCEPTED 10-07 | proof of income | accepted proof-of-income document | ok |
| 1 PROOF_OF_RESIDENCY REQUESTED, MEDICAID_DETERMINATION_NOTICE REQUESTED, MISSING_INFORMATION_NOTICE 2025-10-07 | 80% tier requires income, residency and the BadgerCare Plus determination notice; income accepted -> not requested; due 2025-11-06 = 10-07 + 30 | ok |
| 1 MEDICAID_SCREENING_REFERRAL 2025-10-07 | 80% tier requires screening; deadline 2025-11-21 | ok |

Result: no further miss in either world (task 0: 3 accounts, 37 encounter rows, 1 case, 7 assist rows; task 1: 2 accounts, 19 encounter rows, 1 inquiry, 1 case, 6 assist rows).

## Round-9 final gate block (difficulty-wide, 2026-10-22T00:55:20Z; replay with --check)
    check_extended: EXTENDED OK
    check_task_tools: TASK TOOL CONTRACT OK
    replay_tasks: REPLAY OK
    check_solvability: SOLVABILITY OK
    check_compute: COMPUTE OK
    check_grounding: GROUNDING OK
    check_cross_fire: SCOPE OK
- Scratch in /tmp/payment_plan_servicing_0073/ removed after this run.

REWORK round 9: gates 7/7 green
