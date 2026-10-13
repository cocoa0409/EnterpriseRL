# Policy-task audit — coverage_reviews_prior_auth_step_therapy / charter-global

## charter_global_frozen

- Freeze time: 2026-10-08 07:20 UTC (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Auditor: erl-task-policy-audit subagent (independent of the instantiator; did not read `worklog.md`).
- Hashes of the shared inputs (verified with `sha256sum` at audit start, equal to the brief):
  - `tasks/coverage_reviews_prior_auth_step_therapy/review.extended.yaml` — `40663ab77951fb1e7e2116ed1b7b6d01f753d7e72077d24452540559f1d9d96e`
  - `tasks/coverage_reviews_prior_auth_step_therapy/task_tools.py` — `cfda23dba57e3992c4035d7b87396ddadc82a74f07f67b800cbc663a89f13cfe`
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/review.yaml`, `blueprint/products/mail.yaml` and `retail.yaml` (only the parameters/event meanings the cross-category reads name), the extended charter, `task_tools.py`, the two masked views; `erlbench/determinism.py` (`ctx.now()` stamp) and the DSL primitive definitions in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `_within`, `LATEST`, `X*`, `CPARAM`) to fix the semantics of the restricted expressions.
- Masked / unread: `tasks/*.json` (all GT fields: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closures), `worklog.md`, any prior audit. No recursive search touched `tasks/`.
- Entry conditions (Step 0): gate snapshot supplied with the brief (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred to the KB stage); masked views supplied with hashes, verified equal (`task_0.view.json` → `c7bd03de5cc80fa77f2bf2edb895e4d3b972fc99517bf63c51cdf4b474722d5c`; `task_1.view.json` → `8783207d761dc5c0f69ba8ad31699230c0f62d043cf79a6a2578e1ee8d6f4857`). Input complete.
- Base copy: the extended file with `extended_policies` removed is YAML-identical to `blueprint/products/review.yaml` (programmatic `safe_dump(sort_keys=True)` diff: empty). Base section verbatim.

### policy_conflict_scan

Six extended policies, six task tools, one per policy:

| policy | subject / computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- |
| review_ext_member_request_quantity | review_case_opened / requested_quantity_per_30 (first-time, member-filed) | file_coverage_review_request_fd0cbfbe (user) | [] |
| review_ext_exception_approved_quantity | review_case_approved / approved_quantity_per_30 (first-time QL exception) | approve_quantity_exception_611b3a5d (agent) | ← member_request (value_input, state) |
| review_ext_continuity_quantity | review_auth_granted / approved_quantity_per_30 (continuity of care) | grant_continuity_authorization_38eb93b7 (agent) | [] |
| review_ext_renewal_request_quantity | review_case_opened / requested_quantity_per_30 (renewal, member-filed) | file_renewal_request_18124eb7 (user) | ← continuity (value_input, state) |
| review_ext_renewal_approved_quantity | review_case_approved / approved_quantity_per_30 (QL renewal) | approve_quantity_renewal_696a9005 (agent) | ← renewal_request (value_input, state); ← overturn (value_input, state) |
| review_ext_overturn_quantity | review_auth_granted / approved_quantity_per_30 (appeal overturn) | grant_overturn_authorization_6da113c2 (agent) | [] |

- Overlapping subjects: two policies compute `requested_quantity_per_30` on `review_case_opened`, separated by `is_renewal` (first-time vs renewal; each rule names the other kind as out of its scope: "a renewal request ... carry no requested quantity under it" / "a first-time request carries no quantity under it"); the tools write `is_renewal=False` / `True` respectively. Four policies compute `approved_quantity_per_30`, separated by the producing event (first-time approval, renewal approval, continuity grant, overturn grant) and by tool. No two policies claim the same `(target_tool, computes)`.
- Triggers / eligibility: base `review_evt_decision` "a request for a drug that already has an approval of the same type in force is denied with already_approved unless it is a renewal inside the renewal window" separates the first-time approval from the renewal approval once any QL authorization for the drug is in force; base `review_authorization_period` "A renewal case may be opened from renewal_window_days before the current expiration date" gates the renewal filing; base `review_continuity_of_care` "within continuity_of_care_days ... counting that date as day 1" gates the continuity grant. No extended policy weakens these.
- Time anchors: every extended rule anchors its month windows on its own write date (filing date / decision date / grant date / "the date the authorization is put in force"); effective dates: first-time approval = decision date; renewal = day after the renewed authorization expires; continuity = review program effective date; overturn = overturn date. Compatible with base `review_authorization_period` (retro_effective_days is 0 in Essentials/Standard; continuity and overturn anchors are stated by their own rules).
- Cross-category reads: mail (account opened date, auto refill flag, program lead days and eligibility fraction, prescriptions, shipments), retail (claims, paper-claim denials), appeal (overturned appeals). All are reads; no extended policy writes outside `review_cases` / `review_authorizations`.
- Terminal states: each tool writes one approval and/or one authorization row; no policy's write changes another policy's selected object except as declared by the four prerequisite edges.
- Scope exclusivity / completeness (per masked views only, scope inferred from worlds, not from `charter_scope`): task 0's world carries a denied first-time sumatriptan QL case and no QL authorization in force (first-time path: member_request → exception_approved); task 1's world carries a prior-carrier-approval case, an overturned Ubrelvy appeal and no authorizations (continuity → renewal_request → renewal_approved ← overturn). The two trees are disjoint and together cover all six extended policies. Confirmed against `charter_scope` only after reveal (see task files).

### rule_compute_equivalence

Swept every binding of every policy against its `compute_basis` quotation and the rule (programmatic check: every `compute_basis` quotation and every `baseline.rule` sentence occurs verbatim in the rule; every factor binding exists in compute; bindings disjoint per policy). Window semantics: the rules' "dated after the same day of the month N months before" equals the DSL `0 <= MONTHS(d, NOW) < N`. Findings:

- review_ext_member_request_quantity — equivalent. Every tier of the three ladders (refill cycle: lead-day subtraction / eligibility-fraction multiplication / days supply; retail carry-over: pro-rated unused part / whole quantity / nothing; transition: 2 / 1 / 0; ceiling multiple: package maximum / 1.75 / 1.5) is a rule sentence and a branch of its `decides` binding. "within the last 90 days" ↔ `DAYS(mail_opened, NOW) <= 90` (inclusive boundary; no seeded account sits on day 90 in either world).
- review_ext_exception_approved_quantity — equivalent, with one latent looseness recorded as observation O-2: `decided_at` takes the latest approval/denial/withdrawal of the drug of any review type, the rule says "no approval, denial or withdrawal is recorded after its opening" without "on it"; the two coincide literally.
- review_ext_continuity_quantity — equivalent.
- review_ext_renewal_request_quantity — equivalent.
- review_ext_renewal_approved_quantity — **NOT equivalent (F-1)**. Rule sentence 1: "(...; Nurtec ODT, whose limit is 8 units, is renewed under the same terms without the other-drug adjustment)". Compute: `other_drug: "'Ubrelvy' if drug == 'sumatriptan' else 'sumatriptan'"`, and `other_drug_adjusted` applies the subtraction / ×0.95 whenever the other drug's authorization or fills exist. For a Nurtec ODT renewal the compute takes sumatriptan as the other drug and applies the adjustment the rule says is not applied.
- review_ext_overturn_quantity — equivalent (triptan step `triptan_2m / 2 / K('triptan_tablets_per_treatment')` = "the average monthly sumatriptan tablets over those two months divided by 2"). The rule's scope is "a gepant (Ubrelvy ... or Nurtec ODT)"; the compute's `limit` falls through to sumatriptan, which no rule sentence covers (no empty promise in the rule; compute branch unused inside the rule's scope) — observation O-3, tied to F-2.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- Tool bodies (`task_tools.py`): every function only builds ids with `ctx.make_id` and `ctx.create`s rows; none reads the DB, branches on state, raises, or returns an error. The tool layer judges no eligibility and no prerequisite.
- Docstrings name no other tool, state no sequence position. Ordering-word hits: "Afterwards the ... shows ..." (all six; describes the call's own post-state), "first-time" / "first and last days in force" (adjectives), and `grant_overturn_authorization_6da113c2` "the quantity limit authorization owed after an appeal overturned the denial" (refers to the appeal-category event that defines the object, not to another write of this difficulty). Recorded as observation O-4; no sequence leak to another problem's write.
- uuid8s: fd0cbfbe, 611b3a5d, 38eb93b7, 18124eb7, 696a9005, 6da113c2 — pairwise distinct, no shared prefix/suffix, no arithmetic progression, no pattern of a common stem with a changed tail. Pass.

### prerequisite_graph

- `prerequisite` filled on all six policies (`[]` on member_request, continuity, overturn).
- Edges: exception_approved→member_request; renewal_request→continuity; renewal_approved→renewal_request; renewal_approved→overturn. Every `problem` is an extended policy id of this file, never a base id, never self. Graph acyclic (two components: {exception_approved, member_request} and {renewal_approved, renewal_request, continuity, overturn}).
- Each `policy_source` is verbatim in the blocked policy's own rule (programmatic substring check: True ×4).
- All four edges `form: state`, no `fallback_reason` (none needed).
- `kind: value_input` ×4; gates `requested_qty` (exception_approved), `renewed_qty` (renewal_request), `requested_qty` and `other_authorized_qty` (renewal_approved) are real compute bindings and each reads the row the depended-on write creates.
- `resolved_by` equals the depended-on policy's `target_tool` ×4, and each tool's effect creates exactly the row the `condition` names (opening row `is_renewal=False` / `True`; authorization `auth_basis=continuity_of_care` / `appeal_overturn`).
- `condition` vs sentence: three edges match in strength. The edge renewal_approved→overturn does not: see F-2.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test per edge:

1. exception_approved ← member_request. Sentence: "The approved quantity of a first-time quantity limit exception is not fixed until the records carry an undecided first-time quantity limit exception request for the drug." Connective "not ... until"; waited-on state is record-visible (an opening row, first-time, QL type, with no decision after it) in table words; no tool/policy id/snake_case; strength = condition. Writes that produce the state: only `file_coverage_review_request_fd0cbfbe` (writes `is_renewal=False`); `file_renewal_request_18124eb7` writes a renewal, not first-time. Derivation: sentence → "an undecided first-time QL request for the drug" → the only rule that sets the content of a first-time member-filed QL request is review_ext_member_request_quantity → its tool. Single reading. PASS.
2. renewal_request ← continuity. Sentence: "The quantity a member-filed renewal request asks for is not fixed until the records carry a continuity-of-care authorization for every prior carrier's approval on file for the drug." State form; only `grant_continuity_authorization_38eb93b7` writes `auth_basis=continuity_of_care`; derivation sentence → continuity authorization → review_ext_continuity_quantity (its rule: "a continuity-of-care quantity limit authorization ... when a new member's prior carrier's approval for the drug is on file"). Single reading. PASS.
3. renewal_approved ← renewal_request. Sentence: "The approved quantity of a quantity limit renewal is fixed only after the records carry an undecided renewal request for the drug." Only `file_renewal_request_18124eb7` writes `is_renewal=True`. Single reading. PASS.
4. renewal_approved ← overturn. Sentence: "The approval ceiling of a quantity limit renewal is worked out only after the records carry the authorization owed for every appeal overturned on another acute migraine drug." Connective and state form fine; strength **not** equal to the condition (F-2).

Other checks: no rule restates another policy's sentence; the depended-on rules (member_request, continuity, renewal_request, overturn) say nothing about the policies that wait on them; no extended rule names a tool, a policy id or a snake_case token (programmatic `[a-z]+_[a-z_]+` scan of every rule: none). No undeclared cross-problem order stated in an extended rule. Base rules carrying an order: `review_continuity_of_care` "The member must obtain a regular approval before the continuity approval ends." — a base sentence; no tree rests on it as an edge (the renewal edges have their own extended sentences) → observation O-5 only.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (criterion: the scored quantity):

- review_ext_member_request_quantity (`overwrite: []`; refs review_requirements, review_evt_case_intake, review_quantity_limit): base governs which drugs need review, who opens, urgency, one open case, the approval ceiling — none governs the requested quantity; extended does not alter any of them (it files a member-opened, standard, first-time QL case, as base allows with member_initiated_review_allowed true in every package). No conflict.
- review_ext_exception_approved_quantity (overwrite declared on review_quantity_limit "up to ql_exception_max_multiple times that limit per rolling 30 days; a request above that multiple is approved only up to it", verbatim in base): the replacing sentence is in the rule; all remaining base sentences (criteria_met on documented necessity, QL basis, approval period, decide once, already_approved) are inherited and not contradicted. The anonymous-intermediate, 0/1-multiplier and dropped-branch forms: the opioid / preventive / lapsed / cash steps all live inside the declared "approval ceiling"; no base branch dropped. Declared and unique.
- review_ext_continuity_quantity (`overwrite: []`; refs review_authorization_period, review_continuity_of_care, review_quantity_limit): the continuity quantity is not a "quantity limit exception approved" in the base sense (no case decision; base continuity "keeps coverage for it without a new review"), so the base QL ceiling does not govern it on its face. Two latent tensions recorded as observations, neither changing a scored value in either task world: O-6 — under packages whose `ql_exception_max_multiple` is 1.5 (Advanced Plus, Comprehensive, Comprehensive Specialty) the continuity partial tier 1.75 exceeds the base QL maximum, and under `continuity_requires_prior_claims: true` packages the "no prior claims received" tiers describe a member to whom base continuity grants nothing; O-7 — base `review_authorization_period` "An approval covers only the strength requested unless approval_covers_strength_changes is true" (false in Essentials/Standard) vs the extended rule counting the prior carrier's quantity "in tablets of the strength the member now fills": the base sentence governs which strength is covered, not the scored quantity (`review_authorizations` carries no strength field), and the extended sentence fixes the quantity explicitly.
- review_ext_renewal_request_quantity (`overwrite: []`): base renewal window and renewal clinicals sentences inherited; no base sentence fixes the requested quantity. No conflict.
- review_ext_renewal_approved_quantity (overwrite declared, same base clause, replacing sentence in rule): inherited base sentences (renewal runs renewal_approval_months, effective the day after current expiration, already_approved exemption inside window) not contradicted. Declared and unique.
- review_ext_overturn_quantity (overwrite declared, same clause): declared and unique. Base `review_authorization_period` "The effective date is the decision date" — the extended "runs from the overturn date" names the appeal decision as that decision; compatible.

No undeclared override of a scored quantity found.

### factor_ladders

Structure only (weight is per task). Counts per policy as declared → after the honesty tests:

| policy | factors (effect) | parameter / method declared | honest method | multi-source factor | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| member_request | refill_cycle_divisor (method), retail_carryover_on_move (method), direction_change_allowance (parameter), member_request_ceiling_multiple (parameter) | 2 / 2 | 2 | refill_cycle_divisor (mail_accounts.auto_refill_enrolled ∧ mail_prescriptions.days_supply_per_fill; ¬auto ∧ mail_orders count) ; retail_carryover_on_move (mail_accounts.opened_date ∧ retail_claims) | mail ×2 |
| exception_approved | diagnosis_and_fill_multiple (parameter), concurrent_opioid_method (method), preventive_allowance (parameter), lapsed_approval_units (parameter), cash_purchase_units (parameter) | 4 / 1 | 1 | diagnosis_and_fill_multiple (review_cases diagnosis ∧ retail_claims), preventive_allowance (review_authorizations ∧ retail_claims) | retail ×4 |
| continuity | current_strength_count (method), continuity_cash_units, home_delivery_move_allowance, continuity_ceiling_multiple (parameter) | 3 / 1 | **0 (F-3)** | continuity_ceiling_multiple (review_cases info ∧ retail_claims), home_delivery_move_allowance (mail_accounts ∧ retail_claims), current_strength_count (review_cases ∧ retail_claims) | retail ×3, mail ×1 |
| renewal_request | renewal_refill_cycle (method), renewal_use_margin, renewal_cash_units, renewal_growth_multiple (parameter) | 3 / 1 | 1 | renewal_growth_multiple (two review_cases facts: recency of receipt ∧ diagnosis — same table), renewal_refill_cycle (mail_accounts ∧ mail_prescriptions / mail_orders) | mail, retail ×2 |
| renewal_approved | renewal_diagnosis_fill_multiple, continuity_transition_allowance, clinical_response_allowance, renewal_cash_purchase_units (parameter); renewal_opioid_method, other_acute_drug_method (method) | 4 / 2 | 2 | renewal_diagnosis_fill_multiple, continuity_transition_allowance (review_authorizations ∧ review_cases), other_acute_drug_method (review_authorizations ∨ retail_claims) | retail ×4 |
| overturn | overturn_diagnosis_fill_multiple, overturn_ground_units, appeal_path_units, overturn_cash_units (parameter); overturn_opioid_method, concurrent_triptan_method (method) | 4 / 2 | 2 | overturn_diagnosis_fill_multiple, appeal_path_units (level ∧ filer) | retail ×4 |

Per ladder: every factor has exactly three tiers (two conditioned + fall-through), pairwise disjoint as stated; every tier's condition and value/method is a rule sentence and a branch of its `decides` binding; every `decides` is an intermediate, never `result`; every fall-through equals the factor's `baseline` and equals what `baseline.rule` states for that input (cycle divisor = days supply; carry-over/allowances/units = nothing added; multiples = 1.5 / 1.1; opioid / other-drug / triptan steps = "used as it stands"; strength = "taken as stated"). Every `baseline.rule` sentence is in the rule and its `params` keys exist.

Method-label honesty: refill-cycle (subtraction of lead days vs multiplication by a fraction vs none), retail carry-over (pro-rated remainder vs whole fill vs none), opioid (subtract days/3 vs ×0.9 vs none), other-acute-drug (subtract a quarter of the other authorization vs ×0.95 vs none), triptan (subtract a two-month average/2 vs ×0.95 vs none), renewal refill cycle (×d/(d−lead) vs ÷fraction vs none) each change the operation — honest. **current_strength_count is not (F-3)**: its three tiers are `letter_qty * 0.5`, `letter_qty * 2`, `letter_qty` — one formula, three multipliers.

Distinct outcomes: within the package of both task worlds (Northbridge Clinical Standard, `ql_exception_max_multiple: 2.0`) every ladder's three tiers select distinct values/methods. Package-conditional collapse (F-4): every ladder whose top tier is `P('ql_exception_max_multiple')` (member_request_ceiling_multiple, diagnosis_and_fill_multiple, continuity_ceiling_multiple, renewal_diagnosis_fill_multiple, overturn_diagnosis_fill_multiple) selects 1.5 at the top and 1.5 at the fall-through under Advanced Plus / Comprehensive / Comprehensive Specialty (`ql_exception_max_multiple: 1.5`), with the middle tier 1.75 exceeding the top tier.

Business realism (judged as observations, none demonstrated to the RED bar): O-8 — preventive_allowance adds acute-drug units because the member is on migraine prevention (prevention would ordinarily be argued to lower acute need); opioid steps subtract "days supply / 3" (days) from a tablet quantity. The remaining conditions (diagnosis, fill history at the limit, cash denials for a required review, lapsed approval, refill cycle, retail-to-mail move, other acute drug, overturn ground and level) are ones a PBM's QL criteria plausibly weigh. No tier condition holds of every customer reaching its write.

### findings

- **F-1 — SOURCE-POLICY RED (charter-global; rule/compute inequivalence).** Symptom: review_ext_renewal_approved_quantity rule says a Nurtec ODT renewal is made "without the other-drug adjustment"; compute applies it with sumatriptan as the other drug. Evidence: rule sentence 1 (quoted above) vs compute `other_drug: "'Ubrelvy' if drug == 'sumatriptan' else 'sumatriptan'"` and `other_drug_adjusted`. Demonstrated consequence: a Nurtec ODT renewal for a member with one paid sumatriptan fill in the last three months — rule: the opioid-step result is used as it stands; compute: it is multiplied by 0.95 (e.g. 8 × 1.5 = 12 → rule ceiling 12, compute int(11.4) = 11). Affected: extended charter, review_ext_renewal_approved_quantity rule sentence 1 / compute `other_drug`. Bears on: task 1 (claims this policy; its renewal is on sumatriptan, so its scored value is untouched — see 1.md).
- **F-2 — SOURCE-POLICY RED (charter-global; prerequisite sentence broader than its condition, and unresolvable hop).** Symptom: the renewal_approved←overturn sentence waits on "the authorization owed for every appeal overturned on another acute migraine drug"; the `condition` and the compute read only "the other acute migraine drug" (Ubrelvy for sumatriptan, sumatriptan for Ubrelvy). Evidence: `policy_source` vs `condition: For every appeal_cases appeal_overturned row on a coverage review denial of the other acute migraine drug ...`; rule sentence 1 lists three acute migraine drugs (sumatriptan, Ubrelvy, Nurtec ODT); review_ext_overturn_quantity's scope is "a gepant (Ubrelvy ... or Nurtec ODT)". Demonstrated consequence: (a) sumatriptan renewal, member with an overturned Nurtec ODT QL denial not yet effectuated — sentence: the ceiling cannot be worked out until the Nurtec authorization is recorded (an edge); condition/compute: no edge, the Nurtec authorization changes nothing; (b) Ubrelvy renewal, member with an overturned sumatriptan denial — sentence/condition require an authorization that no policy of this difficulty puts in force (overturn rule covers gepants only), so the hop has zero resolving writes. Affected: review_ext_renewal_approved_quantity rule sentence 3 / `prerequisite[1]`, review_ext_overturn_quantity rule sentence 1. Bears on: task 1 (no Nurtec or sumatriptan overturn in its world — see 1.md).
- **F-3 — SOURCE-FACTOR RED (charter-global structure; mislabelled method, computation below the method floor).** Symptom: current_strength_count is labelled `method` but its tiers only substitute a multiplier (0.5 / 2 / 1) into `counted_qty = letter_qty × r`. Evidence: ladder methods "the prior carrier's quantity is multiplied by 0.5 / multiplied by 2 / taken as stated"; compute `counted_qty`. Consequence: review_ext_continuity_quantity has 4 factors, all of which change a number (3 declared parameter + 1 mislabelled), so it carries 0 honest `method` factors, below the floor of 1 per computation. Affected: review_ext_continuity_quantity `factors[0].effect`. Bears on: task 1 (continuity is in its tree).
- **F-4 — SOURCE-FACTOR RED (charter-global structure; package-conditional tier collapse and inversion).** Symptom: ladders whose top tier is "the package's maximum exception multiple" and whose fall-through is 1.5 select the same value at both ends under the three packages with `ql_exception_max_multiple: 1.5`, and their middle tier (1.75) out-ranks their top tier. Evidence: variants Advanced Plus / Comprehensive / Comprehensive Specialty `ql_exception_max_multiple: 1.5`; ladders listed under factor_ladders. Consequence: for a member on those packages, chronic diagnosis + full fills (strongest evidence) gets 1.5 while either alone gets 1.75. Affected: five factors in five policies. Bears on: neither task world (both on Northbridge Clinical Standard, 2.0) — latent; recorded for the charter.
- Observations O-1..O-8 (no consequence demonstrated): O-1 — the first-time approval and the renewal approval decide on "the prescriber's clinical information on file" for the drug, while in both worlds that information was received on an earlier, already-decided case; base `review_evt_decision` ("When the clinical information needed ... is missing, the reviewer makes ... outreach attempts and the case pends") could be read case-by-case, but the extended rules scope it to the drug ("the prescriber's most recent clinical information for the drug"), defeating the pend reading. O-2 — `decided_at` drug-wide (above). O-3 — overturn compute's sumatriptan fall-through outside its rule's scope. O-4 — docstring "Afterwards"/"after". O-5 — base continuity "before the continuity approval ends" ordering sentence. O-6, O-7 — continuity vs base QL maximum / prior-claims requirement / strength coverage. O-8 — business realism of preventive allowance and opioid day subtraction.

## closing_checklist

Not written: the difficulty does not close (charter-global REDs F-1..F-4; per-task verdicts in 0.md / 1.md). See the closing section appended below after the reveals.

### closing status (written after both reveals, 2026-10-08 ~07:30 UTC)

The difficulty does **not** close; Step 4's checklist is evaluated item by item for the record:

- Audit files: `0.md`, `1.md` one-to-one with `tasks/0.json`, `tasks/1.json`, beside this file; first revision, no older revisions. Comparison sections: task 0 PASS; task 1 RED (SOURCE-FACTOR).
- Coverage and scope: the six extended policies are fully covered; `charter_scope` task 0 = {member_request, exception_approved}, task 1 = {continuity, overturn, renewal_request, renewal_approved} — pairwise disjoint, each spanning its whole tree; every task tool is used by exactly one task; uuid8s independent (see `### action_binding_and_uuids`).
- Trees: task 0 n = 1 (1 value_input), task 1 n = 3 (3 value_input); each has an owner=user write; the union of edges is acyclic; no cross-task edge.
- Factors: every computation declares a self-sufficient baseline, 4–6 factors, three-tier ladders stated in the rule; every factor bears weight on its task's world and every whole-baseline number differs from gold (10.0/17.342, 13/17, 13.5/16, 24/28, 16.0/19.5, 13/14). Fails: F-3 (continuity computation has no honest method factor; bears on task 1) and F-4 (package-conditional tier collapse/inversion; latent in both worlds).
- Policy self-consistency: fails at charter level on F-1 (renewal_approved rule/compute, Nurtec ODT branch) and F-2 (renewal_approved←overturn sentence broader than its condition; unresolvable hop for a sumatriptan overturn). Neither moves a scored value in either task world.
- Gates: not re-run by the auditor (the brief's gate snapshot is cited in `## charter_global_frozen`); re-running belongs to the final form after rework.

Per-task verdicts: task 0 **PASS**; task 1 **RED — SOURCE-FACTOR** (F-3). Difficulty-level REDs: F-1, F-2 (SOURCE-POLICY), F-3, F-4 (SOURCE-FACTOR).

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-08 08:47 UTC, before any round-2 task JSON was opened. Auditor: erl-task-policy-audit subagent (same auditor as round 1).
- Shared inputs: `review.extended.yaml` **changed** → `d0f82aca303dd36cd9ebcc9ac9afee03ab6ea2ff37e90981e29863a21c34f37f` (round 1: `40663ab7…d9d96e`); `task_tools.py` **unchanged** → `cfda23dba57e3992c4035d7b87396ddadc82a74f07f67b800cbc663a89f13cfe`. Because the charter hash moved, every charter-global section below is re-derived in full; the tool-only conclusions are re-confirmed against the unchanged tool module.
- Base copy: extended minus `extended_policies` is still YAML-identical to `blueprint/products/review.yaml`.
- Entry conditions: round-2 gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred); rebuilt views supplied with hashes, verified equal (`task_0.view.json` `542fda4a…e1f60`, `task_1.view.json` `cdfd1804…37e40`).
- Masked / unread at this freeze: round-2 `tasks/*.json`, `worklog.md`. Known to the auditor from round 1: the round-1 GT of both tasks (disclosed in each task's revision_2).

### policy_conflict_scan (revision 2)

Unchanged structure: six policies, six tools, the same four edges, the same subject/`computes` separations (`is_renewal` false/true for the two requested quantities; four producing events for the approved quantities). New in the charter: every multiple ladder is now expressed as a share of the package's maximum exception multiple (whole / seven eighths / three quarters), and every baseline ceiling is "the drug's limit times three quarters of the package's maximum exception multiple"; the overturn policy now covers sumatriptan as well as the gepants; the renewal approval names "none" as the other drug of a Nurtec ODT renewal; the continuity policy's move factor now carries the running retail fill (pro-rated / whole / nothing) instead of fixed units. No new overlap of subjects, triggers, time anchors or terminal states; no new cross-category write.

### rule_compute_equivalence (revision 2)

Programmatic sweep: every `compute_basis` quotation and every `baseline.rule` sentence occurs verbatim in its rule; bindings disjoint; every factor binding exists. Manual sweep of the changed sentences:

- Share ladders (member_request, exception_approved, continuity, renewal_approved, overturn): rule "takes the package's maximum exception multiple; ... takes seven eighths of it; any other member takes three quarters of it" ↔ compute `P(...)`, `P(...) * K('partial_share'|'cap_share_case_only')` (0.875), `P(...) * K('default_share'|'cap_share_default')` (0.75). Equivalent.
- exception_approved / renewal_approved "no approval, denial or withdrawal **for the drug** is recorded after its opening" ↔ drug-wide `decided_at`. Equivalent (closes O-2).
- renewal_approved "The other acute migraine drug (Ubrelvy for a sumatriptan renewal, sumatriptan for a Ubrelvy renewal, none for a Nurtec ODT renewal)" ↔ `other_drug: "'Ubrelvy' if drug == 'sumatriptan' else ('sumatriptan' if drug == 'Ubrelvy' else 'none')"`; with `'none'` no authorization and no fill matches, so `other_drug_adjusted = opioid_adjusted`. Equivalent (closes F-1).
- overturn: scope "an acute migraine drug (sumatriptan ..., Ubrelvy ..., or Nurtec ODT ...)" ↔ `limit` three-way; triptan step "of a gepant ... otherwise, and always for a sumatriptan overturn, it is used as it stands" ↔ `drug != 'sumatriptan' and ...`. Equivalent (closes O-3).
- continuity strength: "multiplying it by a strength ratio: the ratio is 0.5 ... 2 ... and 1 otherwise" ↔ `strength_ratio`, `counted_qty = letter_qty * strength_ratio`. Equivalent.
- continuity move: "with a home delivery account opened within the last 60 days, when the most recent paid retail fill ... was dispensed at least 7 days before the grant date and its days supply has not run out, the unused part ... is added ...; when that fill was dispensed fewer than 7 days before ..., its whole quantity is added; an account opened earlier, no home delivery account, or a fill whose supply has run out adds nothing" ↔ `move_units`. Equivalent.
- opioid steps: "one unit for each average monthly opioid day (those days supply divided by 3) is subtracted" ↔ `limit_times_multiple - opioid_days / 3`. Equivalent.

No inequivalence found.

### action_binding_and_uuids (revision 2)

Carried forward on the unchanged `task_tools.py` hash `cfda23db…13cfe`: one `(target_tool, computes)` per policy (targets unchanged); tool bodies judge nothing; uuid8s independent; docstring ordering words as in round 1 (O-4 unchanged).

### prerequisite_graph (revision 2)

Same four edges, all `value_input`, `form: state`, no fallback; acyclic; every `policy_source` verbatim in its blocked rule (programmatic True ×4); gates `requested_qty`, `renewed_qty`, `requested_qty`, `other_authorized_qty` are compute bindings; `resolved_by` = target tools. Edge renewal_approved→overturn: sentence now "... the authorization owed for every appeal overturned on the other acute migraine drug." = condition "the other acute migraine drug" (same scope).

### prerequisite_sentences (revision 2)

Edges 1–3 unchanged and PASS as in round 1. Edge 4 (renewal_approved ← overturn): connective "only after"; state "the authorization owed for every appeal overturned on the other acute migraine drug" — record-visible (overturned appeal rows; authorization rows with the overturn as basis); scope equals the condition; resolving writes: for a sumatriptan renewal (other = Ubrelvy) and for a Ubrelvy renewal (other = sumatriptan) exactly one write — `grant_overturn_authorization_6da113c2`, whose rule now covers both drugs; for a Nurtec ODT renewal the set is empty by definition ("none"), so no hop. Single reading. PASS (closes F-2). No tool/policy id/snake_case in any rule; no depended-on rule restates a sentence; base ordering sentence O-5 unchanged (observation).

### override_declarations (revision 2)

Same three declared overrides (verbatim base clause, replacing sentence in rule). Re-checked the policies with `overwrite: []`:
- continuity: its ceiling is now at most the whole package maximum (top tier), so it can no longer exceed the base QL maximum under any package (closes that half of O-6). The other half of O-6 stays: under packages with `continuity_requires_prior_claims: true` the tiers conditioned on "no prior carrier's claims history received" describe members to whom base continuity grants nothing (observation; no task world on such a package). O-7 (strength coverage) unchanged.
- member_request, renewal_request: no base sentence governs a requested quantity. No undeclared override.

### factor_ladders (revision 2)

| policy | factors (effect) | honest parameter / method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| member_request | refill_cycle_divisor (m), retail_carryover_on_move (m), direction_change_allowance (p), member_request_ceiling_multiple (p) | 2 / 2 | refill_cycle_divisor, retail_carryover_on_move | mail |
| exception_approved | diagnosis_and_fill_multiple (p), concurrent_opioid_method (m), preventive_allowance (p), lapsed_approval_units (p), cash_purchase_units (p) | 4 / 1 | diagnosis_and_fill_multiple, preventive_allowance | retail |
| continuity | current_strength_count (**p**), continuity_cash_units (p), home_delivery_move_allowance (**m**), continuity_ceiling_multiple (p) | 3 / 1 | continuity_ceiling_multiple, home_delivery_move_allowance | retail, mail |
| renewal_request | renewal_refill_cycle (m), renewal_use_margin (p), renewal_cash_units (p), renewal_growth_multiple (p) | 3 / 1 | renewal_refill_cycle (mail_accounts ∧ mail_prescriptions / mail_orders) | mail, retail |
| renewal_approved | 4 p, 2 m (opioid, other acute drug) | 4 / 2 | renewal_diagnosis_fill_multiple, continuity_transition_allowance, other_acute_drug_method | retail |
| overturn | 4 p, 2 m (opioid, triptan) | 4 / 2 | overturn_diagnosis_fill_multiple, appeal_path_units | retail |

- Labels: current_strength_count is now `parameter` deciding `strength_ratio` (0.5 / 2 / 1 — a number); home_delivery_move_allowance is now `method` deciding `move_units` with three different formulas (pro-rated remainder, whole fill, nothing). Both honest. Continuity has ≥ 2 parameter and 1 honest method (closes F-3).
- Distinct outcomes under every package: top tier = M, middle = 0.875 M, fall-through = 0.75 M, where M = `ql_exception_max_multiple` ∈ {2.0, 1.5}; strictly ordered and distinct for every M > 0 (closes F-4). Every fall-through equals its factor baseline and equals `baseline.rule` ("three quarters of the package's maximum exception multiple"; nothing added; as it stands; ratio 1).
- `baseline.params` of the share-based baselines name `ql_exception_max_multiple`, a package parameter read with `P()`, not a policy `params` key; the baseline rule names it in words ("the package's maximum exception multiple"), so a reader can compute it — no defect.
- Realism: the opioid step now states its ground ("a day of opioid treatment displacing one acute migraine dose"), which resolves the day/tablet unit mismatch noted in O-8; the preventive allowance (prevention adds acute units) is unchanged — O-8 is partly closed, the preventive half stays an observation.

### findings (revision 2)

- F-1 **closed** (rule and compute agree on the Nurtec ODT branch).
- F-2 **closed** (sentence scope = condition scope; both other-drug hops have exactly one resolving write; Nurtec ODT renewals have none by definition).
- F-3 **closed** (honest parameter/method labels; continuity has 1 honest method).
- F-4 **closed** (share ladders are distinct and ordered under every package).
- O-2, O-3 closed; O-6 and O-8 partly closed (remaining halves above, observations); O-1, O-4, O-5, O-7 unchanged (observations).
- No new charter-global defect found.

### closing_checklist (revision 2, written after both revision-2 reveals)

- Audit files: `0.md`, `1.md` one-to-one with the tasks, `_difficulty.md` beside them; round-1 text untouched, revision 2 appended to each. Comparison sections: task 0 PASS, task 1 PASS.
- Coverage and scope: six extended policies covered; `charter_scope` task 0 = {member_request, exception_approved}, task 1 = {continuity, overturn, renewal_request, renewal_approved} — pairwise disjoint, each spanning its whole tree; task tools closed over GT; uuid8s independent and unchanged.
- Trees: task 0 n = 1 (1 value_input), task 1 n = 3 (3 value_input); each with an owner=user write; union of edges acyclic, no cross-task edge.
- Factors: every computation has a self-sufficient baseline, 4–6 factors with ≥ 2 parameter and ≥ 1 honest method, three-tier ladders stated in the rule with distinct outcomes under every package; per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor; every factor bears weight; whole-baseline numbers differ from gold (10.0/17.342, 13/17; 13.5/16.2, 24/28, 16.2/19.725, 13/14).
- Policy self-consistency: no open charter-global RED (F-1..F-4 closed); remaining items are observations (O-1, O-4, O-5, O-6 second half, O-7, O-8 preventive half).
- Gates: the orchestrator's round-2 snapshot on the final form is green for all seven instantiation gates (traceability deferred to render); not re-run by the auditor.

Per-task verdicts (revision 2): task 0 **PASS** (no regression); task 1 **PASS** (round-1 SOURCE-FACTOR closed). The difficulty passes the source-layer audit.
