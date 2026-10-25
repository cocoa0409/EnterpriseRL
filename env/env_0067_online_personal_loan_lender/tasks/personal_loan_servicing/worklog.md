# worklog — personal_loan_servicing (env_0067), M=2

## Step 0 — pre-check and draws
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/loan.yaml, db_schema.json,
  share_tools.py, audits/render_source/XF_recipe.md.
- draw_counts.py --tasks 2: task 0 {prereq 1, factors [6,4]}; task 1 {prereq 3, factors [6,4,4,5]}.
- Owner doctrine (blueprint): service actions are the agent's; the borrower's own writes are authorizing a new
  recurring debit (AutoPay enrollment) and consenting to a refinance (refinance application). Every tree therefore
  carries one of those two user writes; they are split across the two tasks.
- Base thinness noted: fee, quote and waiver quantities in the base are near-formulaic; the extended layer adds
  Larkspur servicing conventions/programs, each declared against the base sentence it replaces.

## Task 0 — closed
- Policies loan_ext_refi_payoff_quote (4 factors) and loan_ext_refi_application (6 factors); tools
  issue_payoff_quote_88f1b45e (agent) and submit_refinance_application_9ec5cb64 (user).
- Revision: quote tool first named issue_refinance_payoff_quote_*; base dedup gate one_quote_per_day_purpose binds
  quote_purpose as an action argument -> renamed issue_payoff_quote_88f1b45e with a quote_purpose enum (fresh tool, not
  yet referenced anywhere). Propagated to yaml/task/scratch.
- Revision: replay gate flagged 13 unread rows and '' foreign keys -> ledger read by customer, bank accounts read,
  Credit Builder ledger dropped (Credit Builder credit now decided by the holding: matured status / active with 0.00
  past due), empty fields dropped. Re-run: REPLAY OK (87/87).
- Gate run (task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Figures: quote 6402.81 (all-baseline 6012.47); amount financed 6531 (all-baseline 6601); per-factor figures in 0.json.

## Task 1 — closed
- Policies loan_ext_late_fee (5), loan_ext_returned_fee (4), loan_ext_autopay_enroll (4, user), loan_ext_courtesy_waiver
  (6, root); tools assess_late_fee_8eb98004, assess_returned_payment_fee_e467aa52, enroll_autopay_4dda8507 (user),
  waive_fee_courtesy_87326602. Three value_input state-form edges into the root; L, F, A commute (all 6 orders replayed:
  8.99 / 8.58 / 9.19 / waiver 8.09, identical terminal rows).
- Revision: courtesy unpaid part first ignored earlier waivers (skip-L probe picked the already-waived 2024 fee at 15.00)
  -> rule/baseline/compute now net fee payments AND earlier waivers; skip-L effect is 0.00.
- Revision: solvability flagged prior_step bindings without source_table/source_field on the waiver's dedup and
  request-window gates -> bound to the late-fee call's loan_transactions.loan_txn_id. Re-run: SOLVABILITY OK.
- Revision: L/F ladder and rule wording disambiguated (late fee's / returned-payment fee's assessment date, param prefixes)
  and the AutoPay Credit Builder ladder reworded so no tier sentence attaches to two policies (R's Credit Builder credit).
- Figures: late fee 8.99 (all-baseline 15.00), returned fee 8.58 (15.00), rate 9.19 (12.49), waiver 8.09 (8.99).

## XF recipe — point by point (all six policies)
1 Factor independence. Factor-read table (factor -> plain bindings it reads beyond its own): every factor of Q and R ->
  none; fee_form_by_return -> l_is_c, l_min, l_max, l_pct, l_unpaid (baseline schedule quantities); bank_event_form ->
  f_sched_fee (baseline schedule amount); modified_rate_base -> a_base_rate, a_grade_discount (baseline); return_reason_point
  -> c_fee_due (plain fee selection); all other factors -> none. Mechanical scan: no factor binding reads another factor's
  binding; no factor binding assembles the result (results are assembled only in plain bindings / result).
2 Assembly once, order fixed. Q: "Each rule that follows changes only the one quantity it names ... interest worked out
  once, on the total interest days and the rate each of those days carries ... added-back amount ... after the quoted
  interest". R: reduction and credits come off together, floor 0, then the sizing form, then cent and whole-dollar
  rounding. L/F: form first, shares multiply on the unrounded figure, cap (L: unpaid portion), round once. A: rate base
  replaces base rate, steps add to the grade discount, subtract, round once. C: form decides how, share = base + points,
  clamp 0..1, round once. None of these assembly sentences describes a factor's tiers.
3 Factor-only quantities. Hold days (Q), cushion days (Q), credits (R), shares (L, F), steps (A), points (C) are each
  defined only in their factor's sentence; baselines name only the default quantities (quote window, refinance fee
  percent, schedule figure/amount, base rate less grade discount, whole unpaid part). No rule defines a quantity "as
  another policy figures it"; quantity names carry their policy (late-fee / returned-fee / AutoPay discount step /
  courtesy point / refinance credit).
4 Overwrite hygiene. Every overwrite's replaced_by restates the still-in-force content and names its scope ("For a
  refinance-purpose quote, and only for such a quote ... every other payoff quote ..."; same pattern in R, L, F, A, C).
  No two policies retire the same base clause. Each overwrite retires a clause that genuinely conflicts (quote window,
  quote interest/payoff composition, refinance fee basis x2, late-fee schedule figure, returned-fee amount, AutoPay
  rate, courtesy amount). No rule defers to a retired clause. Known simplification, not a departure in a computed
  figure: the refinance quote record stores payoff and good-through date only (no per-diem field).
5 compute_basis verbatim. Scratch sweep (lint.py): every compute_basis quote of all six policies is a substring of its
  rule; every binding has a basis; every baseline sentence, replaced_by and policy_source is verbatim in its own rule.
6 Rounding. Q "rounded to the cent only at that point" <-> RND on q_interest; R "rounded to the cent and then rounded up
  to the next whole dollar" <-> RND then int-ceil; L/F/C "rounded to the cent once, at the end" <-> single RND on result;
  A "rounded to two decimals once, at the end" <-> single RND. Seeded figures avoid exact half-cent cases (8.9913,
  8.5805, 8.091, 23.573, 6530.23).
7 Docstrings. Only effects the bodies have (fee lines + fees_balance; waiver line + fees_balance; enrollment record +
  AutoPay fields + rate; quote row; application row); no example values; no ordering words (grep before/after/first:
  none); no other tool names.
8 Edge probes (scratch copies, results): Q absent servicing events 6402.98; same-date enroll/cancel tie (enrollment
  later) 6403.14; absent additional-principal payment 6002.81; decoy channel phone_ach 6002.81; return 11 months old
  (10-day tier) 6402.81; next due already past (negative lag -> default window) 6414.68; absent earlier quotes 6400.44.
  R absent quote dated today / decoy borrower_payoff quote today -> no payoff to be covered (the unmet prerequisite
  itself: the rule fixes the amount only after that quote exists); absent FlexLine 6563; closed FlexLine 6563; absent
  Credit Builder 6547; loan not itself a refinance 6533. L schedule_b NY 8.99; schedule_c MD 6.54; R01 form 9.81; absent
  modification 9.99. F decoy FlexLine return on another account (tier b) 5.16; schedule_c 0.00 (no line). A pre-plan =
  base rate 8.69; decoy broken modification 12.19; absent Credit Builder 9.29. C courtesy 5 months ago (form a) 3.99;
  no earlier courtesy (form c) 8.99; decoy borrower_request cancellation 6.74; absent PracticePay 7.19; absent
  servicing events 5.39. Ties: LATEST keeps the first row recorded — stated in every rule that uses a latest record.
  Month-end: all seeded dates use day <= 28 and rules say "a month being complete on the same day number of the later
  month". Entries vs periods: installment counts are "payments of type scheduled_installment posted less payments
  returned", stated as such. Exclusions in rules (purpose filter on quotes, returned AutoPay debits, borrower_payoff
  quotes not counted, earlier waivers) are all compute filters.
9 Method tiers (pairwise, distinguishing input): window_anchor_rule d-1 / d / 10 (AutoPay on vs off with due in 5 days:
  4 vs 5 vs 10); day_rate_split current-disc before cancel / current+disc before enroll / flat (cancel 2 days after
  paid-through: -1.00 vs +1.00 vs 0 rate-days); refi_sizing_form P / P(1+f) / P/(1-f) (P=6402.81, f=1.99%: 6403 /
  6531 / 6533); fee_form_by_return pct no-min on unpaid / pct of full installment with min-max / schedule on unpaid
  (installment 274.87, past due 100.00: 5.00 / 15.00 / 15.00 vs past due 274.87: 13.74 / 15.00 / 15.00 — tiers b and c
  differ when a partial payment leaves past due below the installment and pct x installment > min, e.g. installment
  400, past due 100: 20.00 vs 15.00); bank_event_form proportional / minus half FlexLine fee / flat (15 x 274.87/330.83
  = 12.46 vs 7.50 vs 15.00); modified_rate_base modified+disc / modified / base (9.99 / 9.49 / 12.99);
  courtesy_waiver_form unpaid-5 / unpaid x share / whole (3.99 / 8.09 / 8.99). No two tiers coincide on their domain.
10 No factor id is a substring of any tool name (scan: none).
11 Cross-record pairing: the bank-event form compares the latest loan return and the latest FlexLine return (date,
  account) — both single latest records, computable in the DSL; no N-day window pairing across records is used.
