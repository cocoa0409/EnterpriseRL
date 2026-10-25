# Policy-task audit — cpi_insurance_verification_and_force_placement / charter-global

## revision_1

## charter_global_frozen
- Freeze time: 2026-10-19T23:54Z (written before any task GT field was read). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes: `cpi.extended.yaml` d9eb8303f825378d330621b22f4c659372b207600401f3e669bd259499db64b3; `task_tools.py` 445dcefbdcf88bd724f6d02a9a99b7fab63f00501bf64324718a534024389efd (both match the brief).
- Masked views used (hashes match brief): `.audit_views/policy/cpi_insurance_verification_and_force_placement/r1/0.json` 93a00a23…, `1.json` 7d2e852e….
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/cpi.yaml, products/contract.yaml (for cross-category producibility), the extended charter, task_tools.py, the masked views, `audits/render_source/XF_recipe.md`, erlbench DSL helper `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics only).
- Masked / not read before the freeze: tasks/*.json, plan.md, worklog.md, every evaluation_criteria / computations / charter_scope / required_documents / design_rationale / solvability_contract / prerequisite_closure field. No recursive grep over the difficulty directory was run.
- Scratch: /tmp/audit_cpi_0072/ (recompute.py replays the charter's own `compute` through check_compute.build_env on the masked worlds; probe.py, sweep.py).
- Entry conditions: gate snapshot supplied by coordinator (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred). Masked views and hashes supplied. Entry conditions met.

Base copy: a YAML-level compare of every top-level key of `products/cpi.yaml` against the extended file (category … policies) is identical; only `extended_policies` is added.

Extended policies (5): `cpi_ext_feed_proof_rereview` (FEED, tool rereview_feed_proof_7d2611c6, agent), `cpi_ext_upload_proof_rereview` (UPLOAD, rereview_uploaded_proof_b3d9c591, agent), `cpi_ext_closing_month_refund` (CM, mail_closing_month_refund_38a32c3f, user), `cpi_ext_fax_proof_rereview` (FAX, rereview_faxed_proof_fc99cba3, agent), `cpi_ext_closing_period_refund` (CP, mail_closing_period_refund_6483f0cd, user).

### policy_conflict_scan
- Subjects: FEED/UPLOAD/FAX all write `cpi_proof_verified` (computes proof_result) and are partitioned by `verification_source` (insurer_edi_feed / declarations_page_upload / insurer_fax). CM and CP both write `cpi_premium_refunded` (amount_usd), partitioned by the charge's period: CM "billing period ends on the closed_date", CP "billing period runs past the closed_date". Scopes are disjoint as stated.
- Graph: CM <- FEED, CM <- UPLOAD; CP <- FAX. Expected task split (from the masked worlds alone): task 0 = {CM, FEED, UPLOAD}, task 1 = {CP, FAX}. Pairwise disjoint and jointly complete over the 5 extended policies (confirmed against charter_scope only after reveal, see task files).
- Conflicts found (details under override_declarations / findings): CM's overwrite tail re-asserts the base pro-rata-from-proof clause for "every other charge refunded after accepted proof", which includes CP's charge, while CP's rule fixes that same charge differently (CW-5f); neither CM nor CP retires the base flat-cancel clause (CW-5e); the three re-review overwrites retire the same base clauses with tails that neither restate the out-of-scope content nor name each other (CW-5a/b); the three re-review rules apply different acceptance tests to the same borrower policy depending on the arrival channel, and CM/CP apply different delay-interest and accrual-interest schedules to the same quantity (CW-4).
- Trigger rule (XF 26): tools write `cpi_proof_verified` (base triggers stay in cpi) and `cpi_premium_refunded` with refund_disposition mailed_to_borrower (base cross-category triggers fire only for credited_to_contract_balance / credited_to_deficiency_balance). No cross-category write. PASS.

### rule_compute_equivalence
Sweep (sweep.py): every `compute_basis` quote is verbatim in its rule (0 misses in 5 policies); every baseline.rule sentence is in its rule; every `superseded_clause` is verbatim in its base rule and every `replaced_by` is verbatim in the extended rule; no rule names a tool or policy id.
Per-binding correspondence checked for all five policies; the following do not hold at edge inputs (all members of CW-6, listed exhaustively there):
- FEED/UPLOAD/FAX absent-record case: rule "where the record carries no feed/uploaded/faxed proof there is nothing to re-review and the outcome is not_applicable"; compute evaluates the reach/binder binding before `result` and raises (probe: FAX on the task-0 world -> TypeError `None >= str`; UPLOAD on the task-1 world -> ValueError int('None'); FEED on a scratch copy of task 1 with feed rows removed -> TypeError). The `not_applicable` branch is unreachable.
- FEED lienholder tiers overlap as stated (same policy number AND different insurer name): two rule sentences, no precedence; compute silently takes the policy-number tier.
- CM covered-days tier 2 says "exactly one accepted proof shows coverage inside the charge's billing period" (any channel); compute counts only the latest-effective accepted feed proof and the latest-effective accepted upload; an accepted fax or agent-call proof inside the period is invisible to tiers 1/2 but visible to the tier-3 `latest_eff` read. Tier 1 says "an accepted feed proof" (any); compute tests only the latest-effective one.
- Same-day ties unstated for every first-match LATEST read: fp_*/up_*/fx_* (activity_date), onfile_flag/insurer_flag/carrier_flag (activity_date), CM fe/fx/ue/ux/latest_eff (policy_effective_date), CP xe/xx (activity_date).
- CP `c_settle_on` = XLATEST over all the customer's contract ledgers (no contract filter); rule: "the date of the contract's latest insurance-settlement payment".
- CM/CP notice window "mailed within the last N months": compute uses whole-month MONTHS() (`0 <= m < N`, day-of-month comparison); the rule does not word the boundary.
- CM/CP delay days run "to the re-review date"; compute uses NOW; the rule names a date no record holds when no re-review happened (CP world without a fax) or when the two CM re-reviews fall on different dates.
- UPLOAD "the coverage, VIN, named-insured and binder-period tests the earlier review already passed are not repeated": the base order puts rejected_binder_term after rejected_no_lienholder, so an upload rejected at lienholder never had its binder test run; the sentence asserts a record fact that does not exist.
- RND is Python round() on floats while rules say half-up; no gold-world value sits on a half-cent (observation only). CM/CP `result` sums rounded parts without a final RND (float artefacts such as 48.330000000000005; observation).

### action_binding_and_uuids
- (target_tool, computes): (rereview_feed_proof_7d2611c6, proof_result), (rereview_uploaded_proof_b3d9c591, proof_result), (rereview_faxed_proof_fc99cba3, proof_result), (mail_closing_month_refund_38a32c3f, amount_usd), (mail_closing_period_refund_6483f0cd, amount_usd): each claimed once.
- uuid8s 7d2611c6, b3d9c591, fc99cba3, 38a32c3f, 6483f0cd: no shared prefix/suffix, no sequence; independent. No factor id is a substring of any tool name (XF 7 PASS).
- Function bodies judge nothing (no refusal, no error, no hint on missing prerequisites). Docstrings name no other tool and carry no ordering word; no example values (XF 28 PASS).
- Observations: (i) the three re-review docstrings say `not_applicable` is "never a re-review outcome" while each rule says the outcome is not_applicable when the record carries no proof of that channel (contract vs rule disagree on a non-gold edge); (ii) the re-review tools leave status and policy-on-file untouched, while the rules say a re-review on a record that is not closed "follows every other part of the proof-review rule" (which returns the record to compliant and updates the policy on file) — non-gold edge on these worlds (both records closed); (iii) the CM tool stamps refund_basis pro_rata_from_proof_effective although CM's own overwrite reserves that basis for "every other charge".

### prerequisite_graph
- `prerequisite` filled on all five ([] on FEED/UPLOAD/FAX). Edges: CM->FEED (gate cm_covered_days), CM->UPLOAD (gate cm_covered_days), CP->FAX (gate cp_refund_days); all `kind: value_input`, `form: state`, no fallback_reason (correct for state form). Every `problem` is an extended policy id of this file, none is base, none self; graph acyclic.
- Each `policy_source` is verbatim in the blocked rule and absent from the depended-on rule (sweep). Each `gate` names an existing compute binding; each `resolved_by` equals the depended-on target_tool; each `effect` is true of the compute (the accepted re-review adds the span fe/fx, ue/ux or xe/xx that the covered-days / refundable-days ladder reads).
- `condition` vs sentence: the sentences say "every rejected insurer-feed / uploaded / faxed proof whose shown coverage reaches into that billing period" (open set); the conditions say "for the rejected feed proof …" (singular). Narrower in wording; no demonstrable consequence on either world (one such proof each). Observation.
- No authoring-viewpoint phrasing.

### prerequisite_sentences
Four-point test on the three sentences:
1. "The closing-month refund is fixed only after the records carry an accepted re-review of every rejected insurer-feed proof whose shown coverage reaches into that billing period." — own result ("the closing-month refund is fixed") + ordering connective ("only after") + record-visible state (an accepted proof-review entry of that feed proof) + no tool/id/snake_case token. PASS.
2. "The closing-month refund is not fixed until the records carry an accepted re-review of every rejected uploaded proof whose shown coverage reaches into that billing period." PASS.
3. "The closing-period refund is fixed only after the records carry an accepted re-review of every rejected faxed proof whose shown coverage reaches into that billing period." PASS.
- Exactly one write per state: an accepted `cpi_proof_verified` entry of an insurer-feed / upload / fax proof is produced only by the FEED / UPLOAD / FAX re-review respectively (no other tool of this difficulty writes proof entries). Derivation: sentence -> the record lacks an accepted entry for the rejected proof of that channel -> the depended-on rule ("This rule governs the re-review, at the borrower's request, of a proof … that reached the company through the insurer electronic feed … and was rejected, when the tracking record has since closed …") is the only rule producing one -> one reading.
- No second wording, no tool name, no other problem's id in the blocked rules; depended-on rules do not restate the sentences. The depended-on rules do say a closed-record re-review is done "solely to fix the premium refunds owed on the record" (purpose, no order) — observation.
- Observation: the waited-on state requires an *accepted* re-review; the charter gives CM/CP no result when the re-review is rejected (the refund "is fixed only after" a state that then never arrives). Not reached on either world.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry.

FEED / UPLOAD / FAX vs `cpi_evt_proof_verification`:
- "Proof is reviewed only on a tracking record that is not closed." — handled differently; declared (all three). The three replaced_by tails each speak only of their own channel; none restates the base content still in force for a closed record's proof of any other channel (insurer_agent_call) or for a proof whose coverage began on/after closed_date, and none names the sibling cases (CW-5a).
- "Proof is accepted … only when it arrives through one of the accepted_verification_sources and shows every one of required_coverages …, a named insured …" — followed ("not repeated", already passed by base order).
- "the company listed as lienholder and loss payee (lienholder_listing_required) with the loss_payee_clause wording" / "comprehensive and collision deductibles no higher than …" / "a policy_expiration_date at least min_days_to_expiration_at_verification days after the review date" — declared. Each replaced_by says "every first review keeps the base acceptance tests" — it defers to the very clauses it retires (CW-5c).
- "A binder is accepted only when binder_accepted is true and the binder period is no longer than binder_max_days." — NOT retired, yet FEED ("a feed proof is never treated as a binder"), UPLOAD ("binder-period tests … are not repeated") and FAX (outcome order carries no binder test) all drop it on re-review (CW-5d).
- "Otherwise the proof is rejected with the first failing reason in this order: …" — followed for the remaining tests.
- "proof that does not arrive through an accepted source is not reviewed at all; a deficient-proof notice is mailed within deficient_proof_notice_days and the record's status does not change." — followed for rejections; on a closed record this collides with base notice rule ("deficient-proof and cancellation notices on any record that is not closed") — base-internal edge, non-gold (observation).
- "An accepted proof always updates the policy details on file" — declared; the replaced_by does not restate that an accepted first review still updates the details on file (CW-5b).
- Remaining sentences (status return, cancellation, reinstatement, borrower statement) followed.
- vs `cpi_agg_multi_vehicle_policy`, `cpi_plan_assignment`: followed (plan's borrower_max_deductible_usd read via P()).

CM vs `cpi_cancellation_refund`:
- "A premium charge can be refunded only once." — followed.
- "When accepted proof shows coverage effective on or before the CPI coverage effective date with no gap (flat_cancel_if_continuous), every premium charge of the placement is refunded in full (refund_basis full_no_lapse)." — NOT retired; for CM's charge after such a proof CM computes covered-days × charge + interest + credit, base gives the full charge only (CW-5e).
- "When accepted proof starts after the CPI coverage effective date, each unrefunded charge is refunded for the days … on or after the proof's policy_effective_date …" — declared; tail re-asserts it for "every other charge refunded after accepted proof", which includes CP's charge (CW-5f).
- "Every refund is rounded half-up to the cent" — followed. Closure clause — CM's charge ends on closed_date, base closure gives 0 days; no conflict. Held release, disposition order ("otherwise mailed_to_borrower by check"), closure timing — followed.
- vs `cpi_evt_premium_billing` ("capitalised premium accrues contract interest") — consistent; vs `cpi_agg_multi_vehicle_policy` — followed.
- Event/account semantics: `cpi_premium_refunded` "Premium charged for a billing period is refunded in whole or in part"; account `cpi_premium_net` "decreases (out) with each premium refund". CM/CP write accrual interest, delay interest and a fixed notice credit into that premium-refund amount (CW-7).

CP vs `cpi_cancellation_refund`:
- Closure clause — declared for CP's charge; tail keeps closure basis for other charges (consistent).
- Flat-cancel clause — NOT retired (CW-5e). Pro-rata-from-proof clause — NOT retired and, per CM's tail, explicitly in force for CP's charge after an accepted fax (CW-5f).

### factor_ladders
Counts per policy (all four-to-six, >=2 parameter, >=1 method by label): FEED 4 (method: feed_lien_route, feed_reach_anchor; parameter: feed_comp_cap, feed_coll_cap); UPLOAD 4 (method: upload_lien_route, upload_reach_anchor; parameter: upload_comp_cap, upload_coll_cap); FAX 4 (method: fax_lien_route, fax_reach_anchor; parameter: fax_comp_cap, fax_coll_cap); CM 6 (method: cm_cover_rule, cm_accrual_days, cm_delay_days; parameter: cm_delay_rate, cm_delay_cap, cm_notice_credit); CP 6 (same pattern). Multi-source by construction: feed_coll_cap, upload_comp_cap, upload_coll_cap, fax_comp_cap (vehicle value on the tracking record AND contract model year / credit tier AND binder span). Cross-difficulty (contract): feed_comp_cap, feed_coll_cap, feed_reach_anchor, upload_comp_cap, upload_reach_anchor, upload_coll_cap, fax_comp_cap, fax_coll_cap, cm_accrual_days, cm_delay_rate, cp_accrual_days, cp_delay_rate. Every ladder has three tiers, all three stated in the rule and implemented in compute; `decides` is never `result`; binding sets disjoint; every fall-through equals the factor's baseline.

All-pairs tier tables for every `method` factor (shape test of XF 8; an anchor-date substitution counts as a method change per the instantiate reference, "the anchor the clock starts from"; an aggregate of the same field under another filter is the same input; a constant offset is a parameter):

| factor | pair | T_a | T_b | distinguishing input | verdict |
| --- | --- | --- | --- | --- | --- |
| feed_lien_route | T1/T2 | LATEST(lienholder_listed \| accepted, policy=on file)==True | constant pass | on-file flag False | PASS |
| feed_lien_route | T1/T3 | LATEST(lienholder_listed \| accepted, policy) | LATEST(lienholder_listed \| feed) | same field, filter only | FAIL |
| feed_lien_route | T2/T3 | constant pass | own flag | own flag False | PASS |
| feed_reach_anchor | T1/T2 | exp >= closed_date | exp >= placement_effective_date | exp between the two dates | PASS (anchor) |
| feed_reach_anchor | T1/T3, T2/T3 | exp >= record date | DAYS(NOW,exp) >= 15 | exp after closure, < NOW+15 | PASS |
| upload_lien_route | T1/T2 | waived | LATEST(lienholder_listed \| accepted, insurer=on file) | on-file flag False | PASS |
| upload_lien_route | T1/T3 | waived | own flag | own flag False | PASS |
| upload_lien_route | T2/T3 | LATEST(lienholder_listed \| accepted, insurer) | LATEST(lienholder_listed \| upload) | same field, filter only | FAIL |
| upload_reach_anchor | T1/T2 | eff <= closed_date | exp >= repossession_date | different field and direction | PASS |
| upload_reach_anchor | T1/T3 | eff <= closed_date | DAYS(NOW,exp) >= 15 | eff early, exp past | PASS |
| upload_reach_anchor | T2/T3 | exp >= repossession_date | exp >= NOW+15 | exp between | PASS (anchor) |
| fax_lien_route | T1/T2 | LATEST(lienholder_listed \| accepted, insurer) | constant pass | flag False | PASS |
| fax_lien_route | T1/T3 | LATEST(lienholder_listed \| accepted, insurer) | LATEST(lienholder_listed \| fax) | same field, filter only | FAIL |
| fax_lien_route | T2/T3 | constant pass | own flag | flag False | PASS |
| fax_reach_anchor | T1/T2 | exp >= closed_date | exp >= NOW | exp between | PASS (anchor) |
| fax_reach_anchor | T1/T3 | exp >= closed_date | exp >= NOW+15 | exp between | PASS (anchor) |
| fax_reach_anchor | T2/T3 | exp >= NOW | exp >= NOW + 15 | same anchor, constant offset 0 vs 15 | FAIL |
| cm_cover_rule | T1/T2 | union of feed span and binder span in period | one span bounded by its expiry | second span present | PASS |
| cm_cover_rule | T1/T3, T2/T3 | span-bounded | from latest eff to period end | expiry before period end | PASS |
| cm_accrual_days | T1/T2 | DAYS(cap_date, closed_date) | DAYS(cap_date, repossession_date) | repo date != closed date | PASS (anchor) |
| cm_accrual_days | T1/T3, T2/T3 | DAYS(…) | 0 | any positive span | PASS |
| cm_delay_days | T1/T2 | MX(0, DAYS(latest notice, NOW)-15) | MX(0, DAYS(closed_date, NOW)-15) | notice date != closed date | PASS (anchor) |
| cm_delay_days | T1/T3, T2/T3 | as above | 0 | — (T3 unreachable in scope, see CW-3) | n/a |
| cp_cover_rule | T1/T2 | [max(start,eff) .. end] | span + days after closed_date | fax expiry before closure | PASS |
| cp_cover_rule | T1/T3, T2/T3 | adds the fax span | days after closed_date | fax present | PASS |
| cp_accrual_days | T1/T2 | DAYS(cap_date, closed_date) | DAYS(cap_date, latest settlement txn_date) | settlement date != closed | PASS (anchor) |
| cp_accrual_days | T1/T3, T2/T3 | DAYS(…) | 0 | positive span | PASS |
| cp_delay_days | as cm_delay_days | | | | PASS / n/a |

Parameter labels honest (all select numbers). Realism and scope findings on the ladders are CW-3 / CW-4 below.

### findings
Charter-wide RED classes; every member listed. Each bears on the task(s) whose tree contains the policy (task 0: FEED, UPLOAD, CM; task 1: FAX, CP); demonstrations in the task files.

**CW-1 (SOURCE-FACTOR RED; XF A1/A3/A5/A6) Factor independence and assembly in CM and CP.**
1. CM assembly sentence "The closing-month refund is assembled in this order: first the premium part, the charge amount multiplied by the covered days …; then the accrual interest, … by the accrual days …; then the delay interest, … by the delay-interest rate and by the delay days after their limit is applied …; and finally the notice credit is added" names five factor-owned quantities (covered days, accrual days, delay-interest rate, delay days with their limit, notice credit).
2. CP: the same sentence with "refundable days".
3. cm_delay_cap is gated through cm_delay_days: its rule sentences are "The closing-month refund's delay days are limited to cm_cap_long_days when …" (it acts only on another factor's output) and it contributes nothing on its own against the baseline (task 0 world: delay-rate baseline alone 95.86; adding the delay-days or delay-cap baseline still 95.86).
4. cp_delay_cap: same (task 1: 86.48 in every such combination).
5. cm_delay_days and cm_delay_rate are each gated through the other (delay interest = premium part × rate × min(days, cap)); against the baseline (rate 0, days 0) neither contributes alone.
6. cp_delay_days / cp_delay_rate: same.
7. CM baseline sentence "As the standard method, the closing-month refund is the charge amount multiplied by its covered days and divided by its period days, rounded half-up to the cent, with no interest and no credit added." names factor-only quantities (interest, credit) and serves as the default for three factors at once (A5/A6).
8. CP baseline: the same sentence.
9. CM `apr` and CP `c_apr` are plain bindings feeding only the accrual-interest quantity that only the accrual factor uses (A5).

**CW-2 (SOURCE-FACTOR RED; mislabelled method, XF B8) Method pairs that fail the shape test** (table above): feed_lien_route T1/T3; upload_lien_route T2/T3; fax_lien_route T1/T3 (the same lienholder_listed flag read from a differently filtered record); fax_reach_anchor T2/T3 (exp >= today vs exp >= today + 15: a threshold offset).

**CW-3 (SOURCE-FACTOR RED; unreal or scope-restating tiers, XF B9/B10)**
1. cm_delay_cap: the condition "the record carries more than cm_long_placement_charges premium charges" (count of premium charges) is not something a lender weighs when capping interest on a late refund, and longer placements get the shorter cap (60 vs 90); its tier-2 part "at least one" holds of every customer who reaches this write (CM's charge is a capitalised premium charge), so the fall-through "limited only by the calendar days from the record's opened_date" (= the baseline) is unreachable within scope.
2. cp_delay_cap: both tiers test "the record closed …"; every CP customer's record has closed (CP scope), so the fall-through/baseline "limited only by the calendar days from the record's opened_date" is unreachable.
3. cm_delay_days: tier 2 "has closed" holds of every CM customer; the fall-through/baseline "no delay days are counted" is unreachable within scope.
4. cp_delay_days: same.
5. upload_comp_cap: Tier 4–6 contracts get +500 (binder) / +250 (policy) while Tier 1–3 get the plan ceiling only — the worst-credit borrowers receive the most lenient deductible tolerance, the inverse of FEED's and FAX's credit-tier ladders; and a temporary binder gets a higher allowed deductible than a full policy. No lender grades a deductible ceiling that way.
6. feed_lien_route tier 2: "a feed proof from an insurer other than the insurer on file passes because an insurer sends its electronic feed only to the lienholders its policy names" — the stated reason holds of every feed proof (including the fall-through: same insurer, other policy), so the condition is not what divides customers; and it passes a proof whose own feed record says lienholder_listed false.
7. cm_accrual_days tier 2: "For a contract paid off by redemption, … accrual days are … to the contract's repossession_date" — contract.yaml: "While repossessed, the contract accrues simple interest …" and redemption pays off the balance on its posting date; the interest charged on the capitalised premium ran to the redemption payoff (closed_date), so stopping at repossession is not a treatment the business gives.

**CW-4 (SOURCE-FACTOR RED; one quantity, contradictory sibling schedules)**
1. Delay-interest rate on a late CPI refund: CM — TX/OK/LA/AR/NM 6, CA/NY/NJ/IL/MA 9, else 0; CP — OK/KS/NE/TX/AR 6, MI/OH/IN/WI/MN 5, else 0. A CA borrower gets 9% on CM and 0% on CP; LA 6% vs 0%; KS 0% vs 6%.
2. Accrual interest by payoff reason: CM pays it for redemption (to repossession) and not for total loss; CP pays it for total loss (to settlement) and not for redemption.
3. Proof acceptance by arrival channel (same borrower policy, same contract): for the task-0 contract (Tier 5, ACV 11,200, model year 2019, Plan B max 500) a policy with 1,000/1,000 deductibles passes the FAX deductible tests (comp 500+500 for ACV <= 15,000 and MY <= 2020; coll 500+500 for Tier 4–5), fails FEED (comp 750, coll 750) and fails UPLOAD as a policy (comp 750). Lienholder on a closed record: UPLOAD waives always, FAX waives only for another insurer, FEED never waives. Coverage reach on a closed record: FEED/FAX expiry >= closed_date, UPLOAD effective <= closed_date. A lender's insurance requirement does not depend on how the proof arrived.

**CW-5 (SOURCE-POLICY RED; overwrite hygiene, XF D19–D22)**
- a. "Proof is reviewed only on a tracking record that is not closed." is retired by FEED, UPLOAD and FAX; each tail covers only its own channel; none restates that a closed record's other proofs (insurer_agent_call; any proof beginning on/after closed_date) are still not reviewed, and none names the sibling cases.
- b. "An accepted proof always updates the policy details on file" retired three times; no tail restates that accepted first reviews still update the details on file.
- c. Each re-review rule's tail "every first review keeps the base acceptance tests" defers to the lienholder/deductible/expiration clauses its own overwrite retires (D21).
- d. Base "A binder is accepted only when … the binder period is no longer than binder_max_days." is not retired but is dropped on re-review by FEED ("a feed proof is never treated as a binder"), UPLOAD ("binder-period tests … are not repeated") and FAX (no binder test in its outcome order). A 45-day binder rejected first for the lienholder gets rejected_binder_term under base and accepted under the re-review rule.
- e. Base flat-cancel ("When accepted proof shows coverage effective on or before the CPI coverage effective date with no gap …, every premium charge of the placement is refunded in full") is retired by neither CM nor CP, while both compute a different amount for that charge after such a proof (covered/refundable-days share plus accrual, delay interest and a credit).
- f. CM's overwrite tail "every other charge refunded after accepted proof keeps the days of its billing period on or after the proof's policy_effective_date (refund_basis pro_rata_from_proof_effective)" covers CP's charge after an accepted fax, while CP's rule says "the refund is fixed by the closing-period refund rule"; CP's overwrite retires only the closure clause. Two in-force clauses fix one charge (demonstrated in task 1).

**CW-6 (SOURCE-POLICY RED; rule != compute at edges, XF C11–C13/C17)** the nine members listed under rule_compute_equivalence: (a) absent-record crash in FEED/UPLOAD/FAX; (b) FEED lienholder tier overlap; (c) CM tier-2 "exactly one accepted proof" vs feed+upload-only compute; (d) CM tier-1 "an accepted feed proof" vs latest-effective only; (e) unstated same-day ties on every LATEST proof/flag read; (f) CP settlement read lacks a contract filter; (g) notice-window month boundary unworded; (h) "the re-review date" vs NOW; (i) UPLOAD "binder-period tests the earlier review already passed".

**CW-7 (SOURCE-POLICY RED) Non-premium amounts booked as a premium refund.** CM and CP put accrual interest (contract interest), delay interest and a flat notice credit into `cpi_premium_refunded.amount_usd` and lower `cpi_premium_net` by it, while the base event says "Premium charged for a billing period is refunded in whole or in part" and the account says "Net force-placed premium charged … decreases (out) with each premium refund". (Demonstrated in task 0, where the refund exceeds the charge it refunds.)

Observations (not grounds for rework): see action_binding_and_uuids (i)–(iii), prerequisite_graph condition wording, prerequisite_sentences (rejected re-review leaves CM/CP undefined), RND/final-rounding notes.

## closing_checklist
Written after both reveals (2026-10-19T23:59Z). The difficulty does not close: every task carries open REDs.
- Per-task files 0.md, 1.md correspond to tasks 0 and 1; this file sits alongside; revision_1 is the first revision (no older revision to preserve).
- Coverage and scope: charter_scope task 0 = {FEED, UPLOAD, CM}, task 1 = {FAX, CP}; pairwise disjoint and complete over the five extended policies; each tool claimed once; uuid8s independent (PASS).
- Problem trees: task 0 n = 2 with 2 value_input edges, task 1 n = 1 with 1 value_input edge; each root owner=user; difficulty graph acyclic; every edge unmet at opening and load-bearing (PASS on structure).
- Factors: counts and ladders well-formed on paper and every factor moves its scored value on its world, but CW-1/CW-2/CW-3/CW-4 strike factors so that no policy keeps 4 surviving factors and FAX keeps no method (FAIL).
- Seeds: both tasks' contracts violate the contract charter's term and LTV limits (FAIL); task 0 seed_consistency and factor-trace text stale (FAIL).
- Unique solution: task 1 has a second defensible amount (75.68 vs 86.67) from CW-5f; both personas steer the agent's figure (FAIL).
- Gates were not re-run by this auditor (instantiation-stage gates are the coordinator's; snapshot cited at entry).
- Cross-task class note for rework: the contract-seed class has exactly two members (task 0 contract 1bba7a25…: term 60 > 54, LTV 124.9 % > 115 %; task 1 contract 39fbbaec…: term 72 > 60, LTV 128.2 % > 120 %); the persona-correction class has exactly two members (one line in each user_scenario); the stale-proof class: task 0 upload_coll_cap tier_taken / factor_trace / design_rationale card, task 0 seed_consistency 478.01, both design_rationales' not_applicable claims.

VERDICT revision_1: task0=RED task1=RED charter=CW-1,CW-2,CW-3,CW-4,CW-5,CW-6,CW-7

## revision_2

## charter_global_frozen (revision_2)
- Freeze time: 2026-10-20T05:12Z, before any revision_2 GT field was read. Auditor: independent policy-task auditor.
- Entry: `tail -1 worklog.md` = "REWORK round 2: gates 7/7 green". Gate snapshot (coordinator snapshot.sh, 2026-10-20T05:05:01): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r2: 0.json 58431a15…acc2, 1.json 5737d9f3…1944. Source hashes: cpi.extended.yaml 47bbab70…0e8e, task_tools.py dc338a58…c8ed — both changed since revision_1, so every charter-global section below is re-derived in full.
- Read: extended charter, task_tools.py, rework_claims_r2.md (item ids only), blueprint, products/contract.yaml, masked views r2, XF_recipe.md. Not read: tasks/*.json, plan.md, worklog.md (beyond its last line).
- Base copy: identical to products/cpi.yaml on every key (YAML compare).

### policy_conflict_scan (r2)
- Same five extended policies, tools and graph (CM <- FEED, CM <- UPLOAD; CP <- FAX). Subjects partitioned as in revision_1. The three re-review rules are now textually identical apart from the channel name (normalised diff of params, compute, factors, rule: no difference), which closes the channel-dependent acceptance contradiction.
- CM's tail now hands the charge running past closed_date to CP and CP retires both the pro-rata-from-proof and the closure clauses for its charge, naming CM's case; both tails keep flat cancellation (full_no_lapse). The two refund rules share one schedule (same parameter values).
- New conflicts: R2-E below (re-review tails put the sibling channels among proofs "reviewed only on a tracking record that is not closed"; proof-span tier 2 "reinstated without a gap" vs base reinstatement + flat-cancel).
- Trigger rule: unchanged tools' event set; PASS.

### rule_compute_equivalence (r2)
Sweep: every compute_basis quote verbatim; baseline sentences in rule; every superseded_clause verbatim in base; every replaced_by in its rule; no tool/policy id in any rule. Probes on the r2 worlds (charter compute replayed): FEED/UPLOAD/FAX return not_applicable on a record without a proof of their channel (fax on task 0, feed/upload on task 1) and after their own accepted re-review — CW-6a closed. Same-day ties worded on every pick ("the one recorded first counts") — CW-6e closed. Settlement read, notice windows, "re-review date" in delay sentences, "already passed" wording — removed or reworded (CW-6f/g/h/i closed).
Remaining mismatches (members of R2-F):
1. CM/CP proof-span tier 2: rule "its proof days run from the day after the expiration date on file through the closed_date" (within the charge's period); compute `DAYS(MX(ch_start, F('policy_expiration_date')), closed)` drops the period's first day when the expiration on file precedes the period start (e.g. on-file expiry 2026-02-14, period 2026-07-06..08-05, closed 08-05: rule 31 days, compute 30).
2. CP post-closing tier 2 when the contract carries no lien release: rule silent; compute falls back to the closed date.
3. CM/CP gap allowance: "when the record stayed compliant for at least … whole months from its opened_date to its lapse_date" — the record is pending_verification from opened_date until its first accepted proof; compute counts MONTHS(opened_date, lapse_date). A reader counting the months the record was compliant gets another tier (demonstrated in task 0).
4. Scope edge: re-review scope "a … proof whose coverage began before the record's closed_date" and the tail's "any proof whose coverage began after the closed date" leave a proof beginning on the closed_date in neither; the reach tier 1 test "begin on or before the record's closed_date" accepts it.

### action_binding_and_uuids (r2)
Unchanged bindings; uuid8s unchanged and independent; no factor id inside a tool name. Docstrings: no example values, no ordering words; `not_applicable` now described as "the record carries no proof of this arrival channel, so there is nothing to re-review" — narrower than the rule (also: latest entry already accepted or rejected for its binder period); observation. Refund tools unchanged in behaviour (CM stamps pro_rata_from_proof_effective; observation as in revision_1).

### prerequisite_graph (r2)
Edges: CM->FEED (value_input, gate cm_proof_days), CM->UPLOAD (value_input, gate cm_binder_days), CP->FAX (value_input, gate cp_proof_days); all state form; sources verbatim in the blocked rule, absent from the depended-on rules; gate bindings exist; resolved_by = target tools; effects true of compute. Acyclic. PASS (condition wording singular vs "every": observation, as in revision_1).

### prerequisite_sentences (r2)
Same three sentences as revision_1; four-point test PASS; exactly one write per waited-on state; single-reading derivation as in revision_1. PASS.

### override_declarations (r2)
- FEED/UPLOAD/FAX: retire "Proof is reviewed only on a tracking record that is not closed.", "An accepted proof always updates the policy details on file", the lienholder, deductible and expiration clauses, and now the binder clause (declared; CW-5d closed). Tails no longer defer to retired clauses (CW-5c closed) and restate first reviews, agent-call proofs and the policy-on-file update (CW-5a/5b closed as to content). But each tail reads: "… a proof that arrived through an insurance agent call, any proof whose coverage began after the closed date, and an uploaded or faxed proof (which the re-review rule for its own channel governs with the same tests) are reviewed only on a tracking record that is not closed …" — the sibling channels are placed inside the base restriction instead of being excluded (R2-E1).
- CM/CP vs cpi_cancellation_refund: pro-rata-from-proof retired by both with tails naming each other (CW-5f closed); closure clause retired by CP; flat-cancel kept in both tails and both scopes exclude proof on/before placement_effective_date (CW-5e closed as written). New: proof-span tier 2 declares "the policy on file counts as reinstated without a gap" while base cpi_evt_proof_verification says "An insurer's reinstatement of the borrower's policy with no gap counts as continuous coverage" and the kept flat-cancel clause refunds every charge in full for continuous coverage (R2-E2).

### factor_ladders (r2)
Counts: FEED/UPLOAD/FAX 4 each (method: *_lien_route, *_reach_anchor; parameter: *_comp_cap, *_coll_cap). CM 6 (method: cm_proof_span, cm_finance, cm_binder_credit; parameter: cm_gap_allow, cm_lien_share, cm_ded_share). CP 6 (method: cp_proof_span, cp_finance, cp_post_close; parameter: cp_gap_allow, cp_lien_share, cp_ded_share). Multi-source: *_comp_cap (vehicle value AND contract model year). Cross-difficulty: *_comp_cap, *_coll_cap, *_reach_anchor, cm_finance, cp_finance, cp_post_close (contract ledger + servicing events). All ladders three tiers, stated in rule and compute, fall-through = baseline, binding sets disjoint, no factor reads another factor's binding (A1 PASS), combination order fixed (A4 PASS), baselines silent about variations (CW-1.7/1.8/1.9 closed).

All-pairs, method factors:
| factor | pair | T_a | T_b | distinguishing input | verdict |
| --- | --- | --- | --- | --- | --- |
| *_lien_route (×3) | T1/T2 | closed: constant pass | open renewal of policy on file: constant pass (compute `True`) | none — both pass on every input | FAIL |
| *_lien_route | T1/T3, T2/T3 | constant pass | own flag | flag False | PASS |
| *_reach_anchor (×3) | T1/T2 | eff <= closed_date | exp >= repossession_date | other field | PASS |
| *_reach_anchor | T1/T3, T2/T3 | as above | exp >= NOW+15 | anchor | PASS |
| cm/cp_proof_span | T1/T2 | [max(start,eff), min(exp,closed)] | (exp on file, closed] | expiry bound | PASS |
| cm/cp_proof_span | T1/T3, T2/T3 | bounded / on-file anchor | [max(start, latest eff), closed] | expiry / anchor | PASS |
| cm/cp_finance | T1/T2 | MN(apr, scra cap) × days/36500 | apr × days/36500 | none on T1's domain: contract.yaml sets apr to min(apr, scra_rate_cap_pct) under the cap, the only event that lowers apr below original_apr_pct, so MN(apr, cap) = apr | FAIL (same value) |
| cm/cp_finance | T1/T3, T2/T3 | rate × days | 0 | — (T3 unreachable, R2-C) | n/a |
| cm_binder_credit | T1/T2 | all binder days | MN(binder days, 5) | binder > 5 days | PASS |
| cm_binder_credit | T1/T3, T2/T3 | days | 0 | binder present | PASS |
| cp_post_close | T1/T3 | DAYS(closed, end) + 1 | DAYS(closed, end) | none — constant offset of one day | FAIL |
| cp_post_close | T1/T2, T2/T3 | closed-anchored | funds-final-anchored | funds_final > closed | PASS (anchor) |

### findings (r2)
Revision_1 classes, by member:
- CW-1: 1.3–1.9 closed (delay factors removed; baselines rewritten; apr owned by finance). 1.1/1.2 OPEN → R2-A.
- CW-2: lien T1/T3 same-flag pairs and fax reach offset closed; new same-method pairs → R2-B.
- CW-3: 3.1–3.7 closed (factors removed or rebuilt).
- CW-4: 4.1–4.3 closed (one schedule, identical re-review ladders).
- CW-5: 5a–5f closed as to their r1 wording; new members R2-E.
- CW-6: 6a–6i closed; new members R2-F.
- CW-7: interest-on-delay and credit removed; finance part remains → R2-G.

**R2-A (SOURCE-FACTOR RED; XF A3) assembly names factor quantities.** CM: "first the proof-covered days are formed as the proof days plus the binder days, multiplied by the lienholder share and by the deductible share; then the covered gap days are added; … then the finance part is that premium part multiplied by the finance factor". CP: "first the proof-covered days are the proof days multiplied by the lienholder share and by the deductible share; then the covered gap days and the post-closing days are added; … finance factor". Binder days, lienholder share, deductible share, gap allowance, post-closing days and finance factor are factor-decided quantities. Members: CM, CP.

**R2-B (SOURCE-FACTOR RED; XF B8/B9) tiers selecting the same method or value.** feed_lien_route, upload_lien_route, fax_lien_route T1/T2 (both a constant pass; the rule's "passes on that policy's listing" reads nothing); cm_finance and cp_finance T1/T2 (equal on T1's whole domain); cp_post_close T1/T3 (constant one-day offset).

**R2-C (SOURCE-FACTOR RED) fall-through unreachable within scope.** cm_finance and cp_finance: both rules refund "the most recent capitalised premium charge … (billing_method added_to_contract_balance)", and base/contract rules post every such charge as a linked contract_ancillary_charge, so "otherwise: no finance part" (= the baseline 0.0) is given to no customer who reaches the write.

**R2-D (SOURCE-FACTOR RED; XF B10) unreal schedules.** (1) cm_lien_share / cp_lien_share: an accepted proof's covered days are refunded at 0.9 / 0.5 because the proof does not list the company — the re-review that accepted it waived that very test "because a closed record's collateral can no longer suffer a loss", and no CPI program refunds a fraction of a day of accepted coverage. (2) cm_ded_share / cp_ded_share: the same for a deductible the re-review's ceilings accepted. (3) cm_binder_credit tier 2: an accepted binder (base accepts binders up to binder_max_days) counts for at most 5 days because the later policy came from another insurer. (4) cm_gap_allow / cp_gap_allow: a grace for uncovered days graded by how many months the record was compliant — a tenure schedule. The rework claims themselves state these are "Harborline schedules chosen to bite on the seeded worlds".

**R2-E (SOURCE-POLICY RED; XF D20/D21) overwrite conflicts.** (1) The three re-review tails each say the sibling channels' proofs "are reviewed only on a tracking record that is not closed", contradicting the sibling rules that re-review them on closed records (demonstrated in both tasks). (2) CM/CP proof-span tier 2 "the policy on file counts as reinstated without a gap" vs the in-force base reinstatement sentence plus the kept flat-cancel clause (full refund of every charge) — tier 2 refunds part of one charge where the base refunds all charges in full.

**R2-F (SOURCE-POLICY RED; XF C11/C12/C17) rule != compute at edges** — the four members under rule_compute_equivalence (r2).

**R2-G (SOURCE-POLICY RED) finance part booked as premium refund.** CM/CP still put the finance part (contract interest) into cpi_premium_refunded.amount_usd and cpi_premium_net ("Premium charged … refunded in whole or in part"; "Net force-placed premium charged … decreases with each premium refund"). Members: CM, CP.

Observations: re-review reach tier 1 is vacuous within scope (scope already requires coverage beginning before closed_date); UPLOAD rule "a uploaded proof" typo; docstring not_applicable narrower than the rule.

## closing_checklist (revision_2)
Written after both r2 reveals (2026-10-20T05:17Z). The difficulty does not close.
- Files and revisions: revision_1 text untouched; revision_2 appended in all three files.
- Scope/tools/uuids: PASS. Problem trees: PASS (task 0 n = 2, task 1 n = 1, all value_input, unmet and load-bearing, user-owned roots, acyclic).
- Seeds: PASS (both contracts inside their tier limits; ledgers reconcile; lien release and wire payoff consistent with contract.yaml).
- Personas: PASS (correction lines removed).
- GT agreement: both tasks' writes, values, baselines and sensitivities match the independent derivations figure for figure.
- Open: R2-A, R2-B, R2-C, R2-D (factor structure and realism; no policy keeps four surviving factors), R2-E (sibling tails; reinstatement vs flat cancel), R2-F (edges; task 0 second answer 21.25), R2-G (finance part booked as premium).
- Gates not re-run by this auditor (coordinator snapshot cited).

VERDICT revision_2: task0=RED task1=RED charter=R2-A,R2-B,R2-C,R2-D,R2-E,R2-F,R2-G

## revision_3

## charter_global_frozen (revision_3)
- Freeze time: 2026-10-20T09:29Z, before any revision_3 GT field was read. Covers rework rounds 3 and 4 (round-3 gate line was "gates 5/7 green" and was answered BLOCKED; this pass follows "REWORK round 4: gates 7/7 green").
- Gate snapshot (snapshot.sh round 3, 2026-10-20T09:24:43): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r3: 0.json 7b96f6da…76c1, 1.json 33a1d9c6…7168. Source hashes: cpi.extended.yaml 2c2f75f5…e5a1 (changed → every charter section re-derived), task_tools.py dc338a58…c8ed (unchanged since revision_2 → action_binding_and_uuids carried forward).
- Read: charter, rework_claims_r3.md / r4.md (item ids), blueprint, contract.yaml, masked views r3, XF_recipe.md. Not read: tasks/*.json, plan.md, worklog.md beyond its last line. Coordinator ruling applied: deductible ceilings by vehicle value/age/state as company schedules, binder max term, expiring-policy window, named-insured, VIN, loss-payee and coverage type tests, and the charter's own refund-basis choices count as real; shares/credits docking covered days, tenure grading, insurer-identity day caps and interest inside premium refunds are banned.
- Base copy identical.

### policy_conflict_scan (r3)
Same five policies, tools and graph (CM <- FEED, CM <- UPLOAD gates cm_cover; CP <- FAX gate cp_cover). FEED and FAX are identical apart from the channel (normalised diff: params, compute, factors 0 differences). UPLOAD is now scoped to uploaded binders (<= binder_max_days) with 4 factors. CM and CP share one refund schedule (same params). Re-review tails name each sibling as governed by its own rule (R2-E1 closed); refund tails name each other and keep flat cancellation, pro rata from proof and pro rata from closure for every other charge. New conflicts: R3-C.

### rule_compute_equivalence (r3)
Sweep: compute_basis verbatim; baseline sentences in rule; superseded clauses verbatim in base; replaced_by verbatim in rule. Probes (charter compute on r3 worlds): FEED/UPLOAD/FAX give not_applicable on records without a reviewable proof of their channel; no failing read. Remaining mismatches (R3-D):
1. UPLOAD: rule scope and pick are "uploaded binder" (period <= binder_max_days) and "where the record carries no uploaded binder … not_applicable"; compute re-reviews the latest upload of any length, giving rejected_binder_term for an uploaded declarations page longer than 30 days.
2. CM/CP: rule "a proof reaches the period when its expiration date falls on or after the period start"; compute also requires the effective date on or before the closed date (cm_a_ok / cp_a_ok).
3. CM/CP: rule "The proofs the … refund reads are the record's accepted insurer-feed (faxed) proof and accepted uploaded binder"; compute's tier-3/tier-4 reads (cm_le/cm_lx/cm_lins/cm_lpol, cp_le…) take the latest accepted entry of every channel (agent-call, the other channels, uploads of any length).

### action_binding_and_uuids (r3)
task_tools.py unchanged (dc338a58…): carried forward from revision_2 (PASS; docstring not_applicable wording now matches the rule's "nothing to re-review").

### prerequisite_graph / prerequisite_sentences (r3)
Edges CM->FEED and CM->UPLOAD (value_input, gate cm_cover), CP->FAX (value_input, gate cp_cover), all state form; sentences verbatim in the blocked rules, absent from the depended-on rules; gate bindings exist; resolved_by = target tools; conditions now say "every rejected proof of that channel" (matches the sentences). Four-point test PASS; one write per waited-on state. PASS.

### override_declarations (r3)
- FEED/FAX: retire the open-record gate, the policy-on-file update, the deductible clause, the expiration clause and the binder clause (declared). UPLOAD: the same minus the binder clause, which it keeps. Tails restate first reviews, agent-call proofs and base acceptance, and hand the siblings to their own rules. Gap (R3-C2): a rejected uploaded declarations page longer than binder_max_days on a closed record is in no rule's scope and no tail restates the retired gate for it.
- CM/CP: pro-rata-from-proof retired by both; closure clause by CP; tails name each other; reinstatement tier now refunds the whole period through the closed date (R2-E2 closed). Undeclared (R3-C1): both refunds divide by a "day basis" of 30 days (TX, LA) or 30.4167 days (OK, AR) instead of the charge's period days, against the in-force base cpi_evt_premium_billing sentence "Premium is earned daily by actual days (premium_earning_basis)" (both list cpi_evt_premium_billing in base_policy_refs), and against the event meaning "refunded in whole or in part": a TX charge of 79.85 for a 31-day period refunded for all 31 days gives 79.85 × 31 / 30 = 82.51 > 79.85; an OK charge of 103.20 for a 30-day period refunded for all 30 days gives 101.79 < 103.20 with every day unearned.

### factor_ladders (r3)
Counts: FEED 6 and FAX 6 (parameter: *_age_allow, *_value_allow, *_tier_allow, *_buffer_days, *_min_term; method: *_reach_anchor); UPLOAD 4 (three allowances + reach anchor); CM 4 and CP 4 (method: *_cover_rule; parameter: *_lapse_tol, *_close_adj, *_day_basis). Multi-source: cm_cover_rule / cp_cover_rule (two proof records, the coverage record). Cross-difficulty: every allowance, reach anchor, buffer, min term, lapse tolerance, close adjustment, day basis (contract record / ledger). Every ladder >= 3 tiers stated in rule and compute; fall-through = baseline; fall-throughs reachable in scope (Tier 6; model years after 2020; book value above 18,000; states outside the lists; LTV above 120 % on Tier 1–3, whose max_ltv_pct is 125–135; debit-card, MoneyGram and third-party-remittance payoffs); no factor reads another's binding; assembly sentences are generic ("plus every allowance this rule states"; "refundable days add together every day count this rule states") — R2-A closed.

All-pairs, method factors:
| factor | pair | T_a | T_b | distinguishing input | verdict |
| --- | --- | --- | --- | --- | --- |
| *_reach_anchor (×3) | T1/T2, T1/T3, T2/T3 | first-review date | repossession date / re-review date | different anchor dates | PASS (anchor) |
| cm/cp_cover_rule | T1/T2 | union of two spans | one span | second proof | PASS |
| cm/cp_cover_rule | T1/T3, T2/T3 | spans bounded by expiry | period start .. closed | reinstated policy cancelled mid-term (on-file expiry after the period start, reinstatement entry starting inside the period) | PASS |
| cm/cp_cover_rule | T3/T4 | period start .. closed | latest effective .. closed | same case | PASS |
| cm/cp_cover_rule | T1/T4, T2/T4 | expiry-bounded | latest effective .. closed | expiry before closed | PASS |
Parameter ladders, value distinctness: every parameter ladder selects three distinct values, except cm_close_adj: in CM's scope the charge "has no post-closing days", so tier 2 (ACH / mailed check: "one post-closing day stays earned", compute MX(0, cm_post + MN(0, -1)) with cm_post = 0) contributes 0 on every input, the same as the fall-through (R3-A). cp_close_adj tiers are distinct in CP.

### findings (r3)
Revision_2 classes, by member: R2-A closed. R2-B closed (lienholder ladders and finance removed; post-closing method removed). R2-C closed. R2-D closed (shares, binder cap, tenure grace removed). R2-E1 closed (new gap R3-C2). R2-E2 closed. R2-F1–F4 closed. R2-G closed (no interest, fee or credit in any refund).

**R3-A (SOURCE-FACTOR RED; XF B8) a tier that adds nothing.** cm_close_adj tier 2 equals the fall-through on CM's whole domain. Member: cm_close_adj.

**R3-B (SOURCE-FACTOR RED; XF B10) schedules no lender publishes.**
1. cm_close_adj and cp_close_adj: the stated rationale is funds finality ("wire_transfer or certified_funds, whose funds are final that day"; "ACH or mailed check, whose funds are not final until later"), but contract.yaml's own payoff_funds_clearance_business_days gives third_party_remittance 0 days (final the same day, yet put in the 0 fall-through) and debit_card_* 3 days and moneygram 1 day (not final that day, yet also in the fall-through); the ladder contradicts the business's own clearance schedule it invokes.
2. cm_day_basis and cp_day_basis: a "state rate-filing" day basis of 30 or 30.4167 days applied to actual-day billing periods, so fully unearned premium is refunded at more than 100 % (TX, 31-day period: 82.51 on a 79.85 charge) or less than 100 % (OK, 30-day period: 101.79 on 103.20). Not a refund-basis choice the charter makes (the charter's bases are full_no_lapse, pro_rata_from_proof_effective, pro_rata_from_closure on actual days).
3. feed_min_term and fax_min_term: minimum policy terms of 7 and 10 days (by LTV at signing) for a document the rule itself declares "counts as a policy"; the charter calls any proof of 30 days or less a binder (binder_max_days 30), and no lender's minimum policy term is measured in single days. The tier values exist to accept the re-seeded 10-day "short-term policies".

**R3-C (SOURCE-POLICY RED; XF D19/D21/D22) base conflicts and gaps.**
1. cm_day_basis / cp_day_basis vs the in-force "Premium is earned daily by actual days (premium_earning_basis)" and the refund event's "refunded in whole or in part" (no overwrite declares the change; see override_declarations).
2. Rejected uploaded declarations page (> binder_max_days) on a closed record: the open-record gate is retired by all three re-review overwrites but no replaced_by restates it for this case and no rule governs it.

**R3-D (SOURCE-POLICY RED; XF C11) rule != compute at edges** — the three members under rule_compute_equivalence (r3).

Observations: in FEED/FAX scope the lienholder re-test always passes and, for a proof first rejected as expiring, the deductible re-test always passes (base order); CM close-day tier refunds the closed date even with no reaching proof (out of scope).

## closing_checklist (revision_3)
Written after both r3 reveals (2026-10-20T09:31Z). The difficulty does not close.
- Revisions 1 and 2 untouched; revision_3 appended in all three files.
- Scope, tools, uuids, prerequisite graph and sentences, problem trees, personas, seeds (contracts in limits, ledgers reconcile): PASS.
- GT agreement: every write, value, baseline and sensitivity in both tasks matches the independent derivations.
- All revision_2 classes closed (R2-A … R2-G).
- Open: R3-A (cm_close_adj tier 2 null in CM), R3-B (close-adjustment channel schedule contradicts contract.yaml clearance days; 30 / 30.4167-day "rate-filing" day basis; 7/10-day minimum policy terms), R3-C (day basis vs in-force actual-day earning basis and "refunded in whole or in part", demonstrated 69.20 vs 66.97 and 81.43 vs 82.56; rejected uploaded declarations page on a closed record unrestated), R3-D (three rule/compute edge mismatches). After strikes CM and CP keep 2 factors each (< 4); FEED/FAX keep 5, UPLOAD 4.
- Gates not re-run by this auditor (coordinator snapshot cited).

VERDICT revision_3: task0=RED task1=RED charter=R3-A,R3-B,R3-C,R3-D

## revision_4

## charter_global_frozen (revision_4)
- Freeze time: 2026-10-20T11:32Z, before any revision_4 GT field was read. Entry: worklog last line "REWORK round 5: gates 7/7 green".
- Gate snapshot (snapshot.sh round 4, 2026-10-20T11:28:58): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r4: 0.json 7b5c1bdc…d9f7, 1.json f6ce42ed…a573. Source hashes: cpi.extended.yaml 87ef0786…93b0, task_tools.py 0a60f264…7a0 — both changed, every charter section re-derived.
- Read: charter, task_tools.py, rework_claims_r5.md (item ids), blueprint, contract.yaml, masked views r4, XF_recipe.md. Not read: tasks/*.json, plan.md, worklog.md beyond its last line. Base copy identical.

### policy_conflict_scan (r4)
Same five policies and graph (CM <- FEED, CM <- UPLOAD gate cm_cover; CP <- FAX gate cp_cover). FEED and FAX identical apart from channel; UPLOAD scoped to binders with a computed not_applicable for longer uploads; every re-review tail now restates that first reviews, agent-call proofs and uploads longer than binder_max_days are reviewed only on an open record (R3-C2 closed). CM and CP each retire both base refund clauses for their own charge and name each other; tails keep pro rata from proof, flat cancel and pro rata from closure for every other charge. Day basis, close adjustment and minimum terms removed (R3-A, R3-B, R3-C1 closed). CP reads accepted uploaded proofs but carries no prerequisite sentence on rejected uploads (observation: no world shows a rejected reaching upload unresolved).

### rule_compute_equivalence (r4)
Sweep: compute_basis verbatim; baseline sentences in rule; superseded clauses verbatim; replaced_by in rule. R3-D1 closed (upload length test in compute), R3-D2 closed ("counts" / "reaches" defined and used exactly), R3-D3 closed (only the named channel and declarations_page_upload are read). Probes on r4 worlds: re-reviews return not_applicable without failing reads where nothing is reviewable. No new mismatch found. Observation: the refund_basis literal pro_rata_from_proof_effective now names two computations — the base clause (every day on or after the proof's effective date, kept for other charges) and CM/CP tier 2 (covered days plus graces plus post-closing days).

### action_binding_and_uuids (r4)
Refund tools now take refund_basis (Enum: full_no_lapse / pro_rata_from_proof_effective / pro_rata_from_closure) and write it; disposition stays mailed_to_borrower (no cross-category trigger). Bindings, uuids, docstring discipline unchanged. PASS.

### prerequisite_graph / prerequisite_sentences (r4)
Unchanged structure; CM's upload sentence now "every rejected uploaded binder", condition matches (binder length named). Four-point test PASS; one write per waited-on state; acyclic. PASS.

### override_declarations (r4)
FEED/FAX retire the open-record gate, policy-on-file update, deductible, expiration and binder clauses; UPLOAD the same minus the binder clause; tails restate everything left under base and name the siblings. CM/CP retire pro-rata-from-proof and closure for their own charge only. No undeclared departure found. PASS.

### factor_ladders (r4)
Counts: FEED/FAX 6 (parameter: *_age_allow, *_ltv_allow, *_value_allow, *_tier_allow, *_buffer_days; method: *_reach_anchor); UPLOAD 4; CM/CP 4 (method: *_cover_rule, *_refund_basis; parameter: *_plan_grace, *_state_grace). Ladders >= 3 tiers, stated in rule and compute, fall-through = baseline, fall-throughs reachable, tiers distinct (claims' probe table agrees with my reading). Realism under the coordinator ruling: re-review allowances by model year, LTV at signing, book value and credit tier, state expiry buffer and reach dates are company acceptance schedules (accepted); refund bases are the charter's own; plan and state graces are schema-enum company schedules (accepted; thin rationale noted as observation).
All-pairs, method factors: *_reach_anchor (anchor dates) PASS; cm/cp_cover_rule T1 union / T2 single expiring span / T3 latest effective .. closed — PASS; cm/cp_refund_basis T1 every period day / T2 covered + counted + post-closing days / T3 post-closing days only — PASS.

### findings (r4)
Revision_3 classes: R3-A, R3-B1–B3, R3-C1–C2, R3-D1–D3 all closed.

**R4-A (SOURCE-FACTOR RED; XF A1/A6) factors gated through the refund-basis factor.** Under the standard refund basis pro_rata_from_closure "they are the post-closing days", so covered days and both graces enter the refund only when the refund-basis factor sits on a non-baseline tier. Demonstrated (refund-basis at baseline, then each other factor also at baseline): task 0 world 0.00 in every case; task 1 world 37.84 in every case. Members: cm_cover_rule, cm_plan_grace, cm_state_grace, cp_cover_rule, cp_plan_grace, cp_state_grace.

**R4-B (SOURCE-FACTOR RED; dishonest baseline) cm_refund_basis.** CM refunds a charge whose period ends on the closed_date, which "has no post-closing days", so its standard method ("As the standard method, the closing-month refund's refund basis is pro_rata_from_closure") refunds 0.00 to every customer in CM's scope — while the base clause CM retires for that charge, and keeps for every other charge, refunds an accepted proof's days under pro_rata_from_proof_effective. A zero where the charter's own standard gives a figure. Member: CM (CP's closure baseline is the base closure refund and is honest).

**R4-C (SOURCE-TASK RED, cross-task class) refunds the charter owes that gold omits.** The re-seeded proofs now start inside the previous billing period, so after the accepted re-review the kept base clause ("every other charge keeps the base refund rule: the days of its billing period on or after an accepted proof's policy_effective_date (refund_basis pro_rata_from_proof_effective)") makes a second capitalised charge refundable, and each persona asks for every refund owed. Members: task 0 charge e73712e2 (2026-06-06..07-05, 79.85; Gulf Coast effective 2026-06-08 → 28/30 → 74.53); task 1 charge ec6d42ef (2026-08-12..09-11, 103.20; Red River effective 2026-08-14 → 29/31 → 96.54). Neither refund tool's contract covers these charges (each is scoped to the charge ending on / running past the closed date). Demonstrations in the task files.

## closing_checklist (revision_4)
Written after both r4 reveals (2026-10-20T11:33Z). The difficulty does not close.
- Earlier revisions untouched; revision_4 appended in all three files.
- PASS: scope/tools/uuids, prerequisite graph and sentences, overwrites and tails, rule/compute equivalence, re-review factor ladders (FEED 6, UPLOAD 4, FAX 6 surviving), problem trees, personas, contract seeds and ledgers; GT values equal the independent derivations in both tasks.
- All revision_3 classes closed.
- Open: R4-A (cover rule and both graces gated through the refund-basis factor; members cm_cover_rule, cm_plan_grace, cm_state_grace, cp_cover_rule, cp_plan_grace, cp_state_grace), R4-B (cm_refund_basis standard pro_rata_from_closure refunds 0.00 to every CM customer), R4-C (gold omits a second refund the kept base clause owes and the persona requests: task 0 e73712e2 74.53, task 1 ec6d42ef 96.54). After strikes CM keeps 0 and CP 1 surviving factor.
- Gates not re-run by this auditor (coordinator snapshot cited).

VERDICT revision_4: task0=RED task1=RED charter=R4-A,R4-B,R4-C

## revision_5

## charter_global_frozen (revision_5)
- Freeze time: 2026-10-20T19:41Z, before any revision_5 GT field was read. Entry: worklog last line "REWORK round 6: gates 7/7 green".
- Gate snapshot (snapshot.sh round 5, 2026-10-20T19:39:12): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. Masked views r5: 0.json 4328b3ec…13a8, 1.json 7c9f8fd1…6be9. Source hashes: cpi.extended.yaml f5605b3c…1575 (changed → charter sections re-derived), task_tools.py 0a60f264…7a0 (unchanged since revision_4 → action_binding_and_uuids carried forward).
- Read: charter, rework_claims_r6.md (item ids), blueprint, contract.yaml, masked views r5, XF_recipe.md. Not read: tasks/*.json, plan.md, worklog.md beyond its last line. Base copy identical.

### policy_conflict_scan (r5)
Graph, scopes and tails as in revision_4 (PASS there). The three re-review rules carry the same factor sets as revision_4 (FEED/FAX 6, UPLOAD 4). CM and CP: the refund basis is now a plain branch (full_no_lapse / pro_rata_from_closure / pro_rata_from_proof_effective) stated once in the rule and computed by a plain binding; refund factors are cover rule (method) and three replacement-grace allowances (plan, contract state, model year) summed by a generic sentence ("as many as the sum of every replacement-grace allowance this rule states"). No conflict found.

### rule_compute_equivalence (r5)
Sweep: every compute_basis quote verbatim; baseline sentences in rule; superseded clauses verbatim; replaced_by in rule; prerequisite sources verbatim in the blocked rule and absent from the depended-on rule. Edge reads (counting / reaching, channel picks, ties, absent proofs, gaps of overlapping or nested spans) match the rule. PASS.

### action_binding_and_uuids (r5)
Carried forward from revision_4 (task_tools.py unchanged, 0a60f264…). PASS.

### prerequisite_graph / prerequisite_sentences (r5)
Unchanged from revision_4 (CM <- FEED, CM <- UPLOAD gate cm_cover; CP <- FAX gate cp_cover; state form; four-point test PASS). PASS.

### override_declarations (r5)
As revision_4; no undeclared departure. The refund standard is now the base rule's own accepted-proof count by actual days ("covered days are counted as the base refund rule counts an accepted proof's days"). PASS.

### factor_ladders (r5)
CM/CP 4 each (method: *_cover_rule; parameter: *_plan_grace, *_state_grace, *_year_grace; cross-difficulty: state and model year from the contract; multi-source: cover rule). Each ladder three tiers, distinct values, fall-through = baseline (0 days / base count), reachable in scope (Plan E/F, other states, model years after 2020). Independence: the gap quantity is a plain binding; each grace and the cover rule moves the refund on its own against the standard (base count, no grace) — R4-A closed. Standard never zero when a proof reaches — R4-B closed. All-pairs, cover rule: T1 union / T2 single expiring span / T3 latest reaching effective .. closed — PASS. Re-review ladders as revision_4 (PASS).
Observation (realism, accepted under the coordinator ruling on schema-enum company schedules): replacement grace is built additively from plan band, contract state and model year (1–2 days each); the rule gives no business reason for any of the three.

### findings (r5)
R4-A closed; R4-B closed; R4-C closed (verified on both worlds: every accepted proof takes effect on or after the refunded charge's period start, so the kept base clause leaves no earlier charge refundable). No new charter-wide defect found on any XF_recipe point.

## closing_checklist (revision_5)
Written after both r5 reveals (2026-10-20T19:41Z).
- Per-task files 0.md and 1.md correspond to tasks 0 and 1; revisions 1–4 untouched; every revision_5 comparison section carries PASS.
- Coverage and scope: task 0 = {FEED, UPLOAD, CM}, task 1 = {FAX, CP}; pairwise disjoint; all five extended policies covered; each task tool bound once; uuid8s independent and frozen.
- Problem trees: task 0 n = 2 with 2 value_input edges, task 1 n = 1 with 1 value_input edge; each root is the customer's own write (owner=user), handed over passively; every edge unmet at opening and load-bearing; the difficulty graph is acyclic.
- Factors: FEED 6, UPLOAD 4, CM 4, FAX 6, CP 4. Each policy has >= 2 parameter and >= 1 method factors, and each task has a multi-source factor (cover rule) and cross-difficulty factors. Every ladder has three distinct, reachable tiers stated in its rule. Each policy's baseline is self-sufficient and honest. Every factor moves its scored value on its own world, and each whole fall-back differs from gold (task 0: rejected_deductible_too_high / 48.94; task 1: rejected_deductible_too_high / 72.24).
- XF_recipe points 1–29 re-checked on every extended policy: no member found.
- Seeds: contracts within tier limits; ledgers reconcile; cross-category rows producible by the contract charter.
- Gates: coordinator snapshot round 5 (2026-10-20T19:39:12) all seven green on the final form. Not re-run by this auditor.
- Observations carried, not grounds for rework:
  - The replacement-grace allowances have a thin business rationale (accepted under the coordinator's schema-enum ruling).
  - The tool docstring's not_applicable wording is narrower than the rule.
  - No lien-release rows are seeded (no rule reads them).

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Freeze time: 2026-10-20T20:39Z, before any revision_6 GT field was read. Entry: worklog last line "REWORK round 7: gates 7/7 green". Context read: audits/render_source/cpi_insurance_verification_and_force_placement/render_r1.md (R1–R7 + trigger note), rework_claims_r7.md.
- Gate snapshot (snapshot.sh round 6, 2026-10-20T20:37:00): all seven gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). Masked views r6: 0.json 4328b3ec…13a8, 1.json 7c9f8fd1…6be9 — identical to r5 (worlds unchanged). Source hashes: cpi.extended.yaml 3a980bb4…312c (changed → charter re-derived), task_tools.py 0a60f264…7a0 (unchanged).
- Base copy identical. compute_basis / baseline / overwrite / prerequisite-source sweeps: all verbatim.

### render items (R1–R7, note)
- R1 CLOSED: cm_gap / cp_gap are plain bindings defined once in the standard method; each grace factor owns only its key and allowance (cm/cp_value_grace on contract book value, state, model year); result reads only decided allowances.
- R2 CLOSED: cm/cp_a_n, _b_n, _ov now cover-rule bindings; the standard count reads only plain bindings.
- R3 CLOSED: "counted as the base refund rule counts…" removed from both standards.
- R4 CLOSED as to the undefined edge (accepted re-reviews on open records now "recorded as a new review entry only"; the base status-return clause retired for them and restated for first reviews) — but the chosen outcome opens R6-A.
- R5 CLOSED: no rule or replaced_by names a sibling's factor quantity (sweep of all five rules for "loan-to-value", "expiry buffer", "grace", "allowance" outside their owners: none).
- R6 CLOSED: binder_accepted restated in every outside-rule sentence.
- R7 CLOSED: both refunds pick "the capitalised premium charge … with the latest billing_period_start"; every other pick names its key and tie rule.
- Trigger note: CP trigger now on_request, matching the borrower-run tool.

### factor_ladders / independence (r6)
Counts unchanged (FEED 6, UPLOAD 4, FAX 6, CM 4, CP 4). Binding-ownership sweep: no plain binding reads a factor-owned binding; no factor reads another factor's binding; result reads only decided values; the only plain bindings used by one factor are cm_le / cp_le, which the standard method states. Every ladder three distinct reachable tiers; baselines honest. Replay on the r6 worlds: CM 77.27 (sensitivities 61.82 / 72.12 / 72.12 / 74.70, fall-back 48.94), CP 99.76 (82.56 / 96.32 / 96.32 / 96.32, fall-back 72.24) — unchanged.

### findings (r6) — classes the renderer did not list, found in the exhaustive sweep
**R6-A (SOURCE-POLICY RED; XF D21 + realism) an accepted re-review on an open force-placed record keeps the placed coverage.** FEED, UPLOAD and FAX now say "on every tracking record, closed or not, an accepted re-review under this rule is recorded as a new review entry only: it never changes the record's status, never updates the policy details on file, never cancels placed coverage and mails no notice", and their reach ladders keep open-record tiers ("the contract's repossession_date when the record is not closed while the contract is repossessed"; "otherwise … the re-review date"). The in-force base lifecycle transition force_placed → compliant reads "Acceptable proof of coverage is verified on a force-placed record; the placed coverage is cancelled." (lifecycle, not retirable by a policy overwrite). With the record left force_placed, base cpi_evt_premium_billing ("Premium is billed only on a tracking record whose status is force_placed") keeps billing periods that the accepted proof covers, and the kept base refund clause ("every other charge keeps … the days of its billing period on or after an accepted proof's policy_effective_date") refunds them — a bill-and-refund loop no lender publishes. Members: cpi_ext_feed_proof_rereview, cpi_ext_upload_proof_rereview, cpi_ext_fax_proof_rereview.

**R6-B (SOURCE-POLICY RED; XF D19) the closing-period charge is handed to CP whatever the proofs, but CP's scope requires counting proofs.** CP's two replaced_by texts and CM's two replaced_by texts state "the charge whose billing period runs past the closed_date of a record closed while force_placed is fixed by the closing-period refund rule" with no proof condition, retiring the base closure clause for that charge; CP's rule "governs the refund … when accepted proofs of the borrower's own coverage that count for that period are a faxed proof, an uploaded proof, or both". For an ordinary payoff with no accepted proof, no in-force sentence restates the base closure refund for that charge (compute happens to give pro_rata_from_closure 10.32 on the task-1 world with proofs removed, but the rule text does not govern it). Members: CP overwrite[0], CP overwrite[1], CM overwrite[0], CM overwrite[1] (the hand-off clause).

**R6-C (SOURCE-POLICY RED; realism, recurrence of r1 CW-4.3) the refund depends on the channel the accepted proof arrived through.** CM reads "the record's accepted insurer-feed proof … and its accepted uploaded proof …, and no proof of any other channel"; CP reads the faxed and uploaded proofs and "no proof of any other channel"; both retire the base pro-rata-from-proof clause for their charge. So an accepted proof that arrived by fax (for CM) or by insurer feed (for CP), or by insurance-agent call (for either), earns no proof days on the refunded charge, whereas the base clause they retire refunds every day on or after any accepted proof's effective date. Demonstrated on the task worlds (charter compute, only verification_source changed): task 0 Gulf Coast proof arriving by fax instead of feed → 15.45 instead of 77.27; task 1 Red River proof arriving by feed instead of fax → 27.52 instead of 99.76. A lender's unearned-premium refund does not depend on how the insurer transmitted the proof. Members: cpi_ext_closing_month_refund, cpi_ext_closing_period_refund.

No other XF_recipe member found (A1–A7, B8–B10, C11–C17, D18–D22 apart from the above, E23–E26, F27–F29 swept).

## closing_checklist (revision_6)
Written after both r6 reveals (2026-10-20T20:40Z). The difficulty does not close.
- Earlier revisions untouched; revision_6 appended in all three files. GT figures equal the derivations in both tasks (unchanged from revision_5).
- Render items R1–R7 and the trigger note: closed.
- Open, each found in the exhaustive sweep and missed in revision_5:
  - R6-A: an accepted re-review on an open force-placed record keeps the placed coverage, against the base lifecycle and the base billing/refund rules. Members: FEED, UPLOAD, FAX.
  - R6-B: the charge running past the closed date is handed to CP whatever the proofs, while CP governs only charges with counting proofs. Members: the CP and CM hand-off clauses, four replaced_by texts.
  - R6-C: the closing refunds ignore accepted proofs from other channels. Members: CM, CP. Demonstrated 15.45 vs 77.27 and 27.52 vs 99.76.
- Gates: coordinator snapshot round 6 cited; not re-run by this auditor.

VERDICT revision_6: task0=RED task1=RED charter=R6-A,R6-B,R6-C

## revision_7

## charter_global_frozen (revision_7)
- Freeze time: 2026-10-20T21:07Z, before any revision_7 GT field. Entry: worklog last line "REWORK round 8: gates 7/7 green". Claims read: rework_claims_r8.md.
- Gate snapshot (snapshot.sh round 7, 2026-10-20T21:05:45): all seven gates OK. Masked views r7: 0.json 4328b3ec…13a8, 1.json 7c9f8fd1…6be9 (unchanged since r5). Source hashes: cpi.extended.yaml 6216604c…1e56 (changed → charter re-derived), task_tools.py 0a60f264…7a0 (unchanged).
- Base copy identical; compute_basis / baseline / overwrite / prerequisite-source sweeps verbatim; uuids and tool contracts unchanged (PASS).

### revision_6 classes
- R6-A CLOSED: FEED, UPLOAD and FAX now govern "on a closed tracking record only"; compute returns not_applicable when the record is not closed (probe: task-0 record set to force_placed → not_applicable for feed and upload); tails restate the base review, policy-on-file update, return to compliant and cancellation for open records. Reach ladders re-keyed to closed-record cases (paid off → first-review date; not paid off with a repossession_date → that date; standard → re-review date), all three tiers reachable and distinct.
- R6-B CLOSED: one shared hand-off in both refunds' replaced_by — the latest charge of a record closed while force_placed by payoff goes to CM / CP "when an accepted proof counts for that charge's period"; "that charge in any other case, and every other charge" keep the base rule with full_no_lapse, pro_rata_from_proof_effective and pro_rata_from_closure restated. CM and CP scope sentences use the same test.
- R6-C NOT CLOSED (R7-A).

### render_r1 classes re-swept (R1–R7)
Binding ownership: no plain binding reads a factor binding; no factor reads another factor's binding; result reads only decided values; cm_union / cm_gap / cm_le (cp_ likewise) are plain and stated in the standard method. No rule or replaced_by names another policy's factor quantity. No deferral to a retired clause. Every retired clause's remaining content restated. Every pick names its key and tie rule. PASS.

### factor_ladders (r7)
Unchanged counts and ladders; replay unchanged: CM 77.27 (61.82 / 72.12 / 72.12 / 74.70; fall-back 48.94), CP 99.76 (82.56 / 96.32 / 96.32 / 96.32; fall-back 72.24). Union by inclusion–exclusion over up to four interval spans is exact; replacement days = earliest-to-latest reaching span minus the union. PASS.

### findings (r7)
**R7-A (SOURCE-POLICY RED; realism, residual of R6-C) the refund still depends on the arrival channel — now on whether two proofs share one.** Both refunds read, "for each channel, the record's accepted proof of that channel with the latest policy_effective_date, a later accepted proof from a channel superseding an earlier one from the same channel", so an accepted proof covering part of the refunded period is dropped whenever a later-effective accepted proof arrived through the same channel, while the base clause both rules retire for that charge refunds the days of every accepted proof. Demonstrated with the task proofs, changing only verification_source:
- task 0: Pecos binder arriving by insurer fax or agent call → 77.27 (unchanged); arriving by the insurer feed, the same channel as the Gulf Coast policy → 48.94 (binder days and replacement grace lost);
- task 1: Sooner State binder arriving by insurer feed → 99.76; arriving by insurer fax, the same channel as the Red River policy → 72.24.
A binder followed by the policy from the same insurer feed is the ordinary case; a lender's unearned-premium refund does not change with that coincidence. Members: cpi_ext_closing_month_refund, cpi_ext_closing_period_refund.

Observation: CM waits by sentence only on feed and upload re-reviews and CP only on fax, while both now read accepted proofs of every channel; in a world with a rejected, re-reviewable proof of another channel reaching the period, the refund would move with that re-review without a sentence saying so (no task world has such a proof; the reworker records it as a residual).

## closing_checklist (revision_7)
Written after both r7 reveals (2026-10-20T21:07Z). The difficulty does not close.
- Earlier revisions untouched; revision_7 appended in all three files; GT equals the derivations in both tasks.
- R6-A and R6-B closed. render_r1 classes re-swept clean. Every other XF_recipe point re-checked: no member.
- Open: R7-A (same-channel supersession drops an accepted proof's days; members cpi_ext_closing_month_refund, cpi_ext_closing_period_refund; demonstrated 48.94 vs 77.27 and 72.24 vs 99.76).
- Gates: coordinator snapshot round 7 cited; not re-run by this auditor.

VERDICT revision_7: task0=RED task1=RED charter=R7-A

## revision_8

## charter_global_frozen (revision_8)
- Freeze time: 2026-10-20T21:55Z, before any revision_8 GT field. Entry: worklog last line "REWORK round 9: gates 7/7 green". Claims: rework_claims_r9.md.
- Gate snapshot (snapshot.sh round 8, 2026-10-20T21:53:10): all seven gates OK. Masked views r8: 0.json e7a3f0dd…0b61 (changed: the 2025 Bluebonnet proof deb2544f now verification_source insurance_agent_call), 1.json 7c9f8fd1…6be9 (unchanged). Source hashes: cpi.extended.yaml 6bc5e00a…dd4 (changed → re-derived), task_tools.py 0a60f264…7a0 (unchanged).
- Sweeps: base copy identical; compute_basis, baseline, overwrite and prerequisite sources verbatim; binding ownership clean (cm/cp_single, _le_b, _lx_b, _base_days, _base_basis are plain); uuids and tools unchanged. Re-review policies, prerequisite graph and sentences unchanged from revision_7 (PASS). Replay: CM 77.27, CP 99.76, all sensitivities and fall-backs unchanged.

### R7-A verification
- In scope (no channel holding more than one accepted proof): one reading — each channel contributes its one accepted proof, union of reaching spans, channel-blind (verified: moving a task proof to an empty channel leaves 77.27 / 99.76). PASS.
- Out of scope: the base rule restated in the hand-off tail plus the reading note "where the base rule reads an accepted proof's policy_effective_date for that charge, it reads the accepted proof with the latest policy_effective_date, whatever its channel"; computed by cm/cp_base_days and _base_basis. Two defects remain (below).

### findings (r8)
**R8-A (SOURCE-POLICY RED; XF C11) the out-of-scope computation is not the restated base rule.** The tail restates "after accepted proof the days of its billing period on or after the proof's policy_effective_date (refund_basis pro_rata_from_proof_effective)"; cm_base_days / cp_base_days apply that only when the latest-effective accepted proof also expires on or after the period start (`cm_lx_b >= cm_start`), otherwise closure days. Probe (task-0 charge 2026-07-06..08-05, record with two accepted feed proofs 2026-04-10..05-10 and 2026-05-11..06-10): restated base text → every day on or after 2026-05-11 = 31 days → 79.85; compute → pro_rata_from_closure, 0.00. Members: cm_base_days / cm_base_basis, cp_base_days / cp_base_basis.

**R8-B (SOURCE-POLICY RED; realism, R7-A residual; departs from the coordinator route's "at most one counting accepted proof per channel") the scope test counts accepted proofs that do not count for the period.** Both scopes and the shared hand-off read "no arrival channel holds more than one accepted proof on the record (a count of the record's accepted cpi_proof_verified entries per verification_source)", including long-expired proofs from before the placement. The refund for the same coverage therefore still turns on a channel coincidence, now with an irrelevant proof:
- task 0: the 2025 Bluebonnet proof (expired 2026-02-14) arriving by the insurer feed, as it did in revisions 1–7, takes the record out of scope → base reading from the Gulf Coast policy's 2026-07-18 → 48.94 instead of 77.27 (binder days and replacement grace lost); the re-seed to insurance_agent_call exists only to keep the task in scope;
- task 1: the 2025 Prairie Shield proof arriving by insurer fax → 72.24 instead of 99.76.
An original proof at funding and a later policy from the same insurer feed is the ordinary case. Members: cpi_ext_closing_month_refund, cpi_ext_closing_period_refund (scope sentence and hand-off clause in each).

## closing_checklist (revision_8)
Written after both r8 reveals (2026-10-20T21:55Z). The difficulty does not close.
- Earlier revisions untouched; revision_8 appended in all three files; GT equals the derivations in both tasks.
- R7-A closed as written in revision_7 (no supersession inside the rule; in-scope reading unique and channel-blind).
- Every other XF_recipe point re-checked: no member.
- Open, members listed exhaustively:
  - R8-A: the out-of-scope computation adds an expiry condition the restated base text lacks. Members: cm_base_days / cm_base_basis, cp_base_days / cp_base_basis.
  - R8-B: the scope counts accepted proofs that do not count for the period, so an expired pre-placement proof on the same channel moves the refund (48.94 vs 77.27; 72.24 vs 99.76). Members: the CM and CP scope sentences and their shared hand-off clause.
- Gates: coordinator snapshot round 8 cited; not re-run by this auditor.

VERDICT revision_8: task0=RED task1=RED charter=R8-A,R8-B

## revision_9

## charter_global_frozen (revision_9)
- Freeze time: 2026-10-20T22:13Z, before any revision_9 GT field. Entry: worklog last line "REWORK round 10: gates 7/7 green". Claims: rework_claims_r10.md. Coordinator ruling applied: the coarse per-channel entry count is an accepted DSL route; judged only on exact statement and exact computation of both sides.
- Gate snapshot (snapshot.sh round 9, 2026-10-20T22:11:48): all seven gates OK. Masked views r9: 0.json e7a3f0dd…0b61, 1.json 7c9f8fd1…6be9 (both unchanged since r8). Source hashes: cpi.extended.yaml 1d0d8edf…0ca0b4 (changed → re-derived), task_tools.py 0a60f264…7a0 (unchanged).
- Sweeps: base copy identical; compute_basis, baseline, overwrite and prerequisite sources verbatim; binding ownership clean; uuids and tools unchanged; re-review policies, prerequisite graph and sentences, factor ladders unchanged (PASS). Replay on both worlds: CM 77.27 (61.82 / 72.12 / 72.12 / 74.70; fall-back 48.94), CP 99.76 (82.56 / 96.32 / 96.32 / 96.32; fall-back 72.24) — unchanged.

### revision_8 classes
- R8-B CLOSED under the ruling: scope sentence and hand-off state the plain record test "no verification_source holds more than one accepted cpi_proof_verified entry", computed as COUNT per channel (cm/cp_single), with no purpose clause.
- R8-A CLOSED: the tail restates the base clauses verbatim, then states three readings (latest-effective proof whatever its channel; "with no gap" = effective on or before placement_effective_date and expiring on or after it; one refund for the union of proof-clause and closure-clause days, basis named accordingly). Independent check: I implemented the base side from the rule text alone and compared it with the charter compute on 716 out-of-scope probe records per both worlds (two accepted proofs on one channel or across channels, 15 candidate dates each, plus the no-proof case): amount and refund_basis agree in every case.

### findings (r9)
**R9-A (SOURCE-POLICY RED; XF C12) the out-of-scope reading picks "the record's accepted proof with the latest policy_effective_date" with no tie rule.** Its expiration date then decides full_no_lapse. compute (cm_lx_b / cp_lx_b = LATEST by policy_effective_date) keeps the first recorded entry. Probe on the task-0 charge: two accepted feed proofs, both effective 2026-02-01, expiring 2026-03-01 and 2026-12-31 → 0.00 (pro_rata_from_closure) when the 03-01 entry is recorded first, 79.85 (full_no_lapse) when the 12-31 entry is. The rule text gives no way to choose. Every in-scope pick and the re-review picks state their tie rule; this one does not. Members: the tail reading sentence of cpi_ext_closing_month_refund and of cpi_ext_closing_period_refund (cm_lx_b / cm_le_b, cp_lx_b / cp_le_b).

## closing_checklist (revision_9)
Written after both r9 reveals (2026-10-20T22:13Z). The difficulty does not close.
- Earlier revisions untouched; revision_9 appended in all three files; GT equals the derivations in both tasks.
- R8-A and R8-B closed. Every other XF_recipe point re-checked: no member.
- Open, members listed exhaustively: R9-A, the out-of-scope latest-effective pick states no tie rule. Members: the CM and CP tail reading sentences. Demonstrated 0.00 vs 79.85.
- Gates: coordinator snapshot round 9 cited; not re-run by this auditor.

VERDICT revision_9: task0=RED task1=RED charter=R9-A

## revision_10

## charter_global_frozen (revision_10)
- Freeze time: 2026-10-20T22:48Z, before any revision_10 GT field. Entry: worklog last line "REWORK round 11: gates 7/7 green". Claims: rework_claims_r11.md.
- Gate snapshot (snapshot.sh round 10, 2026-10-20T22:47:57): all seven gates OK. Masked views r10: 0.json e7a3f0dd…0b61, 1.json 7c9f8fd1…6be9 (unchanged since r8). Source hashes: cpi.extended.yaml 30ebda6c…723f (changed → re-derived), task_tools.py 0a60f264…7a0 (unchanged).
- Sweeps: base copy identical; compute_basis, baseline, overwrite and prerequisite sources verbatim; uuids and tools unchanged.

### R9-A
CLOSED. Both refunds' tail reading sentence (rule, replaced_by, compute_basis) now ends "and where two accepted proofs share that date the one recorded first counts". cm_le_b / cm_lx_b (cp_ likewise) are LATEST by policy_effective_date over the same filter, so both keep the same first-recorded row. Re-running my independent text-only implementation (first-recorded tie, as stated) against the charter compute on the same 716 out-of-scope probes plus the no-proof case: 0 mismatches. In the revision_9 tie probe the first-recorded entry decides, as the sentence now says.

### tie sweep (every record pick in the five policies)
- FEED / UPLOAD / FAX: every read of the re-reviewed entry (result, flag, deductibles, dates, first-review date) is LATEST by activity_date on the channel. The rule states "by review date (where two entries share that date, the one recorded first counts)". Stated.
- CM / CP charge pick: LATEST billing_period_start; the premium is the SUM over that billing_period_start, so equal starts form one charge (one period, one end date). No tie left open.
- CM / CP per-channel proof reads: inside the scope each channel holds at most one accepted entry, so there is no tie; outside the scope they are unused.
- CM / CP base-side pick: stated (above).
- Remaining "earliest / latest" phrases (earliest reaching span start, latest reaching span end, latest effective date among reaching proofs, earliest counting effective date) compare dates only and pick no record.
No unstated tie remains.

### figures
Replay on both worlds unchanged:
- FEED / UPLOAD / FAX accepted, each with the same solo sensitivities.
- CM 77.27: sensitivities 61.82 / 72.12 / 72.12 / 74.70; fall-back 48.94; load-bearing 15.45 / 48.94.
- CP 99.76: sensitivities 82.56 / 96.32 / 96.32 / 96.32; fall-back 72.24; load-bearing 27.52.
All other sections are carried forward from revision_9 (PASS) on unchanged inputs other than the tie sentence.

## closing_checklist (revision_10)
Written after both r10 reveals (2026-10-20T22:48Z).
- Files: 0.md and 1.md correspond to tasks 0 and 1. Revisions 1–9 are untouched. Both revision_10 comparisons carry PASS.
- Scope and coverage:
  - task 0 = {FEED, UPLOAD, CM}; task 1 = {FAX, CP};
  - the two scopes are disjoint and together cover all five extended policies;
  - each task tool is bound once; the uuid8s are independent.
- Problem trees:
  - task 0 has n = 2 with 2 value_input edges; task 1 has n = 1 with 1 value_input edge;
  - each root is the customer's own write, handed over passively;
  - every edge is unmet at the opening and load-bearing;
  - the graph is acyclic.
- Factors:
  - counts: FEED 6, UPLOAD 4, CM 4, FAX 6, CP 4; each policy has >= 2 parameter and >= 1 method factors;
  - each task has a multi-source factor and cross-difficulty factors;
  - every ladder has three distinct, reachable tiers stated in its rule;
  - baselines are honest and self-sufficient; every factor moves its value on its own;
  - each whole fall-back differs from gold (rejected_deductible_too_high; 48.94; 72.24).
- XF_recipe points 1–29 re-checked; render_r1 classes R1–R7 re-checked; revision_6–9 classes closed. The tie sweep is exhaustive (see revision_10 sections).
- Seeds: contracts within their tier limits; ledgers reconcile; cross-category rows are producible.
- Gates: coordinator snapshot round 10 (2026-10-20T22:47:57), all seven green on the final form. Not re-run by this auditor.
- Observations carried, none grounds for rework:
  - the replacement-grace rationale is thin (accepted under the schema-enum ruling);
  - the per-channel entry count is a coarse scope, accepted under the DSL-limit ruling;
  - no lien-release rows are seeded, and no rule reads them.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN
