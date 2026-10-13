# Policy-task audit — appeals_and_grievances / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1.
- Freeze time: 2026-10-11 ≈13:14Z (file mtime). Written before any task's GT was revealed; nothing in this section is derived from `evaluation_criteria`, `computations`, `prerequisite_closure`, `design_rationale`, `solvability_contract`, `charter_scope` or `required_documents`.
- Frozen inputs:
  - `tasks/appeals_and_grievances/appeal.extended.yaml` sha256 `9c352b2df10cace5616eb4d460be1c933a664a79797a88917974e1ea7320954a`
  - `tasks/appeals_and_grievances/task_tools.py` sha256 `bf67ea1fb137460fd046bd81007128cc5a7f46a6874948f63efeb820d9385dbb`
  - Masked views `0.view.json` sha256 `6ddde110…154c0c`, `1.view.json` sha256 `3b69bc87…d63b9b0de4679714f9eeb89cbc84793a8e2ae63d42` (each keeps `frozen_time`, `user_scenario`, `initial_state` only; `_masked_keys` lists charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract).
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures), `blueprint/products/appeal.yaml`, `blueprint/products/select.yaml` and `referral` schema (cross-category parameters the charter reads), the extended charter, `task_tools.py`, `erlbench/` and the gate scripts' DSL definition (`skills/erl-task-instantiate/scripts/check_compute.py`, `references/product_extended.yaml` DSL comment block) to fix the compute semantics.
- Not read: `tasks/*.json`, the difficulty's `worklog.md`, `/tmp/ag55/`, any other scenario, any sibling difficulty's tasks.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cache_diff INFO, check_cross_fire SCOPE OK, check_traceability deferred), the masked views and their hashes. Hashes re-verified locally (`sha256sum`): all four match the brief. Input complete.
- Scratch recomputation scripts: `/tmp/erl55_audit_appeal/recompute.py`, `t0.py`, `t1.py`, `t1b.py`, `t1c.py`, `chk.py` (they import `build_env`/`eval_compute`/`substitute` from the gate script so the compute is evaluated with the DSL's own semantics; worlds are built only from the masked views plus the auditor's own derived writes).

Base copy: `diff <(sed -n 1,860p appeal.extended.yaml) blueprint/products/appeal.yaml` differs only by the 4-line extended banner; a YAML-level comparison of every base key (category … policies) is equal. The base copy is verbatim.

Policy short names used below:
P1 `appeal_ext_late_filed_line_first_case` (file_select_line_reconsideration_8918facf, owner user),
P2 `appeal_ext_late_filed_line_joining` (join_select_line_reconsideration_711ff8e9, user),
P3 `appeal_ext_late_filed_case_formal_review` (request_formal_review_d6793db3, user),
P4 `appeal_ext_stay_charge_review_first_line` (file_allowable_charge_review_fa2a3df4, user),
P5 `appeal_ext_stay_charge_review_joining` (join_line_charge_review_4bed256c, user),
P6 `appeal_ext_stay_reconsideration_second_level` (request_second_level_reconsideration_e1311ea5, user),
P7 `appeal_ext_stay_expedited_continued_stay` (take_expedited_reconsideration_1b494fd4, agent).

### policy_conflict_scan

- Subjects / triggers: P1, P2, P4, P5, P7 are `appeal_file`; P3, P6 are `appeal_escalate`; every one `trigger: on_request`, `computes: amount_in_dispute`. The two families are disjoint by subject record: P1–P3 act on denied Select claim lines (`denied_untimely_filing`) and a decided Claim Factual Reconsideration; P4–P7 act on paid Select inpatient lines, a decided Medical Necessity Reconsideration and a denied Inpatient Mental Health authorization.
- Overlap P1 vs P2 and P4 vs P5: both pairs can write a case record on the same kind of line (a denied late-filed line; a paid inpatient line). They are separated only by the "first / further line" wording; see `prerequisite_sentences` finding G-1 for where that separation fails.
- Time anchors: every filing policy re-states the posted-date / denial-date deadline counted from the day after (consistent with base `appeal_filing_deadline`). P3/P6 inherit base `appeal_next_level` (60 / 90 days, $50 / $0 minimum).
- Cross-category read boundary: all seven read `select` (claim lines, enrollment `ohi_on_file`, tier parameters); P4–P7 also read `referral` (authorizations, unit ledger). No write crosses into another category.
- Terminal states: P1/P2/P4/P5 create `appeal_cases` rows with status `filed`; P7 creates a `filed` expedited row; P3/P6 move a decided case to `escalated`. No two policies drive the same row to different terminal states.
- Scope claims: from the masked views alone (no `charter_scope` read) the two worlds naturally host P1–P3 (task 0: decided CFR on a late-filed line, re-billed denied lines) and P4–P7 (task 1: decided MNR, paid stay lines, denied continued-stay request). The seven policies are jointly covered if so; the confirmation against `charter_scope` is a post-reveal item and is recorded in each task file and in `closing_checklist`, not here.

### rule_compute_equivalence

Compute semantics fixed from the DSL definition (`references/product_extended.yaml` DSL block and `check_compute.build_env`): in-category `SUM/COUNT/MAX/LATEST` are "AUTOMATICALLY SCOPED TO THIS HOLDING (a <holding_pk>=HID filter is added)"; for `appeal_cases` the holding pk is `appeal_case_id`; `X*` reads scope to the customer; `CPARAM/CFIELD` return the first matching holding.

Sweep results, policy by policy (every factor tier was checked to be a rule sentence and a branch of its `decides` binding, and every branch back to a rule sentence; the baseline sentences are all in the rule — verified by script `chk.py`, no "BASELINE SENTENCE NOT IN RULE" output):

- P1: equivalent. Window `within_months=12` on `posted_date` relative to the clock = "posted in the twelve months before the day the amount is figured"; `peer_latest_allowed` without window is only used when ≥1 in-window line exists, so it equals the rule's "most recently posted … such line". `earlier_posting_ohi_paid` (XMAX over all postings of that claim+service date) does not restrict to *earlier* postings — latent only (observation O-3).
- P2: `case_claim_number`, `case_line`, `case_amount_so_far` are in-category `LATEST/MAX` on `appeal_cases`, hence scoped to `appeal_case_id = HID`. The rule's "the patient's Claim Factual Reconsideration most recently filed and still filed" and "the largest amount in dispute recorded on that case's records on the claim that are still filed" select across the patient's records; the compute reads one row (the target holding). Equal only when exactly one such record exists (observation O-1). The compute filters `status='filed'` while the prerequisite sentence admits "filed or under review" (observation O-2).
- P3: `review_eob_held` is holding-scoped on `appeal_case_documents.appeal_case_id` = "held in the case" — equivalent. Carry tiers equivalent.
- P4: equivalent, except tier parameters are read with `CPARAM(..., status='active')` (the patient's active Select enrollment) where the rule says "the tier's" — latent when the line's enrollment is not the active one (observation O-4).
- P5: same holding-scoping pattern as P2 for `join_review_claim` / `join_review_amount_so_far` (observation O-1).
- **P6 and P7: rule/compute break (finding G-2).** Rule tier 1 of the daily allowed amount applies when "every paid day line of the stay stands in a filed Allowable Charge Review". Compute: `sl_reviews_filed: "COUNT('appeal_cases', variant_name='Allowable Charge Review', status='filed', subject_claim_number=sl_stay_claim)"` and `ex_reviews_filed` likewise — an in-category COUNT scoped to `appeal_case_id = HID`, i.e. it can count at most the target holding itself, which for these policies is the Medical Necessity case (variant MNR), so it is 0 on every world; `sl_daily_allowed` / `ex_daily_allowed` can never take tier 1 while the stay has ≥1 paid line. A second break: the rule's fall-through "where the stay has no paid day line, it is the facility's billed amount per covered day on the stay" is computed as `RND(sl_stay_billed / sl_stay_days, 2)` where both sums are filtered `line_outcome='paid'` — on exactly the worlds that reach this tier both are 0 and the expression divides 0 by 0 (finding G-3).

### action_binding_and_uuids

- `(target_tool, computes)`: seven distinct tools, each claimed by exactly one policy. No docstring names another tool or a position in a sequence. Docstrings of the two join tools describe the presumed state ("the Claim Factual Reconsideration already open on that claim", "the Allowable Charge Review already open on that claim") — a state description, no ordering word about another action, no tool name (observation O-6).
- Function bodies: every tool performs exactly one `ctx.create` or `ctx.update`; none reads any table, none refuses, errors or hints when another problem is unresolved. The tool layer judges no prerequisite.
- uuid8s: 8918facf, 711ff8e9, d6793db3, fa2a3df4, 4bed256c, e1311ea5, 1b494fd4 — no shared prefix/suffix, no sequential or adjacent values, none reused. PASS.

### prerequisite_graph

Edges (blocked <- depended-on): E1 P2<-P1 (value_input, gate `case_amount_so_far`); E2 P3<-P2 (state_gate, gate `appeal_cases.subject_claim_line_id`); E3 P5<-P4 (value_input, `join_review_amount_so_far`); E4 P6<-P5 (value_input, `sl_daily_allowed`); E5 P7<-P6 (value_input, `ex_days`); E6 P7<-P5 (value_input, `ex_daily_allowed`). P1 and P4 declare `prerequisite: []`.

- Every policy has `prerequisite`; every `problem` is another extended policy id; no self-loop; graph acyclic (two chains P1→P2→P3 and P4→P5→{P6,P7}, P6→P7).
- Every `policy_source` is verbatim and unique in its own rule (script `chk.py`: verbatim True, count 1 for all six). All `form: state`; no `fallback_reason` present, none needed.
- No authoring-viewpoint phrase ("this task", "opening", "current world") in any `prerequisite` field.
- `kind`/`gate`: value_input gates exist as bindings (E1, E3–E6). E2 is `state_gate` with `gate: appeal_cases.subject_claim_line_id`, which is a column, not an eligibility gate; P3 has no eligibility gate at all (observation O-5).
- `condition` vs sentence: **E4 and E6 conditions are stronger than their sentences (finding G-4).** Sentence (E4): "…the amount carried to the second level is not priced until the highest-numbered paid day line of the stay's claim stands in a filed Allowable Charge Review." Condition: "appeal_cases holds a filed Allowable Charge Review on every paid line of the stay's claim, the last one on the claim's highest line_number paid line". E6 is the same pair. A world in which only the highest-numbered paid line is under a filed review satisfies the sentence and fails the condition.
- `effect` vs compute: E4/E6 effects assert "the count of filed reviews on the stay's claim reaches the count of its paid lines and the daily allowed amount … becomes the earlier admission's rate". Under the compute (G-2) the count never moves, so `resolved_by` does not change the gated binding's value (bound to G-2; demonstrated in `1.md`).

### prerequisite_sentences

Four-point test per edge (ordering connective / record-visible state / no tool, id, snake token / strength):

- E1 "The amount recorded for a further line joining a reconsideration is fixed only after a Claim Factual Reconsideration stands filed or under review on an earlier line of the same claim carrying the same denial." — "only after", state form, clean. Writes that bring it about: only P1 (P2's own record is by definition on the claim's highest-numbered posting, never an "earlier line"). Derivation: sentence + `appeal_cases` (no filed/under-review CFR on the claim) + P1's rule ("A Claim Factual Reconsideration opened on a TRICARE Select claim line that was denied because the claim reached the region after the claim filing deadline…") → open P1 on an earlier denied line. PASS (with O-2 latent).
- E2 "The amount carried to the next level is fixed only after the claim's highest-numbered posting denied for the same reason stands in a Claim Factual Reconsideration that is filed or under review." — connective and form fine. **Two writes bring this state about (finding G-1):** P1 opened directly on the highest-numbered denied posting, and P2 joining that posting. **Second wording (finding G-5):** the same rule also says "The next level hears a claim only once every posting of it denied for the same reason is under review at some level, so that no later posting of the claim lapses at the first level while an earlier one is carried up." — a broader statement of the same dependency (every posting vs the highest-numbered posting) carried in the blocked rule beside the declared sentence.
- E3 "The amount recorded for a further paid line joining an Allowable Charge Review is not fixed until an Allowable Charge Review stands filed on an earlier paid line of the same claim." — "not … until", state form; only P4 brings it about. PASS.
- E4 "Where the stay's paid daily rate falls below the facility's daily rate on the patient's admission of the past twelve months, the amount carried to the second level is not priced until the highest-numbered paid day line of the stay's claim stands in a filed Allowable Charge Review." — connective and form fine; **two writes bring the state about (finding G-1):** P4 opened on the highest-numbered paid line, or P5 joining it.
- E5 "The days at issue on a continued-stay request are counted only after the stay's earlier medical necessity reconsideration stands escalated or its next-level window has closed." — "only after", state form; the escalated state is brought about only by P6 (P3's tool can set `escalated` on any case id, but P3's rule hears only a decided Claim Factual Reconsideration). The alternative "next-level window has closed" is the passage of time, which is a wait, not a write. PASS.
- E6 "Where the stay's paid daily rate falls below that of the patient's admission at the same facility in the past twelve months, the continued-stay amount is not valued until the last paid day line of the stay's claim stands in a filed Allowable Charge Review." — as E4: **two candidate writes (G-1)**.
- No rule names a tool, a policy id or a snake_case token (script check). No depended-on rule restates the blocked rule's sentence.
- Base rule sentences that state a cross-problem order (e.g. `appeal_reinstatement_review` "reinstated only after every past-due fee…") ground no edge here. PASS.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusions only; consequences are demonstrated per task):

