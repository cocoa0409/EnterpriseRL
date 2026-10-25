# Policy-task audit — dental_ppo_member_services / charter-global

## revision_1

## charter_global_frozen

- Auditor: independent policy auditor (erl-task-policy-audit), round 1. Written 2026-10-18T04:3xZ, **before any task's GT was revealed**; nothing in this section derives from a revealed GT.
- Freeze hashes (re-computed by the auditor, equal to the brief):
  - `tasks/dental_ppo_member_services/dental.extended.yaml` sha256 `d20b3a1daafa2da52de63b6584079d1036a76b101b08b2aae0fbd53632dea04d`
  - `tasks/dental_ppo_member_services/task_tools.py` sha256 `9fcd203e0bda207f3efc8ae26e71f56ae2f99a28ba6fd082c221e4a21892cdc8`
  - masked views `.audit_views/policy/dental_ppo_member_services/r1/task_0.json` sha256 `aae13b79…f044`, `task_1.json` sha256 `3ce8fbf0…7534`
- Read: blueprint.yaml, db_schema.json, products/dental.yaml (+ billing.yaml, dhmo.yaml, group.yaml for cross-product seed realism), the extended charter, task_tools.py, the two masked views, `audits/render_source/XF_recipe.md`, `/tmp/erl0070_coord/audit_notes.txt`, the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/LATEST/CFIELD semantics only).
- Masked / unread before freeze: raw `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), `tasks/dental_ppo_member_services/worklog.md`, the scenario worklog, sibling difficulties' audits and tasks.
- Entry conditions: gate snapshot supplied in the brief (check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0); masked views with hashes supplied. Entry complete.
- Base copy: the extended file minus `extended_policies` is identical (YAML-equal) to `blueprint/products/dental.yaml` (diff empty).

### policy_conflict_scan

Six extended policies, two tasks (claimed scope inferred from the policy graph; to be confirmed against `charter_scope` after reveal):

| policy | target_tool (owner) | event written | computes | prerequisite |
| --- | --- | --- | --- | --- |
| dental_ext_upgrade_wait_reprocess | reprocess_upgrade_line_4b0d7156 (agent) | dental_claim_line_adjusted | plan_paid | [] |
| dental_ext_claim_appeal_dispute | file_claim_appeal_86dbcb40 (user) | dental_appeal_filed | amount_in_dispute | ← upgrade (value_input, d_paid) |
| dental_ext_grace_denial_reprocess | reprocess_grace_denial_3809eac7 (agent) | dental_claim_line_adjusted | member_responsibility | [] |
| dental_ext_pended_line_release | release_pended_line_088a5391 (agent) | dental_claim_line_paid | member_responsibility | ← grace (value_input, ded_net) |
| dental_ext_overturned_reprocess | reprocess_overturned_line_be461510 (agent) | dental_claim_line_adjusted | member_responsibility | [] |
| dental_ext_estimate_request | submit_estimate_request_d87add4f (user) | dental_estimate_issued | estimated_member_cost | ← overturned (value_input, ded_net); ← pended (state_gate) |

- Scopes: task 0 = {claim_appeal, upgrade}; task 1 = {estimate, overturned, pended, grace}. Pairwise disjoint, jointly cover all six extended policies. The graph is acyclic.
- Overlapping subject `dental_claim_line_adjusted` (upgrade / grace / overturned) is separated by the selected record (latest *paid* line / latest *DENIED_NOT_ELIGIBLE* line / appealed line of latest *overturned* decision) — no line is selected by two of them. OK.
- Trigger rule (XF#14): the tools write `dental_claim_line_adjusted` (base triggers: dental_max_reversal, dental_max_posting, dental_deductible_reversal, dental_deductible_posting — all dental), `dental_claim_line_paid` (dental_max_posting, dental_deductible_posting, dental_rollover_draw — all dental), `dental_appeal_filed` (none), `dental_estimate_issued` (none). No write lands in another category. **PASS.** (The claimed event types `dental_terminate_voluntary` / `dental_free_look_cancel`, whose base triggers book ortho/billing rows, are written by no tool.)
- Cross-category read boundary: all six read only `dhmo` holdings (CFIELD on terminated DHMO enrollment dates). Observation O1: `dhmo` is a category no difficulty of this blueprint claims (difficulties: dental, ortho, vision, billing, provider), so every `cross_difficulty: dhmo` is cross-*category*, not cross-*difficulty*; the gates accept it as the cross-difficulty read. Recorded, not a RED.
- Conflicts between the extended policies and in-force base clauses are listed under `override_declarations` (C4–C8).

### rule_compute_equivalence

- Mechanical sweep (scratch `/tmp/audit_dental_ppo_member_services_0070`): every `compute_basis` quote is verbatim (whitespace-normalised) in its policy's `rule`; every compute binding has a basis and no basis key lacks a binding; every sentence of every `baseline.rule` is a sentence of the `rule`; every prerequisite `policy_source` is verbatim in its own rule. **PASS (XF#9).**
- Combination order (XF#3) is stated once per policy ("The adjustments below are applied to the standard amount in this order: …") and matches the nesting in `result` for all six (deduction → MX(0) → ceiling → annual-max ceiling; estimate: waiting test → replacements → max ceiling → cost). PASS.
- Factor independence (XF#1/#16), closed transitively: no factor binding reads another factor's binding; no plain binding reads a factor-owned binding; only `result` assembles. PASS.
- Rounding: every rule says "rounded to the cent with a half cent rounded up"; `RND` in the evaluator is Python `round(float, 2)` (round-half-even on exact halves). No half-cent value arises in either task world. Observation O2 (engine-wide, no task effect).
- Edge/absent cases (XF#6): ties on the selecting LATEST are stated ("this rule/figure is not used"); absent records are stated for the estimate ("a person with no such decision is estimated under the base rules"); for the DHMO credit see C9 (first-match on a second record; month-end convention of the credit count).
- Rule-vs-compute mismatches found: none outside C9. The base-vs-extended departures are under `override_declarations`.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are six distinct pairs, each claimed by exactly one policy. PASS.
- uuid8 tails `4b0d7156`, `86dbcb40`, `088a5391`, `3809eac7`, `be461510`, `d87add4f`: distinct, no shared prefix/suffix, no sequence pattern. PASS.
- Tool bodies (task_tools.py lines 10–331): no tool checks eligibility, prerequisites or amounts; each books exactly the caller's values. PASS.
- Docstrings: no example values, no other tool named, no gold figure. Observation O3: every docstring closes with "Afterwards the … shows …" (a post-condition, not a position in a sequence); recorded only.
- Observation O4: `release_pended_line_088a5391` always posts the whole plan payment to the annual maximum and never books `dental_rollover_draw`/ped-OOP rows even for `PAID_ROLLOVER` or pediatric lines, although the base `dental_claim_line_paid` triggers book the rollover draw; no task line is affected.

### prerequisite_graph

| edge | kind / gate | form | policy_source verbatim in own rule | resolved_by = depended-on target_tool | gate exists |
| --- | --- | --- | --- | --- | --- |
| claim_appeal ← upgrade | value_input / d_paid | state | yes | yes | `d_paid` binding exists |
| estimate ← overturned | value_input / ded_net | state | yes | yes | `ded_net` exists |
| estimate ← pended | state_gate / dental_claim_lines.event_type | state | yes | yes | prose-only gate (no compute or eligibility entry reads pended rows) |
| pended ← grace | value_input / ded_net | state | yes | yes | `ded_net` exists |

- Every policy fills `prerequisite`; every `problem` is an extended policy of this file, none self-referencing; acyclic; no action-form edge, so no `fallback_reason` is required. No authoring-viewpoint wording.
- Observation O5: two `condition`s add an effect clause the sentence does not carry — estimate←overturned "…which has posted its deductible", pended←grace "the corrected decision has posted its deductible". The sentence's state ("no longer stands denied …") holds even if the corrected decision took 0.00 deductible; the extra clause is the edge's `effect`, not its gate. No task consequence (both corrected decisions post 45.00).

### prerequisite_sentences

1. claim_appeal ← upgrade — "The amount in dispute on a claim appeal is fixed only after the decision under appeal no longer stands paid at a prior plan's coinsurance for a service whose new waiting period the person's earlier Cascade DHMO coverage has already served." Ordering connective "only after"; state = the decision's recorded coinsurance vs the prior plan's rate; no tool/id/snake_case; strength matches the condition. Exactly one write of this difficulty changes the decision that stands on a *paid* line at a prior plan's rate: the upgrade reprocessing (grace needs a DENIED_NOT_ELIGIBLE line, overturned an overturned appeal, release a pended line). The upgrade rule does not restate the sentence. Single reading. PASS.
2. estimate ← overturned — "An estimate's figures are worked out only after no claim line of the person stands denied for a waiting period that an overturned appeal decision has since reversed." Unique resolving write: the overturned-decision reprocessing. PASS on form.
3. estimate ← pended — "An estimate is not issued until no claim line on any enrollment funded by the same billing account stands pended for premium." Unique resolving write: the pended-line release. Form PASS; **realism and self-consistency fail — C10.**
4. pended ← grace — "A released line's payment is not fixed until no line of the same person with a date of service in the first month of the cured grace period stands denied as not eligible." Unique resolving write: the grace-month reprocessing. The order agrees with base `dental_agg_family_deductible` (same-day lines absorb deductible by claim_number, and the first-grace-month line precedes). PASS.
- No rule states a cross-problem order beyond these four sentences (the sibling-rule names in the scoped overwrite sentences are scope exclusions, XF#8, not orders). No base sentence grounds an edge.

### override_declarations

Each policy declares one or two overwrites: the base credit sentence of `dental_evt_waiting_periods` (all six) and the allowance sentence of `dental_evt_claim_adjudication` (all but the claim appeal). Each `replaced_by` names its own scope and every sibling that overwrites the same clause (XF#8 sibling-exclusion: PASS). Sentence-by-sentence sweep of the remaining in-force base sentences against each policy's rule finds these **undeclared** departures (findings, not yet consequences):

- **C4 — upgrade waiting clause** (`dental_evt_waiting_periods`: "After an upgrade (tier_change_effective_date set and the new plan richer for the service), a service … is paid at the new plan's level only once its new waiting period counted from tier_change_effective_date … has passed; before then it is paid at the prior plan's level if the prior plan covered it … and denied DENIED_WAITING_PERIOD if the prior plan did not cover it.") is contradicted by overturned, pended, grace and estimate, which all test "the waiting period … counted in whole calendar months from the coverage effective date" at the current plan's percentage and never read `tier_change_effective_date`/`prior_variant_name`. Example on Corinne's world shape (group late entrant, coverage 2025-03-01, Value 1000 → Classic 1250 on 2026-01-01, no credit): crown D2750 on 2026-03-05 — base: 2 months from the tier change < 12 → denied (prior plan did not cover major); overturned rule: MONTHS(2025-03-01, 2026-03-05)=12 ≥ 12 → payable at 40 %. Two answers. Neither task world has an upgraded enrollment on these four policies (task 1 enrollments `prior_variant_name: none`).
- **C5 — pediatric EHB** (`dental_evt_pediatric_ehb`: "no annual maximum applies to that person's lines …; once the applicable out-of-pocket maximum is reached … member_responsibility 0.00") is contradicted by overturned, pended, grace and estimate for an individual_exchange enrollee under 19 (all cap at "the plan's annual maximum less the person's maximum postings" and compute the patient share with no OOP cap). Grace/pended are scoped to individual_exchange enrollments, so the case is squarely in scope. The upgrade rule alone excludes pediatric persons. No task effect (Theo is 20, Renata 45).
- **C6 — preventive out-of-network coinsurance** (`dental_evt_claim_adjudication`: "the oon percentages for out_of_network") is dropped by every network ladder: the fall-through "any other line … the plan's in-network percentage for its service class" gives an out-of-network preventive line `coinsurance_preventive_in_network` (100) where base gives `coinsurance_preventive_oon` (90 on Value 1000 and Classic 1250). In scope for pended and grace (any line); out of scope for upgrade/overturned/estimate (preventive never waits; estimate is fillings). For the claim appeal the requested rate is not a base quantity — observation. No task effect (all task lines are basic).
- **C7 — timely filing** (`dental_evt_timely_filing`: a late line "is denied DENIED_TIMELY_FILING; for an in-network line the practice … bears the denied amount and member_responsibility is 0.00") vs grace/pended, which compute and post a normal plan payment for an in-network line received after the in-network limit while setting the patient share to 0.00. A grace-month line denied DENIED_NOT_ELIGIBLE at step (1) was never tested at step (2), so the case is reachable. Base: plan_paid 0.00; extended: normal benefit. No task effect (task 1 lines are out-of-network and timely).
- **C8 — rollover** (`dental_evt_rollover`: "the part of a line's normal benefit above the remaining annual maximum is paid from the rollover balance") vs overturned (any plan) and estimate (individual market, which admits Premier 2000), both capped at "the plan's annual maximum less the person's maximum postings". For a Premier/Elite person with an exhausted maximum and a rollover balance, base pays from rollover, extended pays 0.00 above the maximum. No task effect (Value 1000).
- Base-minus-branch baselines (observation O6): several baseline sentences depart from in-force base on their own ("figured on the line's allowed amount", "in-network percentage", deductible / maximum room without backing out the replaced decision, estimate deductible = full individual deductible), but in every case a factor tier restores the base reading in the merged rule, so the merged semantics are unique. Recorded, not RED.

### factor_ladders

Per policy (effect; tiers; multi-source; cross_difficulty). Method-shape all-pairs tables follow (XF#4/#15).

- **claim_appeal** (4): requested_allowance_basis (parameter; 3 tiers), requested_network_rate (parameter; 3), requested_other_carrier (method; 3), appeal_dhmo_credit (parameter; 3; multi-source — plan credit method ∧ DHMO row ∧ enrollment effective date; cross dhmo). 3 parameter / 1 method / 1 multi-source / 1 cross. Structure PASS.
- **upgrade** (6): dhmo_wait_credit (parameter; multi-source; cross dhmo), oon_upgrade_rate (parameter), alternate_or_billed_allowance (parameter), deductible_after_backout (method — **fails C1/C3**), maximum_room_after_backout (method — **fails C1/C3**), secondary_payer_adjustment (method). Survivors 4 (3 parameter, 1 method) — bound still met, but two declared ladders are unreal.
- **grace** (5): dhmo_months_credited (parameter; multi-source; cross), network_coinsurance (parameter), allowance_basis (parameter), other_carrier_adjustment (method), patient_share_basis (labelled method — **C2 mislabel**). Survivors 5 with 1 honest method.
- **pended** (6): as grace + deductible_satisfied_so_far (method — **fails C1**). Survivors 5 (patient_share as parameter), 1 honest method.
- **overturned** (5): dhmo_months_credited, network_coinsurance, allowance_basis, other_carrier_adjustment (method), patient_share_basis (**C2 mislabel + C3 dead tier**). Survivors 4, 1 method.
- **estimate** (4): dhmo_months_credited (parameter; multi-source; cross), network_coinsurance (parameter — **C3 dead tier**), estimate_allowance_basis (parameter), deductible_satisfied_so_far (method — **C1, C3**). Survivors 2 (both parameter), 0 method → **bound failure (C3)**.

Every tier's condition is a real dental-benefits criterion (prior-coverage credit, OON vs in-network coinsurance, posterior-composite / molar-crown alternate benefit, lesser-of billed or allowed, non-duplication vs standard COB, deductible satisfied, backout of the replaced decision's postings, timely filing, OON balance billing). Every tier is stated in the rule and implemented in compute. No straw-man fall-through (each fall-through is the base treatment for its own domain). Observation O7: on Plus 1500 and Elite 2500 the OON basic/major rates equal the in-network ones, so the network ladders are value-identical on those plans (both task worlds are on Classic/Value, where they differ).

Method-shape all-pairs (A = an accumulator aggregate of the same field; per XF#15 a different filter of the same sum is the same input):

| factor | pair | verdict |
| --- | --- | --- |
| requested_other_carrier / secondary_payer_adjustment / other_carrier_adjustment (×3) | non-dup `MX(0,NB−o)` vs standard `MN(NB, allowed−o)` | PASS (subtraction vs ceiling) |
| | non-dup vs none `NB` | PASS (adds input o) |
| | standard vs none | PASS (adds ceiling op) |
| deductible_after_backout | T2 `MX(0, D−(A_year−A_line))` vs T3 `MX(0, D−A_year)` | **FAIL** — same `D − windowed sum`, only the filter differs; on T3's domain A_line = 0 so T3 is T2 |
| | T1 `0` vs T2/T3 | PASS formally, but T1 is unreachable in scope (C3) |
| maximum_room_after_backout | T3 `M−A_year+A_line` vs T4 `M−A_year` | **FAIL** — same as above, A_line = 0 on T4's domain |
| | T2 (+rollover balance) vs T3/T4 | PASS (adds rollover input) |
| | T1 `allowed` vs others | PASS formally; T1 unreachable in scope (C3) |
| deductible_satisfied_so_far (estimate, pended) | T2 `MX(0, D−A_year)` vs T3 `D` (domain A_year = 0) | **FAIL** — T3 is T2 evaluated on its own zero input; "remaining deductible = deductible − satisfied" is one method |
| | T1 `0` vs T2/T3 | PASS formally; in the estimate's scope T1 is inert (only Preventive 750 has D=0, where fillings are not covered and every tier pays 0.00) |
| patient_share_basis (×3) | T1 `billed − pay` vs T3 `allowed − pay` | **FAIL as method** — same formula, a different number substituted (C2) |
| | T2 `0` vs T1/T3 | substitution of 0 for the base amount (parameter-like) |

### findings

- **C1 SOURCE-FACTOR RED — one method written as two tiers (XF#4/#15).** Members (exhaustive): upgrade.deductible_after_backout (T2≡T3), upgrade.maximum_room_after_backout (T3≡T4), estimate.deductible_satisfied_so_far (T2≡T3), pended.deductible_satisfied_so_far (T2≡T3). Evidence: the ladder texts quoted in each policy's `factors[].ladder` and the compute lines `ded_line`, `room_cap` (upgrade), `ded_line` (estimate, pended). Consequence: each ladder has fewer than three distinct outcomes, so none is a valid factor; the conditions "the replaced decision posted a deductible / to the maximum" and "the person's deductible postings are above zero" are not criteria a carrier weighs to pick a method — base itself always backs out the replaced decision's postings and always takes the remaining deductible. Bears on task 0 (upgrade) and task 1 (estimate, pended).
- **C2 SOURCE-FACTOR RED — mislabelled method.** patient_share_basis in overturned, pended and grace: tiers substitute the base amount (billed / 0.00 / allowed) into the one formula "base − plan payment". Bears on task 1 (all three computations).
- **C3 SOURCE-FACTOR RED — tiers unreachable within the policy's own scope (XF#12).** Members: estimate.network_coinsurance "major-class line from an out_of_network practice" (the estimate is scoped to amalgam/composite fillings, mapped to basic or not_covered on every plan — `service_class_map`); estimate.deductible_satisfied_so_far T1 (inert, see table); overturned.patient_share_basis "in-network line received later than timely_filing_days_in_network" (a DENIED_WAITING_PERIOD line passed step (2) timely filing in base `dental_evt_claim_adjudication`'s first-fail order); upgrade.deductible_after_backout T1 and upgrade.maximum_room_after_backout T1 (a preventive line has no waiting period and Preventive 750, the only zero-deductible plan, is rank 1 and cannot be upgraded *to*). Consequence for the estimate: after C1 and C3 only dhmo_months_credited and estimate_allowance_basis survive — 2 factors, 0 method (bound 4–6, ≥1 method). Bears on task 1; upgrade still keeps 4 valid factors (task 0 consequence is the unreal ladders, not the count).
- **C4–C8 SOURCE-POLICY RED (charter-global, no task effect)** — undeclared overrides listed above, each with its two answers.
- **C9 SOURCE-POLICY RED (XF#6/#7, charter-global, no task effect).** The DHMO credit in all six policies reads `CFIELD('dhmo', 'termination_date'|'coverage_effective_date', enrollee_name, enrollee_date_of_birth, status='terminated')`, which returns the first matching row (check_compute.py `CFIELD` → `hs[0]`), while the rule says "has a terminated Cascade DHMO enrollment whose termination date is no more than prior_coverage_max_gap_days … before the coverage effective date". Decoy: a second, older terminated DHMO enrollment of the same person listed first → compute takes its dates, gap > 63 → tier 2/3; the rule's existential reading → tier 1. Separately, "the whole calendar months from that DHMO enrollment's coverage effective date to its termination date" states no month-end convention: MONTHS('2023-01-01','2026-04-30') = 39 while the enrollment covered 40 calendar months; the waiting-period counts state their convention, this one does not. Both tasks' credits (33 and 39) exceed every wait, so no task value moves.
- **C10 SOURCE-CHAIN RED — the estimate's pended-line gate is not a real precondition and contradicts its own rule.** The gate sentence (prerequisite_sentences #3) blocks one person's estimate on any *other* enrollment's line still pended after the grace period was cured; its declared `effect` is "the family's accumulators no longer wait on a held line", yet the same rule says "only the person's own deductible postings are counted" and the cap reads only the person's maximum postings — no family accumulator enters the estimate. A pre-treatment estimate is not a claim; a carrier does not refuse a member's predetermination because a relative's claim line is waiting in a post-cure release backlog. Bears on task 1.
- Observations O1–O7 above.

## closing_checklist

Written after both reveals (post-reveal section; the charter-global section above is unchanged since its pre-reveal hash `889be444…d19e`).

- Per-task files `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; this is revision 1 (no older revision). Both comparison sections carry RED, not PASS.
- Coverage: the six extended policies are covered; scopes {upgrade, claim_appeal} and {grace, pended, overturned, estimate} are disjoint (confirmed against `charter_scope`); task tools and GT are closed; uuid8s independent. PASS.
- Problem trees: task 0 n=1 (1 value_input), task 1 n=3 (2 value_input); both roots are owner=user; the whole graph is acyclic. Structure PASS, but task 1's estimate←overturned edge rests on a seed the base trigger cannot produce (1.md T1-F1) and the estimate←pended gate is unreal (C10 / T1-F2).
- Factors: every declared factor moves its scored value on its task's world and every all-baseline differs from gold (figures identical to GT's `factor_sensitivity`), but C1 (four one-method ladders), C2 (three mislabelled methods), C3 (dead tiers; estimate left with 2 valid factors and no method) and the stamps T0-F2 / T1-F3 fail. FAIL.
- Unique solution: both blind derivations matched GT on every argument; task 0 keeps one undetermined argument (T0-F1) and false proof text (T0-F5). FAIL for task 0, PASS for task 1.
- Charter-global undeclared overrides C4–C8 and the DHMO first-match / month-count defect C9 have no effect on either task world but are defects of the charter that the KB will carry.
- Gates were not re-run (round-1 audit; the brief's snapshot is authoritative).
- The difficulty does **not** pass the source-layer audit.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10

## revision_2

## charter_global_frozen (revision 2)

- Re-audit round 2 under `/tmp/erl0070_coord/reaudit_gate.txt`. Step 1: `tail -n 2 tasks/dental_ppo_member_services/worklog.md` ends with `REWORK round 2: gates 7/7 green`; claims line `REWORK round 2 claims: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, T0-F1, T0-F2, T0-F3, T0-F4, T0-F5, T1-F1, T1-F2, T1-F3, T1-F4, T1-F5`.
- Step 2 snapshot (`/tmp/erl0070_coord/snapshot.sh dental_ppo_member_services 2`, 2026-10-18T09:47:18): check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0 OK. Masked views r2: `task_0.json` sha256 `e59cc2a9…5445`, `task_1.json` sha256 `5630f299…c02`. Sources: `dental.extended.yaml` sha256 `b68d2cb8fdb1529a78093a3a7cc866131c8ad0d69a5fb0493f79f8c492bd1afd`, `task_tools.py` sha256 `c3fa3d76fbab99255f6258bf607d8d6e1433ffc7fed1fc2a6b69e71ad7a5373a`.
- Both shared inputs changed since revision 1 → every charter-global section below is **re-derived in full**, not carried forward. Written before any round-2 GT reveal.
- Base copy still YAML-identical to `blueprint/products/dental.yaml`.

### policy_conflict_scan (r2)

The charter was redesigned: four of the six round-1 policies were replaced.

| policy | target_tool (owner) | event | computes | prerequisite |
| --- | --- | --- | --- | --- |
| dental_ext_initial_wait_reprocess (IW) | reprocess_wait_denial_e5c18a2f (agent) | dental_claim_line_adjusted | member_responsibility | [] |
| dental_ext_estimate_request (EST) | submit_estimate_request_d87add4f (user) | dental_estimate_issued | estimated_member_cost | ← IW (value_input, room) |
| dental_ext_upgrade_paid_reprocess (UP) | reprocess_upgrade_paid_line_3fd2b6c9 (agent) | dental_claim_line_adjusted | member_responsibility | [] |
| dental_ext_grace_denial_reprocess (GD) | reprocess_grace_denial_4c0e9d17 (agent) | dental_claim_line_adjusted | member_responsibility | ← UP (state_gate, coinsurance_pct) |
| dental_ext_upgrade_denial_reprocess (UD) | reprocess_upgrade_denial_9a74d03b (agent) | dental_claim_line_adjusted | member_responsibility | ← GD (value_input, ded_room) |
| dental_ext_claim_appeal_dispute (CA) | file_claim_appeal_86dbcb40 (user) | dental_appeal_filed | amount_in_dispute | ← UD (value_input, d_paid) |

- Inferred scopes (to confirm at reveal): task 0 = {EST, IW}; task 1 = {CA, UD, GD, UP}. Disjoint, jointly complete, acyclic.
- Overlap on `dental_claim_line_adjusted`: IW and UD both select "the latest DENIED_WAITING_PERIOD line" but are separated by the plan-change test (IW: never changed; UD: dated on/after a change to a plan covering a class the prior plan did not); UP selects paid lines, GD DENIED_NOT_ELIGIBLE lines. A waiting-period denial dated before a plan change on a changed enrollment is excluded by both and left to base. OK.
- Trigger rule (XF#14): tools write `dental_claim_line_adjusted` (base triggers: dental max/deductible postings and reversals) plus, through the tool bodies, `dental_rollover_draw`, `dental_ped_oop_posting/reversal` (dental accounts); `dental_appeal_filed` and `dental_estimate_issued` (no triggers). Nothing lands in another category. **PASS.**
- Cross-category reads: all six read `dhmo` holdings; IW and EST also read `dhmo_services` (XLATEST). O1 (dhmo is an unclaimed category) still applies.

### rule_compute_equivalence (r2)

- Mechanical sweep: every `compute_basis` quote verbatim in its rule; every binding has a basis; every baseline sentence is in the rule; every `policy_source` verbatim. PASS (XF#9).
- Order sentences match the nesting of `result` in all six (XF#3). Factor independence closed transitively; no plain binding reads a factor-owned binding (XF#1/#16). PASS.
- Rounding O2 (engine round-half-even) unchanged; no half-cent arises in either world.
- **New member of the XF#6/#7 class — D1:** the DHMO extraction reads are not scoped to the person. IW `ext_plan: XLATEST('dhmo','dhmo_services','dhmo_plan_id', procedure_category='extraction', tooth_or_area=t_tooth, date_of_service=t_ext)` and EST `e_ext` / `ext_plan: XLATEST('dhmo','dhmo_services', …, procedure_category='extraction', tooth_or_area=e_tooth)` filter only by tooth (and, for IW, date). XLATEST is customer-scoped (check_compute.py `_xrows`: rows carrying the customer_id or pointing at any of the customer's DHMO holdings), while both rules say "the person's Cascade DHMO services" / "a Cascade DHMO enrollment of the person". Decoy: a household member's later DHMO extraction of the same tooth number → EST takes that date and, through `ext_plan`, that member's DHMO enrollment dates for the clause credit; the rule's reading takes the person's own record. The waiting-credit reads were fixed (CFIELD with `termination_date=day_before`, unique per person; month count "+1, both months counted" stated) — C9's two members are closed.

### action_binding_and_uuids (r2)

- Six distinct `(target_tool, computes)` pairs; uuid8s `e5c18a2f`, `3fd2b6c9`, `4c0e9d17`, `9a74d03b`, `86dbcb40`, `d87add4f` distinct and unpatterned. PASS.
- Tool bodies validate nothing (the `_LineBook` helper only shapes values). PASS. No example values or gold figures in docstrings; no factor id is a substring of a tool name. O3 ("Afterwards …") unchanged.
- `file_claim_appeal_86dbcb40.dental_claim_line_id` now reads "for a second_level filing, the claim line the first-level filing names (shown on the appeal lookup), even where that line has since been reprocessed", matching CA's rule sentence — closes T0-F1's class.
- O4 closed: the reprocessing tools now book rollover draws (IW) and pediatric OOP postings by `accumulator_track`.

### prerequisite_graph (r2)

| edge | kind / gate | form | source verbatim | resolved_by ok | gate binding exists |
| --- | --- | --- | --- | --- | --- |
| EST ← IW | value_input / room | state | yes | yes | yes |
| CA ← UD | value_input / d_paid | state | yes | yes | yes |
| UD ← GD | value_input / ded_room | state | yes | yes | yes |
| GD ← UP | state_gate / dental_claim_lines.coinsurance_pct | state | yes | yes | prose-only gate |

Acyclic; every policy fills `prerequisite`; no action-form edge. O5-type effect clauses in conditions ("with that decision's postings booked", "with its deductible posted") recur — observation.

### prerequisite_sentences (r2)

1. EST ← IW: "An estimate's figures are worked out only after no claim line of the person stands denied for the waiting period counted from the coverage effective date that the person's earlier Cascade DHMO coverage has already served." Unique resolver IW. PASS on form.
2. CA ← UD: "…only after the decision under appeal no longer stands denied for the new waiting period that followed a plan change, where the person's earlier Cascade DHMO coverage has already served that waiting period." Unique resolver UD. PASS.
3. UD ← GD: "…only after no line of the same person with an earlier date of service stands denied as not eligible for a date on which the enrollment was in force while its funding billing account was in a premium grace period." Unique resolver GD. PASS.
4. GD ← UP: "A reprocessed grace-period line's patient share is fixed only after no line of the same person with an earlier date of service stands paid at a prior plan's coinsurance for a service whose new waiting period the person's earlier Cascade DHMO coverage has already served." **Fails — D2 (charter) / task 1.** The quantifier "no line … stands paid at a prior plan's coinsurance …" is broader than what UP can resolve: UP's own rule removes "a line with an appeal filed for it at any level (such a line is settled through the appeal)" and its selector takes only the single latest paid basic/major line of the change year. A prior-level line that was appealed therefore satisfies the sentence's description, can be resolved by no write of this difficulty, and keeps GD's gate shut for ever; the sentence is broader than the edge's `condition` and than its resolver. Its rationale ("decided on the person's history as it stands after them") also has no basis when the two lines fall in different benefit years (no deductible, maximum, frequency or waiting count of one reads the other); base `dental_agg_family_deductible` orders lines by adjudication date, not date of service.

### override_declarations (r2)

- Every policy now also overwrites the base patient-share sentence (all reprocessing rules and EST) and IW/EST the missing-tooth credit sentence; each `replaced_by` restates the in-force base content for out-of-scope cases and names every sibling (XF#8 PASS).
- Round-1 undeclared overrides re-checked sentence by sentence:
  - C4 (upgrade wait): IW and EST exclude changed enrollments; GD counts from the plan change date on/after a change and leaves prior-covered classes in the new wait to base; UD/UP/CA count from the change. **Closed.**
  - C6 (preventive OON): GD's ladder gains the preventive-OON tier; EST's fall-through is the OON percentage per class; IW/UD/UP/CA cannot select a preventive line (no waiting period / basic-major only / CA scope). **Closed.**
  - C7 (timely filing): GD denies a late line (plan 0.00) and starts the share at 0.00 for a late in-network line; the other reprocessing rules act only on lines that passed step (2). **Closed.**
  - C8 (rollover): IW and EST draw on the rollover balance; UP/GD/UD exclude rollover lines limited by the maximum; CA excludes rollover plans. **Closed.**
  - C5 (pediatric): every rule now applies "no annual maximum" and caps the in-network share at the one-child OOP maximum, and excludes subscribers with two or more exchange children. **Residual member — D3:** base `dental_evt_pediatric_ehb` says "the line that crosses the maximum pays the allowance minus the cost sharing still remaining" and later lines are "paid at the full allowance". The extended rules cap only the patient share; their plan payment stays "the allowance less the deductible taken, times the coinsurance" (EST: the estimated plan payment likewise). On a pediatric in-network line that crosses the maximum, `plan_paid` (a written, scored tool argument of IW/UP/GD/UD; `estimated_plan_payment` of EST) has two readings: the extended normal benefit vs base allowance − remaining cost share. No task effect (no pediatric person in either world).
- O6 (base-minus-branch baselines) persists in the remaining factors (in-network rate for OON lines, allowed amount for alternate-benefit lines, no COB); the merged rules restore base. Recorded only.

### factor_ladders (r2)

| policy | factors (effect, tiers) | survivors | multi-source / cross |
| --- | --- | --- | --- |
| IW | initial_dhmo_months (P,3), initial_clause_months (P,3), initial_coinsurance (P,3), initial_allowance (P,3), initial_maximum_limit (M,3), initial_share_adjustment (M,3) | 6 (4 P, 2 M) | dhmo_months, clause_months / dhmo |
| EST | estimate_dhmo_months (P,3), estimate_clause_months (P,3), estimate_coinsurance (P,4), estimate_benefit_limit (M,4) | 4 (3 P, 1 M) | both credits / dhmo |
| UP | priorlevel_dhmo_months (P,3), priorlevel_coinsurance (P,3), priorlevel_allowance (P,3), priorlevel_coordination (M,3), priorlevel_share_adjustment (M,3) | 5 | dhmo_months / dhmo |
| GD | gracefix_dhmo_months (P,3), gracefix_coinsurance (P,4), gracefix_allowance (P,3), gracefix_coordination (M,3), gracefix_share_start (P,3), gracefix_share_adjustment (M,3) | 6 | dhmo_months / dhmo |
| UD | newplan_dhmo_months, newplan_coinsurance, newplan_allowance (P,3 each), newplan_coordination (M,3), newplan_share_adjustment (M,3) | 5 | dhmo_months / dhmo |
| CA | appeal_requested_allowance (P,3), appeal_requested_coinsurance (P,3), appeal_requested_coordination (M,3), appeal_dhmo_months (P,3) | 4 | dhmo_months / dhmo |

Method-shape all-pairs:

| factor | pair | verdict |
| --- | --- | --- |
| *_coordination (UP, GD, UD, CA) | non-dup `MX(0,NB−P)` / standard `MN(NB, allowed−P)` / none | PASS (subtraction vs ceiling vs no input; "other coverage paid" is a real COB condition) |
| *_share_adjustment (IW, UP, GD, UD) | T1 `MN(OOP room, share−P)` vs T2 `share−P` | PASS (adds cap) |
| | T2 `share−P` vs T3 `share` | PASS (adds input; same COB-presence condition as the coordination factor — observation O8, the two factors read the same `cob_other_paid` field independently) |
| initial_maximum_limit | no max / room+rollover / room | PASS (cap removed; rollover input added) |
| estimate_benefit_limit | T1 ped (no max + OOP cost cap) vs T3 preventive-exempt (no max) | PASS formally (T1 adds the cost cap on in-network); on an out-of-network pediatric estimate T1 and T3 coincide — observation |
| | T2 room+rollover vs T4 room; T3 vs T4 | PASS |

- Round-1 C1 (one method as two tiers): the deductible/maximum backouts are now plain baseline sentences; no surviving ladder has the defect. **Closed.**
- C2 (mislabelled method): `gracefix_share_start` is labelled parameter; the other share-start variants were folded into the baseline. **Closed.**
- C3 (dead tiers): re-checked every tier against each rule's own scope (IW/UD basic-major waiting lines incl. exchange children and rollover plans; UP basic-major; GD any line incl. late in-network; EST any category incl. in-network preventive and pediatric; CA upgrades from Preventive 750/Value to Value/Classic/Plus, so both COB methods are reachable). No unreachable tier found. **Closed.**
- Realism of every surviving tier: prior-coverage credit, missing-tooth credit from where the tooth was lost, OON vs in-network coinsurance, alternate benefit / lesser of billed, non-dup vs standard COB, primary payment reducing the member's balance, pediatric EHB, rollover — all real carrier practice. PASS.

### findings (r2, charter-global)

- **D1 SOURCE-POLICY RED (XF#6/#7)** — person-unscoped DHMO extraction reads in IW and EST (above). No effect on task 0 (one DHMO enrollee).
- **D2 SOURCE-CHAIN RED** — GD's prerequisite sentence quantifies over lines UP can never resolve (appealed prior-level lines) and has no business basis across benefit years; bears on task 1 (demonstrated there).
- **D3 SOURCE-POLICY RED** — residual pediatric plan-payment override (C5 residual). No task effect.
- Round-1 C1, C2, C3, C4, C6, C7, C8, C9, C10 are closed (C10's gate is gone; D2 is a new instance of the same class, not a carry-over of the same sentence). C5 is closed except for D3.

## closing_checklist (revision 2)

Post-reveal; the revision-2 charter-global section above is unchanged since its pre-reveal hash `025f3f43…e013`.

- Round-1 RED closure: C1, C2, C3, C4, C6, C7, C8, C9, C10 closed; C5 closed except residual D3. Task items T0-F1…F5 and T1-F1…F5 closed (per-task files, revision_2).
- New defects: D1 (person-unscoped DHMO extraction reads, XF#7), D2 (GD←UP gate: unresolvable quantifier + no business basis; task 1 T1-G1/T1-G2), D3 (pediatric plan payment when the OOP maximum is crossed); task 0 T0-G1 (base implant-interval frequency declines the abutment estimate after the prerequisite write) and T0-G2 (false base-precondition proof text).
- Regressions: none of the round-1 classes reappears in its old form; D2 is a new member of the C10 class (unreal state gate).
- Coverage/scopes: disjoint, complete (confirmed against `charter_scope`); trees n=1 (task 0) and n=3 with 2 value_input (task 1); owner=user roots; acyclic; uuids independent. Factors: every declared factor bears weight on its handling-time world against an honest baseline, figure-for-figure equal to GT; ladders real; no dead tiers; method-shape tables pass.
- Both blind derivations matched GT on every scored argument.
- Gates: snapshot of round 2 (all OK) cited; not re-run beyond the snapshot script.
- The difficulty does **not** pass the source-layer audit.

VERDICT revision_2: task0=RED task1=RED charter=D1,D2,D3

## revision_3

## charter_global_frozen (revision 3)

- Gate step 1: worklog ends `REWORK round 3: gates 7/7 green`; claims `D1, D2, D3, T0-G1, T0-G2, T1-G1, T1-G2`.
- Gate step 2 (`snapshot.sh dental_ppo_member_services 3`, 2026-10-18T11:31:56): all seven gates rc=0 OK. Views r3: `task_0.json` `e59cc2a9…5445` (unchanged from r2), `task_1.json` `bb4ac4c6…754f`. Sources: extended `cfb8ce1c7abbc39495f5b07e1567c61e336599f948132f21d624367028e4398e`, task_tools `ff8127367901d52f73f9aef8ecae464a6dc41ba356bfc2cdbb5724602d00d243`.
- Both shared inputs changed → charter-global checks re-run in full (mechanical sweeps re-executed; prose re-read on every changed sentence; the claim-appeal policy is byte-identical to r2). Written before the round-3 GT reveal. Base copy still identical.

### changes found and their verdicts

- **D1 (person-unscoped DHMO extraction reads)** — IW and EST now resolve `dhmo_id` = the person's own terminated DHMO enrollment that ended the day before coverage (`CFIELD(..., enrollee_name, enrollee_date_of_birth, status='terminated', termination_date=day_before)`), read its dates by `dhmo_plan_id`, and filter `XLATEST(dhmo_services ...)` by `dhmo_plan_id=dhmo_id`; the rule says "the person's DHMO services are read only from that enrollment's own service records, never from another enrollment of the same subscriber". EST now takes the extraction date from the person's most recent claim line for the tooth. Rule == compute in every branch. **Closed.**
- **D2 (GD←UP gate)** — the sentence is now "…only after the person's most recently decided paid basic- or major-class line, when it is booked to this line's benefit year although its date of service falls in an earlier one and was paid at a prior plan's coinsurance for a service whose new waiting period the person's earlier Cascade DHMO coverage has already served, has been reprocessed." Singular and conditional, so it names exactly the line UP's selector takes (latest paid basic/major line; UP no longer restricts to the change year and books the correction to the calendar year of the date of service, tool gains a `benefit_year` argument and posts to it). The edge is now `value_input` on `ded_room`: a 2025-dated line wrongly booked to 2026 consumed 2026 deductible, and correcting it frees that deductible for the 2026 grace-period line — a real reason for the order (base takes deductible by benefit year). UD←GD likewise narrowed to "the person's most recently decided line denied as not eligible, when it is dated earlier than this line in the same benefit year …". **Closed**, subject to the per-task demonstration (task 1).
- **D3 (pediatric plan payment)** — every reprocessing rule and EST now state that for a pediatric in-network line the share is first limited to the OOP room, then reduced by any primary payment, "and the plan payment on such a line is the allowance less that limited share, so the line that crosses the pediatric out-of-pocket maximum pays the allowance minus the cost sharing still remaining and a later line pays the full allowance" (EST: estimated plan payment likewise) — base `dental_evt_pediatric_ehb` restated. Share order sentence updated ("its limit applied before its reduction and its zero floor last") and matches `result` (`MX(0, MN(share_cap, base − pay) − share_less)`). **Closed.**
- **T0-G1 class (frequency)** — EST declares a new overwrite of base `dental_evt_frequency_age_limits`' interval sentence (superseded clause verbatim; replaced_by scoped "For a requested estimate under this rule, and only for such a case, implant services of the same kind are those with the same procedure code on the same tooth position, so an implant body, its abutment and its implant-supported crown each run their own implant interval; every other case remains under the base rule: …" restating the full base sentence). Matches real carrier practice (D6010 / D6057 / D6065-type limits run per code). **Closed** for EST; IW's own exclusion ("a line that a frequency or age limit would deny") is unaffected (an implant body with no prior paid implant on the tooth).
- Prerequisite sentences now end "… has been reprocessed" (EST←IW, GD←UP, UD←GD) with `form: state`. "Reprocessed" is the record word (remark `ADJUSTED_REPROCESSED`, event `dental_claim_line_adjusted`) and each sentence names the record (the person's most recently decided line of a stated kind), so the state reading holds; observation O9 only.

### re-run of the standing checks

- compute_basis verbatim, binding/basis closure, baseline sentences in rule, policy_source verbatim, every overwrite's `superseded_clause` verbatim in its base rule: PASS (scratch sweep).
- Trigger rule: unchanged event set; UP's postings stay in dental accounts. PASS.
- uuid8s unchanged and distinct; no example values or gold figures in docstrings (UP's new `benefit_year` arg: "four-digit year (YYYY)"). PASS.
- Factor ladders: same ids, effects and tier counts as revision 2; changed tiers are the pediatric share-adjustment methods (cap-then-reduce, plan = allowance − capped share) and the DHMO credit conditions (now "the person has an earlier DHMO enrollment" as defined). Method-shape table of revision 2 still holds (the pediatric tier now adds a cap and a plan-payment replacement). No dead tier introduced (UP's selector widened to any year; EST frequency overwrite narrows a decline, no ladder affected). Factor independence and plain-binding rule: PASS.
- Overwrite hygiene: EST's new frequency overwrite names its own scope only (no sibling overwrites the interval sentence) and restates the base content. PASS.
- Sweep for undeclared base departures on the changed sentences (UP's booking-year rule vs base `dental_evt_accumulators` "Accumulators are moved … for the benefit_year of the line" and the event field "benefit_year: Benefit period counted"): booking the corrected decision to the DOS-year benefit period is what base requires; the tool backs out the wrong-year postings for their own year. No conflict.

### findings (revision 3, charter-global)

- None open. D1, D2, D3 closed; T0-G1's class closed in the charter. Observation O9 (perfect-passive state wording) recorded.

## closing_checklist (revision 3)

Post-reveal; the revision-3 charter-global section is unchanged since its pre-reveal hash `b72117ad…d038`.

- Round-2 REDs: D1, D2, D3, T0-G1, T0-G2, T1-G1, T1-G2 — all verified closed (per-task files revision_3). No new defect found in the exhaustive XF 1–17 re-sweep of the changed policies, tools and seed; no regression of any round-1 or round-2 class.
- Per-task files correspond one-to-one with tasks 0 and 1; both revision-3 comparisons PASS; older revisions untouched.
- Coverage: six extended policies, scopes {IW, EST} and {UP, GD, UD, CA} disjoint and complete (confirmed against `charter_scope`); tools and GT closed; uuid8s independent and frozen.
- Trees: task 0 n=1 (1 value_input), task 1 n=3 (3 value_input); owner=user roots; every edge unmet at the opening and load-bearing; whole-difficulty graph acyclic.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors (≥2 parameter, ≥1 method), ≥1 multi-source and ≥1 cross-category (dhmo) per task; ladders ≥3 distinct, real tiers stated in the rule; every factor bears weight against an honest baseline; each all-baseline figure differs from gold.
- Gates: round-3 snapshot (all seven OK) cited as the re-run on the final form.
- The difficulty passes the source-layer audit (observations O1–O9 remain recorded, none a RED).

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision 4)

- Gate step 1: worklog ends `REWORK round 4: gates 7/7 green`; claims `F1, F2, XF8, EST-TIES` (the renderer's pre-scan findings in `audits/render_source/dental_ppo_member_services/render_r1.md`, read as instructed).
- Gate step 2 (`snapshot.sh dental_ppo_member_services 4`, 2026-10-19T07:43:46): seven gates rc=0 OK. Views r4 `task_0.json` `e59cc2a9…5445`, `task_1.json` `bb4ac4c6…754f` — both identical to r3. Sources: extended `f298a853751a47e72092ca28e54dd3a9ae8bcf86f2365745ad11191d53969736` (changed), task_tools `ff812736…d243` (unchanged from r3 → tool-contract section carried forward on that hash).
- Extended changed → mechanical sweeps re-run on all six policies and every changed sentence, compute line and factor re-read; written before the round-4 reveal. Base copy identical.

### verification of the render-source findings (treated as round-3 items)

| item | what changed | verdict | should the policy audit have caught it? |
| --- | --- | --- | --- |
| **F1** (XF#2/#16, UP: baseline defined the pediatric OOP back-out that only `priorlevel_share_adjustment` uses, and the factor's own sentence omitted the back-out) | baseline sentence "The pediatric out-of-pocket postings a reprocessed prior-level line counts are …" removed from rule and `baseline.rule`; the factor sentence now reads "…net of reversals for the line's benefit year, after any pediatric out-of-pocket posting the replaced decision made to that benefit year is backed out…", ladder tier 1 says the same; `oop_used` moved into the factor's bindings; the booking-year sentence drops "pediatric out-of-pocket" from the counts it lists. Rule == compute (`oop_used` subtracts the replaced line's 2025-year posting). | **Closed** | **Yes — missed.** The baseline/factor split existed from revision 2 (baseline back-out sentence; ladder "net pediatric out-of-pocket postings" without it) and widened in r3; XF#2 ("the baseline never defines a quantity only a factor uses") and rule==compute on the factor sentence were not checked binding-by-binding against the baseline sentences. |
| **F2** (XF#6, CA: unstated same-day ties for the first-level decision and the decision under appeal) | new sentence "Where several upheld first-level decisions share that latest decided date, or several decisions on that claim number and line number share that latest decision date, this rule is not used and the appeal states no amount under it." | **Closed** (same pattern as the five siblings; task 1 has no tie: `89a16e94` alone on 2026-04-29, the claim line's decisions on distinct dates) | **Yes — missed.** CA's selector was rewritten in r2 and I did not re-run the tie sweep on it. |
| **XF8** (CA: deductible omitted the family limit of base `dental_agg_family_deductible`) | scope adds "on an account with no more than three enrolled persons"; new sentence "Because every Cascade plan's family deductible maximum is three times its individual deductible, on an account with no more than three enrolled persons the family limit never falls below the person's own remaining deductible, so the payment requested on a claim appeal counts only the person's own deductible postings." Verified against params (family max = 3 × individual on all six plans). | **Closed** (an undeclared-departure member; Corinne's account has one enrolled person, so no task value moves) | **Yes — missed.** The r1 sweep found this sentence in the other policies but the r2/r3 sweeps did not re-check CA's deductible after its redesign. |
| **EST-TIES** (EST: service-class and extraction-date reads without tie sentences) | both sentences now carry "where several … share that latest decision date this rule is not used". | **Closed** (no tie in task 0: the implant-category and tooth-19 latest decisions are single rows) | **Yes — missed** (minor). |
| Lower note: factor-only plain bindings (`oop_used`) | `oop_used` is now a binding of the share-adjustment / benefit-limit factor in IW, EST, GD, UD (and UP); EST's `ped` is a binding of `estimate_benefit_limit`; allowance factors now own `t_cat/t_cdt/t_tooth/t_alt` where only they read them. | **Closed** | Partly — this is binding placement, not a two-answers defect. |

### re-run of the standing checks (revision 4)

- compute_basis / baseline / prerequisite / superseded_clause verbatim; binding↔basis closure: PASS.
- Binding audit (mechanical, scratch): no factor binding appears in two factors; no plain binding reads a factor-owned binding; the only plain bindings read by a single factor are the baseline quantities that factors' fall-through tiers return (IW `room_std`, EST `room`, CA `d_used`) — these are standard-method quantities stated in each `baseline.rule`, not factor-only quantities. PASS.
- Tie sweep, every LATEST / XLATEST / CFIELD read in all six policies: each selecting read carries a stated tie sentence or reads by a unique id/date; DHMO reads are unique by `termination_date = day before`. PASS.
- Family-deductible sweep: all six policies now carry the ≤ 3-person sentence (IW, EST, UP, GD, UD, CA). PASS.
- Trigger rule, uuids, docstrings: unchanged tools (hash). PASS.
- Factor ladders: tiers, effects and counts unchanged from r3; method-shape table holds. PASS.

### findings (revision 4, charter-global)

- None open.

## closing_checklist (revision 4)

- Round-3 items (D1, D2, D3, T0-G1, T0-G2, T1-G1, T1-G2) remain closed on the r4 charter; render-source findings F1, F2, XF8, EST-TIES and the binding-placement note verified closed (table above). All four were members of XF classes the policy audit is bound to check (XF#2/#16, XF#6, XF#8) and should have been caught in revisions 2–3; the revision-4 sweeps above were run binding-by-binding, read-by-read and policy-by-policy to cover those classes exhaustively.
- Per-task comparisons PASS; trees, factors and unique solutions unchanged from revision 3; gates green on the r4 snapshot.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision 5)

- Gate step 1: worklog ends `REWORK round 5: gates 7/7 green`; claims `src-1` (KB audit, `audits/policy_kb/dental_ppo_member_services/_difficulty.md`: "`dental_evt_claim_adjudication` overwrites in all five reprocessing/estimate policies restate the residual base rule more narrowly than the clause they retire — the allowance residual omits 'such a line is paid with remark PAID_ALTERNATE_BENEFIT'; the member-share residual omits 'and the practice may not bill more'").
- Gate step 2 (`snapshot.sh dental_ppo_member_services 5`, 2026-10-19T09:48:51): seven gates OK. Views r5 identical to r4 (`e59cc2a9…5445`, `bb4ac4c6…754f`); task_tools unchanged (`ff812736…d243`); extended changed → `b51f17bf00364ed7e055165b456f2abbac1b0ad9d61985cf1c2f33670ccb6d3c`.
- Change set (mechanical diff r4→r5): in IW, EST, UP, GD and UD only the two `dental_evt_claim_adjudication` `replaced_by` texts and their verbatim copies in the rule changed (+4/−2 rule sentences each); compute, compute_basis, factors, baseline, prerequisites and params are byte-identical; CA unchanged. Written before the round-5 reveal.

### src-1 verification — every overwrite's residual against the clause it retires (exhaustive, 19 overwrites)

| base clause retired | policies | residual now restates | complete? |
| --- | --- | --- | --- |
| `dental_evt_waiting_periods` credit sentence | all six | month_for_month → shortened by prior_coverage_months, never below zero; none → no credit | yes |
| `dental_evt_claim_adjudication` allowance sentence | IW, EST, UP, GD, UD | allowed amount, replaced by the alternate allowance when an alternate benefit applies (posterior composite on a posterior-composite-alternate plan; porcelain/ceramic crown on a molar on a molar-crown-alternate plan) **and such a line is paid with remark PAID_ALTERNATE_BENEFIT** | yes (the molar list is the base's `molar_teeth`, already enumerated in each rule's own allowance sentence) |
| `dental_evt_claim_adjudication` member-share sentence | IW, EST, UP, GD, UD | in-network: allowed − plan payment **and the practice may not bill more**; out-of-network: submitted − plan payment | yes |
| `dental_evt_missing_tooth_clause` exemption sentence | IW, EST | group open-enrollment / new-hire / special-enrollment exemption; prior coverage months covering the extraction date | yes |
| `dental_evt_frequency_age_limits` interval sentence | EST | full interval list and payability test | yes |

- Every `replaced_by` is still verbatim in its rule, still scoped "only for such a case", and still names every sibling that retires the same clause (XF#8). **src-1 closed.**
- Should the policy audit have caught it? **Yes** — XF#8 requires `replaced_by` to restate the in-force content for out-of-scope cases; revisions 2–4 checked that each residual existed and was scoped, but did not compare it phrase by phrase with the retired clause. The table above is that comparison, now done for all 19 overwrites.
- Standing checks re-run on r5: compute_basis / baseline / policy_source / superseded_clause / replaced_by verbatim — PASS; binding ownership, factor independence, tie and family-deductible sweeps — unchanged code, PASS; trigger rule, uuids, docstrings — tools unchanged, PASS.

### findings (revision 5, charter-global)

- None open.

## closing_checklist (revision 5)

- src-1 verified closed by a phrase-by-phrase comparison of all 19 overwrite residuals with the clauses they retire (table above); the policy audit should have caught it under XF#8 in revisions 2–4.
- All earlier items (round-1 C/T, round-2 D/G, round-4 F1/F2/XF8/EST-TIES) remain closed on the r5 charter; compute and factors byte-identical to r4, so trees, factor weight and unique solutions stand as verified in revision 4; both per-task comparisons PASS; gates green on the r5 snapshot.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision 6)

- Gate step 1: worklog ends `REWORK round 6: gates 7/7 green`; claims `src-2, src-3, src-4` (KB audit revision_3, `audits/policy_kb/dental_ppo_member_services/_difficulty.md`).
- Seed-only round confirmed: `dental.extended.yaml` sha256 `b51f17bf00364ed7…6d3c` and `task_tools.py` `ff8127367901d52f…d243` — both identical to revision 5, so every charter-global section of revision 5 (and the analyses it carries forward) stands by reference on these two hashes.
- Gate step 2 (`snapshot.sh dental_ppo_member_services 6`, 2026-10-20T04:24:47): seven gates OK. New views: `r6/task_0.json` `8b917488…cf2e`, `r6/task_1.json` `daa9d02c…1cbd`.
- Charter-global findings: none (unchanged charter). Seed findings are per task (below) and summarised in the closing checklist.

## closing_checklist (revision 6)

- KB re-judge items: **src-2 closed** (PPO agreement behind every recorded in_network_ppo line and estimate in task 0; assigned DHMO PCD agreements in both tasks); **src-3 closed** (DHMO copays include the 5.00 office-visit copay); **src-4 closed** (Corinne's member-only renewal +11.92 % ≤ 12 % cap; June invoices re-priced and paid in full).
- New seed defect **E1** (XF#12): the three new provider agreements record an `application_date` after their `effective_date` — a state the provider charter's events cannot produce (`provider_recredentialed` never writes `application_date`); introduced by the src-2 fix; no scored value moves in either task. Should the policy audit have caught src-2/3/4 earlier? src-2: yes — revision 1 checked network status only through the dental rule, not that a provider agreement backs each recorded network status (XF#12 "supporting records"); src-3 and src-4: yes, partially — DHMO copay pricing and group renewal-cap pricing are cross-product pricing checks I did not run on the rebuilt worlds of revision 2.
- Unchanged: charter and tools (hashes as revision 5); both re-derivations equal gold; trees, factor weight and unique solutions PASS; gates green on the r6 snapshot.

VERDICT revision_6: task0=RED task1=RED charter=CLEAN

## revision_7

## charter_global_frozen (revision 7)

- Gate step 1: worklog ends `REWORK round 7: gates 7/7 green`; claims `E1`.
- Seed-only round confirmed: `dental.extended.yaml` `b51f17bf00364ed7…`, `task_tools.py` `ff8127367901d52f…` — unchanged; revision-5 charter-global sections stand by reference.
- Gate step 2 (`snapshot.sh dental_ppo_member_services 7`, 2026-10-20T04:57:12): seven gates OK. Views `r7/task_0.json` `27493b27…b94d`, `r7/task_1.json` `2ee83161…9036`.
- Seed diff r6 → r7: the three provider agreements' `application_date`, `effective_date` and `npi_number`, and the Proctor practice's `profile_opened_date`. Nothing else changed.

### exhaustive lifecycle check of every seeded provider-agreement, DHMO, billing and group row (both tasks, one pass)

Provider agreements (task 0 `0c81cbc2` Ashford PPO, `1dbe0b0d` Proctor DHMO PCD; task 1 `6843d33b` Lincoln DHMO PCD), against `provider_credentialing`, `provider_recredentialing`, `provider_credentialing_approved`, `provider_recredentialed`:

| check | 0c81cbc2 | 1dbe0b0d | 6843d33b |
| --- | --- | --- | --- |
| practice profile opened ≤ application | 2014-09-22 ≤ 2014-11-10 | 2015-05-12 ≤ 2015-05-26 | 2015-05-11 ≤ 2016-01-11 |
| application → effective = first of month after a decision within 90 days | 2014-11-10 → 2015-02-01 (decision in Jan 2015, 52–82 d) | 2015-05-26 → 2015-09-01 (decision 2015-08-01…24, ≤ 90 d) | 2016-01-11 → 2016-04-01 (decision in Mar 2016, 50–80 d) |
| decision date = latest recredentialing; due = decision + 36 m | 2024-01-18 → 2027-01-18 ✓ (cycle chain 2015→2018→2021→2024) | 2024-07-29 → 2027-07-29 ✓ | 2025-03-24 → 2028-03-24 ✓ |
| NPI valid (10 digits, Luhn with 80840 prefix) | 1195360486 ✓ | 1447290671 ✓ | 1502833795 ✓ |
| specialty / location allowed; liability ≥ 1M / 3M; licence and liability unexpired at frozen time | ✓ | ✓ | ✓ |
| active, open panel, not terminated; in force on every date it backs | claim lines 2025–2026 and estimate ✓ | DHMO 2022-01-01 → 2025-02-28 ✓ | DHMO 2022-05-01 → 2025-05-31 ✓ |

- **E1 closed**: every `application_date` now precedes its `effective_date` and fits the approval timing; recredentialing left it untouched as the provider events require.
- **Missed in revision 6 (now closed):** the r6 NPIs were 9 digits (119536045, 144729060, 150283374), not valid NPIs under `provider_credentialing` ("a valid NPI"); I did not check the NPI format then. The r7 values are valid.

DHMO plans (task 0 `730905b4`, task 1 `0fa737e7`) against `dhmo_enrollment_eligibility`, `dhmo_coverage_end`, `dhmo_pcd_assignment`, `dhmo_evt_copay_schedule`: application → first of next month (2021-12-10 → 2022-01-01; 2022-04-12 → 2022-05-01) ✓; assigned PCD holds an active open-panel DHMO PCD agreement in WA from before the effective date ✓; pcd_effective = coverage effective ✓; voluntary termination on a month-end (2025-02-28; 2025-05-31) ✓; services by the assigned PCD at scheduled copay + 5.00 office visit (15.00, 90.00), cleanings ≤ 2 per year ✓.

Billing accounts against `billing_account_lifecycle`, `billing_evt_invoicing`, `billing_evt_payment_application`, `billing_grace_and_lapse`:
- DHMO direct-bill accounts (`5cac8d44`, `108db16e`): opened on the DHMO application date; one 15.40 invoice per covered month (38 = 2022-01…2025-02; 37 = 2022-05…2025-05), each issued exactly 20 days (`invoice_lead_days`) before the due day; first payment `binder`, the rest `regular`, none late; paid-through = DHMO termination date; balance 0.00; closure request created 2025-03-04 / 2025-06-03, confirmed, effective 2025-03-06 / 2025-06-05, after no funded enrollment remained ✓.
- Group list bills (`51e780a5`, `846b3f5f`): base invoices issued 30 days before the due day; amounts = contract rates × census (2,097.55 / 2,047.30 + 50.25; 1,194.40 / 1,037.80 + 28.95); every due month through the frozen date paid, the next month's invoice open as `balance_due`; task 1's January 2026 premium unpaid on its due date and cured in full on 2026-01-28 within `grace_period_days` 31 (`grace_cure`) ✓.

Group contracts and eligibility events against `group_member_reporting`, `group_renewal_rules`, `group_census_participation`: late-entrant adds effective the first of the month after the request (2025-02-10 → 2025-03-01; 2025-05-12 → 2025-06-01), reported within 31 days ✓; rate guarantees end the day before the next renewal ✓; censuses within every 12 months ✓; participation: each group dipped below the 75 % contributory minimum on one census (task 0 2025-01-02: 23/31; task 1 2025-05-01: 19/26) and was back above it within `participation_cure_days` 60 by the member's late-entrant add (24/31; 20/26) before the renewal audit ✓; task 1's renewal increase for the visible tier 28.95 → 32.40 = 11.92 % ≤ 12 % ✓.

Remaining members of any defect class: **none.** Observations carried (no id, no rule violated that a seed field can express): the supplementary "A" group invoices (issued 17–18 days ahead after a mid-cycle add) have no explicit invoicing sentence, though their totals equal the charter's monthly premium; the prior plan year's group rates (task 1 June 2025, Value 1000) and the prior offering are not recorded, so the June base invoice is consistent but not re-derivable; DHMO PCD agreements require a site visit, which no table records.

## closing_checklist (revision 7)

- E1 closed for all three agreements; the exhaustive lifecycle pass over every seeded provider-agreement, DHMO, billing and group row of both worlds found no remaining member of any defect class (table and lists above). The 9-digit NPIs of revision 6 were a member I missed then; they are now valid.
- Charter and tools unchanged (revision-5 hashes); both re-derivations equal gold; trees, factor weight and unique solutions PASS; gates green on the r7 snapshot.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
