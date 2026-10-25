# worklog — cancellation_reinstatement_and_exclusions (auto), M=2

## Step 0 (difficulty)
- draw: task0 prereq 2, factors [4,5,6]; task1 prereq 2, factors [5,6,6].
- Constraint found: the Statement of No Loss, the Named Driver Exclusion form and the cancellation-request
  record carry no computable quantity, so none is a problem; the owner=user problems must be money writes the
  named insured makes personally: (a) the signed cancellation request taking effect (lifecycle in_force->cancelled
  by user) and (b) lifting a named driver exclusion at the insured's signed request (task 1).

## Task 0 — CLOSED (per-task gates 7/7: extended, task_tools, replay, solvability, compute, grounding, cross_fire)
Tree: auto_ext_insured_request_cancel_return (user, confirm_cancellation_request_98c044dc, 5 factors)
  <- value_input ic_rw_amt <- auto_ext_lapse_reinstatement_rewrite (agent, reinstate_lapsed_term_12128c9a, 6 factors)
  <- value_input rw_ret_amt <- auto_ext_nonpay_cancel_return (agent, cancel_term_for_nonpayment_77de57b0, 4 factors)
Gold: NC 223.48 (38 days, closed 2026-09-25) -> RE 301.58 (36 days, effective 2026-10-07, fee 25.00) -> IC 234.83 (34 days, 2026-10-09).
Baselines: NC 343.68, RE 205.84, IC 219.10. Edge skips: skip RE -> IC 218.44; skip NC -> RE 0.00.

### Probe table (scratch copies, check_compute engine)
| read | decoy/edge | rule words | result |
|---|---|---|---|
| fr filing status filed (EXISTS/CPARAM) | withdrawn duplicate FD | "status filed" | FD ignored |
| cancellation request (LATEST by received date, status received) | withdrawn June request (replaced_with_other_insurance) | "latest ... with request_status received" | RQ1 picked |
| nonpayment return entry (SUM keyed on effective_date = cancellation effective date) | none / absent | "entry whose effective date is the term's cancellation effective date" | absent -> 0.00, MX(pd,1) guards division |
| re-write entry (SUM keyed on recorded reinstatement_date) | absent | "effective on that reinstatement date" | absent -> rate basis (218.44) |
| latest payment (XLATEST posted_date) + channel (XCOUNT on that date) | earlier partial payment 2026-09-21, returned ACH 2026-08-12 | "every payment posted on that date is considered" | no first-listed tie |
| late fees net of courtesy waivers (XCOUNT 6 months) | waived July fee | "less the late fees waived as a courtesy" | 3-1=2 -> 5% (miscount 3 -> 10%) |
| lead days | requested before receipt | "counting as fewer than one day" | short-notice tier |
| recapture days | fee dated after cancellation | "a reinstatement date later than ..." | none |
| month windows | MONTHS() whole months | "complete on the same day number of a later month" | stated |

### Pairwise method-tier table
| factor | T1 vs T2 | T2 vs T3 | T1 vs T3 |
|---|---|---|---|
| nc_returned_days_runoff | run-off tariff param vs data-selected certificate_end_date | end-date anchor vs C | adds tariff param |
| rw_daily_basis_rule | adds change shares | rate/term_days vs entry/premium_days | different inputs |
| rw_restart_date_rule | no offset vs postmark input | postmark replaces posting date | drops offset |
| ic_daily_basis_rule | data-selected re-write vs rate+shares | adds shares | different inputs |

### Trigger rule
auto_cancelled_nonpayment -> auto:auto_return_premium (written); auto_reinstated -> auto:auto_reinstatement_fee, auto:auto_additional_premium (written);
auto_cancelled_insured_request -> auto:auto_return_premium (written). No trigger lands in another category.