12 Realism. Base-grounded: state fee schedules, R02/R01 return semantics, the completed Term Extension Modification's
  permanent rate, AutoPay split accrual by rate in force, uncleared ACH funds held on a payoff, courtesy waivers,
  serial-refinance (anti-flipping) fee treatment. Larkspur program factors (loyalty/AutoPay/relationship credits and
  shares, re-quote cushion) are stated as the company's own schedules. Seeded cross-category rows are states their
  charters produce (FlexLine frozen for a returned payment with its returned-payment and late fees; matured Credit
  Builder; PracticePay paid off; Short-Term Payment Deferral offer expired; Term Extension Modification completed with
  documents and credited trial installments). No fee on interest never billed, no post-closing fee, no pyramiding (the
  late fee's R01 form charges on the installment, never on fees).
13 Runtime: frozen_time "YYYY-MM-DD HH:MM:SS EDT" in both tasks; task_tools.py imports only erlbench; every write tool
  calls ctx.create/update in its own body; no date maths in the tools.
14 Proof text swept after every revision above: design_rationale, prerequisite_closure (skip effects 0.00 / 8.99 /
  5.39), tracing and factor_trace figures regenerated from the same verification run as computations.

## Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (branches mean 51, steps mean 18,
history_rows_max 121, branches_max 72); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional). TRACEABILITY: only the six
unlock tool names miss (pre-publication, expected); no other miss.
- Scratch /tmp/personal_loan_servicing_0067/ removed (authoring scripts, harness, probes).
REWORK round 1: gates 7/7 green

## Rework round 2 (audit audits/policy_task/personal_loan_servicing/, revision_1)
Items closed one by one, each with its class across all six policies (details in rework_r2_claims.md):
- PLS-G1: late fee fee_form_by_return and flexline_month_relief -> pay_cycle_form (method: shared by amounts past due /
  two cycles within one schedule maximum / schedule figure) + loan_tenure_relief; returned fee return_reason_share ->
  returned_fee_autopay_relief. Courtesy return_reason_point kept (discretionary).
- PLS-G2(a–g), PLS-G3, O-1…O-10, T0-O1, T1-O1, T1-O2 as listed in the claims file.
- Re-world: T0's 2026-10-05 refinance quote recomputed under the quote rule of its date; T1's earlier returned-payment
  fees assessed at the borrower's contact dates (2024-12-22, 2025-08-12, the latter cure taken by phone), PracticePay
  ledger seeded (charge, payments, one 2025-03-05 late fee) with a find_pos_transactions read node (task-1 steps shifted
  by one; prior_step references renumbered).
- New figures (scratch harness, equal to check_compute): T0 quote 6438.42 (all-baseline 6012.47), amount financed 6519
  (6637); T1 late fee 9.30 (15.00), returned fee 8.58 (15.00), rate 9.19 (12.49), waiver 8.37 (9.30); every factor moves
  its result; all six orders of T1's prerequisites give the same values; skip effects T1 0.00 / 9.30 / 5.58, T0 stale-quote
  alternative 6459.
- Proof text swept: computations, factor traces and sensitivities, tracing, prerequisite_closure (conditions and
  sentences copied from the revised policies), necessity texts, seed-consistency checks, both design_rationale dossiers.

### Probe table (scratch copies; result = recomputed figure)
| policy | probe | result |
|---|---|---|
| loan_ext_refi_payoff_quote | as seeded | 6438.42 |
| loan_ext_refi_payoff_quote | absent servicing events | 6438.58 |
| loan_ext_refi_payoff_quote | tie: enrollment same date as cancellation | 6438.75 |
| loan_ext_refi_payoff_quote | decoy: latest extra payment already returned (PLS-G2e) | 6038.42 |
| loan_ext_refi_payoff_quote | decoy: second extra payment same date by phone (tie keeps first recorded) | 6438.42 |
| loan_ext_refi_payoff_quote | absent additional-principal payment | 6038.42 |
| loan_ext_refi_payoff_quote | next due 1 day away, AutoPay on (O-10 -> default window) | 6414.68 |
| loan_ext_refi_payoff_quote | next due already past (negative lag) | 6414.68 |
| loan_ext_refi_payoff_quote | month-end: return dated 2025-10-31 vs quote 2026-10-20 | 6438.42 |
| loan_ext_refi_application | after the quote | 6519 |
| loan_ext_refi_application | absent refinance quote dated today (prerequisite unmet) | RAISE TypeError |
| loan_ext_refi_application | decoy: borrower_payoff quote today only | RAISE TypeError |
| loan_ext_refi_application | decoy: FlexLine closed (only open lines count) | 6551 |
| loan_ext_refi_application | decoy: second Credit Builder account, active, past due | 6519 |
| loan_ext_refi_application | decoy: row-order swap, active current builder listed first, no matured | 6528 |
| loan_ext_refi_application | absent Credit Builder | 6535 |
| loan_ext_refi_application | loan not itself a refinance | 6520 |
| loan_ext_late_fee | as seeded | 9.3 |
| loan_ext_returned_fee | as seeded | 8.58 |
| loan_ext_autopay_enroll | as seeded | 9.19 |
| loan_ext_late_fee | absent FlexLine holding and ledger | 11.2 |
| loan_ext_late_fee | decoy: FlexLine late fee for a due date 30 days earlier (previous cycle) | 3.73 |
| loan_ext_late_fee | decoy: FlexLine past due already cured (0.00) | 11.2 |
| loan_ext_late_fee | schedule_b origination state (NY) | 8.52 |
| loan_ext_late_fee | schedule_c origination state (MD), flat in every form | 7.46 |
| loan_ext_late_fee | absent hardship plan | 10.34 |
| loan_ext_returned_fee | decoy: later FlexLine return on another account (PLS-G2a) | 5.16 |
| loan_ext_returned_fee | decoy: FlexLine return same day, other account (not one event) | 5.16 |
| loan_ext_returned_fee | absent FlexLine ledger | 10.33 |
| loan_ext_returned_fee | schedule_c state (fee 0, no line) | 0.0 |
| loan_ext_autopay_enroll | decoy: broken modification (not completed) | 12.19 |
| loan_ext_autopay_enroll | modification with pre-plan rate = base rate | 8.69 |
| loan_ext_autopay_enroll | absent Credit Builder | 9.29 |
| loan_ext_courtesy_waiver | after L, F, A | 8.37 |
| loan_ext_courtesy_waiver | decoy: auto-cancel, enroll, borrower cancel, enroll (PLS-G2b) | 6.98 |
| loan_ext_courtesy_waiver | decoy: two active PracticePay plans, no paid-off plan (PLS-G2c, row order irrelevant) | 7.91 |
| loan_ext_courtesy_waiver | decoy: two loan returns same date, R01 recorded first (PLS-G2d tie) | 8.37 |
| loan_ext_courtesy_waiver | earlier courtesy 5 months ago (form a, monotone) | 3.37 |
| loan_ext_courtesy_waiver | no earlier courtesy (form c) | 9.3 |
| loan_ext_courtesy_waiver | absent PracticePay | 7.44 |
| loan_ext_courtesy_waiver | absent servicing events | 5.58 |
Reads and their absent-record tiers: refinance quote LATEST (absent -> no figure: the unmet prerequisite of the
application); servicing LATEST enrollment/cancellation (absent -> flat rate / AutoPay point 0); additional-principal
LATEST (absent -> nothing held); returns COUNT/LATEST (absent -> no hold tier change / schedule form / return-reason 0);
FlexLine CFIELD open line and XLATEST late fee / returned payment / fee (absent -> credit 0 / schedule figure / schedule
amount); hardship CFIELD completed modification (absent -> share 1 / base rate); Credit Builder CFIELD + EXISTS (absent
-> 0); PracticePay EXISTS + XCOUNT (absent -> 0). None-guards on every LATEST/CFIELD; no division by zero (denominators
are the loan unpaid portion or returned payment plus a non-negative amount); negative date lags fall to the default
window; ties: every LATEST states "on a tie of dates, the first one recorded"; month-end: one stated convention equal to
MONTHS().

### XF recipe re-applied to every policy touched (all six)
1 no factor binding reads another factor's binding (scan: none); 2 assembly stated once per policy with order fixed
(late fee: pay-cycle form, then shares, cap, one rounding; others unchanged); 3 factor-only quantities in their own
sentences, quantities named for their policy (late-fee / returned-fee / AutoPay discount step / courtesy point /
refinance credit); 4 overwrites self-scoped, none retiring a gate sentence (the "once for each returned payment" gate
sentence is left in force and the policy's object stated instead), new pricing overwrite declared for the add-on form;
5 compute_basis sweep: every quote verbatim, every binding claimed, no stale basis keys; 6 rounding sentences match RND;
tools now round the same way; 7 docstrings: no examples, no ordering words, no other tool names, effects as coded;
8 probe table above; 9 method tiers: pay_cycle_form shapes ratio / min-with-offset / identity (distinguishing inputs:
FlexLine late fee 0 vs 30 days from the due date), window_anchor_rule d-1 / d+grace / fixed, others as recorded in
round 1; 10 no factor id inside a tool name (scan: none); 11 no N-day cross-record pairing (latest-record comparisons
only); 12 replaced factors are fee-program and cross-product practices; seeded rows are states their charters produce;
13 frozen_time format, imports, writes in bodies unchanged; 14 proof text swept as listed.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 2: gates 7/7 green

## Rework round 3 (revision_2 audit: PLS-R2-1, R2-O1, R2-O2)

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_2: task0=PASS,
task1=PASS, charter=PLS-R2-1).

### Changes
- PLS-R2-1 (loan_ext_late_fee): the rule's pay-cycle passage now says the form applies only to schedule_a and
  schedule_b, and a schedule_c loan takes its flat amount whatever the FlexLine shows (this matches compute
  `l_form_fee = l_sched_fee if l_is_c else ...`, which is unchanged). Tier 2 names "the loan's schedule maximum
  (late_fee_schedule_a_max_usd on schedule_a, late_fee_schedule_b_max_usd on schedule_b)". Also updated:
  replaced_by (rule copy included), the assembly sentence, the pay_cycle_form ladder (tiers scoped to a/b, schedule_c
  in "otherwise"), and the compute_basis for l_form_fee, l_line_late_amount and l_line_late_due.
- Class sweep over every policy's fee-schedule / state branches:
  - late fee: the a/b/c branches and every pay-cycle tier were probed (below).
  - returned fee: the a/b/c branches and every bank-event tier were probed. The rule now states that on schedule_c
    every form works from that schedule's amount.
  - courtesy waiver: the returned-fee prerequisite sentence (rule and policy_source) and its condition now require a
    fee-bearing schedule, because schedule_c writes no fee line and the sentence otherwise names an object that
    never appears. The task-1 dossier quote and the prerequisite_closure copy were updated.
  - grade branches: every grade variant carries every P() parameter that any compute reads (scan: none missing).
  - payoff quote, refinance and AutoPay: no state or schedule branch.
- R2-O1: pay_cycle_form tier 1 now says the loan's own late fee is cut to its part of the two amounts past due
  (the FlexLine fee stays as charged), and tier 2 says it is held within the loan's own schedule maximum. Class
  member bank_event_form: "one bank event is carrying two fees" / "split by size" became the loan's own fee cut to
  the loan's part of that one bank event. The basis quotes, ladders and task-1 trace/necessity text were swept
  (no "one late charge", "split by size" or "carrying two fees" left).
- R2-O2: `EXISTS('builder', status='active', amount_past_due=0.0)` in refinance and AutoPay is replaced by
  `*_builder_active_pd = CFIELD('builder','amount_past_due', status='active')` and
  `*_builder_active_current = pd != None and pd == 0`. The rule now states that a borrower holds at most one
  active Credit Builder account (builder_agg_multi_holding) and that the amount is compared as an amount. The new
  binding is in the factor's bindings and has its own basis. Sweep: no other numeric value in any equality
  filter.
- Scored values are unchanged: T0 Q/R and T1 L/F/A/C all re-evaluated equal to expected, so no figure in the proof
  text moved.

### Branch probe table (scratch copies of the task-1 world at each call's step; rule reading coded independently)
| policy | branch (state) | tier | form by rule | compute | rule reading |
|---|---|---|---|---|---|
| late_fee | schedule_a (PA, OH) | same cycle, FlexLine past due | loan's part | 9.3 | 9.3 |
| late_fee | schedule_a (PA, OH) | previous cycle (30 days) | within schedule_a max | 3.73 | 3.73 |
| late_fee | schedule_a (PA, OH) | outside both windows | schedule figure | 11.2 | 11.2 |
| late_fee | schedule_a (PA) | same cycle, FlexLine nothing past due | schedule figure | 11.2 | 11.2 |
| late_fee | schedule_a (PA) | no FlexLine late fee | schedule figure | 11.2 | 11.2 |
| late_fee | schedule_b (NY, CA) | same cycle | loan's part | 8.52 | 8.52 |
| late_fee | schedule_b (NY, CA) | previous cycle | within schedule_b max (floored at zero) | 0.0 | 0.0 |
| late_fee | schedule_b (NY, CA) | outside / nothing past due / no fee | schedule figure | 10.26 | 10.26 |
| late_fee | schedule_c (MD, NC, WI) | same cycle (the audit's PLS-R2-1 probe) | flat, no form | 7.46 | 7.46 |
| late_fee | schedule_c (MD, NC, WI) | previous cycle / outside / nothing past due / no fee | flat, no form | 7.46 | 7.46 |
| returned_fee | schedule_a (PA, OH) | one bank event | loan's part | 8.58 | 8.58 |
| returned_fee | schedule_a (PA, OH) | FlexLine fee < 1 month, other event | less half | 5.16 | 5.16 |
| returned_fee | schedule_a (PA, OH) | otherwise | schedule amount | 10.33 | 10.33 |
| returned_fee | schedule_b (NY, VT) | one bank event / less half / otherwise | as tier | 5.72 / 1.72 / 6.89 | 5.72 / 1.72 / 6.89 |
| returned_fee | schedule_c (MD, NC, WI) | every tier | 0.00, no fee line | 0.0 | 0.0 |
| refi_application | active Credit Builder, amount past due 0 (int) / 0.0 | active tier | credit applies | 6528 | 6528 |
| refi_application | active, past due 12.5 / None / absent | no credit | none | 6535 | 6535 |
| autopay_enroll | active Credit Builder, amount past due 0 (int) / 0.0 | active step | step applies | 9.24 | 9.24 |
| autopay_enroll | active, past due 12.5 / None / absent | no step | none | 9.29 | 9.29 |
| courtesy_waiver | schedule_c (MD), no returned-fee line | prerequisite not owed; fee load one | no load point | 9.3 | 9.3 |
Under the old string-matched EXISTS, the int-0 builder row read as not current. A string "0.00" is not a valid
number under db_schema, so no seed stores it.

### XF recipe re-applied to every policy touched (late fee, returned fee, refinance, AutoPay, courtesy waiver)
1 mechanical scan: no factor binding reads another factor's binding (the new *_builder_active_pd sits inside
its own factor); 2 assembly sentence still stated once with its order (late fee: form on a/b or flat on c, then
shares, cap, one rounding); 3 factor-only quantities stay in their own sentences; 4 the late-fee replaced_by is
restated and kept verbatim in the rule, still self-scoped and still restating the a/b/c schedule for every other
fee, and no new overwrite was needed; 5 compute_basis sweep: every quote verbatim, every binding claimed, no stale
key; 6 rounding is unchanged and matches RND; 7 task_tools.py is unchanged; 8 the probe table above (decoy:
matured row closed with an active row added; absent FlexLine late fee; absent builder; zero, None and int/float
past-due values; schedule branches); 9 pay_cycle_form tiers are still ratio / min-with-offset / identity on
schedule_a and schedule_b (distinguishing inputs: FlexLine late fee 0 / 30 / 90 days from the due date); on
schedule_c the form is out of scope by rule, not a coinciding tier; 10 no factor id inside a tool name; 11 no
cross-record N-day pairing added; 12 realism: flat-fee states charge the flat amount without cross-product
apportioning, and the relief wording now describes exactly what is reduced; 13 runtime constraints unchanged; 14
proof text swept (task-1 trace, necessity, dossier quote, prerequisite_closure; plan.md has no stale phrase;
task 0 is unaffected).

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 3: gates 7/7 green

## Rework round 4 (revision_3 audit: PLS-R3-1)

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_3: task0=PASS,
task1=PASS, charter=PLS-R3-1).

### Changes (zero-result class, every write policy)
- Late fee: new sentence after the order-of-steps sentence (that sentence is left intact): a late fee that works out
  to 0.00 is not charged, no late-fee line is written, and it is not counted as a late fee charged. pay_cycle_form
  tier-2 method text says the same.
- Returned fee: new sentence after the order-of-steps sentence: a fee that works out to 0.00 (always so on
  schedule_c) is not charged, writes no fee line and does not count toward the monthly returned-fee limit.
- Courtesy waiver: new sentence after the order-of-steps sentence: a 0.00 waiver is not granted and writes no
  line, so it uses no courtesy allowance and is not the fee's one waiver; with no late fee on the loan there is
  nothing to waive. Compute `c_unpaid` gains a None guard (0 when there is no late fee), so that world evaluates
  to 0.00 instead of raising. Form tier-1 method text says the same.
  - Prerequisite sentences: L now reads "..., where that late fee works out above 0.00." and F now reads "...
    where its return code bears one and that fee works out above 0.00.".
  - Both conditions now end "a ... that works out to 0.00 writes no line, and then nothing is waited on." The
    rule, policy_source and the task-1 prerequisite_closure and dossier copies are synced.
- Payoff quote: issued only on a loan with unpaid principal, so it is always above 0.00 and always recorded; a
  loan with no unpaid principal is not quoted.
- Refinance: the amount financed is never below the payoff, so it is always above 0.00; a loan with no unpaid
  principal is not quoted and so never sized (this is consistent with the R <- Q sentence).
- AutoPay: the enrollment is recorded in every case; the rate is always above 0.00 (no rate base is as low as the
  grade's discount plus every step).
- Tools are unchanged: each records only the amount it is given; "not written" means the tool is not called.
- Scored values are unchanged (T0 Q/R and T1 L/F/A/C re-evaluated equal to expected). Task-1 skip-effect text now
  says the 0.00 waiver is not granted.

### Zero-edge probe table (scratch copies)
| policy | world | compute | rule outcome |
|---|---|---|---|
| late_fee | task-1, CA (schedule_b), FlexLine late fee in previous cycle | 0.0 | not charged, no line |
| courtesy_waiver | same world, L writes no line | latest late fee is the earlier one, unpaid 0 -> 0.0 | not granted, no line; nothing waited on, no deadlock |
| returned_fee | task-1, MD (schedule_c) | 0.0 | not charged, no line |
| courtesy_waiver | same world, F writes no line | fee load 0 -> 9.3 | computed; edge F waits on nothing |
| courtesy_waiver | courtesy 6 months back, AutoPay not restored, R01 return | share 0.4, form 1 -> 0.0 | not granted, no allowance used |
| courtesy_waiver | no late fee on the loan | 0.0 (None guard) | nothing to waive |
| refi_payoff_quote | task-0, principal 0.01, no fees | 400.01 (held payment added back) | above 0.00, recorded |
| refi_application | task-0, payoff quote 0.01 | 1 | above 0.00, recorded |
| autopay_enroll | Grade A, modification at the 5.99 floor | 5.19 | above 0.00, recorded |
| all six | task worlds as seeded | unchanged scored values | — |

### XF recipe re-applied (all six policies touched)
1 scan: no factor binding reads another factor's binding (c_unpaid is a plain binding); 2 every order-of-steps
sentence is kept byte-for-byte, and each zero sentence follows it as its own sentence; 3 zero sentences name only
their own quantity, and no depended-on rule mentions the courtesy waiver; 4 overwrites unchanged, and
replaced_by/policy_source are verbatim in their rules (lint); 5 compute_basis sweep clean; 6 RND placement
unchanged; 7 task_tools.py unchanged; 8 zero-edge and absent-record probes above (absent late fee, absent fee
line, zero share); 9 method tiers unchanged in shape; 10 no factor id in a tool name; 11 n/a; 12 realism:
servicers do not post 0.00 fees or 0.00 waivers, and an unposted zero uses no allowance or limit; 13 runtime
constraints unchanged; 14 proof text swept (task-1 prerequisite_closure policy_source/condition, dossier quotes,
skip-effect lines; task 0 has no copy of a changed sentence).

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 4: gates 7/7 green

## Rework round 5 (revision_4 audit: PLS-R4-1, PLS-R4-2)

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_4: task0=PASS,
task1=PASS, charter=PLS-R4-1,PLS-R4-2).

### Changes
- PLS-R4-1 (refinance r_installments, late fee l_inst_12m, returned fee f_inst_12m, courtesy c_inst): return rows
  carry no payment_type (db_schema: payment_type is "empty on non-payment lines"; the return event has no such
  field), so the DSL cannot tell which returns undid an installment. The rules now state the computed measure:
  scheduled_installment payments posted, less one for every payment returned whatever it was for. "Credited"
  becomes "net" in rules, ladders and basis quotes. Realism: underwriting and fee relief weigh every bounced
  payment against the payment record. Compute is unchanged.
- AutoPay counts (refinance r_ap_debits_12m, late fee l_ap_24m, returned fee f_ap_24m, AutoPay a_debits_24m): the
  task-1 seed has AutoPay hardship_plan_payment debits, so "AutoPay installment debits" had a second reading.
  The text now says "AutoPay debits", and each rule defines an AutoPay debit as any payment AutoPay took (a
  hardship plan payment included) and an AutoPay debit returned as a return of such a payment. Compute is
  unchanged.
- PLS-R4-2 (late fee pay_cycle_form, returned fee bank_event_form): new bindings in each form's factor:
  - `*_id` = XLATEST line_txn_id of the same latest fee;
  - `*_waived` = XSUM line_fee_waived amount related_txn_id = that id (0 when there is no fee);
  - `*_net` = MX(0, amount − waived).
  - Late fee: cycle gap is set only when net > 0, and the tier-2 offset uses net.
  - Returned fee: same-event needs net > 0, tier 2 needs net > 0, and the offset uses net / 2.
  - Rule: a new sentence after each form says the fee is taken net of every FlexLine fee waiver applied to it:
    waived in full counts as no FlexLine fee, waived in part counts at its unwaived amount. The tier-1 premise
    now reads "left as it stands", and the ladders say "not waived in full" and "net of its waivers".
- Courtesy waiver (reversed rows, same class): c_pay_n = COUNT of fee payment lines on the fee; c_pay_id = LATEST
  of them; c_pay_reversed = SUM of loan_fee_payment_reversed on that line. c_unpaid adds back the reversed amount
  when there is at most one line; with two or more it is 0, so the waiver is not granted. Rule sentence and
  policy baseline sentence updated identically. The ledger links a reversal only to its fee payment line, and a
  two-hop join is not expressible, so a fee paid through two or more lines is stated as outside this policy's
  courtesy amount.
- Scored values are unchanged (T0 Q/R, T1 L/F/A/C re-evaluated equal to expected). Task-1 proof text: "credited"
  becomes "net" (dossier and traces), and the FlexLine fees are marked "not waived" in the factor traces.

### Read-site table (rule wording vs compute filter; probe on a scratch copy)
| policy | read | rule wording | compute filter | decoy probed -> result |
|---|---|---|---|---|
| quote | q_last_enroll/cancel | latest AutoPay record, same-date enrollment later | LATEST servicing events by type | carried (r2 decoys) |
| quote | q_returns_12m | a payment on the loan was returned (any) | COUNT returned, 12 m | carried (any return by wording) |
| quote | q_extra_* + q_extra_returned | latest additional-principal payment, excluded if returned | LATEST posted additional_principal; COUNT returns related to it | carried (r2: returned 400 -> 6404.19) |
| quote | q_requotes | refinance-purpose quotes, other purposes not counted | COUNT quotes purpose refinance, 1 m | payoff-purpose quote -> unchanged |
| refi | r_payoff | refinance quote dated the application date | LATEST purpose refinance, quote_date NOW | prerequisite edge |
| refi | r_installments | sched. installments posted less every returned payment | COUNT posted sched.; COUNT all returns | returned additional-principal -> one fewer (as worded) |
| refi | r_late_24m / r_line_late_12m | late fees charged (a later waiver does not undo a charge) | COUNT assessed | charged-class, single reading |
| refi | r_ap_debits_12m / r_ap_returns_12m | AutoPay debits (plan payments included); AutoPay debit returned | autopay_ach posted / returned | non-AutoPay return -> unchanged; AutoPay plan payment -> +1 |
| refi / AutoPay | builder CFIELDs | matured; one active account, past due compared as an amount | CFIELD status | r3 probes |
| late fee | l_line_late_* | latest FlexLine late fee, first recorded on ties, net of waivers | XLATEST assessed; XSUM waivers related to it | waived in full -> schedule figure; part-waived previous cycle -> cap on net; waiver of another fee -> unchanged |
| late fee | l_line_pd | open FlexLine (active/frozen/repayment) | CFIELD by status | closed FlexLine with past due -> unchanged |
| late fee | l_late_12m | late fee charged on the loan | COUNT assessed | charged-class |
| late fee | l_inst_12m | as r_installments, 12 m | as above | returned additional-principal -> one fewer |
| late / returned | l_tem_closed / f_tem_closed / a_tem_* | completed TEM on the loan (max_uses_per_loan 1) | CFIELD completed TEM, loan | r2 broken-plan decoy |
| late / returned / AutoPay | l_ap_24m / f_ap_24m / a_debits_24m | AutoPay debits less AutoPay debits returned | autopay_ach posted − autopay_ach returned | non-AutoPay return -> unchanged; plan payment -> +1 |
| returned | f_ret_* | latest returned payment, first recorded on ties | LATEST returned | later posted payment -> unchanged |
| returned | f_line_ret_* | latest FlexLine returned payment | XLATEST returned | r2 other-account decoy |
| returned | f_line_fee_* | latest FlexLine returned-payment fee, net of waivers | XLATEST assessed; XSUM waivers | waived in full -> schedule amount; part-waived same event -> share unchanged; part-waived other event -> less half the net |
| returned | f_other_returns_12m / f_inst_12m | other returned payments; net installments | COUNT returns − 1; as above | returned additional-principal -> one fewer |
| courtesy | c_fee_* | latest late fee charged | LATEST assessed | r2 tie decoy |
| courtesy | c_fee_paid / c_pay_* / c_fee_waived | fee payment lines not reversed; earlier waivers; two or more lines outside | SUM paid; reversal on the one line; SUM waived | 4.00 line -> unpaid less 4.00; reversed -> restored; other line's reversal -> unchanged; two lines -> 0.00 |
| courtesy | c_last_courtesy | latest courtesy waiver | LATEST waived, reason courtesy | lender_error waiver -> unchanged |
| courtesy | c_last_enroll/cancel/reason | latest enrollment / cancellation | LATEST by type | r2 decoy chain |
| courtesy | c_late_3m / c_ret_3m | fees charged in 3 months (0.00 fees write no line) | COUNT assessed | charged-class |
| courtesy | c_inst | net installments (whole history) | as above | returned additional-principal -> one fewer |
| courtesy | c_pos_* | plan paid in full; active plan; PracticePay late fees charged | EXISTS status/reason; XCOUNT assessed | cancelled plan -> unchanged |
| courtesy | c_ret_date/code | latest returned payment | LATEST returned | r2 tie decoy |
Every probe above agrees between rule and compute.

### XF recipe re-applied (all six policies touched)
1 scan: no factor binding reads another factor's binding (the new *_id/_waived/_net bindings sit in their own
form's factor; c_pay_* are plain bindings); 2 every order-of-steps sentence is intact, and the new sentences follow
the form passages; 3 each new quantity is defined in its own factor's sentence; 4 overwrites unchanged, and
replaced_by/policy_source/baseline rule are verbatim in their rules (lint); 5 compute_basis sweep clean (new
bindings each claimed); 6 RND placement unchanged; 7 task_tools.py unchanged; 8 decoy table above, plus absent-fee
None guards on every new read; 9 method tiers keep their shapes (a fee waived in full falls to the identity tier);
10 no factor id in a tool name; 11 no cross-record N-day pairing; 12 realism: a waived FlexLine fee no longer
offsets the loan's fee, a reversed fee payment leaves the fee unpaid, and bounced payments weigh on the record;
13 runtime unchanged; 14 proof text swept (task-1 dossier/traces "credited" -> "net", FlexLine fees "not
waived"; task 0 says "AutoPay debits" already).

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 5: gates 7/7 green

## Rework round 6 (revision_5 audit: PLS-R5-1; XF#14 in task 0 and task 1)

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_5: task0=RED, task1=RED,
both SOURCE-FACTOR / XF#14; charter=PLS-R5-1).

### PLS-R5-1 (courtesy waiver)
- Removed: c_fee_paid, c_pay_n, c_pay_id, c_pay_reversed, the "two or more fee payment lines" clause in the rule and
  the policy baseline sentence, and their basis lines.
- New measure, exactly as the records carry it:
  - `c_fees_owed = F('fees_balance')` (db_schema: "unpaid late fees and returned-payment fees; identically the sum
    of the fees_due account deltas"; the late-fee, returned-fee and waiver tools keep it).
  - `c_unpaid = MX(0, MN(RND(c_fee_amount - c_fee_waived, 2), c_fees_owed))` (0 with no late fee).
  - Rule and baseline: "Its waivable part is its amount less every earlier waiver line applied to it, held to no
    more than the loan's fees balance (...), so a courtesy waiver never exceeds the fees the borrower owes and
    never refunds money already paid; a fee payment applied to the waived fee, or a reversal of one, changes its
    waivable part only through the loan's fees balance, and the waiver comes off the fees the loan still owes."
- The overwrite's replaced_by and the rule copy now say "never more than the loan's fees balance". Every other
  waiver keeps the base per-fee wording.
- Why not a per-fee unpaid part: a reversal links only to the fee payment line, and the DSL cannot follow
  reversal -> line -> fee for several lines. Taking only the latest line understates the unpaid part (the
  auditor's 5.00 paid / reversed / 3.00 paid case), which would take away part of a waiver the base grants.
- Monotone check: whenever base unpaid part U > 0, amount − waived ≥ U and fees balance ≥ U, so waivable ≥ U.
- "Unpaid part" became "waivable part" in the courtesy rule, baseline, ladders and quotes. The tool docstring now
  says "all or part of one fee" (it no longer claims the fee is unpaid).
- Probes (scratch copy of task 1 at the waiver step):

| world | fees balance | waivable | waiver |
|---|---|---|---|
| as seeded | 17.88 | 9.3 | 8.37 (scored, unchanged) |
| 5.00 paid, reversed, 3.00 paid (auditor probe 1) | 14.88 | 9.3 | 8.37, granted |
| 2.00 + 2.00 paid (auditor probe 2) | 13.88 | 9.3 | 8.37, granted |
| fees balance cut to 4.00 | 4.00 | 4.0 | 3.6 |
| fees balance 0.00 | 0.00 | 0 | 0.0, not granted (zero rule) |
| earlier 2.00 waiver on the fee | 15.88 | 7.3 | 6.57 |

### XF#14 (proof text regenerated from the current charter)
- Scratch tiers.py evaluated every factor on its task world at the call's step, decided the tier taken (parameter
  tiers by value, method tiers by their conditions), set tier_taken to the current ladder `when` string, and
  re-checked baseline_result by substituting the factor's baseline.
  - Relabelled: task 0 autopay_record_credit; task 1 pay_cycle_form, autopay_history_relief, bank_event_form,
    returned_fee_autopay_relief, debit_record_step, installment_record_point.
  - All baseline_result values matched, and a re-run shows 0 stale labels.
  - The JSON was re-serialised with the original formatting (indent 4, non-ASCII kept; a round-trip of the
    untouched file is byte-identical).
- Mechanical trace check: every factor_trace names a current factor with its current effect and cross label,
  and every factor has a trace.
- Retired-term sweep over both task files and plan.md: credited, installment debit, stays as charged, one late
  charge, shared, carrying two, in every form, charges more than, unpaid part, still unpaid, fee payment line.
  Courtesy amount, trace and dossier text now say "waivable part", citing the fees balance 17.88. The remaining
  hits are descriptive, not retired terms ("day-rate split" is the factor id; "AutoPay installments" describes the
  seeded debits; "still unpaid" refers to the installment).
- Scored values are unchanged (T0 Q/R, T1 L/F/A/C re-evaluated equal to expected).

### XF recipe re-applied (courtesy waiver touched; the task files swept)
1 scan clean (c_fees_owed is a plain binding); 2 the order-of-steps sentence is intact; 3 the waivable part is
defined in its own sentence; 4 replaced_by states the new cap with self-scope, and every other waiver keeps the
base wording, verbatim in the rule (lint); 5 compute_basis clean; 6 RND placement unchanged (the waivable part
is rounded as before, the result once at the end); 7 docstring claims only what the body does; 8 probes above
(absent fee, zero balance, earlier waiver, payment/reversal decoys); 9 courtesy form tiers unchanged in shape; 10
no factor id in a tool name; 11 n/a; 12 realism: a courtesy credit comes off fees owed and never refunds, and no
existence condition zeroes a base-fixed amount; 13 runtime unchanged; 14 proof text regenerated as above.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 6: gates 7/7 green

## Rework round 7 (revision_6 audit: PLS-R6-1; task-1 XF#14 members g, h)

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_6: task0=PASS,
task1=RED SOURCE-FACTOR,SOURCE-CHAIN; charter=PLS-R6-1).

### PLS-R6-1 (coordinator decision applied)
- replaced_by (and its copy in the rule) now reads: "For a courtesy waiver of a late fee with no fee payment
  posted against it, and only for such a fee, the amount waived is the one set below, never more than that fee's
  amount less every earlier waiver line applied to it; every other fee, a late fee with a fee payment posted
  against it included, remains under the base clause: a late fee or returned-payment fee may be waived only on one
  of the bases of loan_evt_fee_waiver, one waiver line per fee, for the part of the fee still unpaid (a fee
  already paid in full is not waived; a refund of a paid fee is outside this policy)."
- The scope is a late fee, not "late or returned-payment fee", because this policy waives only the latest late fee;
  returned-payment fees stay wholly under the base clause.
- Rule and baseline sentence: "This policy's courtesy amount is set only for a waived fee with no fee payment
  posted against it; its unpaid part is then its amount less every earlier waiver line applied to it."
  "Waivable part" became "unpaid part" throughout (form sentences, ladders, quotes, the L prerequisite effect).
- Compute: c_fees_owed removed; `c_unpaid = RND(c_fee_amount - c_fee_waived, 2)` (0 with no late fee). No
  balance cap, no reversal netting.
- The scope is decided by rule; outside it the base clause sets the waiver, so this policy's computation is not
  the answer there.
- Task 1 is in scope: the waived fee ltx_8d8913a6aba3 has 0 fee payment lines. The L skip world's 2024-12-21
  fee has no fee payment either, is waived in full, gives 0.00 and is not granted, so the skip text still holds.
- Probes (scratch copy of task 1 at the waiver step):

| world | in scope | unpaid part | waiver |
|---|---|---|---|
| as seeded | yes | 9.3 | 8.37 (scored, unchanged) |
| earlier 2.00 lender_error waiver | yes | 7.3 | 6.57 |
| earlier waiver of the whole fee | yes | 0.0 | 0.0, not granted |
| a fee payment posted on the fee (auditor's paid-fee probe) | no | — | base clause: only the part still unpaid; a paid-in-full fee is not waived; no credit to another fee |

### XF#14 sweep (both task files)
- (g) returned-fee first_return_relief trace: "11 credited" became "11 net".
- (h) late-fee edge flips_to_true_by: "taken from its unpaid part (no fee payment has posted against it)".
- Courtesy amount tracing, factor_trace (form and plain line) and dossier: "waivable"/"fees balance" became
  "unpaid part", citing the no-fee-payment scope. The order_uniqueness text names the loans.fees_balance field
  explicitly. The hardship necessity line no longer says "credited".
- Mechanical checks (scratch sweep.py), all 0 issues:
  - every tier_taken is a current ladder `when`;
  - every prerequisite_closure edge's policy_source, condition, resolved_by, gate, form and kind equal the
    charter's;
  - every dossier quote is verbatim in a rule;
  - every factor_sensitivity and computation baseline_result re-evaluates equal;
  - every factor_trace names a current factor with its current effect and cross label.
- Retired-term grep over both task files: credited, waivable, fees balance, installment debit. The only hits
  left are the hardship_plan_payment_credited event type.

### XF recipe re-applied (courtesy waiver)
1 scan clean; 2 the order-of-steps sentence is intact; 3 the unpaid part is defined in its own sentence; 4 the
self-naming overwrite restates the base clause for every other fee, verbatim in the rule (lint), and the rule no
longer defers to anything it retires; 5 compute_basis clean; 6 RND unchanged; 7 tools unchanged since r6; 8 probes
above; 9 form tiers unchanged; 10 no factor id in a tool name; 11 n/a; 12 realism: a courtesy waiver of an
untouched late fee, with paid or partly paid fees left to the base clause, so no refund in substance; 13 runtime
unchanged; 14 proof text swept as above. Scored values are unchanged.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 7: gates 7/7 green

## Rework round 8 (revision_7 audit: PLS-R7-1, PLS-R7-2 (a)-(d))

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_7: task0=PASS,
task1=PASS, charter=PLS-R7-1,PLS-R7-2).

### Changes
- R7-1 + R7-2(a), courtesy waiver:
  - replaced_by and its rule copy: "For a courtesy waiver of the latest late fee charged on the loan (on a tie of
    dates, the first one recorded) while no fee payment has posted against it, and only for such a fee, ...; every
    other fee, an earlier late fee, a returned-payment fee and a latest late fee a fee payment has already reached
    included, remains under the base clause: <base restated>".
  - Rule and baseline: "This policy's courtesy amount is set only for the latest late fee charged on the loan while
    no fee payment has posted against it, ...".
  - New rule sentence, after the baseline span: the business boundary (a fee payment reaches a late fee only after
    accrued interest and older fees are paid, so the borrower is already paying it; the standard clause clears the
    remainder).
  - Compute unchanged.
- R7-2(b), returned fee: replaced_by and its rule copy are scoped to "the returned-payment fee owed on the latest
  returned payment on the loan (on a tie of dates, the first one recorded)", and every other returned-payment fee
  is under the base clause, restated verbatim. The rule gives the business reason for charging an earlier return's
  fee at the schedule amount. Compute unchanged.
- R7-2(c)+(d), payoff quote:
  - New scope sentence: the policy issues the refinance-purpose quote of a loan with at most one enrollment and at
    most one cancellation after its paid-through date, and no additional-principal payment other than the latest
    still on hold. Any other refinance-purpose quote is an ordinary payoff quote under loan_evt_payoff_quote.
  - The three overwrites now say "a refinance-purpose quote this policy issues"; their "every other payoff quote"
    clauses add "a refinance-purpose quote this policy does not issue included".
  - Day-rate split: new bindings q_cancel_after and q_enroll_after (in the factor). q_rate_adjust adds the
    both-after cases: cancellation first gives +discount × days(cancellation → enrollment); enrollment first gives
    −discount × days(enrollment → cancellation); a same-date pair gives 0 under the enrollment-is-later tie rule.
    The rule sentence now reads "the rate in force that day, read from the loan's latest AutoPay enrollment and
    latest AutoPay cancellation", and the ladder has 4 tiers plus otherwise.
  - Hold sentence: "looking only at" became "looking at" (the scope covers the rest).
- Task 0 is in scope:
  - AutoPay changes after the paid-through date 2026-10-16: only the 2026-10-18 cancellation.
  - Additional-principal payments: 2026-10-16 (held) and 2026-06-05 (long cleared).
  - Task 1's waived fee is the latest late fee with no fee payment.
  - No seed change was needed, and scored values are unchanged (T0 Q/R, T1 L/F/A/C re-evaluated).

### Probes (scratch copies)
| member | world | result |
|---|---|---|
| (d) | task 0, cancellation 10-17 then enrollment 10-19 (auditor probe) | adjust +1.00 rate-days (= base rate in force each day; the old rule gave +1.50) |
| (d) | task 0, enrollment 10-17 then cancellation 10-19 | adjust −1.00 |
| (d) | task 0, cancellation and enrollment on 10-18 | adjust 0 (tie: enrollment later) |
| (d) | task 0 as seeded | adjust −1.00, payoff 6438.42 (unchanged) |
| (c) | task 0: 2026-06-05 extra payment long cleared, 2026-10-16 held | in scope, hold 400.00 |
| (c) | two extra payments both inside their hold | out of scope: ordinary payoff quote (base), stated |
| (b) | task 1 plus an earlier unfeed R01 return 09-03 (auditor probe) | latest return's fee 10.09 (this policy); 09-03 fee at the base schedule amount, by the stated scope and reason |
| (a)/R7-1 | task 1 waiver | latest late fee, no fee payment: 8.37 (unchanged) |
| (a)/R7-1 | a fee payment posted on it / an earlier late fee | base clause: the whole part still unpaid |

### Mechanical proof-text sweep (scratch sweep.py + tiers.py)
- Labels: tier_taken regenerated (task 0 day_rate_split relabelled; re-run shows no relabel and no
  baseline_result change).
- Traces: every factor_trace has its current factor/effect label; every computation's all-baseline result
  re-evaluates equal.
- Edges and quotes: every edge copy equals the charter; every dossier quote is verbatim in a rule.
- Retired terms: grep found only "latest AutoPay record is" in task 1, which describes the courtesy AutoPay status
  test (a non-member; the charter still reads the latest AutoPay records there), so it is kept.
- Text edits: task-0 day-rate trace and necessity, task-0 hold trace (scope fact), task-1 courtesy amount tracing
  (latest late fee).

### XF recipe re-applied (payoff quote, returned fee, courtesy waiver)
1 scan clean (q_cancel_after/q_enroll_after belong to day_rate_split); 2 every order-of-steps sentence is intact,
and the new sentences stand alone; 3 the new quantities are defined in their own sentences; 4 every overwrite is
self-naming, restates the base content for every other case, and is verbatim in its rule (lint); 5
compute_basis clean; 6 RND unchanged; 7 tools unchanged; 8 probes above, with the same-date tie; 9 day-rate
tiers are distinct shapes (anchor at the paid-through date vs at the earlier record, sign +/−); 10 no factor id in
a tool name; 11 no cross-record N-day pairing; 12 realism: the boundaries carry business reasons, and
out-of-scope cases are ordinary base handling; 13 runtime unchanged; 14 proof text swept as above.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 8: gates 7/7 green

## Rework round 9 (revision_8 audit: PLS-R8-1)

Read: audits/policy_task/personal_loan_servicing/_difficulty.md, 0.md and 1.md (revision_8: task0=PASS,
task1=PASS, charter=PLS-R8-1).

### Change (loan_ext_refi_payoff_quote)
- Scope sentence, now in record terms: "This policy issues the refinance-purpose quote of a loan whose interest
  paid-through date is fewer than two whole calendar months before the quote date, whose AutoPay record shows at
  most one enrollment and at most one cancellation dated fewer than two whole calendar months before the quote
  date, and which has at most one payment of type additional_principal posted fewer than one whole calendar month
  before the quote date; a refinance-purpose quote on any other loan, one with a longer or busier recent record, is
  issued as an ordinary payoff quote under loan_evt_payoff_quote."
- Compute (plain bindings, each with a basis quote):
  - q_pt_recent = MONTHS(paid-through, NOW) < 2;
  - q_enroll_2m and q_cancel_2m = COUNT servicing events within 2 whole months;
  - q_extra_1m = COUNT additional_principal posted within 1 whole month;
  - q_issued = all four tests;
  - q_ordinary_interest = RND(principal × current rate × (days paid-through→quote + validity days) / 100 / 365, 2);
  - result = this policy's payoff if q_issued, else RND(principal + ordinary interest + fees, 2).
  - Factor bindings and the order-of-steps sentence are untouched.
- Why this is exact inside the scope:
  - MONTHS is monotone, so every date after a paid-through date under two whole months old is itself under two
    whole months old. Every AutoPay change after the paid-through date is therefore counted, and "at most one of
    each" is exactly the case the two-record day-rate split describes.
  - The hold windows (hold_days_standard / hold_days_after_return) are shorter than one whole calendar month, so
    with at most one additional-principal payment in that month no earlier payment can still be on hold; the
    latest-payment hold rule then covers every payment that could still come back.
- Task 0 is in scope: paid-through 2026-10-16; AutoPay records in 2 months: the 2026-10-18 cancellation only (the
  enrollment is 2025-06-20); additional-principal payments in the month: 2026-10-16 only (the other is 2026-06-05).
  Scored values are unchanged.

### Probes (scratch copies of the task-0 world at the quote step)
| world | issued | held | payoff |
|---|---|---|---|
| as seeded | yes | 400.00 | 6438.42 (scored) |
| auditor: second extra payment 100.00 on 10-19 (principal 5886.36, paid-through 10-19) | no (2 in the month) | — | 5912.06 ordinary quote, single reading |
| second extra payment two months back | yes | 400.00 | 6438.42 |
| second extra payment 25 days back | no | — | 6012.47 ordinary |
| re-enrollment 10-19 (one of each in 2 months) | yes | 400.00 | 6438.66 (cancellation→enrollment days at +discount) |
| a second cancellation in 2 months | no | — | 6012.47 ordinary |
| paid-through three months back | no | — | 6230.85 ordinary |
The out-of-scope side is the base ordinary quote, as for every other payoff quote; this is stated in the rule
and is the declared narrowing the coordinator chose for R7-2(c).

### Class sweep (conditions phrased through another rule's selection)
Every scope phrase in the six rules was listed: "this policy issues" (now defined by record counts), "a late fee
this policy assesses" (oldest unpaid installment, stated directly), "the latest returned payment" (direct), "the
latest late fee ... while no fee payment has posted" (direct), "a refinance application this policy sizes" and "an
enrollment this policy sets" (objects described directly in their opening sentences). No other member.

### Proof text
Task 0: hold trace (one additional-principal payment in the month), day-rate necessity text (paid-through age and
the one AutoPay record in two months), plain trace (scope tests). Re-check: tier labels current, every
factor_sensitivity and all-baseline result re-evaluates equal, no reference left to "still on hold under the hold
rule".

### XF recipe re-applied (payoff quote)
1 scan clean (the scope bindings are plain, not factor bindings); 2 the order-of-steps sentence is intact; 3 the
scope quantities are defined in their own sentence; 4 overwrites unchanged and self-naming through "this policy
issues", verbatim in the rule (lint); 5 compute_basis clean; 6 RND placement: the ordinary interest is rounded to
the cent as base says, and the result once; 7 tools unchanged; 8 probes above (boundary neighbours both sides); 9
method tiers unchanged; 10 no factor id in a tool name; 11 no cross-record pairing (counts only); 12 realism: a
short, settled recent record gets the refinance quote, any other loan the ordinary quote; 13 runtime unchanged; 14
proof text swept.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 9: gates 7/7 green

## Rework round 10 (renderer source scan audits/render_source/personal_loan_servicing/render_r1.md, items 1-7)

### Changes
1. Courtesy waiver:
   - New param courtesy_share_standard (0.5), also listed in the policy baseline params.
   - Baseline sentence: "The amount waived is the unpaid part times the courtesy share, which is
     courtesy_share_standard, rounded to the cent."
   - Order-of-steps sentence: the form sets the starting share and any amount kept back; points are added to the
     share; the share is held between 0 and 1; amount = unpaid × share − kept, never below 0; rounded once.
   - Form (bindings c_last_courtesy, c_form, c_form_start, c_form_kept):
     - fewer than 12 months: start courtesy_share_base and keep back repeat_courtesy_retained_usd;
     - 12–23 months: start courtesy_share_base;
     - otherwise: start courtesy_share_standard (the baseline).
   - `c_share = MN(1, MX(0, c_form_start + Σ points))`; `result = RND(MX(0, c_unpaid × c_share − c_form_kept), 2)`.
   - Task 1 keeps 8.37 and every per-factor baseline result; the all-baseline result moves 9.3 → 4.65.
2. c_fee_due moved into return_reason_point. Scan: every plain binding is quoted from a plain sentence; the
   remaining single-factor plain bindings (l_sched_fee, f_sched_fee, a_base_rate) are the factors' baseline
   expressions, so they are not members.
   - XF1 re-scan found f_ret_in_12m (first_return_relief) reading f_ret_date (bank_event_form); f_ret_date, the
     shared selection of the return being charged, is now a plain binding.
3. AutoPay:
   - Scope sentence for an active rate-setting hardship plan (one open plan per loan, hardship_agg_multi_holding),
     restating base loan_evt_autopay / loan_cmb_hardship_and_benefits.
   - `a_plan_rate_active = CFIELD('hardship','plan_interest_rate', status='active', loan_id=HID)`; the result is
     the plan rate when it is set.
   - The rule and the tier-2 ladder now read "equalled the base interest rate or was above it".
4. Returned fee: `f_ret_in_12m`; `f_other_returns_12m = COUNT(12 m) − (1 if the charged return is in the window
   else 0)`. The rule sentence states it.
5. Windows: the first-late and first-return sentences read "the time fewer than 12 whole calendar months before
   ...", and "in those months" became "in that time". Ladder sweep: every "in the N whole months before" became
   "fewer than N whole months before" (6 tiers). Task-1 tier labels relabelled (3, plus first_late_relief).
6. Conventions:
   - The shared convention sentence was removed from all six rules.
   - Each sentence counting whole months now carries "(whole calendar months being the difference in calendar
     months, less one when the later date's day of the month is smaller than the earlier date's)".
   - Each day-count sentence carries "(a count of days between two dates being the later date minus the earlier)":
     quote window, day-rate split, hold, pay-cycle form, AutoPay restored point.
   - Rules were re-wrapped; bases re-fitted mechanically (20 + 4 + 5); lint clean.
7. Refinance: "rounded up to a whole dollar (an amount already in whole dollars is kept as it is)". AutoPay: "the
   borrower enrolls personally, by phone," (the tool records request_channel phone). Refinance: "submitted by the
   borrower personally".

### Probes (scratch copies)
| item | world | result |
|---|---|---|
| 1 | task 1 as seeded (courtesy 21 months back) | start 0.30, share 0.90, 8.37 |
| 1 | courtesy moved beyond 24 months | start 0.50, share 1.00 (held), 9.3 |
| 1 | courtesy 5 months back | start 0.30, kept 5.00, 3.37 |
| 1 | each point factor alone against the all-baseline (both worlds, every policy) | moves the result (no inert factor) |
| 3 | active Temporary Rate Reduction Plan at 5.99 | 5.99 (plan rate governs) |
| 3 | active plan without a plan rate | 9.19 (this policy's rate) |
| 3 | completed TEM with pre-plan rate above base | rate base = modified rate, 8.69 |
| 4 | charged return 13 months old | others 0 (was −1), first-return share applies |
| 5 | late fee dated exactly 12 whole months before | not counted (share 0.90) |
| 5 | late fee 11 whole months before | counted (no share) |
| 7 | amount financed ceiling 6518.26 | 6519; a whole-dollar amount stays as it is |

### Mechanical sweeps
lint (quotes, bindings ↔ basis, replaced_by, policy_source, baseline rule) clean; XF1 clean; XF10 clean; gating
(parameter factor alone vs all-baseline) clean; tiers, per-factor and all-baseline results, trace labels, edge
copies and dossier quotes clean; retired-term grep (next whole dollar, enrolls in person, in those months,
waivable, credited install, all baselines 9.3) clean.

### XF recipe re-applied (all six policies touched)
1 scans clean (see above); 2 the courtesy order-of-steps sentence is restated once with its order (start, points,
hold, multiply, keep back, round); the other order sentences are intact; 3 the courtesy share and the waived fee's
due date are now defined where their users are; 4 the AutoPay scope restates the base content and is verbatim in
the rule; 5 compute_basis re-fitted and clean; 6 RND unchanged except the courtesy result (single rounding at the
end, as stated); 7 tools unchanged (the AutoPay docstring already said "by phone"); 8 probes above; 9 form tiers:
subtract-kept / start-low / start-standard, distinct; 10 clean; 11 n/a; 12 realism: a first courtesy in two years
starts from a larger standard share and repeats start lower, and an active plan rate governs, as in base; 13
runtime unchanged; 14 proof text swept.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 10: gates 7/7 green

## Rework round 11 (revision_10 audit: PLS-R10-1 (a)(b); XF#14 in both task files)

### Changes
- Courtesy waiver:
  - Params: courtesy_share_standard removed; repeat_courtesy_fraction 0.9 added; baseline params
    [courtesy_share_base].
  - Baseline sentence: unpaid part × courtesy share (courtesy_share_base).
  - Order-of-steps sentence: the form sets the figure the share is taken from in place of the unpaid part; points
    are added to the share, which is held between 0 and 1; amount = figure × share; rounded once.
  - Form (c_form → c_form_figure; bindings c_last_courtesy, c_form, c_form_figure): fewer than 12 months: MX(0,
    unpaid − keep-back); 12–23 months: repeat_courtesy_fraction × unpaid; otherwise (standard): unpaid. These are
    three shapes (subtract / multiply / identity); the form reads only c_unpaid and the history.
  - `c_share = MN(1, MX(0, courtesy_share_base + Σ points))`; `result = RND(c_form_figure × c_share, 2)`.
  - The monotone order holds whenever the unpaid part ≤ 50 (late fees ≤ 30).
- AutoPay:
  - modified_rate_base (value-picking) is replaced by enrollment_rate_form (method, cross hardship). The acting
    base is fixed: standard = base rate − (grade discount + steps).
  - Tier 1, completed TEM: MX(program floor via CPARAM modified_rate_floor_percent, standard − (pre-plan − plan
    rate)).
  - Tier 2, no completed TEM and an AutoPay return fewer than 3 whole months before: base − grade discount
    (steps withheld).
  - Otherwise: standard.
  - Plain a_total_discount and a_standard; result applies the form (with the active-plan-rate scope from round 10
    kept first).
  - The rule sentence, assembly sentence and >0 sentence were updated, and the cross-category note/reads trimmed.
  - A first draft used a broken hardship plan for tier 2. It was dropped: check_compute requires seeded X-history
    rows for it, and a broken plan would wrongly undo a completed modification.
- Scored values:
  - Task 0 unchanged (6438.42 / 6519).
  - Task 1: late fee 9.3, returned fee 8.58 and rate 9.19 unchanged. The courtesy waiver 8.37 → 7.53 (forced:
    the form needs shapes, the baseline must keep the share, and task 1 must sit on a non-standard tier).
- Task-1 proof text regenerated:
  - eval amount 7.53;
  - courtesy trace, sensitivities (8.37 / 5.02 / 8.37 / 5.86 / 6.70 / 6.70), all-baseline 2.79;
  - amount tracing, dossier waiver and rate paragraphs, order_uniqueness, three skip effects (0.0 / 8.37 / 5.02),
    dossier recomputation line;
  - AutoPay trace, sensitivity (enrollment_rate_form → 12.19) and rate tracing.
- Retired-phrase regeneration in both task files: "in the N whole months (before)", "in the last N whole months",
  "in the whole month before" became "fewer than N whole months before"; "in person" became "personally" (4
  strings in task 0, 7 in task 1).

### Probes (scratch copies)
| member | world | result |
|---|---|---|
| courtesy | task 1 (courtesy 21 months back) | figure 0.90 × 9.3 = 8.37, share 0.90 → 7.53 |
| courtesy | courtesy 5 months back | figure 4.30 → 3.87 |
| courtesy | no courtesy in 24 months | figure 9.30 → 8.37 |
| AutoPay | task 1 (completed TEM) | 12.19 − 3.00 = 9.19 (floor 5.99 not reached) |
| AutoPay | modified rate 6.20 | 12.19 − 6.29 = 5.90 → floored 5.99 |
| AutoPay | no TEM, AutoPay return 2026-09-08 | steps withheld: 12.49 |
| AutoPay | no TEM, no recent AutoPay return | standard 12.19 |
| all | every parameter factor alone vs the all-baseline (both worlds) | moves the result |

### Mechanical sweeps
lint clean (quotes, bindings ↔ basis, replaced_by, policy_source, baseline rule, unused params); XF1 clean;
isolated-factor gating clean; method count per computation ≥ 1 (quote 2, refi 1, late 1, returned 1, AutoPay 1,
courtesy 1), parameters ≥ 2; tier labels, factor sets, per-factor and all-baseline results, trace labels, edge
copies and dossier quotes clean; retired-term grep clean.

### XF recipe re-applied (AutoPay, courtesy waiver; task files)
1 scans clean; 2 order-of-steps sentences restated once with their order (courtesy: figure, points, hold,
multiply, round; AutoPay: steps, standard, form, round); 3 the form-only quantities sit in the form bindings and
the shared ones are plain; 4 overwrites unchanged and verbatim; 5 compute_basis clean; 6 single rounding at the
end; 7 tools unchanged; 8 probes above; 9 method tiers are distinct shapes (subtract / multiply / identity;
floored reduction / steps withheld / standard); 10 no factor id in a tool name; 11 n/a; 12 realism: repeat
courtesies waive less, a completed modification's rate reduction survives AutoPay re-enrollment with its floor,
and a recent AutoPay bounce withholds loyalty steps; 13 runtime unchanged; 14 proof text regenerated as above.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 11: gates 7/7 green

## Rework round 12 (revision_11 audit: PLS-R11-1, PLS-R11-2, task-1 stale necessity)

### Changes
- AutoPay enrollment_rate_form tier 2 (no completed TEM, AutoPay debit returned fewer than 3 whole months before):
  was "the steps are withheld"; now "autopay_return_surcharge_percent (new param 0.25) is added back to the
  standard rate, never taking it above the loan's base interest rate" (rule sentence, its basis copy, ladder
  method).
  - Compute tier 2: `MN(a_base_rate, a_standard + K('autopay_return_surcharge_percent'))`.
  - Fall-through ladder text: "the standard rate, unchanged".
- AutoPay overwrite replaced_by and its rule copy: "the rate in force from the enrollment date is the one set
  below from the loan's base interest rate, the grade's AutoPay discount and the AutoPay discount steps".
- tasks/1.json evaluation_criteria[6].necessity: "the AutoPay rate base" became "the AutoPay enrollment rate form
  (the modification's rate reduction and its program's floor)".
- Scored values unchanged: task 0 6438.42 / 6519; task 1 9.3 / 8.58 / 9.19 / 7.53. Task 1 sits on tier 1
  (completed TEM), so no proof figure moved.

### Probes (scratch copies of task 1)
| world | form | rate | each step factor's baseline |
|---|---|---|---|
| as seeded (completed TEM) | 1 | 9.19 | 9.29 (steps bear weight) |
| TEM removed, AutoPay return 2026-09-08 (auditor probe) | 2 | 12.44 (= 12.19 + 0.25) | 12.54 each (steps bear weight; was inert) |
| same, base rate 12.49 | 2 | 11.94 (cap at base not reached) | — |
The cap at the base rate keeps AutoPay from raising a rate (it binds only where the total discount is below the
surcharge).

### Sweeps
- Ladder sweep of all six policies for tiers that name, read or switch off another factor's quantity: none left
  (refi_sizing_form's "refinance fee percent" is a baseline quantity; the floors at 0 are edges of their own
  figure).
- Charter and both task files grepped for retired terms (rate base, steps withheld, courtesy_share_standard,
  starts from, waivable, hardship_rate_form, modified_rate_base, in the 12 whole, in the last, in person): clean.
- lint (incl. unused params) clean; XF1 clean; isolated-factor check clean; tier labels, per-factor and
  all-baseline results, edge copies and dossier quotes clean.

### XF recipe re-applied (AutoPay)
1 scans clean; 2 the order-of-steps sentence is unchanged; 3 the surcharge is defined in the form's own
sentence; 4 replaced_by is self-scoped and verbatim in the rule; 5 compute_basis clean; 6 rounding unchanged; 7
tools unchanged; 8 probes above; 9 tiers are distinct operations (floored reduction / capped surcharge /
identity); 10 clean; 11 n/a; 12 realism: a recent AutoPay bounce costs part of the discount until the record is
clean, and never more than the full discount; 13 runtime unchanged; 14 proof text swept.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY: only the
six unlock tool names miss (pre-publication, expected).
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 12: gates 7/7 green

## Rework round 13 (proof-only; audits/policy_kb + audits/runtime_context, item S4)

Read: audits/policy_kb/personal_loan_servicing/0.md, 1.md; audits/runtime_context/personal_loan_servicing/0.md,
1.md. Only S4 is routed here (K1/K2 to the renderer; S1/S3 not routed; S2 BLUEPRINT-KNOWN).

### Changes (tasks/1.json only)
- Late fee: computations[0].factor_trace (plain) and evaluation_criteria[15] amount tracing changed from
  "12.4627 x 0.90 x 0.90 x 0.95 x 0.97 = 9.2970" to "12.462745 (unrounded) x 0.90 x 0.90 x 0.95 x 0.97 = 9.3024"
  (exact 15.00 × 274.87 / 330.83 × shares = 9.30238).
- Same class, returned fee: computations[1].factor_trace (plain) and evaluation_criteria[17] amount tracing changed
  from "= 8.5805" to "12.462745 (unrounded) x 0.85 x 0.90 x 0.90 = 8.5806" (exact 8.58060).

### Sweep
A scratch parser recomputed every inline arithmetic claim (operator chains and less/plus chains) in both task
files, outside initial_state/db_closure: 34 operator claims plus the word-operator chains. After the fix, 0 differ
beyond their stated precision. Hand-checked the task-0 plain lines: quote interest 5979.24 × (14.49 × 25 − 1.00) /
100 / 365 = 59.18; payoff 6438.42; fee percent 1.24; 6438.42 × 1.0124 = 6518.26 → 6519.

### Frozen files
loan.extended.yaml sha256 616075d9d73eca17…, task_tools.py 30da55a2b8320d8e…, unchanged (verified before and after).
Scored values unchanged.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY OK.
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 13: gates 7/7 green

## Rework round 14 (seed-only; KB revision_3 cross-product re-judge S5-S10 + own loan rows)

Read: audits/policy_kb/personal_loan_servicing/0.md, 1.md; audits/runtime_context/personal_loan_servicing/0.md,
1.md; docs/line (billing/payment terms, interest and annual fee, rate schedule, payments and fees, late-fee and
returned-fee booking/amount/figuring/share docs), docs/pos (late fee amount/charging/level/partial
payment/principal band), docs/hardship rows as cited by the re-judge.

### Seeds changed
FlexLine ledgers (scratch generator):
- Interest: Σ daily end-of-day balance over the cycle (prev closing, closing] × 25.24/36500, rounded to the cent.
- Statement closing at due − 25 days; minimum payment max(35, 3% of the statement balance), paid on the due
  date; draw fee 2.5%.
- Annual fee 39.00 on the open-date anniversary (FlexLine Standard does not waive year 1).
- Fees by the docs (half-even).

Task 1 FlexLine:
- annual fee added 2025-11-18 and statement 2026-09-10 added;
- the 2026-09-05 minimum 57.49 bounced (R02) 2026-09-08;
- returned fee 15 × 0.85 × 1.00 × 0.90 × 1.00 = 11.475 → 11.48;
- late fee 2026-09-16: 25% × 57.49 = 14.37 (below 25) × balance tier 0.80 × grace 1.00 × history 0.80 × tenure
  1.00 = 9.20;
- holding: outstanding 1976.71, past due 57.49, minimum due 116.52 (the 2026-09-10 cycle minimum plus the
  amount past due), next due 2026-09-05 (the late-fee booking doc charges the record's next due date).

Task 0 FlexLine:
- annual fee 2026-01-15 and statement 2026-10-16 added;
- 2025-08-10 minimum 44.82 missed (no payment assumed in the 2025-08-16 interest);
- late fee 2025-08-21: 25% × 44.82 = 11.20 × 0.80 × 1.00 × 0.80 × 1.00 = 7.17;
- catch-up payment 2025-08-26 = 44.82 + 7.17 = 51.99;
- holding: outstanding 1889.75, minimum due 56.69, next due 2026-11-10, past due 0.

Other products:
- PracticePay (task 1): late fee 2025-03-05 = 20.00 × 0.95 × 1 × 0.9 × 1 = 17.10; payment 2025-03-06 = 217.10.
- Hardship: task 0 STPD closed_date 2026-01-23; task 1 TEM closed_date 2024-05-05.

Own loan rows (task 0, closed loan 0031d905):
- late fee 2024-02-05 15.69 → 15.71 (5% of 314.15, schedule_a, Grade C).
- current rate 15.49 (AutoPay ended at payoff, reason loan_closed).
- The AutoPay enrolment/cancellation records for this loan were tried and then removed: replay_tasks requires
  initial_state = db_closure, and no gold read touches that loan's servicing events. The installments of every
  loan were checked as level payments.

db_closure is mirrored. New ids are uuid4 (re-minted after a replay flag). seed_consistency entries were added,
then removed together with the rows.

### Gold and proof text (task 1)
Real-tool replay:
- late fee 9.3 → 9.26 (15 × 274.87 / 332.36 = 12.4054 × 0.746415);
- returned fee 8.58 → 8.54;
- AutoPay rate 9.19 unchanged;
- waiver 7.53 → 7.50, on late-fee line ltx_5f8e8ff5f60a (the id is re-derived because the amount changed).
- Sensitivities:
  - late fee 11.2 / 10.29 / 10.29 / 9.75 / 9.55;
  - returned fee 10.33 / 10.05 / 9.49 / 9.49;
  - courtesy 8.33 / 5.00 / 8.33 / 5.83 / 6.67 / 6.67, all-baseline 2.78;
  - skips 0.0 / 8.33 / 5.00.
- Swept: computations, eval args and tracing (steps 15, 17, 21), objectives, closure texts, dossier (FlexLine fee
  amounts, PracticePay fee, TEM date). Task 0 seed_consistency late-fee figure updated.
- Inline arithmetic re-verified: 34 claims, 0 issues. Mechanical sweep (tiers, per-factor and all-baseline results,
  edges, quotes) clean.

### Frozen files
loan.extended.yaml 616075d9d73eca17…, task_tools.py 30da55a2b8320d8e…, unchanged.

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY OK.
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 14: gates 7/7 green

## Rework round 15 (proof-only; KB revision_4 note S11)

### Changes (tasks/1.json text only)
- Courtesy waiver:
  - The form figure is now stated unrounded everywhere: "9.26 x 0.90 = 8.334 (unrounded)", in the factor trace,
    the plain trace, the step-21 amount tracing and the dossier.
  - Each point-factor baseline line shows "8.334 x share = … -> result" (5.0004 → 5.00, 8.334 → 8.33, 5.8338 →
    5.83, 6.6672 → 6.67).
  - The form baseline shows "9.26 x 0.90 = 8.334 -> 8.33".
- Same class: the pay-cycle / bank-event figure "12.4054" became "12.405374 (unrounded)" (step 15 and 17
  tracing, factor traces, dossier), matching the plain lines that already used 12.405374.

### Sweep
A scratch checker recomputed every inline product (42 claims after the edit) and flagged any intermediate stated
at one precision and used at another within the same line: 0 issues in both task files. initial_state hashes
2921c223072b7ad7 / 9acb2259ed964dd5 are unchanged, as are loan.extended.yaml 616075d9d73eca17… and
task_tools.py 30da55a2b8320d8e…. Scored values unchanged (task 0 6438.42 / 6519; task 1 9.26 / 8.54 / 9.19 /
7.50).

### Final gate run (difficulty, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY OK.
- Scratch /tmp/personal_loan_servicing_0067/ removed.
REWORK round 15: gates 7/7 green
