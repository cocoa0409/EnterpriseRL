# Policy-task audit — cancellation_reinstatement_and_exclusions / charter-global

## revision_1

## charter_global_frozen

- freeze time 2026-10-18T11:00Z (written after both task derivations were frozen and before any GT reveal; nothing here derives from a revealed GT); auditor: independent policy-task auditor.
- `auto.extended.yaml` sha256 505b8438ca6c50b98f6699b09789e9b9abcec7152ac027382d1ed7d5fce51217; `task_tools.py` sha256 25465fb173195cf3588264d40a31cc21c5c299ce84dd6e79cca2be92a2defe1f.
- read: blueprint (blueprint.yaml, db_schema.json, share_tools.py, products/auto|billing|fr|physdam.yaml), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the DSL evaluator of check_compute.py. Masked: every GT field of tasks/*.json, plan.md, worklog.md (never opened).
- entry conditions (step 0): gate snapshot supplied (7 gates rc=0, file /tmp/erl0071_coord/snap_cancellation_reinstatement_and_exclusions_r1.txt), masked views supplied, hashes re-checked and equal. Complete.
- Base copy: lines 1-2825 of the extended file are byte-identical to `blueprint/products/auto.yaml` (diff empty). Six extended policies: nc = auto_ext_nonpay_cancel_return, rw = auto_ext_lapse_reinstatement_rewrite, ic = auto_ext_insured_request_cancel_return, ex = auto_ext_exclusion_endorse_return, ad = auto_ext_household_resident_relist, ab = auto_ext_exclusion_lift_premium.

### policy_conflict_scan

- Subjects / tools: nc auto_cancelled_nonpayment (cancel_term_for_nonpayment_77de57b0), rw auto_reinstated (reinstate_lapsed_term_12128c9a), ic auto_cancelled_insured_request (confirm_cancellation_request_98c044dc, user), ex auto_driver_excluded (endorse_driver_exclusion_e6038767), ad auto_driver_added (relist_household_resident_37288c8c), ab auto_driver_added (lift_driver_exclusion_0b127d81, user). ad and ab share a subject; scopes are disjoint by the claim report's driver_household_status (unlisted_household_resident vs named_excluded_driver) and each overwrite names the other's case.
- Return premium is written by nc/ic/ex with distinct transaction_reason; additional premium by rw/ad/ab with distinct reason/scope. Time anchors: nc on/after notice CED; rw within window and SNL age; ic not before receipt; ex not before signing; ad from date of loss; ab on the processing date. Cross-category reads are read-only (billing, fr, physdam); every tool writes only auto rows; base triggers of every event written (auto_cancelled_nonpayment, auto_cancelled_insured_request, auto_reinstated, auto_driver_excluded, auto_driver_added) land in auto only (XF14 clean).
- Conflict found: CG-16 (exclusion cap vs ab's endorsement edge; deadlock in part of the domain). CG-07 (ad back-dating vs physdam coverage decision) is a cross-charter contradiction.
- Scopes: task 0 claims {nc, rw, ic}, task 1 {ex, ad, ab} (derived from the worlds' trees; to be compared with charter_scope after reveal) — pairwise disjoint, jointly complete over the six policies.

### rule_compute_equivalence

- Scratch sweep (`/tmp/audit_…/scripts/sweep.py`): every compute_basis quote is verbatim in its own rule; every baseline.rule sentence is in its rule; every prerequisite policy_source and every replaced_by is in its rule; every superseded_clause is verbatim in its base policy. XF4 clean.
- Rounding: every rule says "rounded once, at the end, to the nearest cent, half up"; every compute has a single outer RND (rw_charged_short's inner RND is the comparison the rule rounds explicitly). XF6 clean.
- Order of non-commuting adjustments is stated in every rule (XF3 clean).
- Mismatches (rule word vs compute, XF11) — CG-12: ab "driver changes of every kind" vs `COUNT('auto_policy_changes', …)` which also counts auto_vehicle_added / auto_vehicle_removed rows (schema enum); ad "all claims reported on the term's physical damage coverage" and ex "claims reported on the term's physical damage coverage" (singular coverage) vs XCOUNT keyed on auto_policy_id over every coverage of the term.
- Assembly sentences naming a single factor-only quantity (XF2) — CG-17: ab "the loss payee notice charge is then added"; ex "the credit is then added"; nc "the retained percentage then acts" (nc's baseline retains nothing, so the percentage is factor-only). ic/rw/ad assembly sentences name only baseline-defined quantities or classes.
- Factor independence (XF1) — CG-04: `ic_recap_days` and `ic_fee_on_date` (bindings of ic_reinstatement_recapture) read `ic_rw_eff`, a binding owned by ic_daily_basis_rule. Every other factor reads only its own bindings and plain bindings (checked binding by binding for all 32 factors).

### action_binding_and_uuids

- Six (target_tool, computes) pairs, each claimed by one policy. uuid8 tails 77de57b0, 12128c9a, 98c044dc, e6038767, 37288c8c, 0b127d81: pairwise unrelated, no shared prefix or sequence; no collision with share_tools (no uuid tails there).
- Docstrings: no ordering words relating tools, no tool names, no example values (formats only); effects claimed are in the bodies. Observations: `endorse_driver_exclusion_e6038767` hard-codes prior_driver_status rated (correct only inside ex's rated-driver scope); nc's docstring says return_premium is "a positive amount" while nc floors at 0.00 and base auto_unearned_premium_return says "a computed return of 0.00 is not booked" (zero edge not priced, XF8 observation).

### prerequisite_graph

| edge | kind / gate | form | policy_source in own rule | resolved_by = depended-on target_tool | condition vs sentence |
|---|---|---|---|---|---|
| rw -> nc | value_input / rw_ret_amt (exists) | state | yes | yes | condition adds "status cancelled, reason nonpayment" — co-produced by the same write; observation |
| ic -> rw | value_input / ic_rw_amt (exists) | state | yes | yes | condition adds "status in_force" — co-produced; observation |
| ab -> ex | value_input / ab_changes (exists) | state | yes | yes | equal |
| ab -> ad | value_input / ab_changes (exists) | state | yes | yes | condition requires the driver-added row "dated on or after the date of loss"; sentence does not — CG-13 |

All policies fill `prerequisite` (nc/ex/ad `[]`); every `problem` is an extended id, none self; graph acyclic (two chains nc<-rw<-ic, {ex,ad}<-ab); no fallback/action forms; no authoring-viewpoint phrasing in the fields.

### prerequisite_sentences

- rw: "The re-written premium of a reinstatement with lapse is fixed only after the term carries the return premium entry booked for its cancellation for nonpayment." Ordering connective "only after"; record-visible state (a return premium row, reason cancellation_nonpayment); no tool/id/token. One write books it: nc. Derivation: sentence -> premium rows lack it -> nc's rule describes booking "the nonpayment return premium" -> cancel_term_for_nonpayment. Single reading. PASS.
- ic: "Once a notice … has reached its cancellation effective date with less than the minimum due paid by then, the return premium of a cancellation at the insured's request is not fixed until the term carries the additional premium entry booked for its reinstatement." "not … until"; state; one write (rw; relist/lift book reason driver_added). PASS.
- ab #1: "… fixed only after every Named Driver Exclusion form on file for the term has its exclusion endorsement recorded." One write (ex). PASS.
- ab #2: "… not fixed until the term carries a driver-added entry for every household resident reported operating a scheduled vehicle on a claim of the term while unlisted." One rule (ad) describes that write. Strength: CG-13.
- Depended-on rules do not restate the sentences; no second wording, no tool name. Docstrings silent about sequence.
- Undeclared cross-problem order: CG-16.

### override_declarations

Sentence by sentence against each base_policy_refs entry (findings only):
- nc vs auto_cancellation_nonpayment: s1 followed; s2 "the processing date must be on or after the cancellation effective date itself, with processing_lag_days added" is restated without "with processing_lag_days added" and no overwrite names it — undeclared departure (CG-05; the parameter is defined nowhere in the charter). s3, s4 followed; s5 (pro rata, fees) declared; s6 (billing/certificates under their own rules) inherited. vs auto_unearned_premium_return: the transaction-by-transaction clause and "nonpayment and underwriting … in full pro rata" declared; replaced_by keeps the underwriting case only by name (CG-08).
- rw vs auto_reinstatement: both changed clauses declared; every other sentence followed or inherited. Observation: base auto_premium_charging "Additional premium for a reinstatement is computed under auto_reinstatement (… prorated with lapse)" is not in base_policy_refs; rw's loaded premium is no longer a pure proration, but the sentence is a deferral to auto_reinstatement, whose clause rw declares.
- ic vs auto_insured_cancellation / auto_unearned_premium_return: three clauses declared; others followed. replaced_by for the transaction-by-transaction clause: "a cancellation for nonpayment and an underwriting cancellation keep their own rules" (CG-08).
- ex vs auto_driver_exclusion: effective-date clause declared; replaced_by restates the removal case but not the effective date of an exclusion of an unlisted driver (out of ex's scope, retired by the same clause) (CG-08). vs auto_unearned_premium_return: declared, removal restated. auto_agg_household_drivers followed.
- ad vs auto_driver_schedule / auto_premium_charging: declared with every-other-driver restatement; sibling ab excluded by name. Followed otherwise.
- ab vs auto_premium_charging: declared; sibling ad excluded by name; auto_driver_schedule's "added effective the date the change is requested, never earlier" followed.
- No anonymous intermediate, 0/1 multiplier or dropped branch found beyond the above.

### factor_ladders

Counts as declared (method / parameter / multi-source by distinct records / cross): nc 4 (1/3/1: nc_delinquency_retained_pct / fr, billing, billing); rw 6 (2/4/1: rw_daily_basis_rule / billing, fr, billing); ic 5 (1/4/1: ic_daily_basis_rule / fr); ex 5 (1/4/0 / physdam); ad 6 (1/5/1: ad_backcharge_start_rule / physdam ×4); ab 6 (1/5/0 — ab_lift_share_basis tier 2 tests the exclusion entries only / physdam ×2). Every ladder has 3 tiers stated in the rule and branched in compute, disjoint as stated; every `decides` is an input; binding sets disjoint; every fall-through equals the baseline.

All-pairs method-shape table (XF10; aggregates of one field = one input, constants ignored):

| factor | T1 | T2 | T3 (fall-through) | T1-T2 | T1-T3 | T2-T3 |
|---|---|---|---|---|---|---|
| nc_returned_days_runoff | MX(0, DAYS(ced,exp) − runoff_days[fr variant]) | MX(0, DAYS(MX(ced, certificate_end_date), exp)) | DAYS(ced,exp) | PASS (different inputs) | PASS (adds tariff input + floor) | PASS (adds input + max pick) |
| rw_daily_basis_rule | (full + shares)/term_days | full/term_days | ret_amt/ret_pd | **FAIL**: T2 holds only when the term has no change rows, so shares = 0 and T2 is T1's formula | PASS | PASS |
| rw_restart_date_rule | DAYS(MX(pay, snl), exp) | DAYS(MX(postmark, snl), exp) − offset | DAYS(MX(pay, snl), exp) − offset | PASS (postmark input) | **FAIL**: same inputs, differ by offset = 1 in all six packages (a number, not an algorithm) | PASS |
| ic_daily_basis_rule | rw_amt/rw_pd | (full + shares)/term_days | full/term_days | PASS | PASS | **FAIL** (same as rw T1-T2) |
| ex_effective_date_by_delivery | MX(0, MN(DAYS(sign,exp) − 5, DAYS(req,exp))) | MX(0, MN(DAYS(sign,exp), DAYS(req,exp), DAYS(now,exp))) | MX(0, MN(DAYS(sign,exp), DAYS(req,exp))) | PASS | **FAIL**: same MN of the same inputs, one shifted by the constant mail_receipt_days | PASS, but T2 is never produced (CG-03) |
| ad_backcharge_start_rule | DAYS(loss,exp) | DAYS(term_eff,exp) | DAYS(now,exp) | PASS | PASS | PASS (shape); T3 unreachable in scope (CG-06) |
| ab_lift_share_basis | recorded share | MX(full × pct, minimum) | full × pct | PASS | PASS | PASS (max pick + minimum) |

Reality of conditions and outcomes (XF9/XF16), per factor: nc — runoff (real SR-26 run-off liability), acquisition (minimum earned premium on early new-business cancellation), plan charge (installment cancellation charge) held real; delinquency retention held a company schedule (observation: most states treat insurer cancellations pro rata; acceptable only as the company's published schedule). ic_reason_retained_pct real (short rate waived for moving out of state / vehicle sold). ex_brief_rating_retention (minimum earned on a short-lived driver add), ad_platform_use_load (rideshare surcharge practice), ab_recent_exclusion_load, ab_exclusion_points_load, ab_lift_share_basis (25% default share as company schedule) held real or honest company schedules (observations on the first three). Struck: see CG-01, CG-02, CG-03, CG-04, CG-06, CG-07, CG-10.

### findings

All charter-global; RED unless marked; "bears on" names the task files that carry the demonstration.

- **CG-01 SOURCE-FACTOR RED — two tiers one method (rw_daily_basis_rule T1/T2; ic_daily_basis_rule T2/T3).** Rule rw: "…and the term carries any driver or vehicle change, the daily basis is the current full-term rate divided by term_days; when that entry is lower than that amount and the term carries no driver or vehicle change, the daily basis is the full_term_premium divided by term_days". The current full-term rate is full_term_premium plus/minus change shares; with no change rows it equals full_term_premium. Same in ic. The "carries any change" condition divides no customers. Bears on 0 (rw tier taken: 7.16 = T1 formula 7.16).
- **CG-02 SOURCE-FACTOR RED — method label (rw_restart_date_rule).** T1 vs fall-through differ only by reinstatement_effective_offset_days (1 in every package). Bears on 0.
- **CG-03 SOURCE-FACTOR RED — unproducible tier and constant-shift pair (ex_effective_date_by_delivery).** Base event auto_exclusion_form_signed: "delivery_method: e_signature or mail"; the email tier never occurs on a form; mail vs fall-through is a constant shift. Bears on 1.
- **CG-04 SOURCE-FACTOR RED (XF1) — ic_reinstatement_recapture reads ic_rw_eff (owned by ic_daily_basis_rule).** Bears on 0.
- **CG-05 SOURCE-POLICY RED (XF5f) — undeclared departure from auto_cancellation_nonpayment s2 (processing_lag_days dropped).** No demonstrable second value on task 0 (parameter undefined). Bears on 0 (observation there).
- **CG-06 SOURCE-FACTOR RED (XF9) — tiers unreachable in the policy's own scope.** ad_backcharge_start_rule fall-through (a reported claim's loss is never after the processing date; no claim = out of scope); ad_loss_cause_load "no cause recorded" (physdam_claim_reporting records the cause on every report); ab_excluded_operation_load "none" (the driver concerned is defined by such a report). Each leaves two in-scope tiers; the baseline is never the in-scope fall-through. Bears on 1.
- **CG-07 SOURCE-FACTOR RED (realism, cross-charter) — ad back-charges from the date of loss of a claim denied because the resident was unlisted.** After the listing row, physdam_coverage_decision's "the latest change on or before that date for that driver decides" reads the resident as rated at the loss while the denial stands ("A coverage decision is made once per claim"). No carrier charges premium for a period in which it refused the same driver's loss. Bears on 1.
- **CG-08 SOURCE-POLICY RED (XF5a/e) — replaced_by drops still-in-force content.** nc overwrite 2 ("an underwriting cancellation keeps the transaction-by-transaction computation") and ic overwrite 2 ("…keep their own rules") retire the only clause stating that computation and restate it only by name; ex overwrite 1 retires the effective date of every exclusion and restates none for an exclusion of an unlisted driver. No task consequence (no underwriting cancellation or unlisted-driver exclusion in either world).
- **CG-09 SOURCE-POLICY RED (XF8) — same-day tie rule unstated for every first/latest read:** ic_req_date/ic_recv_date/ic_reason (requests by received date); ex_name/ex_form_date/ex_form_req/ex_via (forms by signing date); ex_add_date/ex_share/ex_points (driver-added entries); ad_name/ad_loss/ad_entry/ad_cov/ad_cause (reports by date of loss); ad_last_date/ad_share (resident's entries); ab_name/ab_cov (reports); ab_ex_date/ab_ex_prior/ab_points (exclusion entries); rw_postmark (several mailed payments on the latest date); nc_runoff/nc_sr26_end (several filed / SR-26'd certificates, "that certificate's"); nc_plan / rw_plan (CFIELD first plan). No duplicates in either world.
- **CG-10 SOURCE-FACTOR RED (realism) — outcomes no nonstandard auto carrier publishes:** rw_lapse_length_load (re-rating the reinstated remainder by lapse length; the lapse's consequences are the fee and the uncovered days), rw_filer_certificate_load (a second SR-22/FR-44 surcharge on reinstated days of a term already rated to back the filing), rw_short_remainder_load (dearer per-day premium because fewer days remain), rw_returned_payment_load (premium surcharge for NSF; the billing charter's NSF fee and certified-funds rule are the consequence), ic_sr26_handling_withheld (charging for the statutory SR-26; fr_filing_fee_rule's only fee is the filing fee), ic_short_notice_withheld (charge for cancelling on short notice), ex_points_surcharge_retention and ex_loss_involvement_retention (keeping part of an excluded driver's unearned share for points already priced or for claims, e.g. an animal strike), ex_late_endorsement_credit (paying a credit for desk lag that changes no covered day), ad_household_frequency_load (other drivers' claims loading this resident), ad_vehicle_value_load (vehicle value loading a driver share), ad_late_report_load (a 6-day report the physdam charter treats as normal surcharging premium), ab_schedule_change_load (incidental endorsement count), ab_loss_payee_notice (a notice charge folded into premium; auto_fees knows only the policy and reinstatement fees). Bears on 0 and 1.
- **CG-11 SOURCE-FACTOR RED — no genuine multi-source factor survives in task 1** (ab_lift_share_basis tier 2 single-record; ad_backcharge_start_rule struck). Bears on 1.
- **CG-12 SOURCE-POLICY RED (XF11) — rule word vs compute** (ab_changes counts vehicle changes; ad_claims/ex_claims count every coverage of the term). No consequence in task 1's world (one coverage, no vehicle changes).
- **CG-13 SOURCE-POLICY RED (check 6/7) — ab edge #2 sentence weaker than its condition.** For a resident added mid-term, removed, then reported operating unlisted, the sentence "carries a driver-added entry for every household resident…" already holds by the old entry while the condition (entry dated on or after the loss) does not: two readings of whether ad must run. No consequence in task 1 (Brianna has no driver-added entry).
- **CG-14 SOURCE-FACTOR RED — stamp agreeing with the tier.** `auto_policies.financial_responsibility_filing` ("state certificate the term is written to back") names the filer tier that nc_returned_days_runoff, rw_filer_certificate_load and ic_sr26_handling_withheld derive from fr_filings. Bears on 0 (stamp "sr22" agrees with every tier taken).
- **CG-15 SOURCE-POLICY RED (XF8) — date-difference boundaries and month-end not stated in words:** nc_days_in, rw_lapse_days, rw_remaining, ic_lead_days, ic_recap_days, ex_rated_days, ex_lag, ad_late, ab_ex_age give "calendar days from A to B" with no counted/not-counted statement (the days-returned/charged sentences have one); the "whole month … same day number of a later month" sentences (nc, rw, ab) give no month-end convention for a day number the later month lacks. Bears on 0 (ic_lead_days exposure, see 0.md).
- **CG-16 SOURCE-POLICY RED — deadlock between ex's cap gate and ab's edge.** ex: "The number of currently excluded drivers on the term … must be below max_excluded before another exclusion is endorsed"; ab: "The additional premium for lifting a named driver exclusion is fixed only after every Named Driver Exclusion form on file for the term has its exclusion endorsement recorded." On a Cardinal Point 100/300/100 or 250/500/100 term (max_excluded_drivers 2) with two drivers excluded, one of them lift-eligible under ab, and a third signed form pending, the endorsement waits for a lift and the lift waits for the endorsement: no solution. No consequence in task 1 (one excluded driver, cap 3).
- **CG-17 SOURCE-POLICY RED (XF2) — assembly sentences naming a factor-only quantity** (ab notice charge, ex credit, nc retained percentage). No task consequence.
- Observations: rw/ic edge conditions add a status co-produced by the depended-on write; nc zero-return edge; endorse tool's hard-coded prior status; ad/ab could both claim one person who was reported unlisted and later reported excluded; ic's confirmation overwrites the term's nonpayment CED (history then lives only in the lapse dates); nc_delinquency_retained_pct realism (company schedule).

## closing_checklist

Not reached: the difficulty does not pass (see VERDICT). Gates were not re-run by this auditor (the brief's snapshot stands as entry evidence).

### revision_1 post-reveal status

Both reveals agreed with the blind derivations value for value (0.md, 1.md source_gt_comparison): unique solution PASS in both tasks; problem tree PASS in task 0, SOURCE-CHAIN RED in task 1 (value_input edges carried only by a struck factor); SOURCE-FACTOR RED in both tasks; charter-global REDs CG-01 … CG-17 as listed under findings.

VERDICT revision_1: task0=RED task1=RED charter=CG-01,CG-02,CG-03,CG-04,CG-05,CG-06,CG-07,CG-08,CG-09,CG-10,CG-11,CG-12,CG-13,CG-14,CG-15,CG-16,CG-17

## revision_2

## charter_global_frozen (revision_2)

- written 2026-10-19T09:30Z, after both revision_2 task derivations were frozen and before any revision_2 GT reveal.
- entry: worklog tail "REWORK round 2: gates 7/7 green"; snapshot `/tmp/erl0071_coord/snapshot.sh cancellation_reinstatement_and_exclusions 2` (2026-10-19T09:15:53): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; `auto.extended.yaml` a4590bdce6795007f4f6c4806b88a3fe47968924363a9d9125908f69459e31d3 (changed -> every charter-global section re-derived), `task_tools.py` 25465fb173195cf3588264d40a31cc21c5c299ce84dd6e79cca2be92a2defe1f (unchanged -> action_binding_and_uuids carried forward from revision_1), views r2/0 eb6001c1…, r2/1 60cf3309…. Claims file read as claims only.
- base copy still byte-identical to products/auto.yaml.

### sweeps (XF1-XF22, every policy)

- XF4 quotes, baseline sentences, policy_source, replaced_by in rule, superseded in base: clean (scratch sweep). XF1: no factor binding reads another factor's binding (mechanical sweep; only assembly bindings read factor outputs) — CG-04 closed. XF3/XF6 clean. XF14 unchanged tools, triggers auto-only. XF15 clean. XF21: every window (6-month late fees, ages, claim reports) falls inside seeded history from inception.
- prerequisite graph: rw->nc state_gate, ic->rw value_input (ic_rw_amt), ex->ad value_input (ex_share), ab->ex state_gate; acyclic; sentences verbatim in own rules; conditions equal to sentences in effect (rw/ic conditions add an entry "when one is due", co-produced) — CG-13 closed; ab's carve-out removes the cap deadlock — CG-16 closed.
- overrides: nc restates "with processing_lag_days added" verbatim (CG-05 closed; the parameter is defined nowhere in the blueprint — base defect, observation); nc/ic replaced_by restate the underwriting transaction-by-transaction computation; ex replaced_by restates "an exclusion of any other driver" (CG-08 closed; but see R2-09).
- ties, counted ends, month-end, birthdays stated (CG-09, CG-15 closed) except R2-10/R2-11.

### method-shape table (revision_2, all method factors)

| factor | T1 | T2 | T3 | T1-T2 | T1-T3 | T2-T3 |
|---|---|---|---|---|---|---|
| nc_returned_days_runoff | MX(0,DAYS(ced,exp)−runoff) | MX(0,DAYS(MX(ced,end),exp)) | DAYS(ced,exp) | PASS | PASS | PASS |
| rw_rewritten_days_rule | MX(0,MN(R, DAYS(ced,exp)−runoff)) | MX(0,MN(R, DAYS(MX(ced,end),exp))) | MX(0,R) | PASS | PASS | PASS |
| rw_daily_basis_rule | (full+shares)/term_days | entry/premium_days | premium_written/term_days | PASS | PASS (adds shares); T3 unreachable through the tools (R2-07) | PASS |
| ic_earned_premium_method | kept 0 | kept 100 | kept package pct | **FAIL** (constant multipliers 1 vs 0) | FAIL (a number into the same formula) | FAIL — R2-03 |
| ic_daily_basis_rule | entry/premium_days | (full+shares)/term_days [changes] | premium_written/term_days [no changes] | PASS | PASS | **FAIL** — on T3's domain shares = 0 and premium written = full_term_premium unless a limits change re-rated it, in which case T3 prices at the superseded premium (R2-01) |
| ex_effective_date_rule | DAYS(listing,exp) | MX(0,MN(DAYS(sign,exp)−5, DAYS(req,exp))) | MX(0,MN(DAYS(sign,exp),DAYS(req,exp))) | PASS | PASS | **FAIL** constant shift (R2-02) |
| ad_listing_start_rule | DAYS(report,exp) | DAYS(loss,exp)−1 | DAYS(now,exp) | PASS | PASS | PASS |
| ab_lift_share_basis | recorded share | MX(full×pct, minimum) | full×pct | PASS | PASS | PASS |

### findings (revision_2)

Status of revision_1 items: CG-01 **not closed** (R2-01); CG-02 closed (restart date no longer a factor); CG-03 **not closed** (email tier gone, constant-shift pair kept: R2-02); CG-04 closed; CG-05 closed; CG-06 closed for its three members (struck) — new member R2-08; CG-07 closed (listing effective after the loss; physdam standing at the loss still unlisted); CG-08 closed; CG-09 closed except R2-10; CG-10 closed for every listed member — replaced in part by new company add-ons (R2-04/R2-06); CG-11 **not closed** (R2-12); CG-12 closed; CG-13 closed; CG-14 closed (tiers now need stamp and certificate status; observation below); CG-15 closed except R2-11; CG-16 closed; CG-17 closed except R2-13.

- **R2-01 SOURCE-FACTOR RED — ic_daily_basis_rule T2/T3 one method** (rule: "when it carries no such entry and carries any driver or vehicle change, the daily basis is the current full-term rate divided by term_days; otherwise the daily basis is the amount of the premium-written entry divided by term_days"; base auto_premium_charging: "Premium written equals the term's full_term_premium"). Not reached in task 0 (T1 taken).
- **R2-02 SOURCE-FACTOR RED — ex_effective_date_rule mail vs otherwise is a constant shift (mail_receipt_days 5) inside the same MN.** Bears on 1 (mail tier taken: 48 vs 50 days).
- **R2-03 SOURCE-FACTOR RED (XF10) — ic_earned_premium_method labelled method; its tiers substitute 0, 100 or the package percentage into unearned × (1 − kept/100).** Bears on 0.
- **R2-04 SOURCE-FACTOR RED (XF16/XF17 realism) — members:** ic_earned_premium_method tier 2 ("when a total-loss payment was issued on a claim of the term's physical damage coverage, the premium is fully earned and nothing is returned" — a past paid physdam claim cutting the liability refund); rw_class_change_credit (age re-rating gated on "a term backing an owner-operator certificate whose filed driver is the named insured" — a condition no carrier weighs for a driver class; customers.date_of_birth exists); nc_delinquency_retained_pct and rw_delinquency_relativity (late-fee counts, an incidental billing count; escalated from the revision_1 observation under XF17 added this round); rw_plan_relativity (a plan relativity applied only to re-written days); ex_elected_exclusion_retention (short rate on a driver-exclusion endorsement, and an invented 5% where the package's own retention is 0); ex_backcharged_listing_retention (desk processing lag of the listing — in task 1 created by the prerequisite write itself); ad_household_return_rel (days since the resident moved out); ab_recent_exclusion_load (time since exclusion; escalated under XF17). Bears on 0 and 1.
- **R2-05 SOURCE-FACTOR RED (XF22) — one dimension charged twice:** ex_youthful_driver_retention (age already priced by the 1.85 class relativity in the re-listed share it returns); ab_exclusion_points_load on the recorded-share tier (points priced in the recorded driver_term_premium); ic_reinstatement_recapture (on top of the fully earned reinstatement fee); ic_acquisition_withheld and ic_installment_plan_withheld on a term whose nonpayment return already withheld them and whose re-write "so the withheld charges stay earned" kept them (task 0: 40.00 acquisition, 30.00 plan charge on one term); rw_delinquency_relativity / rw_plan_relativity against nc's retention and plan charge on the same cycle. Bears on 0 and 1.
- **R2-06 SOURCE-FACTOR RED (XF22 "removing beats adding") — struck factors replaced by new company add-ons:** rw_delinquency_relativity, rw_plan_relativity, ex_elected_exclusion_retention, ex_youthful_driver_retention, ex_backcharged_listing_retention, ad_household_return_rel (the claims file flags them as "kept for the factor floor").
- **R2-07 SOURCE-POLICY RED (XF20) — zero-amount edges.** nc's return is 0.00 on reachable worlds (CED within certificate_runoff_days of expiration with a filed certificate; withheld charges at or above the pro rata); db_schema auto_premium_transactions.amount is a "positive amount", base says "a computed return of 0.00 is not booked", and `cancel_term_for_nonpayment_77de57b0` always books a row — the cancellation rw waits on cannot be recorded faithfully; rw's "no return entry" daily-basis tier is the blocked-side carve-out but no tool produces a nonpayment cancellation without an entry. Same for rw -> ic (re-written days 0 when run-off reaches expiration) and for ex -> ab (an exclusion of an unlisted driver has no premium change, yet the only endorsement tool books a return with prior status rated).
- **R2-08 SOURCE-FACTOR RED (XF9) — ex_elected_exclusion_retention fall-through ("points exceed the package's maximum") unreachable in scope:** the points read are those on the driver-added entry, and auto_driver_schedule adds a rated driver "only when the driver's violation points do not exceed the package's max_points".
- **R2-09 SOURCE-POLICY RED — ex's scope/replaced_by vs its prerequisite sentence for a reported-unlisted driver with a signed form** (quotations in 1.md revision_2): one passage endorses the exclusion now with no premium change, the other makes it wait for a re-listing and a return. Bears on 1 (second terminal state).
- **R2-10 SOURCE-POLICY RED (XF11/XF12) — ex_txn reads LATEST transaction_date of any driver_added additional premium with effective_date equal to the entry's date, while the rule says "its transaction date"; a second driver added the same day can supply the date.** No task consequence.
- **R2-11 SOURCE-POLICY RED (XF8) — ex_brief_rating_retention: a listing effective after the signing date gives a negative count that falls in the "fewer than brief_days_short" tier; the rule states no such case.** No task consequence (18 days).
- **R2-12 SOURCE-FACTOR RED — no genuine multi-source factor in task 1** (CG-11 persists; see 1.md).
- **R2-13 SOURCE-POLICY RED (XF2) — ic assembly sentence names a factor: "the earned-premium method then acts on that unearned premium".**
- Observations: stamp conjuncts (nc/rw/ic) add a term field a filed owner certificate already implies — no charter path shown to file an owner certificate on a term not written to back one, so the conjunct divides no real customers; ad/ab platform-use factors key on counts of claim reports rather than on use (held, real dimension); processing_lag_days undefined in the blueprint; ad's relisting back-charges from the report date for a resident whose household wants her excluded (business shape, see R2-09).

### revision_2 post-reveal status

Both revision_2 reveals equal the blind derivations value for value (task 1 under reading B). Task 0: tree and unique solution PASS, SOURCE-FACTOR RED (every computation below 4 surviving factors). Task 1: SOURCE-POLICY/SOURCE-TASK RED (R2-09, second terminal state), SOURCE-FACTOR RED (ex below bounds; no multi-source factor). Closed from revision_1: CG-02, CG-04, CG-05, CG-07, CG-08, CG-12, CG-13, CG-14, CG-16 and CG-06/CG-09/CG-10/CG-15/CG-17 for their listed members; open: CG-01 (R2-01), CG-03 (R2-02), CG-11 (R2-12); new: R2-03 … R2-13. Nothing in the artifacts regressed; nc_delinquency_retained_pct and ab_recent_exclusion_load are struck under XF17 (added this round) and ab_exclusion_points_load under XF22, though unchanged since revision_1.

## closing_checklist (revision_2)

Not reached: the difficulty does not pass. Gates per the coordinator snapshot (7/7 OK) were not re-run by this auditor.

VERDICT revision_2: task0=RED task1=RED charter=R2-01,R2-02,R2-03,R2-04,R2-05,R2-06,R2-07,R2-08,R2-09,R2-10,R2-11,R2-12,R2-13

## revision_3

## charter_global_frozen (revision_3)

- written 2026-10-20T03:55Z after both revision_3 task freezes, before any revision_3 reveal. Entry: worklog tail "REWORK round 3: gates 7/7 green"; snapshot round 3 (2026-10-20T03:48:32): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; `auto.extended.yaml` a18e95a7…, `task_tools.py` 1cae732e… (both changed -> every charter-global section re-derived); views r3/0 eb6001c1… (unchanged world), r3/1 012c36ac…. Base copy byte-identical. XF_recipe points 1-24 applied; points 23-24 applied exactly as written.

### sweeps

- XF4 quotes / baseline sentences / policy_source / replaced_by / superseded: clean. XF1: no factor reads another factor's binding (ab_lift_share_basis carries its own "then" relativities). XF3/XF6 clean. XF14/XF15 clean (tool names unchanged; triggers auto-only). XF7: docstrings carry formats only; observation — the return/rewritten arg descriptions still say "a positive amount" while the bodies and the opening paragraphs accept and skip 0.00. XF20: every tool skips a 0.00 premium row (lines 44, 99, 152, 219, 274, 329) and rw carves out "recorded cancelled for nonpayment … but no such entry was booked" — closed. XF21: no look-back windows remain. XF24: no flat-fee computation.
- Graph: rw->nc value_input (rw_ret_pd), ic->rw state_gate, ex->ad value_input (ex_share), ab->ex state_gate; acyclic; sentences equal to conditions in effect (rw's condition adds the co-produced return entry "when one is due").
- Overrides: ex adds an overwrite of base auto_driver_exclusion "When the driver was rated immediately before the exclusion … when the driver was unlisted, there is no premium change", restating the clause for every other driver; ad states the listing is made whether or not a form is on file — R2-09 closed.

### method-shape table (revision_3)

| factor | T1 | T2 | T3 | pairs |
|---|---|---|---|---|
| nc_returned_days_runoff | MX(0,DAYS(ced,exp)−runoff) | MX(0,DAYS(MX(ced,end),exp)) | DAYS(ced,exp) | all PASS |
| rw_rewritten_days_rule | MX(0,MN(R, return premium_days)) | MX(0,MN(R, DAYS(ced,exp)−runoff)) | MX(0,R) | all PASS (added inputs + MN) |
| ic_returned_days_runoff | as nc | | | all PASS |
| ex_effective_date_rule | DAYS(listing,exp) | MX(0,MN(DAYS(req,exp), MX(DAYS(sign,exp)−5, DAYS(now,exp)))) | MX(0,MN(DAYS(sign,exp),DAYS(req,exp))) | all PASS (T2 adds the processing date and a max) — R2-02 closed |
| ad_listing_start_rule | DAYS(report,exp) | DAYS(loss,exp)−1 | DAYS(now,exp) | all PASS |
| ab_lift_share_basis | drv_base × package | recorded share ÷ relativities then | full × pct | all PASS |

### findings (revision_3)

Status of revision_2 items: R2-01 closed (daily basis a plain binding); R2-02 closed; R2-03 closed (ic_retained_pct, a parameter, short rate by days in force); R2-04/R2-05/R2-06 closed for every listed member — the replacements are rating-plan relativities, which XF23 accepts as dimensions, but see R3-01; R2-07 closed; R2-08 closed (struck); R2-09 closed; R2-10 closed; R2-11 closed; R2-12 closed (ad_listing_start_rule: every non-fall-through tier tests two records); R2-13 closed.

- **R3-01 SOURCE-FACTOR RED — relativity factors whose combined outcome is already recorded on the record the computation reads (stamp; skill "a tier read off a stamp … reading it and reading the rule cannot be told apart by the score"; XF18).** Term level: the term's full_term_premium is "full-term premium rated for the term at binding" (db_schema) and, in both worlds, equals term_base_rate × every relativity to the cent (task 0 1317.44; task 1 1948.45). The certificate-form, certificate-type and payment-plan relativities therefore change nothing for a reader who prices from the term's own premium. Members: nc_certificate_form_rel, nc_certificate_type_rel, nc_payment_plan_rel, rw_payment_plan_rel, rw_certificate_form_rel, rw_certificate_type_rel, ic_certificate_form_rel, ic_certificate_type_rel. Driver level: a driver entry's driver_term_premium is "full-term premium share the rating attributes to the driver as a rated driver", and the rules name that very entry as the rating source. Members: ad_age_class_rel, ad_relationship_rel, ad_violation_points_rel (the removal entry's 448.00 encodes them), ex_age_class_rel, ex_relationship_rel, ex_violation_points_rel, ex_accident_rel, ex_platform_use_rel (the re-listing entry's 644.00 encodes all five). Not members: rw/ic nonpayment-history (not in the binding rating), ab's relativities on an unlisted-at-exclusion driver (no stored share). This class was introduced by the round-3 rework. Bears on 0 and 1.
- **R3-02 SOURCE-POLICY RED — the rating plan has no driver component, but the current-rate sentence subtracts the shares of drivers rated at binding.** Rule (nc, same in rw/ic): rated premium "term_base_rate multiplied by the vehicle … package … state … points … relativities", then "minus the driver_term_premium of every driver-excluded or driver-removed change". For a driver rated at binding (no driver-added change), the subtraction removes a share the rated premium never contained. Task 1's seed shows it: written premium 1948.45 equals the bare term rating, yet Brianna's 448.00 binding share was returned (418.78) on 2026-06-01, so under nc/rw/ic that term's current rate would be 1948.45 − 448.00. No scored consequence in either task.
- Observations: rw/ic nonpayment-history counts every notice on the term, the rescinded July notice included, as "nonpayment history" (accepted under XF23's "prior cancellation for nonpayment" dimension); the stamp ∧ certificate conjunctions in the run-off factors carried from revision_2 (task 0's only multi-source tiers); ad/ex/ab platform-use keyed on claim reports showing platform use (held as a real dimension); "a positive amount" docstring wording; processing_lag_days undefined in the blueprint.

### revision_3 post-reveal status

Both revision_3 reveals equal the blind derivations value for value. Task 0 and task 1: unique solution PASS, problem tree PASS, SOURCE-FACTOR RED under R3-01 (task 0: nc 1/4, rw 2/5; task 1: ad 3/6, ex 1/6). All revision_2 items closed; new: R3-01 (introduced by this rework's rating-plan rebuild), R3-02 (charter-only, no scored consequence). No artifact regression beyond R3-01.

## closing_checklist (revision_3)

Not reached: the difficulty does not pass. Gates per the coordinator snapshot (7/7 OK) were not re-run by this auditor.

VERDICT revision_3: task0=RED task1=RED charter=R3-01,R3-02

## revision_4

## charter_global_frozen (revision_4)

- written 2026-10-20T08:11Z after both revision_4 freezes, before any revision_4 reveal. Entry: worklog tail "REWORK round 4: gates 7/7 green"; snapshot round 4 (2026-10-20T08:04:39) 7/7 OK; `auto.extended.yaml` d7f4f79e…, `task_tools.py` 5a982b7f… (both changed: full re-derivation; new policy `auto_ext_reported_resident_exclusion` with new tool `exclude_reported_resident_5c3e91a4` replaces the exclusion return); views r4/0 6541bb01…, r4/1 9fe52cca…. Base copy byte-identical. XF points 1-26 applied; 23-26 exactly as written.

### sweeps

- XF4 clean (quotes, baseline sentences, policy_source, replaced_by, superseded). XF1 clean (no factor reads another factor's binding). XF3/XF6 clean. XF7: docstrings now say "0.00 or more" where 0.00 is skipped. New uuid8 5c3e91a4 is unrelated to the other five. XF14: the new tool writes auto_driver_added (trigger -> auto_additional_premium) and auto_driver_excluded with prior status rated (trigger -> auto_return_premium); both triggers land in auto. Observation: it books no return for the rated-then-excluded change, as the declared overwrite (one net listing charge) intends, so the terminal ledger shows a rated-then-excluded change with no return row.
- XF20 closed (tools skip 0.00; rw states zero re-written days when no return was booked). XF21: no look-back windows. XF26: term relativities removed; ad prices on the recorded share and re-rates only what changed; ex/ab rate drivers with no recorded share — R3-01 closed. R3-02 closed (the current rate is the recorded premium, which carries binding drivers' shares).
- Graph: rw->nc value_input, ic->rw state_gate, ab->ex state_gate, ab->ad value_input; acyclic; sentences match conditions. ab's second sentence excludes form-named residents, ad's rule sends them to ex, ex's overwrites name ad's and ab's cases — consistent.

### method-shape table (revision_4)

| factor | T1 | T2 | T3 | pairs |
|---|---|---|---|---|
| nc_returned_days_runoff / ic_returned_days_runoff | MX(0,DAYS(ced,exp)−runoff) | MX(0,DAYS(MX(ced,end),exp)) | DAYS(ced,exp) | all PASS |
| rw_rewritten_days_rule | MX(0,MN(R, return premium_days)) | 0 (recorded cancelled, no entry) | MX(0,R) | all PASS (input + MN; data-selected zero) |
| ex_listing_start_rule | DAYS(report,·) | DAYS(loss,·)−1 | DAYS(now,·) | all PASS |
| ad_listing_start_rule | DAYS(report,exp) | 0 (already listed after the loss) | DAYS(now,exp) | all PASS |
| ab_lift_share_basis | drv_base × package | recorded share ÷ relativities then | full × pct | all PASS |

### findings (revision_4)

Status of revision_3 items: R3-01 closed; R3-02 closed.

- **R4-01 SOURCE-FACTOR RED (XF23 "retaining premium for days with no exposure"; cross-charter) — the added run-off days keep premium past the certificate's latest end under the fr charter.** fr_sr26_notice: "An SR-26 is transmitted no later than sr26_transmit_within_days calendar days after the date coverage under the backing term ended" (3 for every certificate) and "The certificate end date is the SR-26 date plus certificate_runoff_days calendar days" (10 for every certificate). So the company is bound to the state for at most 13 days after the cancellation date. nc/ic already deduct certificate_runoff_days and then deduct state (5/15), form (2/10), type (1/3) and out-of-state (5/10) days on top — up to 38 retained days for an FL FR-44 owner-operator term. The nc/ic tier for an SR-26 already sent, by contrast, runs from the recorded certificate_end_date (at most 13 days). Members: nc_runoff_state_days, nc_runoff_form_days, nc_runoff_type_days, nc_runoff_out_of_state_days, ic_runoff_state_days, ic_runoff_form_days, ic_runoff_type_days (and ic's plain out-of-state days). XF25 makes these keys acceptable but does not license retention beyond the exposure the fr charter fixes. Bears on 0.
- **R4-02 SOURCE-FACTOR RED (XF9) — tiers unreachable within scope:** nc_runoff_out_of_state_days tier "a filing state … not one of the company's states" (fr: "The filing state must be one of the certificate's eligible_states", all within FL, VA, TX, GA, AZ, OH); rw_prior_lapse_rel fall-through "no lapse takes relativity 1" (every reinstatement with lapse has a lapse of at least one day; the reinstating payment posts after the cancellation effective date). Each leaves two reachable tiers. Bears on 0.
- **R4-03 SOURCE-FACTOR RED — ad_points_change_rel: the tiers "rose" and "fell" select the same value, "tier relativity now / tier relativity then", which the "unchanged" fall-through (1) also equals.** The ladder is one formula written as three tiers. Bears on 1.
- **R4-04 SOURCE-POLICY RED — ab's occasional-operator count omits drivers rated at binding.** The rule counts "the named insured, plus one for each driver-added entry on the term, less one for each driver-removed or driver-excluded entry that records prior status rated, plus the lifted driver". The same charter (nc/rw/ic) states the recorded full_term_premium "carries the shares of the drivers rated when the term was bound" without any driver-added entry. On a term with a second driver rated at binding, the count is one short and selects the wrong tier. No consequence in task 1 (only the named insured was rated at binding).
- **R4-05 SOURCE-FACTOR RED (realism, regression of R2-04 member) — rw_insured_class_change_rel is gated on the term backing an owner-operator certificate** ("…from the date of birth that the term's filed owner-operator certificate certifies…; … a term with no such certificate, takes relativity 1"). A named insured crossing an age class without such a certificate gets no re-rate, a condition no carrier weighs for driver class. This is the revision_2 R2-04 member rw_class_change_credit reintroduced. Bears on 0.
- Observations: nonpayment-history counts the rescinded July notice (carried); stamp ∧ certificate conjunctions in the run-off method (carried); platform-use relativities (held); the new tool's rated-then-excluded change without a return row (declared overwrite); sr26_lag_days, like processing_lag_days before, is undefined in the fr blueprint.

### revision_4 post-reveal status

Both revision_4 reveals equal the blind derivations value for value. Task 0: unique solution and tree PASS, SOURCE-FACTOR RED (R4-01, R4-02, R4-05; every computation below 4 surviving). Task 1: unique solution and tree PASS, factor counts in bounds, SOURCE-FACTOR RED on ad_points_change_rel (R4-03). Revision_3 items R3-01 and R3-02 are closed. R4-05 regresses a revision_2 strike (R2-04, rw_class_change_credit).

## closing_checklist (revision_4)

Not reached: the difficulty does not pass. Gates per the coordinator snapshot (7/7 OK) were not re-run by this auditor.

VERDICT revision_4: task0=RED task1=RED charter=R4-01,R4-02,R4-03,R4-04,R4-05

## revision_5

## charter_global_frozen (revision_5)

- written after both revision_5 freezes, before any revision_5 reveal. Entry: worklog tail "REWORK round 5: gates 7/7 green"; snapshot round 5 (2026-10-20T14:51:56) 7/7 OK; `auto.extended.yaml` 9a373b5e… (changed), `task_tools.py` 5a982b7f… (unchanged; action_binding_and_uuids carried from revision_4); views r5/0 27efc884…, r5/1 9fe52cca…. Base copy byte-identical; XF points 1-26 applied (23-26 exactly).
- Sweeps: XF4 clean; XF1 clean; XF3/XF6 clean; graph rw->nc state_gate, ic->rw value_input, ab->ex state_gate, ab->ad value_input — acyclic, sentences match conditions. rw now computes the reinstatement fee (overwrite of base auto_fees declared and restated for rescission / no-lapse); its re-written premium is a plain rule.
- Method shapes: nc/ic run-off PASS; rw_fee_basis_rule (percent of the re-written premium / max(package fee, floor) / package fee) PASS; ic_daily_basis_rule (entry rate × days / whole entry / recorded rate × days) PASS; ex/ad listing starts and ab share basis unchanged PASS.

### findings (revision_5)

Status of revision_4 items: R4-01 closed (only certificate_runoff_days plus at most sr26_transmit_within_days are kept, the fr charter's own window); R4-02 closed (unreachable tiers gone with their factors; the new ladders' tiers are all reachable); R4-03 closed; R4-04 closed (charter convention stated in nc/rw/ic/ab; worlds conform); R4-05 closed (struck, nothing added).

- **R5-01 SOURCE-FACTOR RED (XF23 "one dimension charged twice"; cross-charter) — rw_certificate_handling_charge's refile tier.** rw: "a certificate whose SR-26 has been transmitted (status cancellation_filed), which a new filing with filing_reason reinstatement_refiling must replace, adds fee_refile". fr_filing_fee_rule: "The filing fee is the certificate's filing_fee, charged once when a filing is requested for a reason in fee_charged_filing_reasons", and every certificate's fee_charged_filing_reasons includes reinstatement_refiling (filing_fee 25.00). The same refiling is charged 25.00 by the fr charter and fee_refile (15.00) again on the reinstatement fee. Bears on 0 (the factor sits in task 0's rw; this world takes its "continues" tier, so the scored figure does not move; rw keeps 5 surviving factors).
- Observations: rw_lapse_charge reads lapse length as "how coverage was restored" (XF25), accepted; ic_installment_plan_withheld charges a second plan-cancellation charge because the reinstatement reactivated the plan (billing's reactivated_installment_rule), accepted; nc/ic SR-26 transmission days cap the kept days at fr's deadline even when processing is later (in the customer's favour); carried observations (rescinded-notice count, stamp ∧ certificate conjunction, platform use, the exclusion tool's rated-then-excluded change without a return row, sr26_lag_days undefined).

### revision_5 post-reveal status

Both revision_5 reveals equal the blind derivations value for value. Task 0: tree, unique solution and counts PASS, SOURCE-FACTOR RED on rw_certificate_handling_charge (R5-01, a defective tier not taken on this world). Task 1: all four relationships PASS. All revision_4 items closed; no regression found.

## closing_checklist (revision_5)

Not reached: the difficulty does not pass while R5-01 stands. Task 1 is ready to close: its audit file corresponds to the task, the comparison carries PASS, its scope {reported_resident_exclusion, household_resident_relist, exclusion_lift_premium} is disjoint from task 0's, its tree has 2 prerequisite problems with 1 value_input edge and an owner=user root, and every computation has 5-6 surviving factors with an honest baseline. Gates per the coordinator snapshot (7/7 OK) were not re-run by this auditor.

VERDICT revision_5: task0=RED task1=PASS charter=R5-01

## revision_6

## charter_global_frozen (revision_6)

- written after both revision_6 freezes, before the revision_6 reveal. Entry: worklog tail "REWORK round 6: gates 7/7 green"; snapshot round 6 (2026-10-20T15:50:09) 7/7 OK; `auto.extended.yaml` 372545c1… (changed), `task_tools.py` 5a982b7f… (unchanged), views unchanged. Base copy byte-identical.
- Sweeps over all six policies: compute_basis quotes, baseline sentences, policy_source, replaced_by, superseded clauses, factor independence — clean. Factor lists unchanged except rw_certificate_handling_charge -> rw_certificate_exposure_charge.
- R5-01: the new ladder is "certificate still filed through the lapse" -> fee_continue (5.00); "SR-26 transmitted, certificate_end_date on or after the reinstatement effective date" -> fee_continue_part (3.00); "certificate ended before coverage was restored, or none" -> nothing. It prices the state liability carried through lapse days that bore no premium. The refiling case now adds nothing, so fr's reinstatement_refiling filing fee is the only charge for a refiling. Keys are the certificate's standing and how coverage was restored (XF24/XF25). Every tier is reachable: on scratch copies, an SR-26'd certificate ending 2026-10-06 after the 2026-10-04 reinstatement gives 3.00, one ending 2026-10-01 gives 0.00, and the seeded filed certificate gives 5.00. Distinct values; no other add-on; fee_refile removed. **Closed.**

### findings (revision_6)

None. Carried observations from revision_5 stand (lapse-length key read as "how coverage was restored"; second plan charge after reactivation; SR-26 transmission days capped at fr's deadline; rescinded-notice count; stamp ∧ certificate conjunction; platform use; exclusion tool's rated-then-excluded change without a return row; sr26_lag_days undefined).

### revision_6 post-reveal status

Both reveals equal the blind derivations value for value. Task 0 PASS (R5-01 closed); task 1 PASS (unchanged). Charter clean.

## closing_checklist (revision_6)

- Audit files 0.md and 1.md correspond to tasks 0 and 1, with `_difficulty.md` alongside. Revisions 1-6 are kept in order, and each revision's comparison section carries its verdict; revision_6 carries PASS for both tasks.
- Coverage and scopes: the six extended policies are covered. Task 0 {nonpay_cancel_return, lapse_reinstatement_rewrite, insured_request_cancel_return} and task 1 {reported_resident_exclusion, household_resident_relist, exclusion_lift_premium} are pairwise disjoint over whole trees. Task tools and GT are closed. uuid8 tails (77de57b0, 12128c9a, 98c044dc, 5c3e91a4, 37288c8c, 0b127d81) are independent.
- Trees: task 0 nc <-state_gate- rw <-value_input- ic (owner=user root); task 1 ab -state_gate-> ex, ab -value_input-> ad (owner=user root). Each has 2 prerequisite problems and at least 1 value_input edge; difficulty-wide graph acyclic.
- Factors: every computation has a self-sufficient baseline and 4-6 surviving factors (nc 4, rw 6, ic 5; ex 6, ad 5, ab 6), with at least 2 parameters and 1 method each. Multi-source: task 0 ic_daily_basis_rule; task 1 ex_listing_start_rule. Cross-difficulty: task 0 fr/billing; task 1 physdam. Ladders have at least 3 distinct, reachable tiers. Every factor bears weight against an honest baseline, and each all-baseline figure is definite and differs from gold.
- Gates: the coordinator's round-6 snapshot of this difficulty's instantiation gates on the final form is 7/7 OK (cited above); this auditor did not re-run them.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)

- written after both revision_7 freezes, before the reveal. Entry as cited in the task files (snapshot round 7, 7/7 OK; yaml d0d842f3…, tools 5a982b7f… unchanged). Base copy byte-identical. Sweeps over all six policies (quotes, baseline sentences, policy_source, replaced_by, superseded, factor independence) clean. Factor lists and labels unchanged.
- Render items, each checked across its class:
  - **F1 closed.** ab's baseline.rule now names the state and platform-use relativities as plain parts of the standard ("with no other relativity"), and its all-baseline compute equals that sentence. Class sweep: on both worlds, every policy's all-baseline figure matches its baseline.rule reading (nc 343.68, rw 25.00, ic 244.87, ex 0.00, ad 60.28, ab 120.32). No other plain relativity sits outside both its factors and its baseline.
  - **F2 closed in both members.** In ex and ad the report-date and processing-date tiers now take "the later of … and the day after the reported date of loss", and the standard date states the same; the compute uses MN of the day counts. Zero-lag probe on a scratch copy: Wendell's listing falls on 2026-09-19 (62 days) and Brianna's on 2026-09-05, so "never on or before the date of loss" now holds.
  - **F3 closed.** ic's whole-entry tier now requires the entry. The fall-through names the unbooked 0.00 re-write, and same-date entries are "taken together", matching SUM. Probe: reinstatement date after the effective date with no entry gives the recorded-rate basis (7.16), whole 0.00.
  - **F4 closed across the class.** ex and ab each carry "or no such entry on the term, takes relativity 1" in the age-class, relationship and points sentences (3 occurrences each). ad scopes out a resident with no driver-added entry.
  - **F5 closed.** ad counts every form on file naming the resident (COUNT by excluded_driver_name), matching ab's "named on a Named Driver Exclusion form on file". Probe: an older form naming Wendell under a newer Brianna form gives share 0.00 (not re-listed).
  - **F6 closed.** ad's recorded share and points-now and ex's points now key on the most recent entry's own type and date. ab's share, points then, date of birth and relationship use LATEST (first entered kept). ab_vpts sums excluded entries of one date, but the charter's own event key (auto_driver_excluded / auto_driver_added "distinguish_by: driver_name, change_effective_date") allows only one such row per driver per date, so every remaining type-and-date sum reads one row. ic states "taken together".
  - **F7 closed.** The lift's form gate (sentence and condition, which match) now waits only on the latest form by signing date when it names a reported unlisted resident. That is exactly the form the reported-resident exclusion handles, so no form is left that no tool can endorse. The cap carve-out is kept.

### findings (revision_7)

None. No regression: all scored values and factor figures of both tasks equal revision_6; factor counts met. Observations carried from revision_6 stand.

### revision_7 post-reveal status

Both reveals equal the blind derivations. Render items F1-F7 are closed across their classes; no new defect; no regression. Task 0 PASS, task 1 PASS.

## closing_checklist (revision_7)

As in revision_6's checklist, re-confirmed on the revision_7 form:
- tasks 0 and 1 have their audit files, with `_difficulty.md` alongside and revisions 1-7 in order; both revision_7 comparisons carry PASS;
- the scopes are disjoint and cover the six extended policies, and the uuid8 tails are independent;
- each tree has 2 prerequisite problems, at least 1 value_input edge and an owner=user root, and the difficulty-wide graph is acyclic;
- surviving factors per computation: nc 4, rw 6, ic 5, ex 6, ad 5, ab 6, each with at least 2 parameters and 1 method; multi-source and cross-difficulty are present in each task; baselines are honest, and each all-baseline figure is definite and differs from gold;
- gates per the coordinator's round-7 snapshot of the final form: 7/7 OK.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (revision_8)

- written after both revision_8 freezes, before the reveal. Entry as cited in the task files. Base copy byte-identical; sweeps over all six policies clean; factor lists unchanged.
- **G1 closed for its edge.** ab's second prerequisite sentence and its condition now wait only on "the household resident on the term's latest claim report recording an unlisted household resident, unless named on a Named Driver Exclusion form on file". That is exactly the resident ad prices: ad_name, ad_report and ad_loss are all keyed to that latest report. ad's scope sentence and both of its replaced_by sentences name the same single resident.
- **Edge sweep (each wait no broader than what its depended-on policy prices):**
  - rw->nc waits on the recorded nonpayment cancellation, which nc writes.
  - ic->rw waits on the term being in force from a reinstatement date after the nonpayment CED; rw writes it, with its re-written entry.
  - ab->ex waits on the latest form when it names a reported-unlisted resident; ex handles exactly that form.
  - ab->ad waits on the latest unlisted report's resident; ad prices exactly that resident.
  - All four hold.
- **ab_vpts note closed:** it is now LATEST by change effective date, so the first entered is kept.
- Wider class sweep (rule words describing cases the compute does not price, XF12) — two members remain, see R8-01.

### findings (revision_8)

- **R8-01 SOURCE-POLICY RED (XF12; same class as G1, outside the edges) — scope words broader than what the priced policy computes.**
  - (a) auto_ext_reported_resident_exclusion's rule and first overwrite say "A household resident reported operating a scheduled vehicle on a claim of the term while unlisted and named on a signed Named Driver Exclusion form is first listed as a rated driver and then excluded, in one endorsement, and is charged the listing premium worked out below", and override base "when the driver was unlisted, there is no premium change" for every such resident. But "The form handled is the term's latest Named Driver Exclusion form by signing date", and compute (ex_name, ex_sign, ex_req, ex_via) reads only that form. Example world: R1 on an older form, R2 on the latest form, both reported while unlisted. R1 may not take the base no-premium exclusion, yet no policy prices R1's listing, so R1's form can never be endorsed under the rules. The lift no longer waits on it (F7 scoping), so this is not a deadlock but a words-only case.
  - (b) The sibling replaced_by sentences still defer the old, broader set to the re-listing rule. ab: "the re-listing of a household resident reported operating while unlisted … keep[s] [its] own rule[s]". ex: "the re-listing of a resident reported operating while unlisted who is named on no such form … keep their own rules". But ad now covers only the latest report's resident and sends "every other driver" to the base charge. Example: a resident reported unlisted on an earlier report, named on no form. Read through ab/ex, they take the re-listing method (from the report date, re-rated share). Read through ad, they take the base add (effective the request date, driver_term_premium × days ÷ term_days). The two give different premiums.
  - No consequence in either task: task 1 has one form-named resident, on the latest form, and the only other reported resident is the latest report's.
- Observations carried from revision_7 stand.

### revision_8 post-reveal status

Both reveals equal the blind derivations; no regression. G1 and the ab_vpts note are closed. The XF12 class sweep found two remaining charter-level members (R8-01): the exclusion rule's scope beyond its latest-form compute, and the sibling deferrals still naming the old, broader re-listing set. Neither has a consequence in either task. Task 0 PASS, task 1 PASS.

## closing_checklist (revision_8)

Not re-confirmed: the difficulty-level close waits on R8-01. Per-task items (files, disjoint scopes, trees, factor counts nc 4 / rw 6 / ic 5 / ex 6 / ad 5 / ab 6, honest baselines, independent uuid8s, the coordinator's 7/7 gate snapshot) all still hold as in revision_7.

VERDICT revision_8: task0=PASS task1=PASS charter=R8-01

## revision_9

## charter_global_frozen (revision_9)

- written after both revision_9 freezes, before the reveal. Entry as cited in the task files. Base copy byte-identical; mechanical sweeps (quotes, baseline sentences, policy_source, replaced_by, superseded clauses, factor independence) clean on all six policies; factor lists unchanged.
- **R8-01 closed.**
  - (a) ex's opening scope sentence and first replaced_by now name "the resident named on the term's latest Named Driver Exclusion form by signing date, when that resident is reported operating … while unlisted". This matches ex_name, ex_sign, ex_req and ex_via, which read the latest form. Every other driver keeps the restated base clause (rated -> return premium, which base auto_unearned_premium_return still prices; unlisted -> no premium change).
  - (b) Every sibling replaced_by in ex (two), ad (two) and ab (one) now names exactly the three priced cases: the latest unlisted report's resident rated earlier and not on the latest form; the latest form's reported-unlisted resident; and the latest excluded-operator report's driver. ad hands off only the latest form's resident, matching ad_form_name (LATEST form).
- **One exhaustive pass for sentences describing a case the compute does not price (XF12).** Every scope sentence, overwrite, replaced_by, edge sentence, edge condition, ladder sentence and carve-out of all six policies was read against the compute.
  - nc: nonpayment return, run-off and transmission days, acquisition "once … at its first cancellation", plan charge — each priced. The restated underwriting computation is base content, still priced by the base.
  - rw: re-written premium, re-written days (tie stated, LATEST), fee basis and charges — priced. "a reinstatement without lapse keeps its own rule" and "a rescission … charged none" are base content.
  - ic: the three daily-basis tiers (absent entry named), run-off, transmission days, retention and plan charge — priced. The pending-cancellation-earlier-date case runs on the recorded-rate tier.
  - ex: scope, listing and exclusion dates, and the six relativities (no-entry cases named) — priced.
  - ad: scope, hand-off and the "not decided by this rule" carve-out for a resident with no driver-added entry (compute: share 0) — priced or explicitly not decided.
  - ab: scope ("a lift for any other excluded driver is not decided by this rule"), both edges, the three share-basis tiers and the six relativities — priced.
  - **Result: no remaining member of the XF12 class.**
- The pass found one member of a neighbouring class, listed below.

### findings (revision_9)

- **R9-01 SOURCE-FACTOR RED (XF26; false qualifier) — auto_ext_reported_resident_exclusion rates "the resident … who carries no rated share on the term", but its scope also covers a latest-form resident who was rated earlier in the term.**
  - Rule: "The resident's listing share is the company's filed driver rating of the resident, who carries no rated share on the term: drv_base_rate multiplied by the package relativity … and by the age-class, relationship, violation-points, accident and platform-use relativities below".
  - The scope (sentences 0 and 4) is the latest form's reported-unlisted resident, with no restriction to never-rated residents. ad explicitly hands such a resident to this rule even when rated earlier ("is not the resident named on the term's latest Named Driver Exclusion form").
  - On a world where that resident has an earlier driver-added entry, the qualifier is false, and the entry's recorded driver_term_premium already embeds the age-class, relationship and points tiers at its rating date. XF26: "A factor is not load-bearing if a recorded amount the agent can read already embeds it (… a driver's recorded rating share)".
  - Scratch probe on task 1's world, with a 2026-05-25 driver-added entry for Brianna at 448.00 (= 180 × 1.10 × 1.04 × 1.85 × 1.05 × 1.12): ex still prices 644.00 -> 80.50, which equals 448.00 × 1.25 × 1.15. So the three relativity documents can be bypassed by reading the recorded share, as in revision_3's R3-01.
  - No consequence in either task: Brianna's only entries are her binding exclusion and her 2026-06-01 removal, with no share.
- Observations carried from revision_8 stand.

### revision_9 post-reveal status

Both reveals equal the blind derivations; no regression in either task. R8-01 is closed, and the one exhaustive XF12 pass found no remaining member. The pass did find one member of the neighbouring XF26 class (R9-01): ex's "who carries no rated share on the term" qualifier is false for a latest-form resident rated earlier in the term, whose recorded share then embeds three of ex's relativities. It is charter-level only. Task 0 PASS, task 1 PASS.

## closing_checklist (revision_9)

Not re-confirmed: the difficulty-level close waits on R9-01. Per-task items (files, disjoint scopes, trees, factor counts nc 4 / rw 6 / ic 5 / ex 6 / ad 5 / ab 6, honest baselines, independent uuid8s, the coordinator's 7/7 gate snapshot) all still hold.

VERDICT revision_9: task0=PASS task1=PASS charter=R9-01

## revision_10

## charter_global_frozen (revision_10)

- written after both revision_10 freezes, before the reveal. Entry as cited in the task files. Base copy byte-identical.
- **R9-01 closed.** ex's scope, its first replaced_by and its result are bounded by the record test "carries no driver-added entry on the term", enforced by `ex_added_n` (result 0.0 when any such entry exists). The base clause is restated and computed outside the test. Probe on a scratch copy: Brianna with an earlier 448.00 driver-added entry gives listing premium 0.00. ad's hand-off sentence and ab's form gate (sentence and condition) carry the same test.

### exhaustive class pass (rounds 1-9 classes; XF 1-27) — every remaining member

| class (first raised) | check on the current charter | remaining members |
|---|---|---|
| two tiers one method / one formula as several tiers (CG-01, R2-01, R4-03) | ladder values pairwise distinct in all 32 factors (mechanical); points/age change ladders state distinct values per transition | none |
| method shape, XF10 (CG-02, CG-03, R2-02, R2-03) | all method factors (nc/ic run-off, rw fee basis, ic daily basis, ex/ad listing start, ab share basis) pass all pairs | none |
| factor independence, XF1 (CG-04) | mechanical sweep | none |
| **assembly sentence names a factor-only quantity, XF2 (CG-17, R2-13)** | read every "The adjustments below…" sentence | **4 — R10-01** |
| order of non-commuting adjustments, XF3 | stated in all six | none |
| verbatim quotes / baseline sentences / policy_source / replaced_by / superseded, XF4 | mechanical | none |
| overwrite hygiene, XF5 (CG-05, CG-08, R8-01b) | every replaced_by restates the retired clause's still-in-force content and names the siblings' exact cases; no deferral to a retired clause (ad's "excluded under the base clause" is restated in ex's replaced_by) | none |
| rounding, XF6 | single final RND plus the stated share rounding | none |
| docstrings, XF7 | tools unchanged since revision_4; formats only; 0.00 handling stated | none |
| ties, absent records, zero, negative lag, month-end, counted ends, XF8 (CG-09, CG-15, F3, F4, F6, R2-10, R2-11) | ties stated and keyed (type+date keys unique by the charter's distinguish_by); no-entry cases stated; MX(0,…) where stated; birthday rule; ends stated | none |
| unreachable tiers, XF9 (CG-06, R2-08, R4-02) | every tier reachable within its scope (ex's record test leaves all ex tiers reachable) | none |
| rule words vs compute, XF11 (CG-12, F1) | every factor and scope sentence matches its binding; all-baseline equals baseline.rule on both worlds | none |
| words-only cases, XF12 (R2-09, G1, R8-01, R9-01) | scope, carve-out and hand-off sentences either priced, restated base, or "not decided by this rule"; scopes bounded by exact record tests in compute | none |
| seed realism, XF13 (R3-02) | worlds unchanged since revision_4/5; ledgers consistent; carried observations only | none |
| trigger rule, XF14 / names, XF15 | auto-only triggers; no factor id inside a tool name (mechanical) | none |
| realism and keys, XF16/17/23/24/25 (CG-10, R2-04, R4-05, R5-01) | term factors are run-off/transmission days, acquisition once, plan charge; fee keys are state schedule, lapse length, certificate standing, form, type, filing vs garaging; driver factors are age class, relationship, points, accidents, platform use | none |
| stamp, XF18 (CG-14, R3-01) | run-off tiers need stamp and certificate status (carried observation); no recorded figure decides a tier | none |
| edge strength / deadlock, XF19 (CG-13, CG-16, F7) | all four edges equal their conditions and wait only on what the depended-on policy prices | none |
| zero edges, XF20 (R2-07) | tools skip 0.00; carve-outs stated | none |
| look-backs, XF21 | no look-back windows | none |
| one dimension twice / add-ons, XF22 (R2-05, R2-06, R5-01) | acquisition once; refiling not priced by the fee; plan charge per closing (observation) | none |
| retention without exposure (R4-01) | run-off within fr's 10 + 3-day window | none |
| recorded figure embeds a factor, XF26 (R3-01, R9-01) | ex rates only never-rated residents; ad and ab tier 2 act on changes since the recorded share; term computations start from the recorded premium | none |
| filing dimensions, XF27 | cancellation reason and certificate standing separate; lapse length keys restoration; no standalone filing-state-group factor, so (b) does not apply | none |

### findings (revision_10)

- **R10-01 SOURCE-POLICY RED (XF2; same class as CG-17 / R2-13) — four assembly sentences name a factor-only quantity or a factor.** The rule must state the combination once, generically, without naming factor quantities. These sentences have stood since revision_5 and I passed them in revisions 5-9: an audit miss, recorded here.
  1. auto_ext_nonpay_cancel_return: "the days returned are settled first, **the SR-26 transmission days** kept being taken off **the days the run-off rule leaves**, never below zero, …" (names nc_sr26_transmission_days's quantity and the run-off method factor).
  2. auto_ext_insured_request_cancel_return: "**the daily basis** and the days returned are settled first, **the SR-26 transmission days** kept being taken off **the days the run-off rule leaves**, never below zero, giving the unearned premium, **the daily basis** multiplied by the days returned; …". baseline.rule defines no "daily basis"; it is ic_daily_basis_rule's quantity, alongside the transmission-days factor and the run-off factor.
  3. auto_ext_lapse_reinstatement_rewrite: "**the fee basis** is settled first; the charges stated as amounts are then added together to it; …". baseline.rule says only "The standard reinstatement fee is the package's reinstatement_fee"; "fee basis" is rw_fee_basis_rule's quantity.
  4. auto_ext_exclusion_lift_premium: "**the share basis** is settled first; the relativities below are then multiplied together with it into the lift share; …". baseline.rule names "the standard lift share"; "share basis" is ab_lift_share_basis's quantity.
  - Not members: ex's and ad's assembly sentences ("the relativities below", the listing and exclusion effective dates and the recorded share are all named in baseline.rule).
  - No scored consequence in either task.
- Observations carried from revision_9 stand.

### revision_10 post-reveal status

Both reveals equal the blind derivations; no regression in either task. R9-01 is closed. The exhaustive pass over every class from rounds 1-9 and XF 1-27 leaves exactly one class with members: R10-01, four assembly sentences (nc, ic, rw, ab). That is the complete list for a bounded next round. Task 0 PASS, task 1 PASS.

## closing_checklist (revision_10)

Not re-confirmed: the difficulty-level close waits on R10-01. Every per-task item still holds (files, disjoint scopes, trees, factor counts nc 4 / rw 6 / ic 5 / ex 6 / ad 5 / ab 6, honest baselines, independent uuid8s, the coordinator's 7/7 gate snapshot).

VERDICT revision_10: task0=PASS task1=PASS charter=R10-01

## revision_11

## charter_global_frozen (revision_11)

- written after both revision_11 freezes, before the reveal. Bounded to R10-01 plus a regression check.
- Comparison basis: no byte copy of the revision_10 charter was retained (by me or in /tmp/erl0071_coord), so the "nothing else changed" check is behavioural and mechanical, not a text diff. Evidence:
  - the tool module and both worlds keep their revision_10 hashes;
  - the factor lists and labels are the same;
  - every compute output and every factor-baseline and all-baseline figure on both worlds equals revision_10;
  - the edge-branch probes give the same results;
  - the mechanical battery (verbatim quotes, baseline sentences, policy_source, replaced_by, superseded clauses, factor independence, distinct tier values, factor-id vs tool-name) is clean on all six policies.
- **R10-01 closed, each sentence generic with its order kept:**
  1. nc: "those that settle the days returned come first, an adjustment that replaces the standard days returned being applied before any that takes further days off them, never below zero, …". This matches `nc_days_returned: MX(0, nc_base_days - nc_lag)`, the run-off method replacing the days and the transmission days then taken off. No factor or factor-only quantity is named. The compute_basis quote for nc_days_returned is verbatim.
  2. ic: the baseline now defines "the daily basis, the current full-term rate divided by term_days", so the name is baseline-defined. The assembly reads "those that settle the daily basis and the days returned come first, an adjustment that replaces the standard days returned being applied before any that takes further days off them, … the daily basis multiplied by the days returned, or the amount an adjustment returns in its place; those stated as a percentage …; those stated as an amount …". This matches ic_days, ic_unearned (ic_whole + ic_daily × ic_days) and result. The compute_basis quotes for ic_days and ic_unearned are verbatim.
  3. rw: "an adjustment that replaces the standard reinstatement fee is applied first; those stated as amounts are then added together to the result", matching fee_basis + charges.
  4. ab: "an adjustment that replaces the standard lift share is applied first; the relativities below are then multiplied together with the result into the lift share, rounded to the cent; …", matching ab_basis × relativities.
  - Each is generic, keeps the non-commuting order (replacement before deductions or multiplication), and names no factor-only quantity.

### findings (revision_11)

None. The classes the revision_10 pass found empty were not reopened, since this diff touched only assembly sentences and ic's baseline sentence.

### revision_11 post-reveal status

Both reveals equal the blind derivations. R10-01 is closed; no regression; no charter finding remains.

## closing_checklist (revision_11)

- Files: 0.md and 1.md correspond to tasks 0 and 1, with `_difficulty.md` alongside. Revisions 1-11 are kept in order, older text untouched; both revision_11 comparisons carry PASS.
- Coverage and scope: the six extended policies are covered. Task 0 {auto_ext_nonpay_cancel_return, auto_ext_lapse_reinstatement_rewrite, auto_ext_insured_request_cancel_return} and task 1 {auto_ext_reported_resident_exclusion, auto_ext_household_resident_relist, auto_ext_exclusion_lift_premium} are pairwise disjoint over whole trees. Task tools and GT are closed. The uuid8 tails 77de57b0, 12128c9a, 98c044dc, 5c3e91a4, 37288c8c and 0b127d81 are independent.
- Trees:
  - task 0: nc <-state_gate- rw <-value_input- ic, root owner=user;
  - task 1: ab -state_gate-> ex and ab -value_input-> ad, root owner=user;
  - each has 2 prerequisite problems and at least 1 value_input edge; the difficulty-wide graph is acyclic; every edge waits only on what its depended-on policy prices.
- Factors:
  - surviving per computation: nc 4, rw 6, ic 5, ex 6, ad 5, ab 6, each with at least 2 parameters and 1 method;
  - multi-source: task 0 ic_daily_basis_rule; task 1 ex_listing_start_rule;
  - cross-difficulty: task 0 fr/billing; task 1 physdam;
  - every ladder has at least 3 distinct, reachable tiers stated in its rule;
  - every factor bears weight against an honest baseline, and each all-baseline figure is definite and differs from gold (nc 343.68, rw 25.00, ic 244.87, ex 0.00, ad 60.28, ab 120.32);
  - no recorded figure embeds a surviving factor.
- Gates: the coordinator's round-11 snapshot of this difficulty's instantiation gates on the final form is 7/7 OK; this auditor did not re-run them.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN

## revision_12

## charter_global_frozen (revision_12)

- written after both revision_12 freezes, before the reveal. Mechanical battery on all six policies is clean (verbatim quotes, baseline sentences, policy_source, replaced_by, superseded clauses, factor independence, distinct tier values, factor-id vs tool-name); factor lists unchanged.
- **S-1 closed.** Every certificate read in nc, ic and rw is keyed to the standing on the transaction's own effective date, stated in the rule and enforced in compute:
  - nc/ic: `*_filed` (filed_date ≤ date, or a cancellation_filed certificate with filed_date ≤ date and sr26_date > date), `*_sr26_end` / `*_cert_end` (only when sr26_date ≤ date), and `*_lag_raw`, `*_runoff`, `*_lag_max` from the filed or cancellation_filed certificate;
  - rw: `rw_cert_filed`, `rw_cert_sent`, `rw_form`, `rw_ctype`, `rw_fstate`, each with its own date binding.
  - The three policies are the only ones reading certificates.
  - An SR-26 or refiling dated the frozen date leaves every task 0 figure unchanged (0.md), and earlier-dated SR-26s still move the tiers. The new conditions are reachable and do not alter any tier on the seeded worlds.
- **N-1 closed.** The "rating date" general sentences are replaced by dates inside each age-class sentence, matching compute.
- **No new defect in the touched lines.**
  - Words match compute, and the first-entered-certificate convention is stated.
  - The certificate-standing rule agrees with fr_sr26_notice: a reinstatement after a transmitted SR-26 does not revive the certificate, and that SR-26 reads as cancellation_filed from its own date.
  - XF27(a) is kept: cancellation reason and certificate standing are separate dimensions.

### findings (revision_12)

None.

### revision_12 post-reveal status

Both reveals equal the blind derivations. S-1 and N-1 are closed; the touched lines introduce no defect; nothing regressed.

## closing_checklist (revision_12)

As in revision_11, re-confirmed on the revision_12 form:
- tasks 0 and 1 have their files, with `_difficulty.md` alongside and revisions 1-12 in order; both revision_12 comparisons carry PASS;
- the six policies are covered by disjoint whole-tree scopes; tools and GT are closed; the uuid8 tails are independent;
- each tree has 2 prerequisite problems, at least 1 value_input edge and an owner=user root; the graph is acyclic and every wait is no broader than what its depended-on policy prices;
- surviving factors per computation: nc 4, rw 6, ic 5, ex 6, ad 5, ab 6, each with at least 2 parameters and 1 method; multi-source and cross-difficulty are present per task; ladders have at least 3 distinct, reachable tiers;
- baselines are honest, and every all-baseline figure is definite and differs from gold;
- certificate reads are now invariant to an fr write made during the conversation;
- gates per the coordinator's round-12 snapshot: 7/7 OK.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

## charter_global_frozen (revision_13)

- written after both revision_13 freezes, before the reveal. Mechanical battery on all six policies is clean (verbatim quotes, baseline sentences, policy_source, replaced_by, superseded clauses, factor independence, distinct tier values, factor-id vs tool-name); factor lists unchanged.
- **G2 closed.**
  - ic's SR-26 transmission-days sentence now ends "processed on or before the cancellation effective date, or with no certificate standing filed on that date, none are", and the ladder's last `when` reads "otherwise (processed on or before the ending date, or no certificate standing filed on that date)".
  - The compute_basis quotes for ic_lag_raw, ic_lag_max and ic_lag are verbatim in the rule.
  - All of this agrees with `ic_lag: … (ic_lag_raw if ic_lag_raw >= 1 else 0)`. Probe on a scratch copy of task 0: requested effective date moved to 2026-10-08, processed 2026-10-06, gives ic_lag_raw −2, kept days 0, result 178.32.
  - nc's twin sentence is untouched and correct (processing is never before its CED).
- **No new defect; nothing else changed** in effect: all figures of both tasks equal revision_12.

### findings (revision_13)

None.

### revision_13 post-reveal status

Both reveals equal the blind derivations. G2 is closed; the touched lines introduce no defect; nothing regressed.

## closing_checklist (revision_13)

Re-confirmed on the revision_13 form, as itemised in revision_12:
- files and revisions 1-13 are in order, and both comparisons carry PASS;
- the scopes are disjoint and cover the six policies; tools and GT are closed; the uuid8 tails are independent;
- each tree has 2 prerequisite problems, at least 1 value_input edge and an owner=user root; the graph is acyclic and every wait is no broader than what its depended-on policy prices;
- surviving factors per computation: nc 4, rw 6, ic 5, ex 6, ad 5, ab 6; multi-source and cross-difficulty are present per task;
- baselines are honest and each all-baseline figure differs from gold;
- certificate reads are as of the transaction's effective date;
- gates per the coordinator's round-13 snapshot: 7/7 OK.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN

## revision_14

## charter_global_frozen (revision_14)

- Seed-only round. `auto.extended.yaml` 657983bf… and `task_tools.py` 5a982b7f… are byte-identical to revision_13 (sha256 re-checked), so every charter-global section carries forward from revision_13 by those two hashes. Snapshot round 14 (2026-10-21T19:57:50) 7/7 OK.
- **S-2 closed** on task 0's seed (details and billing-doc citations in 0.md revision_14). The added agent-assisted fee is priced by plan_fee_schedule and lies outside the past-due amounts. The post-credit balance of 14.19 is above the 10.00 write-off limit, so the plan is final-billed and then reactivated by the reinstatement.

### findings (revision_14)

None (one persona/seed narrative observation in 0.md, with no scored effect).

### revision_14 post-reveal status

Both reveals equal the blind derivations. S-2 is closed; charter and tools are byte-identical; nothing regressed.

## closing_checklist (revision_14)

Re-confirmed, as itemised in revision_12 and revision_13:
- files and revisions 1-14 are in order, and both comparisons carry PASS;
- the scopes are disjoint and cover the six policies; tools and GT are closed; the uuid8 tails are independent;
- the trees are acyclic, each with 2 prerequisite problems, at least 1 value_input edge and an owner=user root;
- surviving factors per computation: nc 4, rw 6, ic 5, ex 6, ad 5, ab 6; baselines are honest;
- task 0's seed is now consistent with billing settlement and reactivation law;
- gates per the coordinator's round-14 snapshot: 7/7 OK.

VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN
