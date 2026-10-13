# Policy-task audit — listing_settings_and_compliance / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent Claude agent; did not author these artifacts). Revision 1.
- Freeze time: 2026-10-07T19:17Z. Written before any task's GT was revealed; nothing below derives from a revealed GT.
- Frozen inputs (sha256, re-checked against the brief before reading):
  - `tasks/listing_settings_and_compliance/listing.extended.yaml` e00681406ebb9c07e3d241ce844fa160eb5e6db36bfe2e060bce32d21f96bddd
  - `tasks/listing_settings_and_compliance/task_tools.py` 376399fd621cd414abd095398739f369cb5ad9b87319e1cf080aa2b4f5a4cd75
  - masked views `/tmp/erl45_views/r1/listing_settings_and_compliance/task_0.view.json` 22fb96ea…fd505, `task_1.view.json` 0a383ab0…d87 (match SHA256SUMS).
- Permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/listing.yaml, products/protect.yaml and products/host.yaml for the cross-category parameter values and charters the factors read), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), `erlbench/`, and the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS / within_months / XCOUNT / CPARAM / LATEST / RND) read only to fix what each compute primitive means.
- Masked and unread until both task derivations are frozen: everything in `tasks/listing_settings_and_compliance/tasks/*.json` beyond the views (evaluation_criteria, computations, solvability_contract, prerequisite_closure, charter_scope, required_documents, design_rationale), `worklog.md` of the difficulty and of the scenario, and every other audit directory.
- Entry conditions (Step 0): gate snapshot supplied with commands and last lines — check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding EXTENDED/CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING OK, check_cache_diff INFO, check_cross_fire SCOPE OK, check_traceability NOT OK (declared as expected before KB rendering). Masked views and hashes supplied. Entry conditions met; traceability is not a policy-task gate and is not used here.
- Base-copy check: `diff <(sed -n '1,975p' listing.extended.yaml) blueprint/products/listing.yaml` differs only by one trailing blank line — the base section is a verbatim copy.

### policy_conflict_scan

Six extended policies, all with subject `[listing_pricing_updated, listing_fee_change_logged]`, each computing a different listing field through its own tool:

| policy | trigger | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| listing_ext_pet_fee_ceiling | state_due | pet_fee | reset_pet_fee_f8e15273 (agent) | [] |
| listing_ext_cleaning_fee_ceiling | state_due | cleaning_fee | reset_cleaning_fee_77ae9a3d (agent) | [] |
| listing_ext_short_stay_cleaning_fee | on_request | short_stay_cleaning_fee | save_short_stay_cleaning_fee_f18844b5 (user) | cleaning (value_input), pet (state_gate) |
| listing_ext_minimum_stay_floor | state_due | minimum_nights | raise_minimum_stay_1aeaa300 (agent) | [] |
| listing_ext_extra_guest_fee_ceiling | state_due | extra_guest_fee | reset_extra_guest_fee_9609655d (agent) | [] |
| listing_ext_pricing_assist_rate | on_request | nightly_rate | save_nightly_rate_d0fc8a90 (user) | min-stay (value_input), extra-guest (value_input) |

- Subjects/terminal states: no two policies write the same field; every write is a single-field overwrite plus one `listing_fee_change_logged` row when the value changes (matches base "Every saved change logs one listing_fee_change_logged row per fee or rate that changed").
- Triggers/eligibility/time anchors: every extended quantity is evaluated "on the day of the reset / change / save / request"; MONTHS is whole calendar months with day-of-month borrow, `within_months=k` is `0 <= MONTHS(date, NOW) < k`, which is the rule's "fewer than k whole months before the day of …". No conflicting anchors.
- Cross-category reads: protect (protection_claims, the active plan's level parameters and effective_date) and host (host_accounts tier / superhost_since, host_account_events strikes and Superhost assessments) — read-only; no policy writes another category.
- Reads that cross policies inside this charter:
  - short-stay reads `cleaning_fee` (written by the cleaning policy) — declared edge;
  - pricing reads `minimum_nights` and `extra_guest_fee` — declared edges;
  - pricing also reads `cleaning_fee` (`cleaning_per_night = F('cleaning_fee') / F('minimum_nights')`) and the cleaning policy is state_due, but pricing declares no edge to the cleaning policy and its rule carries no sentence ordering the two. In a world where the cleaning fee stands above its ceiling the suggested rate would have two values (before / after the reset). See finding G-3 (observation: neither task world has its cleaning fee above ceiling on the pricing listing — to be confirmed in task_1.md).
  - extra-guest reads `nightly_rate` (written by the pricing root through the user). The declared order (extra-guest before pricing) fixes the reading; the realism consequence is task-specific (see task_1.md).
  - short-stay ↔ min-stay: no data link, but a min-stay floor above the space type's `short_stay_max_nights` leaves the short-stay fee with no stay it can apply to. This is a semantic conflict only when both are live on one listing; demonstrated per task where it occurs (task_0.md).
- Scope exclusivity (from the views alone, `charter_scope` masked): task 0's request (short-stay fee on one listing) roots the short-stay tree {short-stay, cleaning, pet}; task 1's request (Pricing Assist rate) roots {pricing, min-stay, extra-guest}. The two trees are disjoint and together cover all six extended policies. To be value-checked against `charter_scope` after the reveal.

### rule_compute_equivalence

Checked binding by binding against `compute_basis` and back against the rule text (each `compute_basis` string is a verbatim substring of the policy's rule; verified by reading).

- pet: claim count window/filters (approved, pet_damage, filed_at date, `<12` months) ✓; three-tier claim allowance ✓; sublimit tiers ≤1000 / ≤2500 / else ✓; deductible tiers ≥500 / ≥250 / else ✓; sum ✓; standing: suspension in 12 months → 0, else warning in 3 months → pet_warning_share, else 1 ✓; result `RND(P('pet_fee_max_usd') + total*share, 2)` = "standard ceiling plus the total as its guest standing leaves it, rounded half up to the cent at that final step only" ✓. The rule's suspension window ("within the last twelve months") carries no parenthetical but `COUNT(... within_months=12)` is the same convention used everywhere in the charter ✓.
- cleaning: deep-clean count and verified-loss sum over the same filter ✓; tiers (≥2 or ≥1000) / (==1 and <1000) / none ✓ complete and disjoint; cleaning sublimit ≤500 / ≤1000 / else ✓; Superhost tier ∧ months ≥24 / Superhost ∧ <24 / else ✓ (compute sets months 0 when superhost_since is empty — "fewer whole months back", consistent); tenure ≥36 / ≥12 / else ✓; turnover from the most recent quality assessment's review_count ≥15 / ≥8 / else ✓; passes in 6 months 0 / 1 / else ✓; result ✓.
- short-stay: `regular_cleaning_fee = F('cleaning_fee')` ✓; typical-stay base: ≥10 stays → 0.5 + 0.5·MN(1, max_nights·stays/nights) ✓; 1–9 stays → 0.5 + 0.5·max_nights/weekly_discount_min_nights ✓; "no Superhost assessment" → 0.5 — compute's third branch is `assessed_stays < 1`, which also catches an assessment that counted 0 completed stays; the rule names no tier for that case (finding G-4, observation); damage 12 m / pet 24 m / deep 24 m additions ✓; warning cut 6 m ✓; share capped at 1 ✓; result rounded once ✓.
- min-stay: party strikes 12 m (host-wide XCOUNT) ✓; property damage 12 m ✓; most recent approved safety reinstatement by decided_at, <12 → 2, <24 → 1, else/none → 0 ✓; sum ✓; record: (≥3 assessments in 12 m and all pass) → ceil(n/2); any warning/suspension in 12 m → 2n; else n ✓ (`-((-n)//2)` is ceiling division); result floor + nights ✓. The rule's tie of "minimum_nights_ceiling" is stated but not computed (the result is only a floor; the ceiling never binds in the formula) — the rule makes no promise about capping the floor at the ceiling, so no empty promise.
- extra-guest: per-guest portion = nightly_rate / extra_guest_threshold ✓; damage-loss sum 24 m ≥2500 / >0 / none ✓; per-claim limit ≤5000 / ≤25000 / else ✓; income-loss nights ==0 / ≤14 / else ✓; phase-in by MONTHS(effective_date) <12 / <36 / else ✓; share combined first, applied once, capped at extra_guest_fee_max_usd, rounded once ✓.
- pricing: all-in night = rate + cleaning/min-nights + extra fee × max(0, max_guests − threshold) ✓; rating (avg ≥4.80 ∧ reviews ≥10) / (avg ≥4.80 ∧ reviews <10) / else ✓; demand nights ≥250 / ≥150 / else (incl. no assessment, `or 0`) ✓; Superhost / Starter / else ✓; responsiveness ≥98 / <90 / else (no assessment → −1 → none) ✓; listing age <12 / <24 / else ✓; confidence counts pass+warning+suspension in 24 m, not_assessed excluded, <3 / <6 / else ✓; result clamp to nightly_rate_min/max then round once ✓.
- Rounding: compute's `RND` is Python `round(float, 2)`; the rule says half up. No divergence is known to reach a scored figure; checked per task.

No compute binding invents a basis absent from the rule, and every rule sentence that decides a number is implemented, except the zero-stay gap noted (G-4).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are six distinct pairs, each claimed by exactly one policy ✓.
- Docstrings: each describes one overwrite of one field + one change-log row; none names another tool, none states a position in a sequence, none carries before/after/first. "from then on" refers to new bookings, not to another action ✓. The cleaning docstring's "the short-stay cleaning fee of the listing is left as it stands" and the extra-guest docstring's "the threshold itself is left as it stands" restate their own rule's terminal-state clause, not an order ✓.
- No tool computes, validates or refuses (bodies read: each rounds the argument, finds the listing, overwrites, logs on change) — the tool layer judges no prerequisite ✓.
- uuid8s: f8e15273, 77ae9a3d, f18844b5, 1aeaa300, 9609655d, d0fc8a90 — no shared prefix beyond a single hex digit, no sequence, no common tail; consistent with independent generation ✓.

### prerequisite_graph

- Every extended policy carries `prerequisite` (four `[]`, two with two edges) ✓.
- Edges: short-stay → cleaning (value_input, gate `regular_cleaning_fee`), short-stay → pet (state_gate, gate `listings.pet_fee`), pricing → min-stay (value_input, gate `cleaning_per_night`), pricing → extra-guest (value_input, gate `all_in_night`). All `problem` ids are extended policies of this file, none base, none self; graph acyclic (two stars of depth 1) ✓.
- `policy_source` of each edge is verbatim in the blocked policy's own rule (located by reading: rule sentences 5 and 6 of short-stay; sentences 4 and 5 of pricing) ✓.
- `form: state` on all four, no `fallback_reason` ✓.
- `condition` restates the sentence's state (field at or below / at or above the ceiling / floor "on the day of …") and adds what a reset leaves in the log; neither strengthened nor weakened ✓. No authoring-viewpoint wording ✓.
- `resolved_by` is the depended-on policy's target_tool in all four ✓; each tool's effect sets exactly the field the condition names ✓.
- `kind`: the three value_input gates are real compute bindings of the blocked policy (`regular_cleaning_fee`, `cleaning_per_night`, `all_in_night`) ✓. The state_gate names a field, `listings.pet_fee`; the short-stay policy declares no `eligibility` entry for it — the gate exists only as the rule sentence (observation G-6).

### prerequisite_sentences

1. short-stay ← cleaning: "The short-stay ceiling is fixed only after the regular cleaning fee on the listing stands at or below the listing's cleaning-fee ceiling." Connective "only after" ✓; waited-on state is record-visible (listings.cleaning_fee against the ceiling the cleaning rule defines) ✓; no tool / id / snake_case ✓; strength = condition ✓. Exactly one write of this difficulty sets cleaning_fee (reset_cleaning_fee_77ae9a3d) ✓. Derivation: sentence → "cleaning-fee ceiling" is defined only in listing_ext_cleaning_fee_ceiling's rule → that rule says a fee above the ceiling "is reset to the ceiling exactly" → the reset write. Single reading ✓.
2. short-stay ← pet: "A short-stay cleaning fee is not added to a listing until the pet fee on that listing stands at or below the listing's pet-fee ceiling." "not … until" ✓; state ✓; exactly one write sets pet_fee ✓; "pet-fee ceiling" is defined only in the pet rule ✓. Single reading ✓. (The charter states no business link between a pet fee and a short-stay cleaning fee — see G-5.)
3. pricing ← min-stay: "A suggested nightly rate is not worked out until the minimum stay on the listing stands at or above the listing's minimum-stay floor." ✓ / one write (raise_minimum_stay_1aeaa300) ✓ / "minimum-stay floor" defined only in the min-stay rule ✓.
4. pricing ← extra-guest: "The suggested nightly rate is fixed only after the extra-guest fee on the listing stands at or below the listing's extra-guest ceiling." ✓ / one write ✓ / "extra-guest ceiling" defined only in the extra-guest rule ✓.
- The depended-on rules do not restate any of these sentences ✓; no rule carries a second wording of a dependency, a tool name or another policy id ✓.
- Undeclared cross-problem order: none stated in any rule. Pricing's read of cleaning_fee is an undeclared *data* dependency on a state_due policy with no ordering sentence (G-3).
- Base rules stating cross-problem order: none of the base sentences used grounds an edge ✓.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- listing_evt_fee_settings
  - "The host sets the nightly rate and the per-stay cleaning fee, pet fee and per-night extra-guest fee within the ceilings of the space type: cleaning_fee no higher than cleaning_fee_max_usd, pet_fee no higher than pet_fee_max_usd, extra_guest_fee no higher than extra_guest_fee_max_usd, and extra_guest_threshold no lower than extra_guest_threshold_min; a setting outside its ceiling is not saved." — the three ceiling clauses are each named in the respective policy's `overwrite` (cleaning, pet, extra-guest) ✓; the threshold clause and "not saved" are followed ✓.
  - "A short-stay cleaning fee may be set only where … allowed is true, must not exceed the regular cleaning fee, and replaces the regular cleaning fee on stays of short_stay_max_nights nights or fewer." — "must not exceed the regular cleaning fee" named in short-stay's overwrite ✓; the rest restated ✓ (the replacement keeps share ≤ 1, so it never exceeds anyway).
  - pet-once-per-stay / extra-guest-per-night charging — followed ✓.
  - "A change takes effect for stays booked after …" — followed (docstrings) ✓.
  - "Every saved change logs one listing_fee_change_logged row …; a value saved unchanged logs nothing." — followed ✓.
  - "Minimum stay settings must lie between minimum_nights_floor and minimum_nights_ceiling" — named in min-stay's overwrite ✓.
  - "Instant Book …" — untouched ✓.
  - The base `formula` block (`pet_fee_within_ceiling: pet_fee <= pet_fee_max_usd`, likewise cleaning / extra-guest) and the `parameter_schema` glosses ("highest pet fee (per stay) the host may set", "highest cleaning fee …", "lowest minimum-night setting the host may choose") still describe the static value. They are the same clauses the overwrites name, not separate policy sentences; their reading equals each policy's declared baseline (G-2, observation).
- listing_evt_discounts — no extended policy computes a discount; Pricing Assist reads no discount ✓.
- listing_evt_quality_assessment — extended policies read outcomes and counts of its rows, change nothing ✓.
- listing_evt_safety_standards, listing_evt_reinstatement (min-stay refs) — read only (safety reinstatement age) ✓.
- Pricing Assist `overwrite: []`: base fixes only that the host sets the nightly rate within nightly_rate_min/max (publishing requirements); Pricing Assist suggests, the host saves, clamp kept ✓.
- No disguised override found: no anonymous intermediate replaces a base quantity, no 0/1 multiplier zeroes a base-fixed amount (the 0-share tiers zero an *extended* allowance, not a base amount), no dropped branch.

### factor_ladders

| policy | factor | effect (declared) | tiers | outcome distinct | multi-source (every non-fall-through fork compound) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| pet | pet_damage_claim_allowance | parameter | 3 | 70 / 40 / 0 ✓ | no | protect |
| pet | pet_sublimit_allowance | parameter | 3 | 50 / 25 / 0 ✓ | no | protect |
| pet | pet_deductible_allowance | parameter | 3 | 30 / 15 / 0 ✓ | no | protect |
| pet | pet_allowance_guest_standing | **method** | 3 | share 0 / 0.5 / 1 | no (tier 1 single) | — |
| cleaning | deep_cleaning_allowance | parameter | 3 | 80 / 45 / 0 ✓ | yes (count ∨ loss; count ∧ loss) | protect |
| cleaning | cleaning_sublimit_allowance | parameter | 3 | 40 / 20 / 0 ✓ | no | protect |
| cleaning | superhost_cleaning_allowance | parameter | 3 | 30 / 15 / 0 ✓ | tiers are tier ∧ months; compute's extra `if CFIELD(...)` fork is not compound | host |
| cleaning | listing_tenure_allowance | parameter | 3 | 20 / 10 / 0 ✓ | no | — |
| cleaning | turnover_allowance | parameter | 3 | 15 / 8 / 0 ✓ | no | — |
| cleaning | cleaning_assessment_record | **method** | 3 | share 0 / 0.75 / 1 | no | — |
| short-stay | typical_stay_base | method | 3 | avg-stay ratio / fixed 2/7 / none ✓ | no | host |
| short-stay | damage_addition | parameter | 3 | .10 / .05 / 0 ✓ | no | protect |
| short-stay | pet_turnover_addition | parameter | 3 | .06 / .03 / 0 ✓ | no | protect |
| short-stay | deep_cleaning_turnover_addition | parameter | 3 | .08 / .04 / 0 ✓ | no | protect |
| short-stay | guest_rating_cut | parameter | 3 | .20 / .10 / 0 ✓ | no | — |
| min-stay | party_strike_nights | parameter | 3 | 2 / 1 / 0 ✓ | no | host |
| min-stay | property_damage_nights | parameter | 3 | 2 / 1 / 0 ✓ | no | protect |
| min-stay | safety_reinstatement_nights | parameter | 3 | 2 / 1 / 0 ✓ | no | — |
| min-stay | party_nights_assessment_record | method | 3 | ceil(n/2) / 2n / n | no (tier 2 single) | — |
| extra-guest | damage_loss_addition | parameter | 3 | .15 / .08 / 0 ✓ | no | protect |
| extra-guest | per_claim_limit_addition | parameter | 3 | .10 / .05 / 0 ✓ | no | protect |
| extra-guest | income_loss_addition | parameter | 3 | .06 / .03 / 0 ✓ | no | protect |
| extra-guest | plan_phase_in | **method** | 3 | share 0.5 / 0.75 / 1 | no | protect |
| pricing | rating_adjustment | parameter | 3 | .06 / .03 / 0 ✓ | yes (avg ∧ reviews on both forks) | — |
| pricing | demand_adjustment | parameter | 3 | .05 / .02 / 0 ✓ | no | host |
| pricing | superhost_adjustment | parameter | 3 | .03 / −.03 / 0 ✓ | no | host |
| pricing | responsiveness_adjustment | parameter | 3 | .02 / −.03 / 0 ✓ | no | host |
| pricing | listing_age_adjustment | parameter | 3 | −.04 / −.02 / 0 ✓ | no | — |
| pricing | assessment_confidence | **method** | 3 | share 0.5 / 0.75 / 1 | no | — |

- Counts as declared: pet 4 (3 P + 1 M), cleaning 6 (5 P + 1 M), short-stay 5 (4 P + 1 M), min-stay 4 (3 P + 1 M), extra-guest 4 (3 P + 1 M), pricing 6 (5 P + 1 M). Every ladder has three pairwise-disjoint tiers, every tier is stated in the rule with its condition and value/method, and every tier is a branch of its `decides` binding (checked above). Bindings disjoint; no `decides` is `result`. Every fall-through equals the policy baseline (0 allowance / share 1 / standard share / current rate).
- **Label honesty (finding G-1, SOURCE-FACTOR RED):** four of the six `method` factors select a number, not an algorithm. In each, all three tiers feed the identical formula and differ only in the multiplier:
  - pet: `pet_standing_share: "0 if pet_suspensions_12m >= 1 else (K('pet_warning_share') if pet_warnings_3m >= 1 else 1)"`, `result: "RND(P('pet_fee_max_usd') + pet_allowance_total * pet_standing_share, 2)"`;
  - cleaning: `cleaning_record_share: "0 if passes_6m == 0 else (K('one_pass_share') if passes_6m == 1 else 1)"`, `result: "RND(P('cleaning_fee_max_usd') + cleaning_allowance_total * cleaning_record_share, 2)"`;
  - extra-guest: `plan_phase_share: "K('plan_new_share') if … else (K('plan_mid_share') if … else 1)"`, `extra_guest_share: "K('standard_extra_guest_share') + extra_guest_addition * plan_phase_share"`;
  - pricing: `confidence_share: "K('confidence_low_share') if … else (K('confidence_mid_share') if … else 1)"`, `result: "… current_rate + all_in_night * adjustment_total * confidence_share …"`.
  The rule's own words confirm it: "multiplied by pet_warning_share", "multiplied by one_pass_share", "multiplied by plan_new_share / plan_mid_share", "multiplied by confidence_low_share / confidence_mid_share"; the "withdrawn" tiers are the multiplier 0. The skill's test — "a factor labelled method whose tiers only substitute a different number into the same formula" — is met verbatim. Counting only honest labels, pet, cleaning, extra-guest and pricing each have **0** method factors (bound: ≥1). Short-stay's `typical_stay_base` is honest (tier 1 reads a different base — the account's average stay — tier 2 a fixed 7-night assumption, tier 3 none). Min-stay's `party_nights_assessment_record` is accepted as honest: its first tier adds a rounding rule (half night rounded up) that the others do not have, i.e. a different operation, though the other two tiers are plain ×2 / ×1.
- Multi-source: deep_cleaning_allowance (cleaning) and rating_adjustment (pricing) are the only factors whose every non-fall-through fork is an and/or. Each combines two measures of one evidence set (count and summed loss of the same approved deep_cleaning claims; average and review count of the same latest assessment row). They meet the gate's "distinct evidence" reading; whether that is "distinct records" is recorded as observation G-7.
- Cross-difficulty factors: protect (pet ×3, cleaning ×2, short-stay ×3, min-stay ×1, extra-guest ×4) and host (cleaning ×1, short-stay ×1, min-stay ×1, pricing ×3).
- Reality of conditions and outcomes (industry check): HostCover claim history, sublimits, deductibles, per-claim limit, uncovered income loss, party strikes, safety reinstatements, quality outcomes, listing age, Superhost status and response rate are all things a short-term-rental platform actually weighs for fee latitude, anti-party minimum stays and price suggestions. Two conditions have a weak link to their quantity and are recorded as observations, not demonstrated as RED: `turnover_allowance` (the review count of the last assessment raising a per-stay cleaning-fee ceiling — the cost of one clean does not rise with booking volume) and `plan_phase_in` (how long a HostCover plan has been in force scaling allowances that measure the plan's coverage gaps) — G-8.

### findings

- **G-1 — SOURCE-FACTOR RED (mislabelled method factors).** Symptom: pet_allowance_guest_standing, cleaning_assessment_record, plan_phase_in and assessment_confidence are declared `effect: method` but every tier substitutes a share (0/0.5/1, 0/0.75/1, 0.5/0.75/1, 0.5/0.75/1) into one fixed formula. Root cause: a multiplier ladder labelled as a method. Evidence: compute lines quoted under factor_ladders; rule wording "multiplied by …". Demonstrated consequence: counting honest labels, the pet, cleaning, extra-guest and pricing computations each carry 0 method factors against a floor of 1. Affected: `listing.extended.yaml` → listing_ext_pet_fee_ceiling.factors[3], listing_ext_cleaning_fee_ceiling.factors[5], listing_ext_extra_guest_fee_ceiling.factors[3], listing_ext_pricing_assist_rate.factors[5]. Bears on task 0 (pet, cleaning) and task 1 (extra-guest, pricing).
- **G-2 — observation.** The base `formula` entries and `parameter_schema` glosses still describe `pet_fee_max_usd` / `cleaning_fee_max_usd` as "highest … the host may set" and `minimum_nights_floor` as "lowest … the host may choose". A reader taking them literally lands on each policy's declared baseline (300 / 300 / 1 for the task listings), which the extended rule explicitly supersedes ("On top of the standard … ceiling a listing may carry …"); not a second defensible answer.
- **G-3 — observation.** Pricing Assist reads `cleaning_fee` while the cleaning-fee reset is state_due, with no prerequisite sentence ordering them. Where a pricing listing's cleaning fee stands above its ceiling, two suggested rates are defensible. Demonstrable only in such a world (checked per task).
- **G-4 — observation.** typical_stay_base: the rule states tiers for ≥10 stays, 1–9 stays and "no Superhost assessment"; an assessment counting 0 completed stays falls into compute's third branch with no rule sentence. Not reached by either task world (to be confirmed per task).
- **G-5 — observation (realism).** The pet-fee gate on adding a short-stay cleaning fee has no stated business rationale anywhere in the charter; the base's only compliance rule is per setting ("a setting outside its ceiling is not saved"). The edge is well formed and bears weight as a gate; the dependency is a platform-made coupling of two unrelated fees.
- **G-6 — observation.** The short-stay state_gate's `gate: listings.pet_fee` points at a field, not an `eligibility` entry; the gate exists only as the rule sentence, which is enough for discovery.
- **G-7 — observation.** The two multi-source factors combine two measures of one evidence set rather than two different records.
- **G-8 — observation (realism).** turnover_allowance and plan_phase_in rest on weakly motivated conditions (see factor_ladders).

## closing_checklist

This section was written after both reveals (GT first read 2026-10-07T19:20:55Z). The charter-global sections above were frozen at 19:18:43Z, sha256 d14e5c83abba587b1937ccd2f438db0a6fcb29b05710c1906b4ffd13cf8ad5fb before this append, and are unchanged. The "Freeze time" in their header was an estimate; the file timestamp is the record.

**The difficulty does not close: not every task passes all four relationships.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict line |
| --- | --- | --- | --- | --- | --- |
| task_0 | PASS (G-1 sits under factors) | **SOURCE-CHAIN RED** (T0-6: proof assertion contradicted by the seeded history) | **SOURCE-FACTOR RED** (G-1 on pet and cleaning) | **SOURCE-TASK RED** (T0-1: min-stay floor due on the suite, outside gold) | SOURCE-TASK RED + SOURCE-FACTOR RED + SOURCE-CHAIN RED |
| task_1 | PASS | PASS | **SOURCE-FACTOR RED** (G-1 on extra-guest and pricing) | PASS | SOURCE-FACTOR RED |

- Files: one per task (`task_0.md`, `task_1.md`) plus this file. First revision; there are no older revisions.
- Coverage and scope:
  - charter_scope task 0 = {pet, cleaning, short-stay} with their three tools.
  - charter_scope task 1 = {min-stay, extra-guest, pricing} with their three tools.
  - The two scopes are pairwise disjoint and together cover all six extended policies, matching the pre-reveal inference in §policy_conflict_scan ✓.
  - Task tools and GT are closed, and each uuid8 is independent (§action_binding_and_uuids) ✓.
- Problem trees:
  - Each tree has 2 prerequisite problems and is acyclic.
  - Value_input edges: 1 in task 0, 2 in task 1, so each tree meets max(n−1, 1).
  - Each tree has one owner=user write.
  - The difficulty-wide graph is two disjoint stars, a DAG ✓.
- Factors:
  - Every computation declares 4–6 factors with ladders of three distinct tiers, honest baselines and definite fall-back numbers different from gold. Every declared factor bears weight on its task's world ✓.
  - Four computations have 0 honest `method` factors (G-1) ✗.
  - Each task has one multi-source factor (G-7 caveat) and protect/host cross-difficulty factors whose rows are seeded ✓.
- Charter-global observations reached in the task worlds:
  - G-3 (pricing reads cleaning_fee with no ordering sentence): not reached.
  - G-4 (zero-stay assessment): not reached.
  - G-5 (pet gate realism): reached in task 0.
- Gate re-run on the final form: not performed. The artifacts are unchanged since the coordinator's snapshot, and the difficulty does not close.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit (independent Claude agent). Round 2 started 2026-10-07T21:14:48Z. This section was written before any round-2 GT was read; the real file time is recorded when the section is appended.
- Inputs: `listing.extended.yaml` sha256 e432286d2a1a4548063b629c86f5652b03a4706e9d82be00d2320dd5ff56535a (**changed** from round 1's e0068140…), `task_tools.py` 376399fd… (unchanged), masked views `/tmp/erl45_views/r2/…/task_0.view.json` da4fb423… and `task_1.view.json` ebfd7eb0… (both match the brief). Because the charter hash moved, every charter-global section is re-derived below; nothing is carried forward by reference.
- Base copy: `diff <(sed -n '1,975p' listing.extended.yaml) blueprint/products/listing.yaml` again differs by one trailing blank line only.
- Entry conditions: the round-2 gate snapshot came with the brief (all green, cache-diff INFO, traceability NOT OK, expected). The reworker's claim list was given by item id only; it was not used as evidence.
- Masked until both round-2 task derivations are frozen: everything in `tasks/*.json` beyond the views, both worklogs.

### policy_conflict_scan (revision 2)

What changed in the charter, compared by reading round-1 against round-2 text:

| policy | factors now | method factor now |
| --- | --- | --- |
| pet | pet_claim_lookback (M), pet_damage_claim_allowance, pet_damage_loss_allowance, pet_sublimit_allowance (P×3). Deductible allowance and guest-standing share removed | look-back of 6 / 12 / 24 months chosen by guest reviews counted in the last three months |
| cleaning | deep_cleaning_lookback (M), deep_cleaning_allowance, cleaning_sublimit_allowance, cleaning_deductible_allowance, superhost_cleaning_allowance, listing_tenure_allowance (P×5). Turnover allowance and assessment-record share removed | look-back of 6 months after a warning/suspension in 12 months, 24 months after ≥ 6 all-pass quarters in 24 months, else 12 |
| short-stay | unchanged factor set | typical_stay_base (unchanged) |
| min-stay | unchanged | party_nights_assessment_record (unchanged) |
| extra-guest | damage_lookback_by_party_record (M), damage_loss_addition, per_claim_limit_addition, income_loss_addition (P×3). Plan phase-in removed; standard share 0.75 → 0.70; base refs now include listing_evt_safety_standards | property-damage look-back of 36 / 24 / 12 months by how recently a party_violation strike was recorded |
| pricing | expected_stay_length (M), rating, demand, Superhost, responsiveness, listing age (P×5). Assessment-confidence share removed; adjustment values lowered | the cleaning fee is spread over min stay, the mean of min stay and the account's average stay, or the mean of min stay and 7 nights |

Other changes:
- short-stay: damage addition window 12 → 24 months; a rationale sentence was added ("The short-stay cleaning fee exists to keep one- and two-night stays affordable, and a short-stay guest who brings a pet pays the pet fee on the same stay, so the per-stay fees of a listing are judged together."); the zero-stay case is now stated.
- pricing: the rating adjustment now reads the assessment of the last three months ("at most one").

Conflict scan:
- Subjects, terminal states and target fields are unchanged; still one field per policy.
- Time anchors are unchanged ("on the day of …").
- Cross-category reads are read-only. Extra-guest now also reads host strikes.
- Cross-policy data reads:
  - pricing → cleaning_fee: still no edge (G-3 unchanged, observation).
  - pricing → minimum_nights: the declared edge holds; minimum_nights still enters every tier of expected_stay_nights.
- Scope inference from the views: task 0 roots short-stay {short-stay, cleaning, pet}; task 1 roots pricing {pricing, min-stay, extra-guest}. Disjoint, and together they cover all six policies.

### rule_compute_equivalence (revision 2)

Binding by binding (every `compute_basis` string is a verbatim substring of its rule; checked by reading):

- pet:
  - `pet_recent_reviews` = SUM(review_count, 3 months, quality rows) ✓.
  - Look-back ladder ≥ 15 → 6 / < 5 → 24 / else 12 ✓.
  - Count and loss over the same filter and window ✓.
  - Claim tiers 50 / 20 / 0 ✓; loss tiers ≥ 1500 → 30, > 0 → 10, else 0 ✓; sublimit tiers ✓.
  - Result = standard + three allowances, rounded once ✓.
  - `within_months=pet_lookback_months` uses the same "fewer than N whole months" convention ✓.
- cleaning:
  - Tier precedence: troubled first, then clean record, then standard. The tiers are disjoint, since all-pass in 24 months excludes a warning in 12 ✓.
  - `quarters_24m` counts not_assessed rows too, which matches "every one of them has outcome pass" ✓.
  - Deductible tiers ≥ 500 / ≥ 250 / else ✓.
  - Result sums five allowances ✓.
- short-stay: `property_damage_24m` matches the rule's new 24-month window ✓. Base share third branch `assessed_stays < 1` now has the rule sentence "or the most recent one counted no completed stays" ✓ (closes G-4).
- extra-guest: strike tiers 12 → 36, (none in 12 but ≥ 1 in 24) → 24, else 12 ✓. The compute's second test `party_strikes_24m >= 1` is reached only when `party_strikes_12m == 0`, so it equals the rule's "at least twelve and fewer than twenty-four" ✓. Share = 0.70 + additions, applied once, capped, rounded once ✓.
- pricing:
  - `expected_stay_nights` tiers match ✓ (zero-stay case stated).
  - `cleaning_per_night = cleaning_fee / expected_stay_nights` ✓.
  - Rating reads SUM over the 3-month window. With quarterly runs on the 1st of Jan/Apr/Jul/Oct, `MONTHS < 3` holds for at most one row on any day, so SUM equals that row's value; a not_assessed row carries average 0 and falls to "otherwise" ✓.
  - Result has no confidence factor ✓.
- min-stay: unchanged text and compute (re-read) ✓.
- No compute basis is invented, and no rule sentence is left without an implementation.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged (same hash), so this section carries forward on that hash. Six distinct `(target_tool, computes)` pairs are unchanged in the charter. Docstrings, uuid8s and non-judging tool bodies are as in round 1 ✓.

### prerequisite_graph and prerequisite_sentences (revision 2)

- The four edges are unchanged in `problem`, `kind`, `gate`, `form`, `policy_source`, `condition` and `resolved_by`.
- The min-stay edge's `effect` was reworded for the expected stay length; it is still true, since minimum_nights enters every tier.
- `gate: cleaning_per_night` still names a compute binding ✓.
- Each `policy_source` is still verbatim in its own rule ✓.
- The graph is acyclic ✓.
- The new short-stay sentence "… so the per-stay fees of a listing are judged together" carries no ordering connective and names no tool or policy. It gives the business reason for the pet gate, and does not reword it as a second dependency ✓.
- No other rule gained a cross-problem order.
- G-6 is unchanged (observation).

### override_declarations (revision 2)

- The overwrite entries are unchanged, and each still names the clause it replaces.
- The new allowances and look-back ladders operate only on the extended ceilings and floor. No base sentence is newly contradicted:
  - the cleaning deductible allowance reads the protect deductible without changing it;
  - extra-guest's new base ref listing_evt_safety_standards is read-only (party ban rationale).
- G-2 is unchanged (observation).

### factor_ladders (revision 2)

| policy | factor | label | honest? | tiers distinct | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| pet | pet_claim_lookback | method | ✓ window 6 / 24 / 12 (a different evidence window, not a number in one formula) | ✓ | no | — |
| pet | pet_damage_claim_allowance | parameter | ✓ | 50 / 20 / 0 | no | protect |
| pet | pet_damage_loss_allowance | parameter | ✓ | 30 / 10 / 0 | no | protect |
| pet | pet_sublimit_allowance | parameter | ✓ | 25 / 10 / 0 | no | protect |
| cleaning | deep_cleaning_lookback | method | ✓ window 6 / 24 / 12 | ✓ | no (tier 1 single) | — |
| cleaning | deep_cleaning_allowance | parameter | ✓ | 60 / 30 / 0 | **yes** | protect |
| cleaning | cleaning_sublimit_allowance | parameter | ✓ | 20 / 10 / 0 | no | protect |
| cleaning | cleaning_deductible_allowance | parameter | ✓ | 20 / 10 / 0 | no | protect |
| cleaning | superhost_cleaning_allowance | parameter | ✓ | 20 / 10 / 0 | (tier ∧ months) | host |
| cleaning | listing_tenure_allowance | parameter | ✓ | 15 / 8 / 0 | no | — |
| short-stay | (unchanged five; damage window now 24 months) | 1 M + 4 P | ✓ | ✓ | no | host, protect |
| min-stay | (unchanged four) | 1 M + 3 P | ✓ | ✓ | no | host, protect |
| extra-guest | damage_lookback_by_party_record | method | ✓ window 36 / 24 / 12 | ✓ | no | host |
| extra-guest | damage_loss_addition / per_claim_limit_addition / income_loss_addition | parameter | ✓ | .15/.08/0, .10/.05/0, .06/.03/0 | no | protect |
| pricing | expected_stay_length | method | ✓ base of the spread changes (min stay / mean with the account's average stay / mean with 7) | ✓ | no | host |
| pricing | rating / demand / superhost / responsiveness / listing age | parameter | ✓ | .04/.02/0, .04/.02/0, .02/−.02/0, .01/−.02/0, −.03/−.02/0 | rating **yes** | host ×3 |

- Counts: pet 4 (1 M, 3 P), cleaning 6 (1 M, 5 P), short-stay 5 (1 M, 4 P), min-stay 4 (1 M, 3 P), extra-guest 4 (1 M, 3 P), pricing 6 (1 M, 5 P). Every computation has an honest method factor and ≥ 2 parameter factors, within 4–6 ✓.
- Every ladder has 3 disjoint tiers stated in the rule and implemented as compute branches ✓. Fall-throughs equal the baseline (standard look-back, 0, min stay) ✓.
- Industry reality of the new conditions:
  - Choosing the claims look-back by booking volume (a busy listing's recent claims suffice) is a plausible actuarial-style rule.
  - Lengthening the property-damage look-back after a party strike is plausible.
  - Spreading the cleaning fee over an expected stay derived from the host's booking record is how all-in nightly pricing is usually estimated.
  - Crediting a cleaning deductible the host bears on every deep-clean claim is plausible.
  - Shortening the deep-cleaning look-back after a quality warning is a weaker motive ("only the deep-cleaning costs of the period the guests' complaints describe are credited"), but it is a coherent penalty-style rule. Recorded as observation R2-G-a, not demonstrated as RED.
- Multi-source: deep_cleaning_allowance (task 0) and rating_adjustment (task 1) remain the multi-source factors. Each still combines two measures of one evidence set (G-7 unchanged, observation).

### findings (revision 2, charter-global, pre-reveal)

- **G-1 — closed.** All four formerly mislabelled method factors were removed. Each of the four affected computations now carries a look-back-window or base-of-spread method factor that changes which evidence or which base is used, not a multiplier.
- **G-4 — closed.** The zero-stay case is stated in both the short-stay and the pricing rules.
- **G-5 — closed as an observation.** The rule now states the business link between the pet fee and the short-stay fee. The edge form is unchanged.
- **G-8 — closed.** turnover_allowance and plan_phase_in were removed. The new conditions are judged above; R2-G-a is the only residual observation.
- **G-2, G-3, G-6, G-7 — unchanged observations**, as claimed.
- No new charter-global RED was found.

### closing_checklist (revision 2)

Written after both round-2 reveals (first GT read 2026-10-07T21:19:30Z). The revision_2 charter-global sections above were on disk at 21:18:06Z and are unchanged.

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| task_0 | PASS | PASS | PASS | PASS | **PASS** |
| task_1 | PASS | PASS | PASS | PASS | **PASS** |

- Files: one per task plus this file. Round-1 text is preserved verbatim above each `## revision_2`. Every revision_2 comparison section carries a PASS.
- Scope (revealed charter_scope):
  - task 0 = {pet, cleaning, short-stay};
  - task 1 = {min-stay, extra-guest, pricing};
  - the two scopes are disjoint and jointly cover all six extended policies.
  - Six task tools, each with an independent frozen uuid8; tools and GT are closed.
- Trees: each has 2 prerequisite problems, ≥ 1 value_input edge (task 0: 1; task 1: 2), an owner=user root, and no cycle. The difficulty-wide graph is two disjoint stars (a DAG).
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors with ≥ 2 parameter and 1 honest method factor, each ladder three distinct tiers stated in its rule.
  - Every factor bears weight on its task's world, and the all-baseline figures differ from gold (300 / 300 / 192.50; 1 / 46.08 / 395.00).
  - Each task has one multi-source factor (G-7 caveat) and seeded cross-difficulty factors (protect, host).
- Round-1 REDs: G-1, T0-1, T0-2, T0-6 and T1-1 are genuinely closed. No regression was found and no new red light. Remaining observations: G-2, G-3, G-6, G-7, R2-G-a, T0-3, T0-4 (residual), T1-3, T1-4, T1-5.
- Gates on the final form: the coordinator's round-2 snapshot (`/tmp/erl45_views/r2/listing_settings_and_compliance/gate_snapshot.txt`) was run on these hashes (charter e432286d…, tools 376399fd…): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK (pending KB render, outside this audit).
- The difficulty passes the source-layer policy-task audit at revision 2.