- `appeal_agg_multi_holding`, `appeal_agg_one_open_case`: followed by P1/P2/P4/P5/P7 (narrowest subject, one open case per line, grouping with own line reference, decided case not reopened at the same level).
- `appeal_tier_selection`: P1/P2/P4/P5/P7 declare an overwrite of "The case's subject_kind must be one of the tier's appealable_subject_kinds." whose replacement restates the same content; no conflict, merged semantics unique.
- `appeal_filing_deadline`: declared overwrites restate the posted-date / denial-date deadline counted from the day after; consistent with base. Good-cause and dismissal sentences inherited.
- `appeal_standing_and_representation`, `appeal_reinstatement_review`, `appeal_grievance_and_charge_review`: followed / not engaged.
- `appeal_amount_in_dispute`: P2, P4, P5, P6, P7 declare overwrites of the lead clause or of the per-subject clause. P1 and P3 declare none; their "payment the line would have carried … no beneficiary liability at issue" is a reading of base "the TRICARE payment denied plus the beneficiary liability at issue" (no conflict on a participating provider's line). **The base sentence "Amounts a nonparticipating provider bills above the allowed amount are never in dispute." is superseded by no policy, while (finding G-6):** P1–P3 fall-through "the amount the provider billed on the line", P4/P5 tier 2 "the line's billed amount divided by its covered days … rate claimed", and P6/P7 baseline and fall-through "the facility's billed amount per covered day on the stay" each place the billed amount — including whatever a nonparticipating provider bills above the allowed amount — into the amount in dispute. Same situation (nonparticipating facility, billed per day above the allowed per day): base says the excess is never in dispute; these sentences put it in dispute.
- `appeal_review_tracks` (P7 via tier selection): P7's "the treating provider's urgent request on record standing as the provider's certification" elaborates base "as certified by the treating provider"; no contradiction on a record whose `review_priority` is urgent and requested by the treating facility (observation O-7).
- `appeal_next_level` (P3, P6): deadlines, appellant-only request and minimum amounts inherited; P3/P6 add how the amount is figured afresh, which base does not fix. No conflict.

### factor_ladders

| Policy | Factors (effect) | Count p/m | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- |
| P1 | allowed_source (method), cost_share_percentage (param), other_insurer_payment (param), payment_method (method) | 2/2 | other_insurer_payment (OHI on file AND line/earlier posting) | all four: select |
| P2 | same four, joining-line versions | 2/2 | joining_line_other_insurer_payment | select |
| P3 | allowed_source (m), cost_share_percentage (p), other_insurer_payment (p), payment_method (m), first_level_outcome_carry (m) | 2/3 | other_insurer_payment (EOB in case AND line/corrected posting); outcome_carry (decided partially AND corrected posting) | select |
| P4 | claimed_rate_source (p), other_insurer_payment (p), cost_share_percentage (p), cost_share_basis (m), payment_method (m) | 3/2 | claimed_rate_source (expired IMH auth at same facility AND within 12 months) | select (+referral read) |
| P5 | joining versions of P4's five | 3/2 | join_claimed_rate_source | select (+referral) |
| P6 | daily_allowed_source (p), days_still_covered (m), daily_other_insurer_payment (p), cost_share_basis (m), payment_method (m), cost_share_percentage (p) | 3/3 | daily_allowed_source | select; days_still_covered: referral |
| P7 | daily_allowed_source (p), days_at_issue (m), daily_other_insurer_payment (p), cost_share_basis (m), payment_method (m), cost_share_percentage (p) | 3/3 | daily_allowed_source | select; days_at_issue: referral |

Counts are within 4–6 with ≥2 parameter and ≥1 method per computation; every ladder states three tiers, all stated in the rule and implemented in compute; bindings disjoint; `decides` never `result`; fall-through tier = factor `baseline` and = `baseline.rule` input on every factor (checked tier by tier). Labels honest (method factors change the algorithm: average/latest/billed, net-of-OHI vs gross, carry less corrected payment vs nothing vs whole, which ledger quantities are subtracted; parameter factors pick a rate/percentage/amount).

Ladder-reality findings (charter-global):

- **G-7 (all seven payment-method ladders).** Tier 2's compound condition includes "the tier the line was billed under makes TRICARE pay second to other health insurance" (P1–P3) / "the tier makes TRICARE pay second to other health insurance" (P4–P7). `blueprint/products/select.yaml` sets `tricare_secondary_to_ohi: true` in all six Select variants (lines 151, 212, 273, 334, 395, 456). That part of the condition holds of every customer who reaches any of these writes (every line is a Select line), so it restates the scope rather than dividing customers; the tier is in fact decided by the counted OHI payment alone.
- **G-8 (inpatient cost-share-percentage ladders of P4–P7).** Tier 2 "the facility is recorded as network and the tier's network inpatient basis is a percentage of the allowed amount" (compute `… == 'percent_of_allowed'`). `select.yaml` parameter_schema line 74: `inpatient_network_basis: string - per_diem_with_minimum, lesser_of_per_diem_or_pct or per_admission_copay`; the six variants carry per_diem_with_minimum (ADFM A ×2), per_admission_copay (ADFM B ×2, Retiree B), lesser_of_per_diem_or_pct (Retiree A). No Select tier can ever reach tier 2; the ladder has two reachable tiers. Further, for a Retiree Group A network stay the ladder's fall-through gives 0 percent, and the basis ladder's lesser-of tier then yields `min(250.00 × days, 0 × base / 100) = 0.00` cost share, while `select_inpatient_cost_shares` charges "the lesser of the daily charge times inpatient_days and the stated percent of the facility allowed amount" with `inpatient_network_pct_of_allowed: 20` — a treatment the business does not give.
- **G-9 (fall-throughs that no Select tier would publish).** P4–P7 cost-share-basis fall-through "the daily inpatient charge for each covered day, never less than the minimum inpatient charge" is what a per_admission_copay tier reaches; for ADFM Group B and Retiree Group B network stays it gives 0.00 (`inpatient_network_daily_charge: 0.00`, `inpatient_network_minimum_charge: 0.00`) where the plan charges `inpatient_network_admission_copay` 76.00 / 201.00. P1–P3 cost-share-percentage fall-through "that tier's network outpatient percentage" gives 0 percent on the fixed-copayment tiers (`network_outpatient_cost_share_pct: 0`, `network_copay_specialty_care_visit: 30.00 / 56.00`).
- Observation O-8: P6/P7 daily-allowed tier 1 conditions the valuation of still-denied days on "every paid day line of the stay stands in a filed Allowable Charge Review" — a coupling of two separate disputes that exists to carry the E4/E6 edges; not demonstrable as unreal beyond judgment, recorded as an observation.

Whether each factor bears weight is per world: see `0.md` / `1.md` `factor_weight`.

### findings

- **G-1 SOURCE-POLICY RED — a state-form edge resolvable by two writes (E2, E4, E6).** Symptom: the waited-on state "the claim's highest-numbered posting denied for the same reason stands in a CFR that is filed or under review" (E2) and "the highest-numbered / last paid day line of the stay's claim stands in a filed Allowable Charge Review" (E4, E6) is brought about by either the first-case policy (P1 / P4) opened directly on that line or the joining policy (P2 / P5). Root cause: the first-case rules (P1, P4) accept any qualifying line; the joining rules (P2, P5) define their line as the claim's highest-numbered posting; nothing in the blocked rules singles out the joining write. Evidence: the four sentences quoted above; P1 rule "A Claim Factual Reconsideration opened on a TRICARE Select claim line that was denied because the claim reached the region after the claim filing deadline…"; P4 rule "An Allowable Charge Review opened on a paid TRICARE Select inpatient line records…". Consequence: task 0 — resolved by G-5's broader sentence (see `0.md`); task 1 — a second write set with a different scored value (see `1.md`). Affects tasks 0 and 1.
- **G-2 SOURCE-POLICY RED — P6/P7 tier 1 of the daily allowed amount is unreachable in compute.** Symptom/evidence above (`sl_reviews_filed`, `ex_reviews_filed`). Consequence demonstrated in `1.md` (compute returns the tier-2 value with or without the Allowable Charge Reviews). Affects task 1 (E4, E6, the root and the second-level amount).
- **G-3 SOURCE-POLICY RED — P6/P7 fall-through tier not computable.** Rule: "where the stay has no paid day line, it is the facility's billed amount per covered day on the stay"; compute: `RND(sl_stay_billed / sl_stay_days, 2)` with both sums over `line_outcome='paid'` rows. On any world with no paid line of the stay, the rule gives a definite number and the compute raises ZeroDivisionError. No task world sits on this tier; no task consequence.
- **G-4 SOURCE-POLICY RED — E4/E6 `condition` strengthened beyond the sentence.** Evidence above. Consequence demonstrated in `1.md` (the one-review world satisfies the sentence, fails the condition, and the two give different scored values).
- **G-5 SOURCE-POLICY RED — second wording of E2 in P3's rule.** "The next level hears a claim only once every posting of it denied for the same reason is under review at some level…" vs the declared "…fixed only after the claim's highest-numbered posting denied for the same reason stands in a Claim Factual Reconsideration that is filed or under review." In the same situation (only the highest-numbered denied posting placed in a CFR, an earlier re-billed denied posting left out) the declared sentence is met and the other is not. Demonstrated on task 0's world in `0.md`.
- **G-6 SOURCE-POLICY RED — undeclared override of base "Amounts a nonparticipating provider bills above the allowed amount are never in dispute."** Evidence above. Task 1's facility is `non_network_nonparticipating`; consequence on its baselines shown in `1.md`. Task 0's provider is participating; no consequence there.
- **G-7 SOURCE-FACTOR RED — payment-method tier 2 conditioned on a fact true of every Select tier.** Affects every computation of tasks 0 and 1 (per-task note in each file).
- **G-8 SOURCE-FACTOR RED — inpatient cost-share-percentage ladder has an unreachable tier and a zero-cost-share outcome for Retiree A network stays.** Affects task 1's four computations structurally (ladder of two reachable tiers).
- **G-9 SOURCE-FACTOR RED — fall-through outcomes no Select tier publishes (zero cost share for fixed-copayment / per-admission-copay network care).** Charter-level; neither task world sits on those tiers (both worlds are non-network).
- Observations O-1 … O-8 as referenced above: O-1 holding-scoped selection in P2/P5 (equal only with one record); O-2 P2 compute `status='filed'` vs sentence "filed or under review"; O-3 XMAX not restricted to earlier postings; O-4 P4–P7 CPARAM/CFIELD read the active enrollment not the line's; O-5 E2 `gate` is a column, not an eligibility gate; O-6 join docstrings describe the presumed open case; O-7 P7 treats the urgent request as the certification; O-8 ACR coupling in P6/P7 tier 1.

## post_reveal_revision

Appended after both tasks' derivations were frozen and revealed (reveal 2026-10-11T13:17:42Z). The charter-global section above is left as written.

- **G-2 reclassified from SOURCE-POLICY RED to observation.** The gold evaluates P2, P5, P6 and P7 with `target_holding_id` = the customer id (task 0 computations[1]; task 1 computations[1..3]). That id is not an `appeal_cases` holding; `check_compute.build_env` then falls back to "search all tables for the id", takes `customers` as the holding table and scopes every in-category `SUM/COUNT/MAX/LATEST` to `customer_id`. Under that evaluation `sl_reviews_filed` / `ex_reviews_filed` count the patient's filed reviews and the compute equals the rule (task 1: 5391.36 / 3594.24; `/tmp/erl55_audit_appeal/post.py`). The residual defect is that the compute's meaning depends on an id outside the DSL contract ("HID the primary id of the holding in this category"); with a case id it cannot reach tier 1. No scored value moves, so it is recorded as an observation. O-1 (P2/P5 patient-wide selection) is resolved the same way on both worlds.
- G-1, G-3, G-4, G-5, G-6, G-7, G-8, G-9 stand as written. G-1's "exactly one write" claim is asserted in both tasks' design_rationale and is false against the declared sentences (see `0.md`, `1.md` § source_gt_comparison).

## closing_checklist

Not closed: the difficulty does not pass the source-layer audit.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; first revision. Comparison verdicts: task 0 SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 SOURCE-POLICY RED + SOURCE-FACTOR RED + SOURCE-TASK RED. Not every comparison carries a PASS.
- Coverage and scope: `charter_scope` task 0 = P1, P2, P3 with their three tools; task 1 = P4, P5, P6, P7 with their four tools. Pairwise disjoint, jointly cover all seven extended policies and seven task tools. uuid8s independent (§ action_binding_and_uuids). PASS.
- Trees: task 0 two prerequisite problems, 1 value_input edge, three user writes, acyclic; task 1 three prerequisite problems, 4 value_input edges, three user writes, acyclic; the difficulty-wide graph is two disjoint DAGs. PASS on shape; task 1's declared tree is not the only one the policy admits (task 1 finding 1).
- Factors: declared counts within 4–6 with ≥2 parameter / ≥1 method everywhere; every factor bears weight on its world and every all-baseline fall-back differs from gold (equal to `factor_sensitivity` / `baseline_result` figure for figure). Fails ladder reality (G-7 all seven computations, G-8 the four inpatient computations, G-9 charter-level); counting surviving factors, P1, P2, P4, P5 fall to 3.
- Gate re-run on the final form: not applicable — the artifacts were not changed by this audit and the difficulty does not close; the coordinator's snapshot (all gates green, traceability deferred) is the one on record.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2, same auditor. Written 2026-10-11 ≈20:33Z (hashed 20:34:16Z), before either reworked task JSON was opened.
- Inputs: `appeal.extended.yaml` sha256 `f5dc41afc5e1511c5287fecebd1914921c806f7ef166824185e1f45812f70421` (**changed** from `9c352b2d…`), `task_tools.py` `bf67ea1f…` (unchanged), views `6ddde110…` / `3b69bc87…` (unchanged). Hashes re-verified locally. Coordinator gate snapshot after rework: all gates green, traceability deferred.
- Because the charter changed, every charter-global section is re-derived below in full; the tool-module conclusions (§ action_binding_and_uuids) carry forward on the unchanged `task_tools.py` hash.
- Base copy: `diff <(sed -n 1,856p appeal.extended.yaml) blueprint/products/appeal.yaml` empty — verbatim.
- Recomputation: `/tmp/erl55_audit_appeal/dump2.py` (policy dump), `chk.py` (prerequisite sentence / baseline / token checks), `r2.py` (compute on both views with the auditor's own derived writes).

### policy_conflict_scan (revision 2)

Subjects, triggers, tools, terminal states and read boundaries as in revision 1. The P1/P2 and P4/P5 overlaps are now separated by the rules themselves: P1 "Such a case is opened on the claim's lowest-numbered posting still standing with that denial, that is, a posting not reversed; the claim's further postings still standing with the same denial join it rather than opening cases of their own."; P4 "A review is opened on the lowest-numbered paid line of the claim whose daily rate is disputed; the claim's further paid lines with the same dispute join it rather than opening reviews of their own." No overlapping subject is left to two policies.

### rule_compute_equivalence (revision 2)

All seven policies re-swept rule ↔ compute, tier by tier:
- P1–P3: allowed-amount fall-through now `RND(billed * 100 / (100 + nonparticipating_balance_billing_limit_pct), 2)` for `non_network_nonparticipating` = "divided for a nonparticipating provider by one plus the tier's nonparticipating balance-billing limit"; fixed-copayment cost share `MN(class copay, base)` = "that tier's network copayment for its service class, never more than the amount the cost share is figured on"; OHI tier 2 XMAX over all postings of that service date = "the largest payment shown on the claim's postings of that service date" (O-3 closed); P3 OHI tiers now also require OHI on file, as the rule says.
- P2: case lookup filed-then-under-review = "most recently filed among those still filed, or, where none is still filed, the one most recently filed among those under review" (O-2 closed).
- P4/P5: tier parameters read with `select_enrollment_id=<line's enrollment>` (O-4 closed); billed-rate tier divided for nonparticipating; cost-share basis ladder adds `per_admission_copay → inpatient_network_admission_copay`; percentage ladder = rule.
- P6/P7: "joined review" = `reviews_on_high_line >= 1 and reviews_on_claim >= 2` = "the highest-numbered paid day line … stands joined to an Allowable Charge Review opened on an earlier paid line"; fall-through and baseline = stay paid rate; tier 2 = `MX(paid_rate, billed_rate)`; the no-paid-line case is excluded by the rule ("a stay with no paid day line … is outside this rule") and the divisions are guarded with `MX(days, 1)` (G-3 closed).
- Remaining latent items: G-2/O-1 (in-category `COUNT/LATEST/MAX` on `appeal_cases` are holding-scoped; equal to the rule only when evaluated with the customer id as target, as in round 1) — observation, as the coordinator states. New observation N-2: under a fixed-copayment tier, a network line whose service class has no `network_copay_*` parameter (e.g. lab_and_xray, durable_medical_equipment) gets `class_copay = -1` in compute and falls to the percentage (0 on those tiers); the rule states no treatment for such a class. Neither world has such a line.
- Baseline sentences of every policy are in its rule; no tool id, policy id or snake_case token in any rule (`chk.py`).

### action_binding_and_uuids (revision 2)

Carried forward unchanged (`task_tools.py` hash unchanged; seven distinct `(target_tool, computes)` pairs re-checked against the new charter: unchanged).

### prerequisite_graph (revision 2)

Same six edges, same kinds and gates, acyclic; every `policy_source` verbatim and unique in its own rule (`chk.py`). Conditions now match their sentences:
- E2 condition "…on the highest line_number posting of the case's claim still standing with the case line's line_outcome, and another such record on an earlier posting of that claim" = sentence "…the claim's highest-numbered such posting stands joined to a Claim Factual Reconsideration opened on an earlier posting of the claim".
- E4 / E6 conditions "a filed Allowable Charge Review record on the highest line_number paid line … and another filed Allowable Charge Review record on an earlier paid line" = sentences "…stands joined to an Allowable Charge Review opened on an earlier paid line of that claim" (G-4 closed).
- O-5 (E2's `gate` is a column, P3 has no eligibility gate) remains an observation.

### prerequisite_sentences (revision 2)

- E1, E3, E5 unchanged and passing.
- E2 "Where a claim has more than one posting still standing with the same denial, the amount carried to the next level is fixed only after the claim's highest-numbered such posting stands joined to a Claim Factual Reconsideration opened on an earlier posting of the claim." — "only after", state form; the state "highest-numbered standing posting joined to a CFR opened on an earlier posting" is brought about only by P2 (P1 opens, it does not join, and is pinned to the lowest-numbered standing posting). The broader "every posting … under review at some level" sentence is gone from P3's rule; no second wording remains (G-1 for E2 and G-5 closed).
- E4 / E6 now say "stands joined to an Allowable Charge Review opened on an earlier paid line of that claim"; only P5 brings that about (P4 opens, pinned to the lowest-numbered paid line) (G-1 for E4/E6 closed).
- New observation N-1: P1 (and P4) say further standing postings / paid lines "join it", while P2 (and P5) define the joining line as the claim's highest-numbered posting / paid line, not restricted to standing postings in P2's compute. With three or more further postings (or a reversed posting numbered above the standing ones) the intermediate ones can never be the joining line. Neither world has that shape (task 0: standing postings 4 and 5; task 1: paid lines 1 and 2).

### override_declarations (revision 2)

Sentence sweep repeated. The base sentence "Amounts a nonparticipating provider bills above the allowed amount are never in dispute." is now honoured wherever a billed amount enters: P1–P3 billed fall-through divided by one plus the balance-billing limit "so that nothing such a provider may bill above the allowed amount comes into dispute"; P4/P5 billed-rate tier likewise; P6/P7 baseline and fall-through are the stay's paid (allowed) rate, and tier 2's billed rate is divided likewise (G-6 closed). Declared overwrites unchanged in substance; no new conflict found.

### factor_ladders (revision 2)

| Policy | Factors (effect) | p/m |
| --- | --- | --- |
| P1, P2 | allowed_source (m), cost_share_percentage (p), other_insurer_payment (p), payment_method (m) | 2/2 |
| P3 | the four above + first_level_outcome_carry (m) | 2/3 |
| P4, P5 | cost_share_percentage (p), cost_share_basis (m, 4 tiers), claimed_rate_source (p), other_insurer_payment (p), payment_method (m) | 3/2 |
| P6, P7 | cost_share_percentage (p), cost_share_basis (m, 4 tiers), daily_allowed_source (p), daily_other_insurer_payment (p), payment_method (m), days (m) | 3/3 |

- G-7 closed: payment-method tier 2 is now "a counted other-insurer payment is below the allowed amount" with no condition true of every tier.
- G-8 closed: inpatient percentage tier 2 is "network and the tier's network inpatient basis is the lesser of a daily charge and a percentage" — reached by Retiree Group A (`lesser_of_per_diem_or_pct`, 20 %); tier 1 now requires a non-network basis that takes a percentage (percent_of_allowed or lesser-of). Three reachable tiers, distinct values.
- G-9 closed: fixed-copayment network outpatient lines take the class copayment; per-admission-copay inpatient bases take `inpatient_network_admission_copay`.
- Every fall-through equals its factor `baseline` and the `baseline.rule` input; labels honest; ladders stated in the rule. Observation O-8 (P6/P7 daily-allowed tier conditioned on the joined review) stands, judgment only. Observation N-3: P6/P7 daily-allowed tier 2 ("the higher of the stay's paid daily rate and its billed daily amount …") coincides in value with the fall-through whenever the (divided) billed rate does not exceed the paid rate; a distinct rule, equal outcome only in that case; not on either world.

### findings (revision 2)

| Round-1 item | Status |
| --- | --- |
| G-1 two writes for E2/E4/E6 | closed |
| G-2 holding-scoped COUNT (observation since round-1 reveal) | open as observation |
| G-3 0/0 fall-through | closed |
| G-4 E4/E6 condition stronger than sentence | closed |
| G-5 second wording of E2 | closed |
| G-6 nonparticipating billed amount in dispute | closed |
| G-7 payment-method condition true of every tier | closed |
| G-8 unreachable inpatient percentage tier | closed |
| G-9 fall-through outcomes no tier publishes | closed |
| O-1 | open as observation (with G-2) |
| O-2, O-3, O-4 | closed |
| O-5, O-6, O-7, O-8 | unchanged observations |

New: observations N-1, N-2, N-3 (latent, no task consequence). No new red light at charter level.

### closing_checklist (revision 2)

Written after both tasks' revision-2 derivations were frozen (2026-10-11 ≈20:33Z) and revealed (20:34:25Z).

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; revision 1 text untouched, revision 2 appended. Every revision-2 comparison carries PASS on all four relationships (task 0 and task 1).
- Coverage and scope: `charter_scope` task 0 = P1–P3 + their three tools; task 1 = P4–P7 + their four tools; pairwise disjoint, jointly complete over the seven extended policies and seven task tools; uuid8s independent and frozen (tool module unchanged). PASS.
- Trees: task 0 — two prerequisite problems, one value_input edge, three user writes, acyclic; task 1 — three prerequisite problems, four value_input edges, three user writes, acyclic; the difficulty-wide graph is two disjoint DAGs; every state-form edge now has exactly one resolving write. PASS.
- Factors: every computation 4–6 factors (P1/P2 4, P3 5, P4/P5 5, P6/P7 6) with ≥2 parameter and ≥1 method; per task ≥1 multi-source and ≥1 cross-difficulty (select; referral in task 1); every ladder ≥3 reachable, distinct tiers stated in the rule; every factor bears weight on its world against an honest baseline; every all-baseline fall-back definite and ≠ gold (242.25 / 344.34 / 242.25; 6979.84 / 2935.04 / 18368.00 / 26240.00). PASS.
- Gates on the final form: coordinator re-run after rework — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; check_traceability deferred until the KB is rendered (cited, not re-run by this auditor).
- Open observations carried (not grounds for rework): G-2/O-1 (holding-scoped in-category aggregates rely on the customer-id target), O-5, O-6, O-7, O-8, N-1, N-2, N-3.

The difficulty passes the source-layer audit in revision 2.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3, same auditor, written 2026-10-11 ≈23:10Z before either round-3 task JSON was opened.
- Shared inputs re-hashed locally: `appeal.extended.yaml` `f5dc41afc5e1511c5287fecebd1914921c806f7ef166824185e1f45812f70421` and `task_tools.py` `bf67ea1fb137460fd046bd81007128cc5a7f46a6874948f63efeb820d9385dbb` — both identical to revision 2. On those grounds every charter-global section of revision 2 (§ policy_conflict_scan … § findings (revision 2)) is carried forward by reference without re-derivation; its conclusions (all round-1 items closed, G-2/O-1, O-5…O-8, N-1…N-3 open as observations) stand.
- Views `6ddde110…` / `3b69bc87…` unchanged. Coordinator snapshot after round 3: all gates green including TRACEABILITY OK.

### closing_checklist (revision 3)

- Files correspond one-to-one with the two tasks; revisions 1 and 2 untouched; revision 3 appended in all three files; both revision-3 comparisons PASS on all four relationships.
- Charter, tool module, views, every write, every scored value, every closure and factor figure identical to revision 2 (hash and value checks in `0.md` / `1.md`); the only change is the position of `find_providers` among stateless reads and the proof text that refers to positions, all of which was verified true against the world and the charter.
- Scope, trees, factor and uuid conclusions of `closing_checklist (revision 2)` carry forward unchanged.
- Gates on the final form (coordinator re-run after round 3): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, TRACEABILITY OK; CACHE-DIFF INFO.
- Open observations (not grounds for rework): G-2/O-1, O-5, O-6, O-7, O-8, N-1, N-2, N-3.

The difficulty passes the source-layer audit in revision 3.
