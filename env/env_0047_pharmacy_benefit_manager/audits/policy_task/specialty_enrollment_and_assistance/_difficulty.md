# Policy-task audit — specialty_enrollment_and_assistance / charter-global

## charter_global_frozen

- Frozen: 2026-10-08 08:12 UTC (written before any task's GT was revealed; nothing in this section is derived from a revealed GT).
- Auditor: independent erl-task-policy-audit subagent (not the instantiator).
- Inputs and hashes:
  - `tasks/specialty_enrollment_and_assistance/specialty.extended.yaml` sha256 `1e19f423e832a04356b5ec42135bf43fb385bd96dd6fd141c9f74efff8cf416e` (matches brief)
  - `tasks/specialty_enrollment_and_assistance/task_tools.py` sha256 `4a9151b0ddc63a72c0f41f6da9d9bbb8a40e64a6490cf1d9c1da4a9ffac4608c` (matches brief)
  - `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/specialty.yaml` (plus `plan.yaml` variant parameters read for the cross-category `CPARAM('plan', …)` binding)
  - masked views `/tmp/env0047_views/specialty_enrollment_and_assistance/task_{0,1}.view.json`, sha256 `08694dd5…6764` / `011dece4…e9a`, both re-hashed and matching the brief
- Permitted: the charter (base + extended), the tool module, the DB schema, the shared tools, `erlbench/`, the masked views (frozen_time, user_scenario, initial_state).
- Masked and not read: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, closures), `worklog.md`, sibling difficulties' tasks and audits, any other scenario.
- Entry conditions (Step 0): gate snapshot supplied with the brief — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred (needs the published KB). Masked views supplied with hashes. Entry conditions met; the gates were cited, not re-run.
- Base copy: the base section of `specialty.extended.yaml` (lines 1–1002) is byte-identical to `blueprint/products/specialty.yaml` (diff differs only by one trailing blank line); a parsed key-by-key comparison of category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies is equal on every key.

### policy_conflict_scan

Extended policies (4), with their write targets and scopes:

| policy | subject | target_tool (owner) | computes | scope stated in its rule |
| --- | --- | --- | --- | --- |
| specialty_ext_card_assistance | specialty_assistance_applied | apply_card_assistance_5ca6ac5a (agent) | amount | latest shipped fill; program standard_coordination or variable_copay; excludes maximizer and accumulator_adjustment plans |
| specialty_ext_member_fill_payment | specialty_payment_posted | pay_fill_balance_998729ec (user) | amount | latest shipped fill of an enrollment **not** on hold for overdue payment, no earlier fill unpaid |
| specialty_ext_maximizer_draw | specialty_assistance_applied | apply_maximizer_draw_3be5be4a (agent) | amount | latest shipped fill; maximizer programs only |
| specialty_ext_hold_release_payment | specialty_payment_posted | pay_hold_release_166e6883 (user) | amount | enrollment on hold for an overdue payment |

- Overlapping subjects: the two `specialty_assistance_applied` policies are split by `copay_assistance_program` (standard/variable vs maximizer), which is a single-valued variant parameter — disjoint. The two `specialty_payment_posted` policies are split by "on hold for an overdue payment" vs "not on hold for an overdue payment" — disjoint.
- Triggers/time anchors: all four read `frozen_time` as "today"; month ages use whole-month counting (`MONTHS`), day ages use calendar days. No two policies anchor the same quantity on different clocks.
- Terminal states: the two agent writes lower `assistance_balance` and `balance_due` and post an assistance-applied + manufacturer payment pair; the two user writes post a member payment and lower `balance_due`. `pay_hold_release_166e6883` explicitly does not change hold status. No two policies write the same field to different values on the same row.
- Cross-category read boundaries: card → plan (`accumulator_adjustment_program`) and retail (`retail_claims`); maximizer → review (`review_authorizations`) and retail; member payment and hold release → none. All reads are read-only.
- Prerequisite components: {member_fill_payment → card_assistance} and {hold_release_payment → maximizer_draw}. With M=2, the natural partition is one component per task; whether the tasks' `charter_scope` claims exactly these is checked per task after the reveal (it is masked here). On the charter alone the two components are disjoint and jointly cover the four extended policies.
- Base/extended conflicts found by the scan are written under `override_declarations` (F-POL-1, F-POL-2, F-POL-3).

### rule_compute_equivalence

Every `compute_basis` quotation was machine-checked to be a verbatim substring of its policy's `rule` (all pass), and every sentence of each `baseline.rule` is a verbatim sentence of its `rule` (all pass). Sweep back, per policy:

**specialty_ext_card_assistance** — `fid/cs/ded/disp` = latest `specialty_fill_shipped` by `ship_date` ("the latest shipped fill"); `basis` implements the three-way card-basis sentence exactly (NB ∧ ded>0 ∧ standard → cs; non-NB → 0; else cs−ded; the `dispensing_pharmacy` enum is exactly {northbridge_specialty_pharmacy, outside_specialty_pharmacy, retail_pharmacy}, so "!= NB" ≡ "outside specialty or retail"); `ld_age`, `take_window`, `card_taken`, `benefit_standing` implement the load-age sentences ("fewer than 12 whole months" ↔ `MONTHS<12`; "dated no more whole months before today than that load" ↔ `within_months = ld_age+1`); `retail_use` implements the retail card-use sentence (paid retail claims, same drug, copay − member paid, window by load age, else 12 months when lapsed, else 0); `remaining` = max(…,0); `result` = RND(min(basis, remaining),2) once. No invented basis, no empty promise. Note (observation O-1): "card payments dated no more whole months before today than that load" is month-granular and so would also count card payments dated before the load inside the load's whole-month bucket; rule and compute agree on this, so it is not a non-equivalence; no audited world contains such a row.
- The `deductible_portion` argument is fixed by the rule ("the card paying the deductible portion first"; "its deductible portion being the part of the payment that covers the fill's deductible portion") rather than by compute; it is uniquely min(payment, fill deductible) on the whole-cost-share tier and 0 on the copay-portion tier.

**specialty_ext_member_fill_payment** — `unpaid` implements the three-way remainder sentence (card = `specialty_assistance_applied` on the fill, member = member `specialty_payment_posted` on the fill); `guar` implements the guaranteed-share sentence; `share_count` implements the proration/started-period sentence (`int((ds+29)/30)` = started 30-day periods); `cap_total`, `credit` (net excess of member payments over what earlier fills left after card payments, else negative enrollment balance, else 0) and `result` (min first, credit off, floor 0, round once) match. Equivalent.

**specialty_ext_maximizer_draw** — `draw_basis`, load-age/benefit, draw window, retail program use, `fill_period`, `fills_left = 1 + int(horizon/period)`, `even_draw`, `result` match their sentences. Two edges (observations, no audited world reaches them): (O-2) `year_end = <program_year>-12-31` presumes the program year is a calendar year — the rule only says "the last day of the program year"; (O-3) `auth_exp/auth_eff` read only the latest `review_auth_granted` row by `effective_date`, so an approval ended by `review_auth_terminated`, or an older in-force approval shadowed by a later future-dated one, would be read differently from "a coverage review approval for the drug is in force today".

**specialty_ext_hold_release_payment** — `open_balance`, `paid_counted`, `set_aside` match. **`release_target` does not match its sentence** (finding F-POL-4): the rule's first tier is "When a shipped fill is past its payment due date (shipped more than the payment due days before today) and no fill has shipped fewer than one whole month before today", i.e. *any* shipped fill past due; the compute tests `latest_ship_age > P('specialty_payment_due_days')`, i.e. the *latest* fill past due, and its second tier tests `past_due_n > 0` where `past_due_n` counts fills not shipped in the last whole month (not fills shipped more than 30 days ago). In a world whose latest shipment is exactly 30 days old (whole-month age 1) and has an older shipment, the rule selects target 0 and the compute selects the credit limit. Neither audited world is in that band (task 1's latest shipment is 43 days old and every shipment is older than one whole month), so no task's scored value moves.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (apply_card_assistance_5ca6ac5a, amount), (pay_fill_balance_998729ec, amount), (apply_maximizer_draw_3be5be4a, amount), (pay_hold_release_166e6883, amount) — each claimed by exactly one policy.
- uuid8s: `5ca6ac5a`, `998729ec`, `3be5be4a`, `166e6883` — pairwise distinct, no shared prefix or suffix, no sequential pattern; consistent with independent generation.
- Docstrings: none names another tool, none states a sequence position, none carries "before/after/first" as an ordering instruction ("Afterwards the fill shows …" describes the call's own effect). No docstring adds a confirmation, review or wait.
- Function bodies: all four tools perform unconditional writes (create ledger rows, update `assistance_balance`/`balance_due`) with no policy check, no refusal path, no hint. The tool layer judges no prerequisite.
- The maximizer tool hardcodes `deductible_portion=0.0` and `accumulator_adjusted=False`; the card tool hardcodes `accumulator_adjusted=False`. For the card tool this is consistent with its rule's exclusion of accumulator_adjustment plans; for the maximizer tool see F-POL-3.

### prerequisite_graph

- Every extended policy has `prerequisite` filled: card `[]`, maximizer `[]`, member payment 1 edge, hold release 1 edge.
- Edges: `specialty_ext_member_fill_payment → specialty_ext_card_assistance` (value_input, gate `unpaid`, state form); `specialty_ext_hold_release_payment → specialty_ext_maximizer_draw` (value_input, gate `paid_counted`, state form). Both `problem`s are extended policy ids of this file, neither a base policy nor self. Graph acyclic (two disjoint single edges).
- `policy_source` of both edges is verbatim in its own policy's `rule` (machine-checked).
- `form: state` on both; no `fallback_reason` present, correctly (none required).
- `condition`: card edge — "The ledger carries a specialty_assistance_applied entry naming the latest shipped fill, written by the copay card rule …"; hold edge — "The ledger carries a specialty_assistance_applied entry (with its manufacturer payment) naming the latest shipped fill, written by the maximizer draw rule …". Both match the state the prerequisite sentence names, neither strengthened nor weakened.
- `resolved_by` equals the depended-on policy's `target_tool` in both edges; each tool's body writes exactly the assistance-applied row (and manufacturer payment row) the condition names.
- `gate` bindings exist in the blocked compute (`unpaid`, `paid_counted`), and both are genuinely moved by the depended-on write (`card_f` → `unpaid` tier 1 and `guar` tier 1; manufacturer payment → `pay_all`).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any prerequisite field.

### prerequisite_sentences

Edge A — "The member payment on the latest shipped fill is figured only after the fill carries the copay card payment owed on it."
- Four-point test: ordering connective "only after" ✓; waits on a record-visible state (the fill carries a copay card payment — visible in `find_specialty_ledger` as an assistance-applied / copay_card payment row naming the fill) with no performer or tool ✓; no tool name, policy id, snake_case token or row id ✓; scope: "the copay card payment owed on it" — the owed amount is the one the copay card rule sets, matching the condition ✓.
- Single write: within this difficulty two tools can put a `copay_card` manufacturer payment on a fill (card tool and maximizer tool). The sentence names "the copay card payment", which is the card rule's own term ("This rule sets the copay card payment …"); the maximizer rule names its write "the maximizer program draw" and excludes standard/variable-copay enrollments, while the member-payment rule's guaranteed share contemplates maximizer enrollments too. On a variable-copay or standard enrollment only the card write can bring the state about. On a maximizer enrollment the "copay card payment owed" is undefined (the card rule excludes it) — observation O-4; no audited task is on that branch for this edge.
- Derivation: member-payment rule → "only after the fill carries the copay card payment owed on it" → the records show no card payment on the latest fill → the card rule ("This rule sets the copay card payment that a manufacturer copay card makes on the latest shipped fill …") is the rule whose write produces that state → its target action applies it. One reading.
- No second wording of the dependency in the blocked rule; the card rule does not restate it.

Edge B — "The hold-release payment is not set until the latest shipped fill carries the maximizer program draw owed on it."
- Four-point test: "not … until" ✓; record-visible state (draw on the fill in the ledger) ✓; no tool/id/token ✓; scope equals condition ✓.
- Single write: only the maximizer rule sets "the maximizer program draw"; the card rule excludes maximizer enrollments. One reading: hold-release rule → draw missing on the latest fill → maximizer-draw rule → apply the draw.
- No second wording; the maximizer rule does not restate it.

Undeclared cross-problem orders: none found. "earlier fills being settled first" / "earlier fills are settled first under the oldest-first rule" (member payment, hold release) are intra-problem payment-allocation statements restating base `specialty_evt_payment`, not orders between this charter's problems. Base rules: `specialty_evt_assistance` "but only after the member's consent is recorded" and "A program benefit may be loaded only once the member's copay program consent is on file" state orders against consent/load events that no extended policy writes; no task tree rests on them.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (findings only; the per-task files demonstrate consequences).

**specialty_ext_card_assistance** (refs: specialty_cost_share_assistance, specialty_evt_assistance)
- cost_share S1 (cost share starts from plan cost share; split-fill proration): followed — the fill's recorded cost share is used.
- S2 standard_coordination ("lesser of the fill's cost share and the assistance balance"): handled differently; **declared** in `overwrite`.
- S3 variable_copay first clause ("assistance is applied the same way"): **declared**. S3 floor clause concerns the member's share, not the card amount — not touched by this policy.
- S4 maximizer: out of this policy's scope.
- S5 ("only to a fill dispensed by Northbridge Specialty Pharmacy and only while the member's consent is on file"): followed (outside fills get basis 0; consent inherited).
- S6 (rounding; deductible paid before copay, recorded as deductible_portion): followed on the whole-cost-share tier; on the copay-portion tier the card pays no deductible, which only arises for non-standard plans that the scope excludes.
- S7 (accumulator_adjustment): accumulator_adjustment plans are out of scope; followed.
- evt_assistance S1 (consent before enrolment), S2 (load once), S4 (load only once consent on file): untouched. S3 "never above the fill's cost share or the assistance balance": **not named in `overwrite`**; the extended cap is "the remaining card benefit", which is not bounded by the enrollment's `assistance_balance` in general — finding F-POL-2 (latent; demonstrated per task where it binds).

**specialty_ext_member_fill_payment** (refs: specialty_agg_therapy_coordination, specialty_evt_payment, specialty_cost_share_assistance)
- agg S1–S4: followed (own fills/balance; combined credit limit concerns holds, not this payment).
- evt_payment S1 (oldest unpaid fill first): followed via the rule's own scope ("once no earlier fill of the enrollment is left unpaid"). S2 instruments: followed. S3 ("never exceeds the unpaid cost share of the fill it pays"): followed (min with unpaid).
- cost_share S3 floor clause: handled differently (floor applies when the card paid part but not all; prorated to days supplied); **declared** in `overwrite`. The proration of the guaranteed share for any fill under 30 days (not only split fills, as base S1 prorates) sits inside the declared replacement of the floor sentence; recorded as realism observation O-5 rather than as an undeclared override.

**specialty_ext_maximizer_draw** (refs: specialty_cost_share_assistance, specialty_evt_assistance, specialty_maximizer)
- cost_share S4 first clause ("an enrolled member pays maximizer_member_cost_share and assistance pays the rest of the cost share up to the assistance balance"): **declared**.
- **specialty_maximizer S2: "A member who enrolls no later than maximizer_enrollment_deadline_days calendar days after the activation date, the activation date being day zero, is charged maximizer_member_cost_share from their next fill; a member who enrolls later is charged the non-enrollee coinsurance on fills shipped before the enrollment date and maximizer_member_cost_share afterwards." — NOT named in `overwrite`.** The extended draw is min(draw basis, even draw); whenever the even draw is below the unpaid remainder the member is left owing more than `maximizer_member_cost_share` (0.00 on the only maximizer variant, Northbridge Specialty Total Care). The base sentence fixes the member's charge at `maximizer_member_cost_share`, so the program must pay the rest; the extended sentence fixes the program payment below that. Both govern the same quantity (how the latest fill's cost share splits between program and member) and reach different numbers whenever the even draw binds. **Undeclared override — finding F-POL-1 (SOURCE-POLICY RED where demonstrated: task 1).**
- cost_share S5 (NB-dispensed only; consent on file): inherited; the extended rule does not zero a non-NB latest fill, but base still forbids it — no conflict, base governs.
- cost_share S6 ("the assistance applied to the deductible portion is recorded as deductible_portion, the deductible being paid before the copay portion") vs extended "The draw … pays no deductible portion": **not named in `overwrite`** — finding F-POL-3 (latent; bears only on a fill with a deductible portion).
- cost_share S7 (accumulator_adjustment → accumulator_adjusted true): the maximizer rule does not exclude accumulator_adjustment plans and the tool hardcodes `accumulator_adjusted=False` — part of F-POL-3 (latent).
- evt_assistance S3 "never above the fill's cost share or the assistance balance": not named; the fall-through draw basis "prorated to 30 days" (unpaid × 30 / days supply) exceeds the fill's unpaid cost share for any fill under 30 days (e.g. a 14-day split fill on Total Care: × 30/14), so the extended draw can exceed the fill's cost share — part of F-POL-2 (latent).
- specialty_maximizer S1, S3, S4: untouched.

**specialty_ext_hold_release_payment** (refs: specialty_agg_therapy_coordination, specialty_evt_payment, specialty_hold_rules)
- hold_rules S2 clause "or the balance brought to the credit limit or below": **declared**. The combined-balance credit limit of agg S2 is narrowed to "the enrollment's own balance only" by the rule's scope sentence, which is the same declared replacement.
- evt_payment S1 (oldest unpaid fill first): the rule posts against the latest fill "earlier fills being settled first"; for retail-pharmacy fills the rule's own set-aside sentence says their cost share was "settled at the dispensing pharmacy", so they are not unpaid. Followed. S3 (never above the fill's unpaid cost share): followed in the audited world (see task 1).
- hold_rules S1, S3, S4: untouched.

### factor_ladders

Structure only (weight lives in each task's `factor_weight`). Declared counts:

| policy | factors | parameter | method | cross_difficulty |
| --- | --- | --- | --- | --- |
| card_assistance | 4 | 2 (card_basis, retail_card_use) | 2 (benefit_standing, payments_taken_window) | plan, retail |
| member_fill_payment | 4 | 3 (guaranteed_share, share_count, credit) | 1 (unpaid_remainder) | none |
| maximizer_draw | 6 | 3 (draw_basis, retail_program_use, fill_period) | 3 (benefit_by_load_age, draws_taken_window, draw_horizon) | retail, review |
| hold_release_payment | 4 | 2 (set_aside, release_target) | 2 (open_balance, payments_counted) | none |

Every factor has a three-tier ladder, `decides` an input binding (never `result`), binding sets are disjoint within each policy, every tier is a sentence of the `rule` and a branch of the `decides` binding, and every fall-through equals the factor's `baseline` and the policy's `baseline.rule`. Each `baseline.rule` is self-sufficient (a reader computes a definite number from it and the records).

The ladder-reality tests strike the following factors (findings F-FAC-1 … F-FAC-6). Each is a property of the charter and of the variant parameters, so it holds in every world:

- **F-FAC-1 `card_basis_by_plan_and_pharmacy` (card) — one condition holds of every customer who reaches this write, and two tiers coincide.** Tier 1's compound condition includes "for a member whose plan counts manufacturer assistance toward the deductible and out-of-pocket (standard accumulation)". The rule's scope sentence excludes "a member whose plan backs assisted amounts out of the accumulators", and `plan.parameter_schema.accumulator_adjustment_program` has exactly two values (standard, accumulator_adjustment). So every in-scope member is on standard: this part of the condition restates the scope and divides no customers. With that part always true, tier 1 = NB fill with ded>0 → whole cost share, and the fall-through for an NB fill can only be reached with ded = 0, where "copay portion (cost share less deductible portion)" = whole cost share. Tiers 1 and 3 therefore select the same value for every in-scope NB fill. The effective ladder has two tiers (NB → whole cost share; outside → 0), and the factor's `cross_difficulty: plan` read is decorative. Struck.
- **F-FAC-2 `card_payments_taken_window` (card) and `maximizer_draws_taken_window` (maximizer) — two tiers whose methods never reach the result.** `card_taken` is read only by tier 1 of `benefit_standing` (`(ld_amt - card_taken) if (ld_date and ld_age < 12) …`); on tier 2 (no load) `benefit_standing` is the enrollment balance and on tier 3 (lapsed load) it is 0, and both ignore `card_taken`. Whatever the window factor selects on its tiers 2 and 3 ("count none" / "last 12 months"), the result is the same. The two tiers are one tier written twice, so the live ladder has two tiers. The factor's tier condition is also exactly the `benefit_standing` factor's tier-1 condition, so it splits one tier of another factor's method into a second "factor". The same holds for `maximizer_draws_taken_window` against `benefit_available`. Both struck.
- **F-FAC-3 `retail_card_use` (card) and `maximizer_retail_program_use` (maximizer) — tier 2 never moves the result.** Tier 2 applies only when "a load is on the ledger but the latest posted 12 or more whole months before today". In that case `benefit_standing`/`benefit_available` is 0, so `remaining = MX(0 - retail_use, 0) = 0` for any card/program use ≥ 0, and the rule defines that quantity as "what the card [program] paid at the counter". Tier 2 and the fall-through (zero) therefore always produce the same result, and the live ladder has two tiers. Both struck. (Observation O-6: the formula "copay less what the member paid there" can be negative on a retail claim where the member paid a deductible or DAW penalty at the counter, which would *raise* the remaining benefit; no audited retail claim carries a deductible or penalty.)
- **F-FAC-4 `guaranteed_share_count` (member payment) — tier 2 is dead in every charter-consistent world.** Tier 2 ("more than 30 days → started 30-day periods") changes the result only when a guaranteed share > 0 applies. A share > 0 applies only under variable_copay (floor 25.00), and both variable_copay variants (Exclusive with Copay Assist, Care Management) have `max_days_supply_specialty: 30`, with base `specialty_evt_fill` stating "Each fill is at most max_days_supply_specialty days". The only variant allowing more than 30 days (Total Care) is maximizer with `maximizer_member_cost_share: 0.0`, so cap = 0 × count whatever the count. When no share applies, the count is unused. Tier 2 thus always yields the fall-through's result. Struck.
- **F-FAC-5 `maximizer_draw_basis` (maximizer) — tiers 1 and 2 select the same value.** The rule's scope is maximizer programs only, and the only maximizer variant (Total Care) has `maximizer_member_cost_share: 0.0`. Tier 1 "the fill's unpaid remainder less P('maximizer_member_cost_share')" = unpaid remainder = tier 2 "the fill's unpaid remainder in full". One tier is written as two. Struck. (Realism observation O-7: the fall-through/baseline "unpaid remainder prorated to 30 days" — for an 84-day fill, ×30/84; for a 14-day split fill, ×30/14, which exceeds the fill's cost share — is not a treatment a maximizer program publishes; see also F-POL-2.)
- **F-FAC-6 `hold_payments_counted` (hold release) — the three tiers are one method.** Payment sources are exactly {member, manufacturer_assistance, foundation_grant} (`db_schema.specialty_ledger.payment_source`; not_applicable only on non-payment rows). Tier 1 counts every payment. Tier 2 applies when no payment is posted, so "count none" = every payment = 0. Tier 3 applies when only member payments are posted, so "count only the member's own" = every payment. Hence `paid_counted ≡ pay_all` in every world: the ladder is one tier written as three, and only the baseline (member-only) differs. Struck.

Surviving factors after the strikes:

| policy | surviving | parameter | method | multi-source survivors | cross-difficulty survivors |
| --- | --- | --- | --- | --- | --- |
| card_assistance | 1 (benefit_standing) | 0 | 1 | none | none |
| member_fill_payment | 3 (unpaid, guaranteed_share, credit) | 2 | 1 | guaranteed_share (variant param + card ledger; + maximizer flag) | none |
| maximizer_draw | 3 (benefit_by_load_age, draw_horizon, fill_period) | 1 | 2 | draw_horizon (review approval + load year), fill_period tier 2 (variant 90-day list + fill) | draw_horizon (review) |
| hold_release_payment | 3 (open_balance, set_aside, release_target) | 2 | 1 | set_aside (retail fills + ledger) | none |

All four computations fall below the four-factor floor; card_assistance and maximizer_draw also fall below two `parameter` factors.

Label honesty (observations, not strikes): `outside_fill_set_aside` (labelled parameter) chooses between "their whole cost share" and "their cost share less those payments", which are two formulas; `maximizer_draw_basis` (labelled parameter) has a fall-through that changes the computation (×30/days supply). Both are borderline method/parameter labels (O-8).

Realism of conditions/outcomes (observations): O-5 — the guaranteed share is prorated for any fill under 30 days, which sweeps standard 28-day biologic fills (Dupixent's normal monthly supply) in with split fills; specialty programs treat a 28-day supply as a monthly fill, and base prorates only split fills. O-7 above.

### findings

- **F-POL-1 (SOURCE-POLICY, undeclared override; bears on task 1).** Symptom: base `specialty_maximizer` sentence "A member who enrolls no later than maximizer_enrollment_deadline_days calendar days after the activation date … is charged maximizer_member_cost_share from their next fill" stays in force, and `specialty_ext_maximizer_draw` charges the member whatever the even draw leaves. Root cause: `overwrite` of specialty_ext_maximizer_draw names only the specialty_cost_share_assistance clause; specialty_maximizer is in `base_policy_refs` but its charge sentence is not superseded. Affected: specialty.extended.yaml `extended_policies[specialty_ext_maximizer_draw].overwrite` / `.rule` vs base `policies[specialty_maximizer].rule` S2. Consequence demonstrated in `1.md`.
- **F-POL-2 (SOURCE-POLICY, latent undeclared override; no audited world binds).** Base `specialty_evt_assistance` "Assistance is applied once per shipped fill, never above the fill's cost share or the assistance balance" is not named by either assistance policy. Card: "remaining card benefit" (load less card payments less retail use) is not bounded by the enrollment's `assistance_balance`. Maximizer: the fall-through basis "prorated to 30 days" exceeds the fill's cost share for fills under 30 days. Neither task's world reaches the binding case (task 0: 380 ≤ 450 and ≤ 930; task 1: 900 ≤ 1050 and ≤ 2100). Not demonstrable on an audited task → recorded charter-global, no task verdict rests on it.
- **F-POL-3 (SOURCE-POLICY, latent undeclared override; no audited world binds).** Maximizer "pays no deductible portion" vs base cost_share S6 "the deductible being paid before the copay portion"; the maximizer scope does not exclude accumulator_adjustment plans while the tool hardcodes `accumulator_adjusted=False` against base S7. Task 1's fill has deductible 0.00 and plan Northbridge Rx Value is `standard`, so the task does not bind.
- **F-POL-4 (SOURCE-POLICY, rule/compute non-equivalence; no audited world binds).** `release_target` compute tests the latest fill's age and counts "not in the last whole month" as past due, while the rule says "a shipped fill … shipped more than the payment due days before today". Demonstration world: latest shipment exactly 30 days before today with an older shipment — rule: target 0; compute: credit limit. Task 1 is outside that band.
- **F-FAC-1 … F-FAC-6 (SOURCE-FACTOR, unreal ladders; bear on both tasks).** As above. Affected: specialty.extended.yaml `extended_policies[*].factors[...]` named in each item. The per-task consequence (surviving factor counts below the floor; for task 0, no surviving cross-difficulty factor) is demonstrated in `0.md` / `1.md`.
- Observations O-1 … O-8 as listed in the sections above, plus O-4 (the "copay card payment owed" state is undefined for a maximizer enrollment reaching the member-payment rule).

## closing_checklist

Written after both reveals (2026-10-08 08:15:28 UTC). The difficulty does **not** pass, so the Step 4 checklist is not closed:

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`; this is the first revision.
- Verdicts:
  - task 0 — policy PASS, tree PASS, factors **SOURCE-FACTOR RED**, unique solution PASS;
  - task 1 — **SOURCE-POLICY RED** (F-POL-1), tree PASS, **SOURCE-FACTOR RED**, **SOURCE-TASK RED**.
- Scopes (from the revealed `charter_scope`): task 0 = {card_assistance, member_fill_payment}, task 1 = {maximizer_draw, hold_release_payment}. They are pairwise disjoint and jointly cover all four extended policies, matching the two prerequisite components. Each task tool has its own uuid8.
- Trees: each has one prerequisite problem, one value_input edge and a user-owned root write. The difficulty-wide prerequisite graph is acyclic.
- Factors: no computation retains four real factors (see `factor_ladders`). Task 0 retains no cross-difficulty factor.
- Gates were not re-run on a final form because no final form exists. The rework belongs to the instantiation stage, not to this audit.

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-08 ~10:15 UTC. Written before any round-2 GT was revealed; nothing here is derived from round-2 `tasks/*.json`.
- Auditor: the same independent auditor as round 1.
- Hashes (re-computed, match the coordinator's brief): `specialty.extended.yaml` `f2e7d7116a0eda4a8b1019bee0e6c4484aefff25bc59407106e2fcef85ef9ef5` (changed from `1e19f423…`); `task_tools.py` `87bb0e536b1ae5167af11105709611d07fabe957ba32bdac7b363786ba3a0373` (changed from `4a9151b0…`).
- Re-derivation: both shared inputs changed, so every charter-global section below is re-derived in full; nothing is carried forward by reference.
- Base section: lines 1–1002 are still identical to `blueprint/products/specialty.yaml` (diff re-run).
- Gate snapshot (orchestrator, full difficulty): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; traceability deferred. Cited, not re-run.
- Masking: as in round 1. Not read: `worklog.md`, sibling difficulties, other scenarios. No recursive search over `tasks/`.
- contamination_disclosure (round 2): this auditor saw round-1 GT for both tasks (round-1 worlds and values). Round-2 derivations are recomputed from the revised charter and the rebuilt views; the task files state how far each overlaps round-1 GT.

### policy_conflict_scan (r2)

Same four extended policies, target tools and owners. Scope changes:
- `specialty_ext_member_fill_payment` is now restricted to standard/variable-copay programs, which also closes O-4.
- `specialty_ext_maximizer_draw` now excludes accumulator_adjustment plans.

Subject splits are still disjoint: assistance by program type, member payment by hold status and program type. Prerequisite components are unchanged: {member payment → card}, {hold release → draw}. The graph is acyclic.

Reworker's design-choice flag (two tools per write family):
- The bodies of `apply_card_assistance_5ca6ac5a` and `apply_maximizer_draw_3be5be4a` are now identical except for id prefixes. Both take `deductible_portion`.
- The bodies of `pay_fill_balance_998729ec` and `pay_hold_release_166e6883` are identical except for id prefixes.
- Each pair is still bound one-to-one to policies with disjoint scopes, and the docstrings name the scope (copay card vs maximizer draw; ordinary fill payment vs hold release). The choice of tool is therefore entailed by the policy, not by the tool.
- Consequence: a wrong-tool call leaves an equivalent DB state under a different tool name, so only the tool-name check separates them. Observation R2-O1; no relationship fails.

### rule_compute_equivalence (r2)

Machine checks: every `compute_basis` is verbatim in its rule; every `baseline.rule` sentence is in its rule; every `overwrite.replaced_by` is verbatim in its rule; every `superseded_clause` is verbatim in its base policy. All pass.

Sweep back:
- **Card.** The program-year window (`py_start/py_end`, Jan 1–Dec 31 now stated in the rule, which closes O-2 for both assistance policies), `take_window`, `benefit_standing` keyed on the latest fill's ship date, `retail_use` with `MX(…,0)` (closes O-6), and `basis` with `mem_on_fill` all match their sentences.
  - Observation R2-O2: "dated fewer whole months before today than the first day of that program year" is month-granular. It excludes in-year payments dated earlier in January than today's day of month (for example, with today 2026-10-07, a 2026-01-05 card payment is 9 whole months back and falls outside the window). Rule and compute agree, so this is a realism concern, not a non-equivalence. No audited world carries such a payment. It replaces round-1 O-1 in a different form.
- **Member payment.** `guar` (split / full / none, plus floor < cost share), `credit_window` (plan year ≤ 6 months → 12; > 6 → from plan-year start; none → whole history), and windowed `mem_w/cs_w/card_w` match.
- **Maximizer.** `draw_mode` (enrolled / not enrolled within deadline → 0 / otherwise unspread), the program-year benefit and windows, `retail_program_use` floored at 0, horizon (O-3 unchanged, as the reworker declares), and `fill_period` match. The deductible-first sentence is enforced through the tool's new `deductible_portion` argument.
- **Hold release.**
  - `open_balance` now counts every payment, which removes the round-1 `paid_counted` ladder. `set_aside` and the release target match. F-POL-4 is closed: the rule now defines due as "once a whole month has passed since it shipped", and the compute tests exactly that (`recent_n == 0`; `due_n > 0 and recent_n > 0`).
  - **New finding R2-F-POL-A (latent non-equivalence):** the overpayment sentence counts "the member's own payments on fills shipped 12 or more whole months before today, together with the program's payments on them". The compute (`mem_old`, `prog_old`) instead selects payments by their own `entry_date` (`total − within_months=12 by entry_date`), not by the ship date of the fill they pay. Example: a fill shipped 2025-09-22 and paid by the member on 2025-10-08, with today 2026-10-07. By the rule the payment is on an old fill and counts toward the returned overpayment; by the compute it is 11 whole months old and does not. In the audited task 1 world every payment on the old fill falls in the same whole-month bucket as the fill (fill 2025-09-22, card 2025-09-25, member 2025-09-30, all 12 months back), so rule and compute agree there.
- **New finding R2-F-POL-B (latent, base tension):** the hold rule's "A fill's payment comes due once a whole month has passed since it shipped" restates a base fact that base states differently. Base `specialty_evt_fill`: "each fill's cost share is due within specialty_payment_due_days of shipment" (30 calendar days); base `specialty_hold_rules` S1 uses "past specialty_payment_due_days". A whole month is 28–31 days, so the two differ on fills between 28 and 31 days old. `specialty_hold_rules` is in `base_policy_refs`; its S1 is not named in `overwrite`. Task 1's fills are all ≥ 44 days old, so it does not bind there.

### action_binding_and_uuids (r2)

- `(target_tool, computes)` pairs: unchanged and each claimed once.
- uuid8s: `5ca6ac5a`, `998729ec`, `3be5be4a`, `166e6883`, unchanged and distinct. `apply_maximizer_draw_3be5be4a` gained `deductible_portion` and kept its uuid8; this is the same tool and the same frozen identifier (observation only).
- Docstrings: no sequencing words, no other tool names.
- Bodies: all four are still unconditional writes and validate no prerequisite.

### prerequisite_graph (r2)

- Edge A (member → card): unchanged. State form, gate `unpaid` exists, `policy_source` verbatim.
- Edge B (hold → draw): gate changed to `open_balance`, which exists and is moved by the draw (every payment now counts). Policy_source verbatim, state form, no fallback.
- No viewpoint phrasing in either edge. Acyclic.

### prerequisite_sentences (r2)

- Both sentences are unchanged and pass the four-point test as in round 1.
- O-4 closed: the member-payment rule now excludes maximizer enrollments, so "the copay card payment owed on it" always refers to the card rule.
- No new cross-problem order sentence appears in any rule.

### override_declarations (r2)

- **F-POL-1 (maximizer charge):** `specialty_maximizer` clause "is charged maximizer_member_cost_share from their next fill" is now declared and replaced. **Closed for on-time enrollees.**
  - Residual R2-O3 (latent): the same base sentence's second half, "a member who enrolls later is charged the non-enrollee coinsurance on fills shipped before the enrollment date and maximizer_member_cost_share afterwards", is not named. For a late enrollee it still fixes the member's charge at `maximizer_member_cost_share` (0.00), against the extended "part … above the even draw stays owed by the member". It binds only for a late enrollee; task 1's member enrolled on day 11.
- **F-POL-2:** `specialty_evt_assistance` "never above the fill's cost share or the assistance balance" is now declared by both assistance policies; the maximizer's prorated basis is gone. **Closed.**
- **F-POL-3:** the maximizer now "pays the fill's deductible portion first" (consistent with base S6, with the tool argument added) and excludes accumulator_adjustment plans (consistent with S7). **Closed.**
- **F-POL-4:** closed (see above). It is replaced by latent R2-F-POL-A/B.
- **Other sentences:** card, member and hold sweeps are as in round 1 with the new declarations. The member-payment overwrite now carries the floor-lower-than-cost-share condition from base S3. No new undeclared conflict was found beyond R2-O3 and R2-F-POL-B.

### factor_ladders (r2)

Declared:

| policy | factors | parameter | method | cross_difficulty |
| --- | --- | --- | --- | --- |
| card | 4: basis_by_pharmacy_and_member_payment (p), benefit_by_program_year (m), payments_taken_by_program_year (m), retail_card_use (p) | 2 | 2 | retail |
| member payment | 4: unpaid_remainder (m), variable_copay_guaranteed_share (p), credit (p), credit_window_by_plan_year (m) | 2 | 2 | plan |
| maximizer | 6: draw_mode (m), benefit_by_program_year (m), draws_taken_by_program_year (m), retail_program_use (p), draw_horizon (m), fill_period (p) | 2 | 4 | retail, review |
| hold release | 4: open_balance (m), retail_fill_set_aside (p), returned_overpayment_on_old_fills (p), release_target (p) | 3 | 1 | none |

Within each policy, bindings are disjoint, each fall-through equals the baseline, and each ladder appears in the rule and in its `decides` binding.

Round-1 strikes, re-tested:
- **F-FAC-1 — closed.** The plan conjunct is gone. Tier 1 is now "NB fill with a deductible portion and no member payment of their own → whole cost share"; tier 3 covers an NB fill with a deductible and a member payment → copay portion. Tiers 1 and 3 now differ whenever a deductible is present. Realism observation R2-O4: "a member who has already paid toward the fill being taken to have paid its deductible portion" treats any member payment, however small, as settling the whole deductible portion. It is a stated rule rather than a straw man, but not an obvious industry practice.
- **F-FAC-2 — closed.**
  - The window ladders are now keyed on today against the load's program year, while the benefit ladders are keyed on the latest fill's ship date. Window tier 2 ("load year ended ≤ 365 days ago") is reached with benefit tier 1 when a fill shipped in the prior program year is paid early in the next year. That case is live.
  - Window tier 3 is reached with benefit tier 1 only when the latest fill is more than a year old. That case is live but contrived (observation R2-O5).
- **F-FAC-3 — closed.** Retail tier 2 is now "no load on the ledger, claims in the last 12 months → taken off the enrollment's assistance balance". That is exactly the benefit fall-through, so it reaches the result.
- **F-FAC-4 — closed.** The share count is replaced by split vs full under variable copay. Split fills exist under both variable-copay variants (`split_fill_program: true`, Ibrance), so all three tiers are live. This also closes O-5: a 28-day full fill now takes the whole 25.00 floor.
- **F-FAC-5 — closed.** `maximizer_draw_mode` has three distinct methods: spread-and-cap, zero while the choice is open, and unspread.
- **F-FAC-6 — closed.** `hold_payments_counted` is removed; the replacement `returned_overpayment_on_old_fills` has three live, distinct tiers.

Label check: `retail_fill_set_aside` is still labelled parameter while choosing between two formulas, so O-8 is still open in part (observation). `maximizer_draw_basis` (the other half of O-8) is gone.

Multi-source survivors:
- card: retail_card_use tier 1 (ledger load + retail claims)
- member: guaranteed share (variant program + card ledger + fill split flag)
- maximizer: draw_horizon (review approval + load year), retail_program_use
- hold: set_aside (retail fills + ledger), returned (fills + ledger by source)

Charter-level structure passes: 4/4/6/4 factors, each with ≥ 2 parameter and ≥ 1 method. Per-task cross-difficulty and seeding checks are in the task files.

### findings (r2)

- Round-1 F-POL-1 … F-POL-4 and F-FAC-1 … F-FAC-6: closed at charter level as described.
- **R2-F-POL-A** (latent rule/compute non-equivalence, overpayment by payment date vs fill ship date): bears on no audited value; recorded charter-global.
- **R2-F-POL-B** (latent undeclared restatement of the payment due point against base `specialty_hold_rules` S1 / `specialty_evt_fill`): bears on no audited value.
- **R2-O3** (late-enrollee half of the `specialty_maximizer` charge sentence still undeclared; latent).
- Observations: R2-O1 (twin tool bodies), R2-O2 (January edge of the program-year window), R2-O4 (any member payment deems the deductible paid), R2-O5 (contrived window tier 3), O-3 unchanged, O-8 in part.

### closing_checklist (r2)

Written after the round-2 reveal (10:14:56 UTC). **The difficulty does not pass yet.**

- Per-task verdicts r2:
  - task 0: PASS on all four relationships.
  - task 1: policy PASS, tree PASS, **factors SOURCE-FACTOR RED (R2-T1-F1, new defect)**, unique solution PASS on the recorded world.
- Round-1 RED closure (verified against the artifacts, not taken from the reworker's list):

| round-1 item | status |
| --- | --- |
| F-POL-1 | closed (on-time half declared; late-enrollee half latent, R2-O3) |
| F-POL-2 | closed |
| F-POL-3 | closed |
| F-POL-4 | closed (replaced by latent R2-F-POL-A/B) |
| F-FAC-1 | closed |
| F-FAC-2 | closed |
| F-FAC-3 | closed |
| F-FAC-4 | closed |
| F-FAC-5 | closed |
| F-FAC-6 | closed |
| task 1 SOURCE-TASK | closed |

- Round-1 observations:
  - Closed: O-2, O-4, O-5, O-6, O-7, T0-O1, T0-O2, T0-O4, T1-O1.
  - Changed form: O-1 is now R2-O2.
  - Still open in part: O-8 (`retail_fill_set_aside` label).
  - Unchanged as declared: O-3, T1-O2.
  - Not settled: T1-O3. Its claimed fix introduced R2-T1-F1.
- Scopes: task 0 = {card, member payment}, task 1 = {draw, hold release}. Pairwise disjoint and jointly complete; the uuid8s are unchanged.
- Trees: one prerequisite each, one value_input edge, user-owned roots. The graph is acyclic.
- Factors: each computation has 4–6 real factors with ≥ 2 parameter and ≥ 1 method. Each task has a multi-source and a cross-difficulty factor, and each factor bears weight against an honest baseline on its world. The exception is task 1's seeded cross-difficulty rows, which contradict the plan and retail charters (R2-T1-F1).
- Regression check: nothing that passed in round 1 now fails, except the task 1 world rebuild (R2-T1-F1).
- New latent charter findings with no audited value bound: R2-F-POL-A, R2-F-POL-B, R2-O3.
- Gates on the final form: not re-run by the auditor; the orchestrator's snapshot is cited (all green). The open red belongs to the task 1 seed.

## revision_3

### charter_global_frozen (revision 3)

- Frozen: 2026-10-08 ~11:12 UTC. Written before any round-3 GT reveal.
- Hashes (re-computed, match the brief):
  - `specialty.extended.yaml` `c7f260e580edb0264ee645bda5cf7ae260d227c8eb3572b1e96fdb0107945ee3` — changed, so every charter-derived section below is re-derived.
  - `task_tools.py` `87bb0e536b1ae5167af11105709611d07fabe957ba32bdac7b363786ba3a0373` — unchanged from round 2, so `action_binding_and_uuids (r2)` is carried forward by reference on this hash.
- Base section: still identical to `blueprint/products/specialty.yaml`. Blueprint files (specialty/plan/retail yaml, db_schema, share_tools) hash the same as in round 2.
- Gates (orchestrator snapshot, cited): all OK; traceability deferred.
- Masking and read isolation as before.
- contamination_disclosure: round-1 and round-2 GT for both tasks were seen.
- **Audit-miss disclosure.** In rounds 1 and 2 this auditor did not catch that the seeded retail claims contradicted the retail charter's own definition of the member payment. `retail.yaml` defines `member_paid_amount` = "deductible_amount + copay_amount + daw_penalty_amount", and `db_schema` says "total the member paid at the pharmacy: deductible_amount + copay_amount + daw_penalty_amount". Yet task 0 rounds 1–2 seeded `copay_amount 300.0, member_paid_amount 0.0`, round-1 task 1 seeded 1050.0 / 250.0, and round-2 task 1 seeded 700.0 / 150.0. The old card-use formula (copay less member paid) depended on that contradiction. It is recorded here as a miss of the earlier revisions, which are left as they are; the reworker found and corrected it.

### policy_conflict_scan (r3)

Same four policies, tools, owners and subject splits. Prerequisite components are unchanged and the graph is acyclic.

### rule_compute_equivalence (r3)

Machine checks re-run: every `compute_basis` and `baseline.rule` sentence is in its rule; every `replaced_by` is in its rule; every `superseded_clause` is verbatim in its base; no tool or policy names appear in rules; bindings are disjoint. 0 failures.

Changed parts, swept back:
- **Card basis.** The rule now reads: "a fill … that carries a deductible portion of which the member's own payments on the fill cover less than all is the fill's whole cost share less what the member has already paid on it …; … any other fill is its copay portion, the member having paid the deductible portion herself". This matches `basis = (cs - mem_on_fill) if (NB and ded > 0 and mem_on_fill < ded) else (0 if not NB else cs - ded)`. **R2-O4 closed.**
  - New latent observation R3-O1: when the member has paid more than the deductible portion, the card basis is the full copay portion, so card plus member can exceed the fill's cost share (for example cost share 450, deductible 150, member paid 200 → card basis 300 → 500 collected). The rule's own cap, "never above the fill's cost share", bounds the card alone, not the sum. No audited world has a member payment on the latest fill.
- **Retail use (both assistance policies).** The rule is now "the member's payment recorded on a paid retail claim for the same drug, which the network pharmacy bills to the manufacturer copay card [program] as secondary payer after Northbridge Rx"; compute `retail_use = rm_py / rm_year` (member_paid_amount). This is now consistent with the retail charter's definition of `member_paid_amount` and its `copay_card_secondary_billing: true` (retail.yaml "the pharmacy may bill a manufacturer copay card after Northbridge Rx"). The extended rule turns the retail charter's "may" into "bills". That is a specialty-side reading of another product's permission, not a contradiction; observation R3-O2.
- **Hold set-aside.** It now covers outside specialty and retail fills; the label is `method` (**O-8 closed**). Rule: "when no payment on the enrollment's ledger names the latest such fill of either kind …". Compute adds payments on the latest retail fill *and* the latest outside fill.
  - Latent ambiguity R3-O3: when both kinds exist, "the latest such fill of either kind" can be read as the single latest outside-dispensed fill, but the compute checks the latest of each kind. Task 1 has outside-specialty fills only, so it does not bind.
- **Overpayment returned.** The rule now defines "the older payments those dated 12 or more whole months before today", which matches the compute's selection by `entry_date`. **R2-F-POL-A closed** (the rule was aligned to the compute).
- **Release target.** The "comes due once a whole month has passed" sentence is removed; the tiers now speak only of fills shipped one or more / fewer than one whole month before today, which is exactly what the compute tests. The release target no longer restates a payment-due point, so **R2-F-POL-B closed.**
- **Maximizer.** `overwrite` now also names "and maximizer_member_cost_share afterwards" (verbatim in base `specialty_maximizer`). **R2-O3 closed.**
- Unchanged and still open as observations: R2-O2 (January edge of the program-year window), R2-O5 (contrived window tier 3), O-3.

### action_binding_and_uuids (r3)

Carried forward from `revision_2`; `task_tools.py` hash `87bb0e53…` is unchanged. R2-O1 (twin tool bodies) is unchanged.

### prerequisite_graph / prerequisite_sentences (r3)

Both edges are unchanged in sentence, form, gate (`unpaid`, `open_balance`) and resolver. They pass as in round 2; the re-run checks are clean.

### override_declarations (r3)

- Round-2 latent items R2-O3 and R2-F-POL-B are closed as above.
- No new base sentence is contradicted by the changed rule text. The card basis follows base S6, "the deductible being paid before the copay portion": the card pays the rest of the deductible first. The retail-use change touches no base specialty sentence.

### factor_ladders (r3)

Counts unchanged:

| policy | factors | parameter | method | cross-difficulty |
| --- | --- | --- | --- | --- |
| card | 4 | 2 | 2 | retail |
| member payment | 4 | 2 | 2 | plan |
| maximizer | 6 | 2 | 4 | retail, review |
| hold release | 4 | 2 (returned, target) | 2 (open balance, set-aside) | none |

- Changed ladders re-tested:
  - Card basis: tier 1 (cost share less member paid) and tier 3 (copay portion) differ whenever the member has paid less than the deductible and the deductible is positive.
  - Retail use: tier 2 still reaches the result through the benefit fall-through.
  - Set-aside: three distinct methods.
- Each fall-through equals its baseline. No tier is dead, no two tiers coincide, and no condition restates scope.
- Charter-level structure: **PASS**.

### findings (r3)

- Closed: R2-F-POL-A, R2-F-POL-B, R2-O3, R2-O4, O-8.
- R2-T1-F1 and R2-T1-O4 are judged in `1.md` / `0.md`.
- New latent observations: R3-O1, R3-O2, R3-O3.
- Unchanged: R2-O1, R2-O2, R2-O5, O-3.
- Audit-miss disclosure above.

### closing_checklist (r3)

Written after the round-3 reveal (11:04:54 UTC).

- Per-task files map one to one to `tasks/0.json` and `tasks/1.json`, with revisions 1–3 kept intact.
- Verdicts r3: **task 0 PASS** (no regression from r2); **task 1 PASS** (R2-T1-F1 closed on a rebuilt, charter-consistent world).
- Round-2 items, verified against the artifacts:

| item | status |
| --- | --- |
| R2-T1-F1 | closed |
| R2-F-POL-A | closed (rule aligned to compute) |
| R2-F-POL-B | closed (due-point restatement removed) |
| R2-O3 | closed (second clause declared) |
| R2-O4 | closed |
| O-8 | closed |
| R2-T1-O4 | closed (both tasks' latest loads follow consent) |
| R2-O1, R2-O2, R2-O5, O-3, T1-O2 | unchanged, observations only |

- Reworker's extra changes: the retail-use redefinition in both assistance policies and the task-0 retail seed correction are both verified consistent with the retail charter. They also expose an audit miss in revisions 1–2, disclosed above.
- New observations, none binding on either task: R3-O1 (card + member can exceed the cost share when the member paid more than the deductible), R3-O2 (the retail charter's "may bill" read as "bills"), R3-O3 ("latest such fill of either kind" vs latest of each kind), R3-T1-O1 (persona "running low").
- Scopes are disjoint and jointly complete. uuid8s are independent and unchanged.
- Trees: one prerequisite each, one value_input edge, user-owned roots. The graph is acyclic.
- Each computation has 4–6 real factors with ≥ 2 parameter and ≥ 1 method. Each task has a multi-source and a cross-difficulty factor on seeded, charter-consistent rows. Every factor bears weight against an honest baseline, and the all-baseline figure is definite and differs from gold (task 0: 300.00/0.00; task 1: 550.00/0.00).
- Gates on the final form: the orchestrator's round-3 snapshot is all green (traceability deferred to the render stage), cited rather than re-run by the auditor.
- **Source-layer audit for this difficulty: PASS (policy self-consistency, problem tree, factors and unique solution all PASS for both tasks).**