### Revisions
- replay red: empty-string FK ids counted as dangling -> seed id fields '' -> null; fr_filing_transactions unread -> added find_fr_filing_transactions read (duplicate fee reversal evidence).
- solvability red: intent kinds must be initial_state/user_scenario; gate evidence needed field paths; prior_step binding needs source_table; temporal evidence must be record refs.
- compute red: history not load-bearing when SUM/COUNT zeroed (LATEST reads only) -> return entry and re-write entry now SUM keyed by exact dates (cancellation effective date / recorded reinstatement date); also removes tie ambiguity.
- no_loss_statement gate binds auto_document_id -> reinstate tool takes the Statement of No Loss id (enters the transaction ids).

## Task 1 — CLOSED (per-task gates 7/7)
Tree: auto_ext_exclusion_lift_premium (user, lift_driver_exclusion_0b127d81, 6 factors)
  <- value_input ab_changes <- auto_ext_exclusion_endorse_return (agent, endorse_driver_exclusion_e6038767, 5 factors)
  <- value_input ab_changes <- auto_ext_household_resident_relist (agent, relist_household_resident_37288c8c, 6 factors)
Gold: EX 60.42 (Wendell, form F2 by mail, effective 2026-10-03, 48 days) ; AD 266.70 (Brianna, from loss date 2026-09-04, 77 days) ; AB 153.32 (Marcus, 2026-10-13, 38 days).
Baselines: EX 100.87, AD 72.72, AB 78.09. EX/AD commute (identical terminal DB both orders); skip either -> AB 148.13.
Design rejections: brand-new undisclosed driver (driver_points gate has no pre-action points record); re-rating the lift on the current
full-term rate (driver shares are not rated off other drivers' shares). Residual weakness (honest): several loads are company schedules
(schedule-change load, late-endorsement credit, report-lag load) rather than statute; the schedule-change load is the only value link
from both prerequisites to the lift.

### Probe table (task 1)
| read | decoy/edge | rule words | result |
|---|---|---|---|
| latest NDE form (LATEST by document_date) | June form F1 already endorsed | "latest Named Driver Exclusion form by signing date" | F2 picked |
| share on driver's latest add entry (SUM keyed on its date) | none / absent entry | "most recent driver-added entry" | absent -> 0 share, brief-rating "no entry" tier |
| claim report driver (XLATEST, household status filter) | Wendell's covered claim (rated_driver) | "recording ... as an unlisted household resident" / "as a named excluded driver" | Brianna / Marcus |
| platform use (XCOUNT rideshare True) | denial reason unlisted first | "while the vehicle was in use on a ride-hailing or delivery platform" | 1 |
| coverage value / loss payee (CFIELD keyed on the claim's coverage id) | no coverage | "or no coverage found" | 18900 / lienholder |
| schedule window (COUNT within 6 months) | removal of 2026-06-01 counts | "driver changes of every kind" | 3 -> 5 |
| form delivery | email / e_signature | stated per delivery | mail tier |
| report lag | report before loss impossible; same day | "fewer than late_days_mid" | 6 days |

### Pairwise method-tier table (task 1)
| factor | T1 vs T2 | T2 vs T3 | T1 vs T3 |
|---|---|---|---|
| ex_effective_date_by_delivery | mail_receipt_days tariff vs processing-date input | adds NOW input | adds tariff param |
| ad_backcharge_start_rule | loss-date anchor vs term-effective anchor | term-effective vs processing date | data-selected anchor |
| ab_lift_share_basis | recorded share vs MX(schedule, minimum) | adds max pick | data-selected input |

### Trigger rule (task 1)
auto_driver_excluded -> auto:auto_return_premium when prior rated (written); auto_driver_added -> auto:auto_additional_premium (written). None crosses categories.

### XF hygiene pass (both tasks)
- compute_basis quotes and replaced_by sentences swept verbatim against their rules (scratch sweep: ok); no factor id is a substring of a tool name.
- sibling overwrites: NC/IC both retire the transaction-by-transaction clause and each names the other's case; relist/lift both retire the
  add-premium clause and each now names the other's case (fixed on review).
- lift effective date reworded to "the processing date, the date the named insured's signed request is made" to match compute (NOW).
- reinstatement payment reads keyed to the term's own plan (billing_plan_id = CFIELD of the term's plan) to match "the term's billing plan".
- rounding: RND only on result everywhere; rules say "rounded once, at the end".
- task_tools.py: no forbidden substrings; helper is a class static method; every write tool calls ctx.create/update in its own body.
- validate_scenario: only "required document not found" errors (KB not rendered yet) for this difficulty.

## Final gate run (difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 61.0, steps 19.0; history_rows_max 9; branches_max 63) / GROUNDING OK / SCOPE OK
check_traceability: to run after the KB is rendered. check_cache_diff: info only.
INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 — design decisions
- Audit items read in full: _difficulty.md (CG-01..CG-17), 0.md (findings 1-7), 1.md (findings 1-6); XF points 1-22.
- Feasibility finding (honest): the term-level money computations of this charter (nonpayment return, lapse re-write,
  insured-request return, exclusion return of a recorded share) admit few dimensions a real carrier prices on; the
  re-listing and lift computations admit a real rating structure (package base, driver class, points, chargeable
  claims, platform use). Every value-carrying edge available in the charter runs into the term-level computations
  (return entry -> re-write -> insured return; relisted share -> exclusion return). Both trees therefore keep at least
  one term-level computation; where real dimensions run out the remaining factors are keyed on substantive record
  dimensions and flagged below as company schedules (not on the coordinator's prohibited list).
- Task 1 rebuilt: lift (user root) <- exclusion of the re-listed resident (state gate) <- re-listing (value: the
  exclusion returns the share the re-listing charged). Re-listing effective the claim REPORT date (after the loss, so
  physdam's standing test still reads her unlisted at the loss: CG-07). Wendell, his claim and its payment removed.
- Task 0 tree kept; struck factors removed; frozen 2026-10-06 with payment 2026-10-02 and statement 2026-10-03 so the
  certificate run-off overlaps the re-write start; request received 2026-10-05 for 2026-10-06.

## REWORK round 2 — methods, probes, sweeps
- Method pair tests (scratch): RE days run-off overlap / cancellation-filed end / reinstatement date; RE daily basis
  withheld-charges current rate / entry daily / premium-written; IC earned method pro rata / fully earned / short rate;
  IC daily basis re-written entry / current rate / premium-written; EX effective date re-listing anchor / mail / later-of;
  AD start report date / day after loss / processing date; AB share recorded / max(pct, minimum) / pct. Distinct formulas.
- Probes (scratch copies, check_compute engine): certificate filed + SR-26'd decoy -> filed tier; SR-26 only, no
  certificate, stamp none -> distinct tiers (CG-14); two payments on the latest day; older statement decoy (now seeded);
  second same-day request (first entered); no received request; never-listed / removed-after-report / no unlisted report;
  exclusion without re-listing -> zero; comprehensive-only report for the lifted driver; None/zero-division guarded
  (no entry -> premium-written basis; empty dates -> -1 sentinels).
- World edits: task 0 older Statement of No Loss decoy (history rows 8 for the suite floor), insured email aligned with
  date of birth; ic_earned_premium_method no longer marked cross-difficulty (task 0 seeds no physical damage coverage).
- Prerequisite sentences reworded without code tokens (RE, IC, AB) in rule and policy_source.
- Sweeps: compute_basis / replaced_by / policy_source verbatim in rules (0 misses); no factor id inside a tool name;
  forbidden substrings absent from task_tools.py; stale amounts/dates/struck-factor names removed from tracing, objectives,
  necessities, closure, solvability and rationale of both tasks.
- Claims file: rework_r2_claims.md.

## Final gate run (rework round 2, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 64.0, steps 18.5; history_rows_max 8; branches_max 71) / GROUNDING OK / SCOPE OK
REWORK round 2: gates 7/7 green

## REWORK round 3 — design decisions (revision_2 items R2-01..R2-13, XF 23/24)
- Amounts rooted in a company-filed rating plan (XF23). Term plan (NC, RE): term base rate x vehicle relativity (plain)
  x package (limits) x state x payment plan x certificate stamp (filer) x points of the highest-rated driver (term
  violation_points). Driver plan (AD, EX, AB): driver base rate x package x state x class (age x relationship) x points
  (violation points on the driver's entry plus accident points per chargeable collision report) x platform use.
  Seeds made consistent with both plans (task 1 full_term_premium and Brianna's binding share re-priced).
- Struck: rw_daily_basis_rule, rw_class_change_credit, rw_delinquency_relativity, rw_plan_relativity (as add-on),
  nc_delinquency_retained_pct, nc_acquisition_withheld and nc_installment_plan_withheld (NC is pure pro rata again, per
  base), ic_daily_basis_rule (plain binding now), ic_reinstatement_recapture, every ex retention, ad_household_return_rel,
  ab recorded-share loads. Acquisition and installment-plan cancellation charge are withheld once, at the insured request.
- IC retention relabelled parameter (R2-03); IC assembly sentence generic (R2-13).
- R2-09: task 1 world keeps the reported-unlisted resident with a signed form; EX's rule now requires that resident to be
  listed first (overwrite of the base "unlisted -> no premium change" clause for that case only) and the endorsement tool
  derives prior status from the driver's latest entry and books no 0.00 return.
- R2-07: every write tool books no premium row when the computed amount is 0.00; waiting sides wait on record states.
- Marcus excluded at binding (prior status unlisted, no share) so the lift is rated from the plan (AB method: share basis
  recorded-share re-rate / package base rate / term-premium share).
- (round 3, gate finding) check_extended rejects factors keyed only on holding fields (package, state, term points,
  stamp): those relativities are plain parts of the standard rating; factors are keyed on records: certificate form
  and type (fr), payment plan (billing), nonpayment-notice history (documents), request reason and days in force,
  driver age (date span), relationship, violation points, chargeable collision and platform-use reports (physdam).
- Allocation: NC 4 (run-off, certificate form, certificate type, payment plan); RE 5 (re-written days, certificate form,
  certificate type, payment plan, nonpayment history); IC 6 (run-off, retention, minimum-earned acquisition,
  certificate form, certificate type, nonpayment history; IC re-derives the rate, no installment charge so the plan
  dimension is not charged twice); AD 6, EX 6 (start/effective-date method + age class, relationship, violation points,
  accidents, platform use); AB 5 (share basis + age class, violation points, accidents, platform use).
- (round 3) Charter rewritten on disk: NC 4, RE 5, IC 6, AD 6, EX 6, AB 5 factors; scratch sweep (compute_basis,
  replaced_by, baseline, policy_source verbatim; XF1 transitive; factor-id/tool-name; params named in rule) clean.
  Edges: RE -> NC value_input on the nonpayment return entry's premium_days (re-written days never exceed the days the
  return gave back; skip NC changes the re-write); IC -> RE state_gate on reinstatement_date; EX -> AD value_input on
  the listing entry; AB -> EX state_gate. task_tools.py: no 0.00 premium rows; exclusion prior status from the share.
- (round 3) task 0 rebuilt: NC 272.08 / RE 293.85 / IC 188.79; per-task gates 7/7.
- (round 3) task 1 rebuilt: AD 248.50 / EX 168.00 / AB 97.05; full gate block 7/7 green (suite branches 88.0, steps 18.5, history_rows_max 8).
- (round 3) Probes on scratch copies: FR-44 owner certificate, SR-26'd certificate only (certificate relativities keep
  the certificate the term was written to back), no certificate, cancellation recorded with a 0.00 return (re-write
  carve-out), three notices, short-rate request, no received request, never-listed resident, no unlisted report,
  e-signed form, second form on the same signing date, recorded-share lift basis, no exclusion entry: all evaluate.
- Stale-text sweep of tracing, objectives, necessities, closure, solvability and rationale in both tasks; compute_basis,
  replaced_by, baseline and policy_source sentences verbatim in their rules (scratch sweep: 0 misses).
- Claims file: rework_r3_claims.md.

## Final gate run (rework round 3, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 91.0, steps 18.5; history_rows_max 8; branches_max 98) / GROUNDING OK / SCOPE OK
REWORK round 3: gates 7/7 green

## REWORK round 4 — design decisions (R3-01, R3-02, observations; XF 25/26)
- Standard figures are the recorded ones (current full-term rate from the term's recorded premium and changes; a
  driver's recorded share); factors carry only what no recorded figure embeds: the transaction's own method (run-off,
  re-written days, earned-premium retention, acquisition, listing start, exclusion effective date) and changes since
  the recorded figure (nonpayment history, prior-insurance lapse and the named insured's class change at the re-write;
  a re-listed resident's age class, points, accidents and platform use since the share was rated), plus the full
  driver rating of drivers no recorded share exists for (never rated on the term).
- SR-26 run-off day count from point-24/25 keys only (company state schedule by filing state, certificate form,
  certificate type, filing state vs garaging state) in NC (factors) and IC (factors, out-of-state plain).
- R3-02: the term rules no longer state a rating plan; the current rate is the recorded full_term_premium plus/minus
  recorded shares (base-consistent). Task 1 re-seeded so no binding-rated driver other than the named insured exists
  (Brianna and Marcus excluded at binding), removing the refund of a share the premium never carried.
- EX re-scoped within its event: the exclusion of a reported-unlisted resident named on a signed form lists her from
  the report date and excludes her from the form's effective date in one endorsement, charging the listing period
  rated in full (she was never rated on the term); AD re-lists a formerly rated resident (Wendell) re-rated for what
  changed since his recorded share; AB rates Marcus (never rated) and carries the occasional-operator relativity, which
  reads the rated-driver count the re-listing changes (value edge).
- (round 4) charter rewritten on disk (NC 5, RE 4, IC 6, AD 5, EX 6 under new id auto_ext_reported_resident_exclusion with tool exclude_reported_resident_5c3e91a4, AB 6); scratch sweep clean. World: task 0 SR-22 filed with Texas; task 1 re-seeded (Brianna and Marcus excluded at binding, Wendell added then removed, Wendell's September claim).
- (round 4) Values: NC 164.68 / RE 164.34 / IC 65.74; AD 111.62 / EX 80.50 / AB 77.64. RE's zero-return carve-out now
  re-writes zero days (nothing was given back). Probes on scratch copies: FR-44 owner certificate in Florida, same-state
  and out-of-region filings, SR-26'd certificate only, no certificate, a cancellation with a 0.00 return, a resident
  named on a form holding the latest report (re-listing charges nothing), an e-signed form, a resident never on the
  term, a third vehicle, a recorded-share lift basis: all evaluate. Stale-text sweep of both tasks clean; scratch sweep
  of compute_basis / replaced_by / baseline / policy_source / XF1 / tool names / params clean.
- Claims file: rework_r4_claims.md.

## Final gate run (rework round 4, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 79.5, steps 18.5; history_rows_max 16; branches_max 89) / GROUNDING OK / SCOPE OK
REWORK round 4: gates 7/7 green

## REWORK round 5 — design decisions (R4-01..R4-05)
- R4-01: the fr charter fixes the liability window (SR-26 within sr26_transmit_within_days of the ending date,
  certificate end certificate_runoff_days after the SR-26), so state/form/type/out-of-state run-off days are struck.
  The run-off now keeps exactly certificate_runoff_days plus the SR-26 transmission lag inside that window (the days from
  the ending date to the processing date, at most sr26_transmit_within_days).
- Task 0 recount with surviving keys only: NC 4 (run-off rule, SR-26 transmission lag, acquisition expense at the
  first cancellation, installment-plan cancellation charge); IC 5 (run-off rule, transmission lag, short-rate
  retention, installment-plan cancellation charge on the plan's second closure, daily-basis method); RE changes its
  computation within its event to the reinstatement fee (point-25 service-charge keys: company state schedule as the
  fee basis, how coverage is restored — the certificate's SR-26 status and the lapse length —, certificate form,
  certificate type, filing state against garaging state); the re-written premium stays a plain rule.
- R4-02: no non-company filing-state tier; lapse ladders start at one day. R4-05: class change struck, no replacement.
- R4-03: points change is a parameter whose tiers carry distinct values. R4-04: every rated driver other than the
  named insured, those rated at binding included, is carried by a driver-added entry (charter convention stated in the
  term rules), so the occasional-operator count includes drivers rated at binding.
- (round 5) Values: NC 215.60 (35 days) / RE fee 63.60 with re-written 270.65 for 35 days / IC 193.79 (27 days, effective
  2026-10-05); task 1 unchanged (AD 111.62 / EX 80.50 / AB 77.64). Probes on scratch copies: SR-26 already transmitted,
  no certificate, FR-44 owner certificate filed with Florida, same-state filing, processing on the ending date, a Texas
  term's fee basis, an insured-request cancellation effective inside the lapse (whole re-write returned), a second
  cancellation (no acquisition), a Monthly EFT plan: all evaluate. Stale-text and compute_basis sweeps clean.
- Claims file: rework_r5_claims.md.

## Final gate run (rework round 5, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 87.0, steps 18.5; history_rows_max 16; branches_max 95) / GROUNDING OK / SCOPE OK
REWORK round 5: gates 7/7 green

## REWORK round 6 (R5-01)
- rw certificate factor re-keyed on the state liability the certificate kept through the lapse (in force / ended
  after reinstatement / ended before or none); the refiling tier and fee_refile removed (the fr filing fee prices the
  refiling). Task 0 values unchanged (world on the first tier); task 1 untouched. Probes and sweeps clean.
- Claims file: rework_r6_claims.md.

## Final gate run (rework round 6, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 88.0, steps 18.5; history_rows_max 16; branches_max 95) / GROUNDING OK / SCOPE OK
REWORK round 6: gates 7/7 green

## REWORK round 7 (render_r1 F1-F7)
- F1 lift standard names state and platform-use as plain parts; F2 listing dates take the later of the report or
  processing date and the day after the loss (exclusion and re-listing); F3 absent re-written entry stated; F4 no-entry
  relativity 1 stated (exclusion, lift); F5 re-listing checks every form on file; F6 same-date reads keyed to one entry;
  F7 lift gate narrowed to the latest form naming a reported-unlisted resident. Scored values unchanged; probes and
  sweeps clean; task 1 closure/rationale synced to the new gate sentence.
- Claims file: rework_r7_claims.md.

## Final gate run (rework round 7, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 89.5, steps 18.5; history_rows_max 13; branches_max 98) / GROUNDING OK / SCOPE OK
REWORK round 7: gates 7/7 green

## REWORK round 8 (render_r2 G1)
- Lift's second prerequisite (sentence, edge condition, closure, rationale) scoped to the resident on the term's latest
  unlisted claim report, unless on a form; re-listing scope and overwrites name that same resident; edge sweep: no wait
  broader than the depended-on policy prices. ab_vpts now LATEST (tie rule). Scored values unchanged.
- Claims file: rework_r8_claims.md.

## Final gate run (rework round 8, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 89.5, steps 18.5; history_rows_max 13; branches_max 98) / GROUNDING OK / SCOPE OK
REWORK round 8: gates 7/7 green

## REWORK round 9 (R8-01)
- Exclusion scope and first overwrite narrowed to the latest form's reported-unlisted resident; sibling overwrites in
  exclusion, re-listing and lift name exactly the depended-on rule's priced case and each other's by name; re-listing
  hands only the latest form's resident to the exclusion rule and leaves residents with no driver-added entry
  undecided; lift's second prerequisite scoped to a resident the re-listing prices; lift scope to the latest excluded
  operator's report. One exhaustive sweep: no words-only case remains. Scored values unchanged.
- Claims file: rework_r9_claims.md.

## Final gate run (rework round 9, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 89.5, steps 18.5; history_rows_max 16; branches_max 98) / GROUNDING OK / SCOPE OK
REWORK round 9: gates 7/7 green

## REWORK round 10 (R9-01)
- Exclusion's priced case limited to a latest-form, reported-unlisted resident with no driver-added entry on the term
  (scope, first overwrite, compute ex_added_n); others excluded under the base clause, no listing premium; siblings,
  hand-off sentence and the lift's form gate/condition name the same test; task 1 closure/quotes synced. Last sweep for
  embedded tiers: none. Scored values unchanged.
- Claims file: rework_r10_claims.md.

## Final gate run (rework round 10, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 90.0, steps 18.5; history_rows_max 16; branches_max 99) / GROUNDING OK / SCOPE OK
REWORK round 10: gates 7/7 green

## REWORK round 11 (R10-01, bounded)
- Four assembly sentences (nc, ic, rw, ab) restated by kind of adjustment with their non-commuting order kept; ic's
  daily basis defined in its baseline sentence; matching compute_basis quotes updated. Nothing else changed; scored
  values unchanged.
- Claims file: rework_r11_claims.md.

## Final gate run (rework round 11, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 90.0, steps 18.5; history_rows_max 16; branches_max 99) / GROUNDING OK / SCOPE OK
REWORK round 11: gates 7/7 green

## REWORK round 12 (S-1, N-1; P-1/P-2/N-2..N-4/X-1 no change)
- S-1: every certificate / SR-26 read in nc, ic (as of the cancellation effective date) and rw (as of the reinstatement
  effective date) keyed in rule words and compute on filed_date / sr26_date; first-entered filed or cancellation_filed
  certificate; rw form/type/state reads get their own date bindings. Ladder whens, compute_basis, fr reads/notes and
  task 0 proof text updated. Class sweep: ex/ad/ab and task tools read no certificate.
- Probes (scratch): SR-26 dated the processing day (+ a refiling filed that day) -> figures hold (old charter moved);
  SR-26 before the effective date -> tiers still move.
- N-1: rating-date definitions moved from the general sentences into the age-class sentences that use them (ad, ex, ab).
- Scored values unchanged. Claims file: rework_r12_claims.md.

## Final gate run (rework round 12, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK (TRACEABILITY OK)
REWORK round 12: gates 7/7 green

## REWORK round 13 (G2 only, bounded)
- ic SR-26 transmission-days sentence: last case now "processed on or before the cancellation effective date, ...";
  matching ladder when and compute_basis quotes (ic_lag_raw, ic_lag_max, ic_lag) synced. nc twin unchanged (never
  processed before its effective date). Scored values unchanged. Claims file: rework_r13_claims.md.

## Final gate run (rework round 13, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
REWORK round 13: gates 7/7 green

## REWORK round 14 (S-2, seed only)
- Task 0 billing re-seed: the 2026-09-21 partial payment taken by agent phone with its 5.00 agent-assisted fee
  (new uuid4 row); account_balance 229.79; debit after the nonpayment return 14.19 > 10.00, so the plan is
  final-billed and reactivated by the reinstatement (premise of the second plan charge holds). Past due, status
  and all auto readings unchanged; gold unchanged. Proof text swept (seed_consistency[8], evaluation_criteria[6],
  design_rationale). yaml 657983bf / task_tools 5a982b7f byte-identical. Claims file: rework_r14_claims.md.

## Final gate run (rework round 14, difficulty level)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
REWORK round 14: gates 7/7 green
