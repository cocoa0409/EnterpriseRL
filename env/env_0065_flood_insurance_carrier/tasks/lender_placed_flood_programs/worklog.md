# lender_placed_flood_programs — instantiation worklog (env_0065, M=2, round 1)

## Draw
task 0: prerequisite_problems 3, factor_counts [5,4,6,6]; task 1: prerequisite_problems 1, factor_counts [5,4].

## Charter (forceplaced.extended.yaml, 6 extended policies) and tools (task_tools.py)
| policy | tool (owner) | computes | factors | task |
|---|---|---|---|---|
| forceplaced_ext_renewal_premium | renew_certificate_c91c4d46 (agent) | annual_premium | 6 (2 method, 1 cross dwelling) | 0 |
| forceplaced_ext_placement_premium | issue_residential_certificate_c6c06832 (agent) | annual_premium | 6 (1 method, 1 cross dwelling multi-source) | 0 |
| forceplaced_ext_overlap_credit | cancel_certificate_on_evidence_b90eab97 (user) | credit_amount | 5 (2 method) | 0 |
| forceplaced_ext_credit_refund (root t0) | refund_program_credit_d16acbc2 (agent) | refund_amount | 4 (1 method, 1 multi-source) | 0 |
| forceplaced_ext_commercial_placement_premium | issue_commercial_certificate_61c928bb (agent) | annual_premium | 5 (1 method, 1 cross nfipcom multi-source) | 1 |
| forceplaced_ext_loan_event_credit (root t1) | cancel_certificate_for_loan_event_5b69d826 (user) | credit_amount | 4 (1 method) | 1 |

Prerequisite edges: credit_refund -> overlap_credit / renewal_premium / placement_premium (value_input, state form; one negated, two affirmative sentences); loan_event_credit -> commercial_placement_premium (value_input, state form, affirmative).

## Key structural decisions
- Holding = master program; per-certificate figures are selected by plain bindings stated in the rules (certificate whose term expires today; latest acceptable evidence; latest first notice; latest issue entry) and chained LATEST reads keyed on the selected certificate/loan. Placement and credit schedules are scoped (self-naming overwrite replaced_by) to the selected object; other cases stay under the base rule.
- Payoff/transfer/LOMA facts exist only in the caller's words, so the loan-event credit can only be a root; the residential and commercial placements are separate policies so both tasks get a discoverable prerequisite.
- Siblings under the refund commute: experience modifiers divide claims by lender payments (not charges); no prerequisite reads a row another writes (verified by reversed-order simulation).
- Overwrites: placement/renewal/commercial placement each retire the base premium formula for their own case and name the siblings; overlap credit retires the flat/pro rata sentence (restating base treatment for other evidence); loan-event credit retires the base PRO_RATA sentence and, for loan-event cancellations only, the evidence-deadline clause (restating it for evidence cancellations); credit refund retires the refund-on-request sentence (termination refund stays in full).

## Results (handling-time recomputation = gold)
task 0 (2026-10-15): renewal 3,965.62; placement 1,186.15; overlap credit 2,710.40 (user); refund 1,570.42 (baseline 5,794.66). Edge deletions: refund 658.24 / 5,536.04 / 2,756.57.
task 1 (2026-10-13): commercial placement 4,105.72; loan-event credit 2,859.29 (user) (baseline 3,149.59); without the placement 2,289.68 on the wrong certificate.

## Revisions
- Refund: pending-placement reserve replaced by a recent-credit hold (a pending first notice would have become the placement's anchor); clearing-hold payment threshold 6.
- Task 0: find_dwelling_policies read added for closure; writes at steps 10/12/14/16.
- Loan-event credit: term retention -> re-placement retention (history must bear weight); overwrite retiring the evidence-deadline gate for loan events (check_solvability); since the checker treats that retirement charter-wide, task 0's step 14 keeps the deadline as a declared base precondition only.

## Known risks for the audit
- Account-level refund holds and the cancellation retentions are company schedules (no federal source); realism is argued in each task's rationale.
- Selection-by-latest anchors are DSL-limited; the scope sentences say so in business words.
- check_traceability: only the six hidden tool names lack a source (KB not yet rendered); no other argument is unsourced.

## Gate block (final, repository root)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
  [INFO]
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
  [FAIL]
TRACEABILITY NOT OK
```
Traceability misses (expected pre-render): unlock tool_name for the 6 hidden tools only (task 0: 4, task 1: 2).

ROUND 1: gates 7/7 green

## REWORK round 2 — class sweeps (XF checklist)
| class | sweep across the charter | result |
|---|---|---|
| A1-A5 factor structure | every factor of the 6 policies acts on a baseline quantity (rated amount, renewal premium, overlap credit, refundable credit, loan-event credit); assembly only in `rated`/`r_rated`/`result`; no factor binding reads another factor's binding (tables per policy in each task's design_rationale) | no factor reads another; the replaced refund and loan-event factors read only their own records |
| A3 order | overlap credit: generic sentence "every amount added to it is added before any amount kept is taken off"; renewal: loss load added after the minimum; refund/loan-event: each hold/retention "without taking it below zero", rounding as the last step | single order |
| A6 method tiers | loss_load graduated vs flat vs 0 (meet only at the 25 percent boundary); renewal_reserve rate method vs minimum-per-notice vs 0 (meet only at the threshold); earned_method, experience, current/prior-term pairs as tabled in task 0 section 6 | distinct |
| B9 basis quotes | scratch sweep: every compute_basis quote, baseline sentence, policy_source and replaced_by is verbatim in its own rule | 0 misses |
| B10 rounding | every rule rounds "half to even to the cent" where the compute uses RND (Python round); refund and loan-event credit round as the last step | matches |
| C12 reads/probes | anchors: latest first notice (placements), certificate expiring today (renewal), latest acceptable evidence (overlap), latest issue entry (loan-event); scope sentences send any other object to the base rule; decoys and absent records listed in each task's probe table | unchanged |
| C13 prerequisite scope | four sentences now name exactly their conditions: credit on a cancellation for confirmed borrower coverage; uncancelled certificates; certificate issued since the loan's latest first notice and evidence since that notice | no earlier cycle satisfies a condition |
| D14 overwrites | coverage-amount overwrites added (placement and commercial placement: lowest-of sentence, siblings named; renewal: recompute sentence); evidence-bar overwrite scoped in both placements, siblings named; premium overwrites rescoped to named tiers | every departure declared |
| E15 cross rows | dwelling and nfipcom rows rebuilt to their charters (RFA on risk plus ICC, anniversary terms, payments on term start) | producible |
| E16 realism | young-program retention and the count-split renewal reserve replaced; tier scopes exclude Gap, Replacement Cost, Manufactured Home and Commercial Building and Contents from schedules not built for them | see audit O7/O8 kept as observations |

## REWORK round 2 claims
- P1: closed by declared overwrites of forceplaced_coverage_amount in the placement, commercial placement and renewal schedules and by scoping them to the Residential Mandatory Amount / Commercial Building tiers.
- P2: closed by anchoring the refund's three prerequisite sentences/conditions and the loan-event sentence/condition to the loan's latest first notice, the confirmed-coverage cancellation reason and uncancelled certificates; base evidence bar overwritten (scoped) in both placement schedules.
- P3: closed by removing the issuing-reply reference from the loan-event tool's certificate_number description.
- P4: closed by defining "the earliest term the credit reaches" and the effective date / flat-or-pro-rata rule in one reading; tool enum texts rewritten.
- F1: closed by rebuilding the dwelling (task 0) and nfipcom (task 1) cross-category rows to their owning charters.
- F2: closed by replacing the refund renewal-reserve tiers (rate vs minimum-premium method by average notice amount), replacing the loan-event young-program retention with a fully-earned certificate fee retention, and scoping the band ladders and the commercial schedule to the tiers they price.
- T0-1: closed with P4 (single reading of the cancellation date and basis).
- T0-2: closed by rewriting task 0's no_user_hint.
- T0-P2, T1-P2: closed with P2.
- T0-F1, T1-F1: closed with F1.
- T0-F2, T1-F2: closed with F2.
- T1-P3: closed with P3.
- Observations: O1 (graduated heavy loss tier), O2 (order sentence), O3 (rounding last), O4 (monthly wording), O-persona (generic hand-over line), O10 (tier scope) closed; O5/O11 superseded by P4 or left as designed; O6, O7, O8, O9, O13 recorded unchanged.

### Gate block (round 2)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- R2-1: closed by naming the residential renewal schedule's renewal-notice rule in the coverage-amount overwrite tails of the residential and commercial placement schedules, and by naming both placement schedules in the renewal schedule's tail (base recompute kept only for the renewal of every other certificate); every "every other ..." / "any other ..." tail in the charter was swept (premium, coverage-amount, evidence-bar, overlap, loan-event and refund overwrites) and each excludes all sibling cases of the clause it retires.
- T1-R2-1: closed by rewriting task 1's find_forceplaced_programs necessity to the reads the charter actually makes; task 1 and task 0 proof text swept for other references to removed factors (none besides dated rework-log lines).

### Gate block (round 3)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- F1: closed by removing the loan-event schedule's overwrite of the evidence-deadline clause (it retired nothing) and its rule sentence; the loan-event subject is now the premium credit it computes, so the deadline gate stays in force for evidence cancellations only; task 0 carries the deadline again as a required time gate (temporal_feasibility).
- F2: closed by restating the base premium formula in the out-of-scope tails of the residential placement, residential renewal and commercial placement schedules (rule and replaced_by); class sweep: every other overwrite tail (coverage amount, evidence bar, overlap, loan-event, refund) restates its in-force base content, and the refund tail no longer defers to "the base rule".
- F3: closed by stating the owned-building factor's record scope as the lender's own NFIP General Property Form or RCBAP premium payments, equal to the compute's scope.
- F4: closed by stating every same-day tie rule the compute applies (first entered in the program's records) for the placement, commercial placement, overlap, loan-event and renewal selections, the renewal-entry precedence, and the latest renewal notice.
- F5: closed by stating the zero-or-below loss-load tier, the notice-on-or-before-lapse retroactive tier (wording aligned to "from the lapse date to that notice date"), the zero overlap credit when the evidence names no certificate (compute guarded), and the absent-record outcomes (no first notice, no issue entry, no renewal notice).
- F6: closed by narrowing the refund's renewal and placement prerequisite sentences and conditions to what the depended-on schedules price (latest term expiring today; the loan on the most recently mailed first notice).
- XF 8-14 re-applied charter-wide: basis/baseline/source/replaced_by quote sweep clean; month and day counts match the rules' words; overwrite tails restate in-force content; proof text swept (task 0 revision (d), task 1 base-invariant card and revision (b), necessity texts).

### Gate block (round 4)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- R4-1: closed by rewriting the renewal tie sentence to the compute's selection (renewal entry before issue entry; among the same kind, the latest processing date; first entered on a processing-date tie).
- R4-2: closed by scoping the renewal premium overwrite (rule head and replaced_by) to renewals of certificates carrying a renewal notice on file, so the no-notice carve-out falls under the restated base premium formula; class sweep: placement, commercial, overlap and loan-event absent-record outcomes already lie outside their scope sentences.
- T1-R4-1: closed by rewriting task 1's find_nfipcom_policies necessity to the factor's full scope (General Property Form or RCBAP); no other narrower statement found.
- Renderer render_r1 F1-F6: re-verified closed (quote/replaced_by sweep clean, no tail defers to "the base rule", tie and absent-record sentences present, prerequisite scopes unchanged).

### Gate block (round 5)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- R5-1: closed by stating and computing the renewal schedule's outcomes for a selected certificate carrying a cancellation entry (no renewal, zero premium), for no certificate expiring today (zero) and for a certificate with no renewal notice (amount from its latest issue or renewal entry, premium overwrite scope restored to every renewal on the tier), with guards so no case errors; the refund's renewal prerequisite and condition now name the same selection and exceptions.
- Adversarial probe sweep (every read, scratch copies): added stated and computed outcomes for no acceptable evidence and for evidence naming an already-cancelled certificate (overlap; refund overlap edge aligned), for a latest issue entry already cancelled and for no issue entry (loan-event), and for no first notice (both placements, computed as zero without error); all other probes (later-processed decoys, earlier cycles, voided payments, window-edge payments, notice before lapse, no renewal notices) gave one answer under rule and compute.
- Renderer render_r1 F1-F6 and earlier rounds: re-verified (quote/replaced_by sweep clean, no deferral to "the base rule", ties and absent records stated).

### Gate block (round 6)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- R6-1: closed by scoping the renewal premium overwrite and schedule to a day when exactly one issue or renewal entry of the program expires (exact-date COUNT), restating the base premium formula for each renewal on a day when two or more expire (schedule gives zero, no compute error), keeping the single-cancelled-certificate outcome (no renewal, zero), and widening the refund's renewal prerequisite and condition to every certificate whose latest term expires today other than a cancelled one or one with acceptable evidence.
- Second-record class (coordinator route), every read and its handling:
  - residential and commercial placement: fn_loan (latest first notice) — (b) scope sentence names "the loan named on the most recently mailed first notice", tail restates the base formula for every other placement; fn_req, band_req, retro_lapse, retro_notice — (a) filtered by loan_number=fn_loan, latest notice of that loan as the rule says; repeat_count — (a) loan_number filter, counts every earlier issue as the rule says; vol_count, exp_*, reo_paid/branch payments — aggregates over the whole set the rule names.
  - renewal: cert (rn_cert/is_cert) — (b) scoped by n_today == 1 (this round); rn_req/rb_req — (a) certificate_number=cert, latest renewal notice, fallback latest issue or renewal entry as stated; zone_code — (a) the certificate's single issue entry; lc_net — (a) claims filtered by certificate; lc_limit — (a) renewal entry filtered by certificate and today's expiration; seq_count, c_cancel — (a) certificate filter; rx_*, ro_* — aggregates over the named set.
  - overlap credit: ev_cert (latest acceptable evidence) — (b) scope sentence names it, tail restates base treatment for other evidence; ev_eff, le_recv — (a) certificate filter on acceptable evidence; current term (latest renewal else issue) — (a) certificate filter, latest entry as stated; prior term — (a) exact filter expiration = current start; sp_orig — (a) the single issue entry; tr_count, ev_cancel — (a) certificate filter.
  - refund: g_* sums, ch_*, rr_*, rc_*, wb_count — aggregates over every entry the rule names (no single-record selection).
  - loan-event credit: c_cert (latest issue entry) — (b) scope sentence names it, tail restates base PRO_RATA for other loan events; c_prem, c_start, c_exp, fk_prem, lp_issued — (a) certificate filter on its single issue entry; c_claimnet, c_cancel — (a) certificate filter; lt_loan/lt_count — (a) loan filter.

### Gate block (round 7)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 7: gates 7/7 green

## REWORK round 8 claims
- R7-1: closed by withdrawing the count-switched renewal pricing: every renewal the schedule processes is priced by the one schedule; the renewal processed today is keyed to the certificate whose current-term entry expiring today carries the latest processing date (renewal entry before issue entry, first entered on a tie); a cancelled certificate so selected is not renewed and nothing is booked; every other certificate expiring the same day is referred to Tidemark's renewal desk with nothing booked today (stated in the rule, the scope sentence and the premium overwrite tail and computed by the same selector); the refund's renewal prerequisite and condition name the same certificate.
- R7-2: closed by reading the loan-event credit's premium, start and expiration from the credited certificate's term in force (its latest renewal entry, else its issue entry) by exact certificate number, in rule, baseline and compute; the fee and late-placement factors keep reading the issue entry by design.
- Proof text swept: task 0 renewal-edge quote, why_false, necessity and the round-7 rationale line (marked superseded); task 1 rationale note added.

### Gate block (round 8)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 8: gates 7/7 green

## REWORK round 9 claims
- R8-1: closed by the coordinator DECISION's renewal branch: the renewal schedule now figures the program renewal rate per 100 in effect on the renewal date from program-level records only, and every eligible certificate of the program whose current term expires today renews today at its renewed limit times that one rate (one method, computed exactly, no certificate selection, no referral, base renewal timing untouched); the renewal tool records the rate applied; the refund's renewal prerequisite and condition cover every such certificate.
- R8-2: closed by measuring the late-placement retention on the issue lag (issue processing date against the start date shown on that issue entry), in rule, factor ladder and compute.
- Proof text swept: task 0 renewal call arguments and tracing, computations, prerequisite closure (edge sentence, why_false, flips_to_true_by, order_uniqueness, deletion figures) and design_rationale current-design sections; dated rework sections marked as history; task 1 rationale note added.

### Gate block (round 9)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 9: gates 7/7 green

## REWORK round 10 claims
- R9-1: closed by making the renewal's claim frequency load count claims reported under the program in the last 12 months, each claim counted once by its first notice of loss (no payment items, no voided items), identically in rule, ladder, compute and inputs; class sweep: the placements' and renewal's experience claim-count rule is an existence test and unaffected.
- T0-R9-1: closed by rewriting the claims read's necessity, the business-object card sentence and the realism note to the current renewal design; the dated rework sections stay marked as history.

### Gate block (round 10)
```
=== check_extended
EXTENDED OK
=== check_task_tools
TASK TOOL CONTRACT OK
=== replay_tasks
REPLAY OK
=== check_solvability
SOLVABILITY OK
=== check_compute
COMPUTE OK
=== check_grounding
GROUNDING OK
=== check_cross_fire
SCOPE OK
=== check_cache_diff
CACHE-DIFF INFO (optional; no correctness gate)
=== check_traceability
TRACEABILITY NOT OK
```
Traceability misses: unlock tool_name for the 6 hidden tools only.

REWORK round 10: gates 7/7 green

## REWORK round 11 claims
- N1: the renewal rule's "unless" list now carries the base non-renewal cases — a cancellation entry (among them a loan paid off, a servicing transfer or a building removed from the Special Flood Hazard Area, the record that the loan is no longer serviced by the lender with the building in that area), acceptable borrower evidence, or a terminated program whose run-off certificates stay in force to expiration and do not renew; the refund's renewal prerequisite sentence and condition carry the same exclusions (run-off certificate of a terminated program / program status not terminated), synced into task 0's prerequisite closure and rationale; the program renewal rate compute is unchanged.
- N2: the renewal tool docstring no longer claims the rate is recorded; it states that the rate supplied is reported in the confirmation only and is not stored on any entry, which is what the body does; the stale rationale sentence in task 0 was corrected the same way.
- N3: each sibling scope sentence now claims only the sibling's own scope — the residential and commercial placement schedules each cover the loan named on the most recently mailed first notice of a program on their tier, and the renewal schedule covers every renewal on the Residential Mandatory Amount tier — in the rule and replaced_by of the residential placement, commercial placement and renewal policies.
- Gates re-run: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire green; check_cache_diff info only; check_traceability shows only the expected unlock tool-name misses.
REWORK round 11: gates 7/7 green

## REWORK round 12 claims
- SRC-1: the renewal schedule now declares an overwrite of the base renewal policy's clause "the limit and premium are recomputed from the balances reported at renewal"; its scoped replaced_by (also a sentence of the renewal rule) covers only renewals on the Residential Mandatory Amount tier and restates the base recompute for every other renewal. No other extended policy overwrites that clause.
- SRC-2: class sweep of base RULE sentences that state pro rata: both are already overwritten with a scoped replaced_by (the evidence-cancellation FLAT/PRO_RATA sentence by the overlap schedule; the loan-event "Each uses its tier's refund method, PRO_RATA" sentence by the loan-event schedule). The remaining statements, premium_proration_basis DAILY_PRO_RATA and the three loan-event refund-method parameters PRO_RATA, exist only as frozen base variant-parameter meanings and values. They are left untouched; the coordinator logs them.
- SRC-3: the refund scope sentence (rule and replaced_by) now states only the rule's own case: the refund paid on request is the refundable credit figured by the refund schedule, and a terminated program's balance is still refunded in full. It no longer announces held-back amounts.
- XF class D14 table (base sentence departed from -> declared overwrite): coverage_amount renewal recompute -> renewal; renewal limit/premium recompute -> renewal (new); effective_date_premium formula -> residential placement, commercial placement, renewal (siblings each exclude the others by name); coverage_amount lowest-of -> both placements; notice_and_placement evidence bar -> both placements; evidence_cancellation FLAT/PRO_RATA -> overlap; loan_event_cancellation PRO_RATA -> loan-event; agg_program_account refund clause -> refund.
- Proof text: task 0's design_rationale has a section 24 for rounds 11-12. Task 1 needed no change, and no scored value moved.
- Gates re-run: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire green; check_cache_diff info only; check_traceability OK.
REWORK round 12: gates 7/7 green
