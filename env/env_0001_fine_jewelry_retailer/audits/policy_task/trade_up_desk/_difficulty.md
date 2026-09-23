# Policy-task audit — trade_up_desk / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (erl-task-policy-audit), single pass over the whole difficulty
- freeze time (this section written before any task's GT was revealed): 2026-09-17
- artefacts and freeze hashes (sha256, first 16 hex):
  - `env/env_0001_fine_jewelry_retailer/tasks/trade_up_desk/tradein.extended.yaml` — `8b59d76a9166cea9` (181710 bytes)
  - `env/env_0001_fine_jewelry_retailer/tasks/trade_up_desk/task_tools.py` — `0f1ff84b7f10d684` (20598 bytes)
  - masked task views: `masked/trade_up_desk/0.json` — `5a7342c8f04c88cc`; `masked/trade_up_desk/1.json` — `7ddfab0197a67755`
- fields permitted while this section was written: the whole of `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/tradein.yaml and the cross-read products appraisal/protection/circle), the whole of `tradein.extended.yaml`, the whole of `task_tools.py`, and per task only `frozen_time`, `user_scenario`, `initial_state`
- fields explicitly masked and not read while this section was written: `design_rationale`, `db_closure`, `db_closure_matches_initial_state`, `solvability_contract`, `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`
- entry conditions (Step 0): the coordinator supplied the masked views with their hashes (both verified above by `sha256sum`) and the actual output lines of the instantiation gate block re-run from the repo root — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, with `check_traceability` excluded because the KB is not yet published. Entry conditions are complete; the gates were not re-run by the auditor. A green gate block is the qualification to enter this audit, not evidence that the policy is self-consistent.

### policy_conflict_scan

The structured policy in force for `tradein` in this difficulty is the base section of `tradein.extended.yaml` (9 policies) plus 6 `extended_policies`. The base section was compared key by key against `blueprint/products/tradein.yaml`: `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures` and `policies` are **byte-identical after canonical JSON serialisation** — the base copy has not been rewritten.

Overlapping subjects across the 6 extended policies:

| policy | subject (base event) | computes | target_tool |
| --- | --- | --- | --- |
| tradein_ext_credit_revaluation | tradein_credit_revaluation_applied | revaluation_amount | apply_credit_revaluation_37908854 |
| tradein_ext_upgrade_minimum_spend | tradein_registration_updated | upgrade_minimum_spend | update_upgrade_minimum_spend_70148cfb |
| tradein_ext_credit_redemption | tradein_credit_redeemed, tradein_credit_partially_spent | credit_applied_amount | spend_upgrade_credit_c2e2bb76 |
| tradein_ext_item_valuation | tradein_item_valuation_logged | valuation_amount | log_item_valuation_6ae79dd2 |
| tradein_ext_custody_declaration | tradein_registration_updated | declared_custody_value | confirm_custody_declaration_bb764f94 |
| tradein_ext_credit_issue | tradein_credit_issued | issued_credit_amount | issue_upgrade_credit_f63e5226 |

`tradein_registration_updated` is subject to two policies, but they settle different quantities on different tools (`upgrade_minimum_spend` on the registration's printed minimum; `declared_custody_value` on the desk's request record), so no quantity is claimed twice. Triggers: `state_due` on four policies, `on_request` on `tradein_ext_credit_redemption` and `tradein_ext_credit_issue` — consistent with the base lifecycle, whose `credit_issued -> partially_redeemed` transition is `by: user` and whose `appraisal_pending -> credit_issued` is `by: agent`.

Eligibility and time anchors: every extended policy inherits, unaltered, the base state gates it sits under (`tradein_credit_grant.grantable_state` = credit_issued/partially_redeemed for the revaluation; `tradein_redemption.spendable_state` = credit_issued/partially_redeemed for the spend; `tradein_condition_grading.inspectable_state` and `tradein_valuation.valuation_state` = registered/appraisal_pending/credit_issued for the valuation). No extended rule weakens any of them and no task tool enforces any of them (see `action_binding_and_uuids`). All time anchors run off `frozen_time` against a dated field on a seeded row (`issued_date`, `original_purchase_date`, `posted_date`, `issued_date` on the appraisal order); no policy anchors on a future date, an external approval or a batch.

Cross-category read boundaries: the declared `cross_category` lists (protection, appraisal, circle) agree item by item with the `EXISTS`/`CFIELD`/`XCOUNT`/`XMAX`/`XLATEST`/`XSUM` calls in each `compute` and with `inputs.cross_category`. Every read is read-only; no task tool writes a row in another category, and no tool writes a `tradein_ledger` field combination that fires one of the base `triggers` into `appraisal:` (only `tradein_valuation_requested` carries such a trigger, and no task tool emits that event type).

Terminal states: `issue_upgrade_credit_f63e5226` lands `credit_issued`; `spend_upgrade_credit_c2e2bb76` lands `partially_redeemed` or `redeemed` by the sign of what is left; `apply_credit_revaluation_37908854`, `update_upgrade_minimum_spend_70148cfb`, `log_item_valuation_6ae79dd2` and `confirm_custody_declaration_bb764f94` move no lifecycle state. All four agree with `lifecycle.transitions`.

Claimed scopes of the two tasks (derived from the `prerequisite` graph alone, before any reveal): the graph has exactly two weakly connected components —
- **A** `tradein_ext_credit_redemption -> tradein_ext_upgrade_minimum_spend -> tradein_ext_credit_revaluation`
- **B** `tradein_ext_credit_issue -> {tradein_ext_item_valuation, tradein_ext_custody_declaration}`

Component A matches the world and persona of task 0 (a Bridal registration standing at `partially_redeemed` with a credit to put on a sale), component B those of task 1 (a Lifetime registration standing at `appraisal_pending` with no credit yet). The two components are **pairwise disjoint** (no policy appears in both) and **jointly complete** (6 of 6 extended policies are covered). No conflict was found that would let a policy of one task's scope decide a quantity of the other's.

### rule_compute_equivalence

Each policy's `compute_basis` was swept binding by binding against its own `rule`, and each `rule` swept back against `compute`. Quantities, windows, filters, tiers, branches, cross-category reads, acting bases, grouping of operations, caps/floors, rounding mode and rounding point are covered in both directions in every policy **except for the two divergences recorded as F-1 and F-2 in `findings`**, and the mis-mapping recorded as F-3.

Points confirmed lossless in both directions (spot list, not exhaustive):
- rounding point: every policy's `rule` fixes the rounding order explicitly ("the result is rounded to two decimal places at that final step only" vs "each of those steps is rounded to two decimal places as it is taken") and `compute` implements exactly that — `tradein_ext_item_valuation` and `tradein_ext_custody_declaration` round at every step (`after_grade`, `after_certificate`, `with_premium`, `after_upkeep`; `subtotal`, `with_margin`), the other four round once at `result` (with the one declared per-leg rounding in `tradein_ext_upgrade_minimum_spend`: `credit_leg` and `uplift_leg` are each rounded, as the rule says "rounded to two decimal places" of each leg).
- floors/ceilings: `MX(0.0, ...)` in `tradein_ext_credit_revaluation` and `tradein_ext_credit_redemption` matches "where the figure comes out at or below nothing, no increase is booked"/"the figure is not taken below nothing"; `MN(...)` against `P('maximum_credit_amount')`, `valuation_ceiling`, `custody_ceiling`, `credit_ceiling` each matches a named ceiling sentence.
- interval counting: `DAYS(anchor, NOW)` is whole calendar days from the anchor day, matching base `tradein_registration_eligibility.temporal_basis.counting_rule` and `tradein_credit_grant.temporal_basis.counting_rule`; `MONTHS` is used only where the rule says "months".
- every `K(...)` constant named in a rule is spelled out in words in that rule ("seventy percent", "sixty-seven and a half percent", "a tenth", "two fifths", "five hundred", "fifteen hundred", "eight percent", "three percent", "nine tenths", "nineteen twentieths", "fifteen thousand", "fifty thousand", "twenty thousand", "sixty thousand", "four hundred", "one hundred and fifty", "eighty-five percent", "seventy-eight percent"), so no tier lives only in `compute`.

Paraphrase between a `factors[].ladder` entry and the `rule` sentence it names (e.g. rule "where the customer has owned it for less than five years and the chain sold it" vs ladder "the customer has owned the piece for less than five years and the chain sold it") is present throughout and is **not** recorded as a defect: the substance, the condition and the outcome are the same in both faces. Only divergences of substance are recorded below.

### action_binding_and_uuids

`(target_tool, computes)` pairs: six policies, six distinct tools, six distinct computed quantities — **no pair is claimed twice** (table in `policy_conflict_scan`). Each policy's subject, base refs, target tool, docstring and terminal state admit one business reading.

uuid8 tails: `37908854`, `70148cfb`, `c2e2bb76`, `6ae79dd2`, `f63e5226`, `bb764f94`. All six are distinct, share no common prefix, are not a sequence, are not adjacent values and are not one tail with a changed last character. Each is frozen with its function and appears nowhere else in the module.

Tool bodies (`task_tools.py`, all six read in full): each function is `ctx.find("tradein_credits", credit_reference=...)` followed by `ctx.create` and/or `ctx.update`. **No function inspects `status`, aggregates history, compares a date, or refuses a call on a policy ground** — the only error path is "no trade-in registration <ref>". In particular `issue_upgrade_credit_f63e5226` sets `status="credit_issued"` with no check that the registration stands at `appraisal_pending`, and `apply_credit_revaluation_37908854` books an entry with no check on the revaluation window. The tool layer therefore judges no prerequisite and no eligibility; that decision stays with the agent, as it must.

Docstrings: none names another tool, none states its own position in a sequence relative to another write. Observation O-1 below records the residual "before calling"/"before handing this over" phrasing in the `Args` blocks.

### prerequisite_graph

| blocked policy | depends on | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| tradein_ext_upgrade_minimum_spend | tradein_ext_credit_revaluation | value_input | `standing_all` | state | apply_credit_revaluation_37908854 | yes |
| tradein_ext_credit_redemption | tradein_ext_upgrade_minimum_spend | value_input | `excess_spend` | state | update_upgrade_minimum_spend_70148cfb | yes |
| tradein_ext_credit_issue | tradein_ext_item_valuation | value_input | `entries_valuation` | state | log_item_valuation_6ae79dd2 | yes |
| tradein_ext_credit_issue | tradein_ext_custody_declaration | value_input | `credit_ceiling` | state | confirm_custody_declaration_bb764f94 | yes |

- `prerequisite` is filled in on all six policies (`[]` on `tradein_ext_credit_revaluation`, `tradein_ext_item_valuation`, `tradein_ext_custody_declaration`).
- Every `problem` names another **extended** policy id present in this file; none names a base policy and none names itself.
- The whole graph is a DAG: two disjoint components, A a path of length 2, B a fan-in of two leaves; no back edge, no cycle across tasks.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (checked character by character against the rule strings).
- `form` is `state` on all four edges; no edge is action-form, so no `fallback_reason` is required and none is present — correct.
- `condition` on each edge restates the state the sentence names at the same strength: "the registration's entries carry every upward revaluation the current appraised value supports while the programme's revaluation window is still open"; "the registration's recorded least the customer must spend answers to the credit the registration's entries now carry"; "the registration's entries carry the appraiser's valuation of the traded piece"; "the upgrade desk's request record for the registration carries a declaration of the value the piece was taken in at that the customer has confirmed". None is quietly strengthened or narrowed relative to its sentence.
- `resolved_by` is in every case the depended-on policy's own `target_tool`, and each genuinely changes the binding named in `gate`: `apply_credit_revaluation_37908854` adds a `tradein_credit_revaluation_applied` row, which is one of the four event types `standing_all` sums; `update_upgrade_minimum_spend_70148cfb` writes `tradein_credits.upgrade_minimum_spend`, which `excess_spend` reads as `F('upgrade_minimum_spend')`; `log_item_valuation_6ae79dd2` adds a `tradein_item_valuation_logged` row, which `entries_valuation` counts and maxes; `confirm_custody_declaration_bb764f94` creates a `tradein_intake` row at `request_status='customer_confirmed'`, which `credit_ceiling` reads through `LATEST('tradein_intake','requested_amount', request_status='customer_confirmed')`.
- `kind` is `value_input` on all four and each `gate` names a binding that genuinely exists in the blocked policy's `compute` (`standing_all`, `excess_spend`, `entries_valuation`, `credit_ceiling` — all present). No edge is a `state_gate`, so no eligibility gate has to be found for one.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in any `prerequisite` block.

### prerequisite_sentences

Four-point test, edge by edge.

1. **tradein_ext_upgrade_minimum_spend -> tradein_ext_credit_revaluation.** Sentence (2nd of its own rule): *"The least the customer must spend is fixed only after the registration's entries carry every upward revaluation of the credit that the programme's window still admits."* — (a) ordering connective "only after" joining this policy's own result ("the least the customer must spend is fixed") to what it waits on; (b) what it waits on is a record-visible state in table words ("the registration's entries carry ... revaluation"), no performer, no action verb of another desk — **state form**, correctly declared; (c) names no tool, no policy id, no snake_case token, no row id; (d) scope matches the edge's `condition`. Exactly one write of this difficulty brings that state about: `apply_credit_revaluation_37908854` is the only tool in the module that creates a `tradein_credit_revaluation_applied` row, and `tradein_ext_credit_revaluation` is the only policy whose subject is that event. Derivation with one reading: entries carrying an upward revaluation → the only rule describing such an entry is `tradein_ext_credit_revaluation` ("the increase is booked as its own entry", inherited from base `tradein_credit_grant`) → its `target_tool`. The blocked rule carries nothing else about the dependency, and `tradein_ext_credit_revaluation`'s own rule does not restate the sentence.
2. **tradein_ext_credit_redemption -> tradein_ext_upgrade_minimum_spend.** Sentence (1st of its own rule): *"Credit is applied to a sale only after the registration carries the least the customer must spend worked out against the credit as it now stands."* — same four points; "the least the customer must spend" is the words the registration's own field carries (`tradein_credits.upgrade_minimum_spend`, schema meaning "the least the customer must spend on the new piece"). Single write: `update_upgrade_minimum_spend_70148cfb` is the only tool that writes that field.
3. **tradein_ext_credit_issue -> tradein_ext_item_valuation.** Sentence: *"The credit issued is fixed only after the registration's entries carry the appraiser's valuation of the traded piece."* — state form, ordering connective "only after", record-visible. Single write: `log_item_valuation_6ae79dd2` is the only tool creating `tradein_item_valuation_logged`.
4. **tradein_ext_credit_issue -> tradein_ext_custody_declaration.** Sentence: *"The credit is issued only once the upgrade desk's request record carries the customer's own confirmed declaration of the value the piece was taken in at."* — state form, "only once", record-visible (`tradein_intake.request_status = customer_confirmed`, `requested_amount`). Single write: `confirm_custody_declaration_bb764f94` is the only tool creating a `tradein_intake` row.

No prerequisite sentence appears in the **depended-on** policy's rule. No rule states a cross-problem order that grounds no declared edge, with the two qualifications recorded as O-2 and O-3 below.

### override_declarations

Sentence-by-sentence sweep of each extended policy against every entry of its `base_policy_refs`. Declared overrides:

- `tradein_ext_upgrade_minimum_spend` declares one, naming `tradein_redemption`'s clause *"Credit is spent only against a new piece costing at least the programme's multiple of the credit, and on the programmes that also require an uplift, at least that much more than the piece traded originally sold for."* and replacing it with the credit-leg + uplift-leg − already-met construction. The named clause is verbatim in base and the replacement is verbatim in the extended rule. **Legal.** See O-4 for the base `formula` block that implements the same clause.
- `tradein_ext_item_valuation` declares two, naming `tradein_condition_grading`'s *"The valuation is reduced by the programme's deduction for the grade the piece was found at, and where the deduction is the whole of the valuation no credit is issued."* and `tradein_valuation`'s *"Where no accepted certificate is presented the valuation is reduced by the programme's missing-certificate deduction, and on the programmes where that deduction is the whole of the valuation the piece is refused rather than valued down to nothing."* Both are verbatim in base; both replacements are verbatim in the extended rule. **Legal.** The desk's own 6%/20% grade ladder replaces the per-programme `condition_deduction_pct_by_grade` table; this is exactly what the first declaration says it does.
- `tradein_ext_credit_issue` declares one, naming `tradein_valuation`'s *"On the programmes that guarantee the original price, the credit is that share of the price the piece originally sold for; on the programmes that value at market, it is that share of the current appraised value."* **Legal.**
- `tradein_ext_credit_revaluation`, `tradein_ext_credit_redemption` and `tradein_ext_custody_declaration` declare `overwrite: []`.

Sentence-by-sentence conclusions on the three `overwrite: []` policies:
- **tradein_ext_credit_revaluation vs tradein_credit_grant** — every sentence followed. Booking once against its own registration, the credit_issued/partially_redeemed state gate, the revaluation window counted from the issue day, "the increase is booked as its own entry", "a credit is never revalued downward" (the `MX(0.0, ...)` floor). No conflict.
- **tradein_ext_credit_revaluation vs tradein_valuation** — recorded as O-5: the extended rule settles the credit the traded piece "now supports" on `credit_pct_of_current_appraisal` taken on the original purchase price, while base's basis sentence, read on a programme whose `valuation_basis` is `original_purchase_price`, would put that figure at `credit_pct_of_original_price` of the original price. Base's sentence is scoped to `tradein_item_valuation_logged`/`tradein_credit_issued`, not to a revaluation entry, so this is recorded as an observation rather than an undeclared override; the numbers are given in `0.md`.
- **tradein_ext_credit_redemption vs tradein_redemption and tradein_agg_credit_stacking** — every base sentence followed. Notably `tradein_agg_credit_stacking`'s *"the remaining credit is the credit issued less that sum plus any revaluation"* agrees exactly with the extended `movements_all` reading, and *"no more of them may be spent on one sale than the programme allows"* and *"each credit is spent from its own registration"* are respected (the `SUM`/`COUNT` aggregates are scoped to one `tradein_credit_id`). No conflict.
- **tradein_ext_custody_declaration vs tradein_registration_eligibility and tradein_estate_purchase** — neither base policy fixes a declared custody value; base only supplies `custody_insurance_cap`, which the extended rule uses as one tier of its ceiling. No conflict.

Inherited base provisions that no `overwrite` touches, checked as still holding: the state gates listed in `policy_conflict_scan`; `tradein_registration_eligibility`'s minimum holding period and proof-of-ownership; `tradein_agg_multi_holding`'s dedup on live registrations; `tradein_expiry_and_forfeit`'s closed set of forfeit grounds; `tradein_valuation`'s "the credit issued is capped at the programme's ceiling" (the extended ceilings are never looser than it). One inherited provision is recorded as O-6.

### factor_ladders

Structure only; whether a factor bears weight is a fact about one world and lives in that task's `factor_weight`.

| policy | factors | parameter | method | ladders >= 3 tiers | multi-source factors (tiers conjoin conditions over distinct records) | cross_difficulty factors (category) |
| --- | --- | --- | --- | --- | --- | --- |
| tradein_ext_credit_revaluation | 5 | 3 | 2 | 5/5 | `upkeep_certified_share` (registration + protection_ledger), `supporting_value_basis` (appraisal_orders + appraisal_ledger + registration) | `upkeep_certified_share` (protection), `supporting_value_basis` (appraisal), `appraisal_fee_offset` (appraisal) |
| tradein_ext_upgrade_minimum_spend | 5 | 3 | 2 | 5/5 | `gain_measured_from` (tradein_ledger + registration), `already_met_share` (tradein_ledger + registration) | `membership_upgrade_multiple` (circle) |
| tradein_ext_credit_redemption | 6 | 3 | 3 | 6/6 | `above_minimum_release` (registration/ledger + protection_plans), `return_window_holdback` (registration + tradein_ledger), `new_piece_price_reading` (circle_ledger + protection_plans) | `single_sale_share` (circle), `above_minimum_release` (protection), `new_piece_price_reading` (circle) |
| tradein_ext_item_valuation | 6 | 4 | 2 | 6/6 | `stone_weight_premium` (registration + appraisal_orders), `certificate_confirmation_deduction` (registration + appraisal_orders), `recorded_grade_deduction` (tradein_ledger count + tradein_ledger grade) | `valuation_resting_figure` (appraisal), `certificate_confirmation_deduction` (appraisal), `stone_weight_premium` (appraisal), `upkeep_treatment` (protection) |
| tradein_ext_custody_declaration | 4 | 3 | 1 | 4/4 | `custody_ceiling_held_to` (protection_plans + registration), `declaration_resting_figure` (appraisal_orders + appraisal_ledger) | `declaration_resting_figure` (appraisal), `standing_addition` (circle), `custody_ceiling_held_to` (protection) |
| tradein_ext_credit_issue | 5 | 3 | 2 | 5/5 | `loyal_holder_share` (circle_memberships + registration) | `loyal_holder_share` (circle), `appraisal_fee_addition` (appraisal), `cover_addition` (protection) |

Per-policy floors (4–6 factors, >= 2 `parameter`, >= 1 `method`) are met by the labels as declared. Per-task floors (>= 1 multi-source, >= 1 cross-difficulty over the task's computations): **component A** has `upkeep_certified_share` and `above_minimum_release` multi-source and cross-difficulty reads into protection, appraisal and circle; **component B** has `stone_weight_premium`, `certificate_confirmation_deduction` and `loyal_holder_share` multi-source and cross-difficulty reads into appraisal, protection and circle. Both floors are met.

Binding disjointness: within each policy no two factors share a `decides` binding, and the `bindings` sets are pairwise disjoint apart from the shared intermediate they each own. Every `decides` is an input to `result`, never `result` itself. Every ladder has exactly three tiers, the fall-through counted, and within a ladder the tiers are pairwise disjoint as stated (each pair is separated by a predicate that cannot hold simultaneously: a count `>= k` against `< k`, a date `<=` against `>`, an equality against its negation, a boolean against its complement).

Findings on this section (details in `findings`): **F-4** (`tradein_ext_item_valuation.upkeep_treatment` labelled `method` but its tiers only substitute a multiplier), **F-5** (`tradein_ext_credit_issue.credit_ceiling_held_to` labelled `method` but its tiers only substitute a ceiling number), **F-6** (`tradein_ext_credit_issue.valuation_the_credit_rests_on`: tiers 1 and 2 select the same value on every world where tier 2 applies, and its declared `baseline` is not what `baseline.rule` states for that input). Charter-wide tier-collapse risks that do not bite on either task's programme are recorded as O-7.

Every declared `baseline.rule` was checked sentence by sentence against its policy's `rule`: all six are verbatim-locatable there, and in five of the six every factor's fall-through tier is exactly the sentence the baseline retains. The sixth (`tradein_ext_credit_issue`) is F-6.

### findings

Charter-global findings. Each names the tasks it bears on; the demonstration of what it costs a task lives in that task's file.

---

**F-1 — SOURCE-POLICY RED. The rule and the compute disagree on which entries "every entry booked to the registration" means, and the rule's reading is the wider one.** Bears on: **task 0** (all three of its policies; demonstrated there). Not in task 1's scope.

- *Symptom.* Three policies state a tier whose method is "the sum of **every entry booked to the registration**, spends included". `compute` implements a sum restricted to four event types (`tradein_credit_granted`, `tradein_credit_revaluation_applied`, `tradein_credit_redeemed`, `tradein_credit_forfeited`), excluding `tradein_item_valuation_logged` and `tradein_condition_inspection_logged`, which are also entries booked to the registration and one of which carries a large positive `amount`.
- *Root cause.* The qualifier "that moves the credit" is present in `compute_basis` and in the `factors[].ladder` of all three policies, and **absent from the `rule`** — the one face of the policy the KB renders as normative prose. `compute_basis` is therefore not a verbatim quotation of the rule, and the rule promises a wider set than `compute` reads.
- *Evidence (three places, quoted exactly).*
  - `tradein_ext_upgrade_minimum_spend.rule`: "Where a spend stands among the registration's entries and the programme allows the credit to be spent in parts, the credit standing is instead read as **the sum of every entry booked to the registration, spends included**" — against `tradein_ext_upgrade_minimum_spend.compute_basis.standing_all`: "... the sum of every entry booked to the registration **that moves the credit**, spends included" — against `compute.standing_all`: `SUM(...granted) + SUM(...revaluation_applied) + SUM(...redeemed) + SUM(...forfeited)`.
  - `tradein_ext_credit_redemption.rule`: "the credit still available is instead read as **the sum of every entry booked to the registration**" — against `compute_basis.available_credit` and `factors[available_credit_reading].ladder[0].method`, both of which add "that moves the credit".
  - `tradein_ext_credit_revaluation.rule`: "it is read as **the sum of every entry booked to the registration, spends included**" — against `compute_basis.standing_credit`, which adds "that moves the credit".
  - Schema: `db_schema.json -> tradein_ledger.event_type` enumerates `tradein_item_valuation_logged` and `tradein_condition_inspection_logged` alongside the four credit-moving types; `tradein.extended.yaml -> events[tradein_item_valuation_logged].fields.amount` = "the value the appraiser arrived at, positive". A valuation entry is therefore an entry booked to the registration carrying a positive amount.
- *Demonstrated consequence.* Two defensible readings, two numbers — see `0.md` for the recomputation on task 0's world (`upgrade_minimum_spend` 11805.00 vs 25115.00; `credit_applied_amount` 4442.00 vs 11324.00).
- *Affected artefact and location.* `tasks/trade_up_desk/tradein.extended.yaml`, `extended_policies[tradein_ext_credit_revaluation].rule` (standing-credit sentence), `extended_policies[tradein_ext_upgrade_minimum_spend].rule` (credit-standing sentence) and its `compute_basis.standing_all`/`.redemption_count`/`.credit_base`, `extended_policies[tradein_ext_credit_redemption].rule` (available-credit sentence) and its `compute_basis.redemptions_booked`/`.available_credit`.
- *Relation to previous revisions.* First revision of this audit; no prior finding.

---

**F-2 — Observation (charter-global rule/compute divergence; consequence not demonstrable on either task's world).** Bears on: **task 0**.

- *Symptom.* `tradein_ext_credit_redemption.rule` says: "the price of the new piece is read as **the largest merchandise spend that account records for the current month**". `compute.merch_latest_spend` is `XLATEST('circle','circle_ledger','qualifying_spend', date_field='posted_date', earn_category='merchandise')` — the **most recent** merchandise entry, with **no month window at all**. `compute_basis.merch_latest_spend` and `factors[new_piece_price_reading].ladder[0].method` both read "the spend that account records against its **most recent** merchandise sale", a sentence that appears nowhere in the `rule`.
- *Root cause.* The rule sentence states an algorithm (largest, within the current month) that `compute` does not implement, and the sentence `compute` does implement is missing from the rule. The tier is present in one face and absent from the other.
- *Evidence.* `extended_policies[tradein_ext_credit_redemption].rule` vs `.compute.merch_latest_spend` vs `.compute_basis.merch_latest_spend` vs `.factors[new_piece_price_reading].ladder[0].method`, quoted above.
- *Consequence.* Recorded as an **observation, not a red light**: on task 0's world the two readings coincide (the customer's largest merchandise entry in the current month and her most recent merchandise entry overall are the same row, `circle_ledger/dfed3525…`, qualifying_spend 12400.00), and task 1's scope does not contain this policy, so no second number can be demonstrated from the artefacts as they stand. The divergence is nonetheless real and would give two numbers on any world whose latest merchandise entry is not its largest in the current month.
- *Affected artefact and location.* `extended_policies[tradein_ext_credit_redemption].rule`, `.compute.merch_latest_spend`, `.compute_basis.merch_sales_month`/`.merch_latest_spend`/`.new_piece_price`, `.factors[new_piece_price_reading]`.

---

**F-3 — Observation (compute_basis mis-mapping).** Bears on: **task 0**.

- *Symptom.* In `tradein_ext_credit_revaluation.compute_basis`, the binding `lab_report_value` (which is `XMAX` over the **appraisal register**) is justified by the sentence "where that report was issued longer ago than the validity window and the registration's **own entries** carry a valuation of the piece, the share is taken on the highest valuation those entries carry" — which is the basis of the *other* binding, `own_valuation_value`. `report_age_days` is justified by the appraisal-register sentence instead.
- *Root cause.* Two `compute_basis` entries were swapped relative to the bindings they justify.
- *Evidence.* `extended_policies[tradein_ext_credit_revaluation].compute_basis.lab_report_value` and `.own_valuation_value` carry the same string; `.report_age_days` carries the sentence `lab_report_value` should carry.
- *Consequence.* No second number follows: the branch selector `basis_value` quotes both sentences in full and `compute` reads the right table for each. Recorded as an observation.
- *Affected artefact and location.* `extended_policies[tradein_ext_credit_revaluation].compute_basis`.

---

**F-4 — SOURCE-FACTOR RED (mislabelled effect).** Bears on: **task 1**.

- *Symptom.* `tradein_ext_item_valuation.factors[upkeep_treatment]` is declared `effect: method`, but its three tiers select `K('upkeep_full')` = 1.0, `K('upkeep_partial')` = 0.95 and `K('upkeep_lapsed')` = 0.9 — three numbers fed into one unchanged formula.
- *Root cause.* A rate has been labelled as an algorithm. The skill's test: a `method` tier must change how the quantity is computed, not which number goes into the same computation.
- *Evidence.* `compute.after_upkeep: RND(with_premium * upkeep_multiplier, 2)` — a single expression, identical under all three tiers; `factors[upkeep_treatment].ladder` values are `upkeep_full`/`upkeep_partial`/`upkeep_lapsed`, declared in `params` as `1.0`, `0.95`, `0.9`.
- *Demonstrated consequence.* `tradein_ext_item_valuation`'s honest label counts are 5 `parameter` and 1 `method`, not 4 and 2; the per-policy floor (>= 1 `method`) still holds, so the consequence is a misdescribed factor rather than a broken floor. Demonstrated against task 1's world in `1.md`.
- *Affected artefact and location.* `extended_policies[tradein_ext_item_valuation].factors[upkeep_treatment].effect`.

---

**F-5 — SOURCE-FACTOR RED (mislabelled effect).** Bears on: **task 1**.

- *Symptom.* `tradein_ext_credit_issue.factors[credit_ceiling_held_to]` is declared `effect: method`, but its three tiers select `P('maximum_credit_amount')`, the declared value from the request record, and `F('original_purchase_price')` — three numbers fed into one unchanged `MN(...)`.
- *Root cause.* A threshold has been labelled as an algorithm. The charter's own practice elsewhere confirms the correct label: the structurally identical `tradein_ext_item_valuation.factors[valuation_ceiling_held_to]` and `tradein_ext_custody_declaration.factors[custody_ceiling_held_to]` are both declared `effect: parameter`.
- *Evidence.* `compute.result: RND(MN(credit_gross + fee_credit + cover_bonus, credit_ceiling), 2)` — identical under all three tiers; the three `ladder[].method` strings differ only in which figure the cap is.
- *Demonstrated consequence.* Taken together with F-6, `tradein_ext_credit_issue` has **no** surviving `method` factor, which is below the per-policy floor of one. Demonstrated against task 1's world in `1.md`.
- *Affected artefact and location.* `extended_policies[tradein_ext_credit_issue].factors[credit_ceiling_held_to].effect`.

---

**F-6 — SOURCE-FACTOR RED (dishonest baseline, and two tiers that select the same value).** Bears on: **task 1**.

- *Symptom (a), dishonest baseline.* `tradein_ext_credit_issue.baseline.rule` retains the sentence *"The valuation the credit rests on is the one valuation the registration's entries carry."* The factor that decides that very input, `factors[valuation_the_credit_rests_on]`, declares `baseline: {entries_valuation: F('original_purchase_price')}`. Those are two different figures on the world the write is evaluated on: the baseline sentence names the valuation the entries carry; the declared baseline names the original purchase price. The factor's fall-through tier ("otherwise: the credit rests on the price the piece originally sold for") corresponds to the rule clause *"where those entries carry no valuation at all"*, which the baseline rule does **not** retain — so the fall-through tier is not the baseline the baseline document states.
- *Symptom (b), a tier written as two.* The ladder's tier 1 is "the registration's entries carry more than one valuation of the piece → the credit rests on the most recent valuation those entries carry"; tier 2 is "the registration's entries carry one valuation of the piece → the credit rests on the highest valuation those entries carry". On every world where tier 2's condition holds there is exactly one valuation entry, so "the most recent" and "the highest" denote the same row and the same value. The two tiers never select different values; tier 2 is tier 1 restated for a singleton.
- *Root cause.* The baseline sentence retained for this input is the tier-2 sentence rather than the fall-through sentence, and the ladder's first two tiers are partitioned on a count that makes their two methods extensionally identical wherever the second applies.
- *Evidence.* `extended_policies[tradein_ext_credit_issue].baseline.rule` (2nd sentence); `.factors[valuation_the_credit_rests_on].baseline`; `.factors[valuation_the_credit_rests_on].ladder`; `.compute.valuation_high` and `.compute.valuation_latest`, which are `MAX` and `LATEST` over the same filtered row set.
- *Demonstrated consequence.* On task 1's handling-time world `valuation_high == valuation_latest == 21725.28`, and a reader of `baseline.rule` alone reaches a whole-computation fall-back of **14500.00**, not the figure the artefact's declared all-baseline substitution produces (**10150.00**). Both numbers and the recomputation are in `1.md`.
- *Affected artefact and location.* `extended_policies[tradein_ext_credit_issue].baseline.rule`, `.factors[valuation_the_credit_rests_on].baseline`, `.factors[valuation_the_credit_rests_on].ladder`.

---

**O-1 — Observation (docstring ordering words).** Every task tool's `Args` block for `credit_reference` ends "read it from the trade-in registration lookup **before** calling" (or "before handing this over"). Check 3 forbids a docstring carrying an ordering word. These phrases order a *read of a parameter* against this same call, name no other tool and state no position relative to another write, so no second reading of the sequence follows; recorded as an observation. Location: `task_tools.py`, all six docstrings.

**O-2 — Observation (base rule states a cross-problem order that grounds no edge).** Base `tradein_condition_grading.rule`: "Every traded piece is inspected and graded **before** any credit is issued". Base `tradein_valuation.rule`: "An appraisal is good as the basis of a credit for the programme's validity window, and an older appraisal is **refreshed before** credit is issued." Both state an order between problems. Neither grounds a declared `prerequisite` edge, and **no task's tree rests on either** (task 1's tree rests on `tradein_ext_credit_issue`'s two own prerequisite sentences, both of which are extended-side and state-form). Per check 6 this is therefore an observation, not a red light. Location: base section `policies[tradein_condition_grading].rule`, `policies[tradein_valuation].rule`.

**O-3 — Observation (an aggregated second wording of both edges).** `tradein_ext_credit_issue.rule` opens: "The credit issued against a traded piece is settled **when the piece has been valued and the customer has said what they are putting it in at**" — one sentence restating both of that policy's prerequisite dependencies together, ahead of the two prerequisite sentences that carry them individually. Check 6 requires that the rule carry nothing else about a dependency. No second reading of either hop follows (the sentence names no tool, no route, and repeats exactly what the two prerequisite sentences say), so this is recorded as an observation. Location: `extended_policies[tradein_ext_credit_issue].rule`, first sentence.

**O-4 — Observation (a declared override whose base `formula` block is not named).** `tradein_ext_upgrade_minimum_spend.overwrite` names the base *prose clause* of `tradein_redemption` and replaces it. The base policy also carries `formula: {minimum_new_piece_price: max(round(issued_credit_amount * minimum_upgrade_multiple, 2), round(original_purchase_price * (100 + minimum_upgrade_spend_uplift_pct) / 100, 2))}`, which is the machine face of exactly the clause named — but the `formula` key itself is not named in the declaration. A reader who follows the base formula rather than the base prose computes a different figure (12800.00 on task 0's world, against the extended 11805.00 — the seeded `tradein_credits/f405b339….upgrade_minimum_spend` is 12800.00, i.e. the base formula's output). Recorded as an observation rather than an undeclared override, because the prose clause the formula implements *is* named and replaced verbatim. Location: base `policies[tradein_redemption].formula`; `extended_policies[tradein_ext_upgrade_minimum_spend].overwrite[0]`.

**O-5 — Observation (a share published for one basis applied to another).** `tradein_ext_credit_revaluation.rule`: "The credit the traded piece now supports is **the share the programme publishes for the current appraised value, taken on the price the piece originally sold for**." For every programme whose `valuation_basis` is `original_purchase_price` (Diamond Trade-Up, Bridal Upgrade, Lifetime Diamond) the programme also publishes `credit_pct_of_original_price`, and base `tradein_valuation.rule` says "On the programmes that guarantee the original price, the credit is that share of the price the piece originally sold for". Reading base's basis sentence onto the revalued figure gives a different supported credit (on task 0: 100% × 6400.00 = 6400.00, hence no increase at all, against the extended 7455.00 and an increase of 980.00). Recorded as an observation, not an undeclared override, because base's sentence is scoped to `tradein_item_valuation_logged` / `tradein_credit_issued` and not to a revaluation entry, and base fixes no amount for a revaluation. Location: `extended_policies[tradein_ext_credit_revaluation].rule`; base `policies[tradein_valuation].rule`.

**O-6 — Observation (an inherited base provision the extended valuation does not honour, with no computable second number).** Base `tradein_valuation.rule` ends "...and **on the programmes that credit the stone alone the mounting is valued at nothing**". The Lifetime Diamond Upgrade Guarantee sets `stone_only_credit: true` and `setting_credited: false`. `tradein_ext_item_valuation` values the whole piece from the appraisal register's figure for the piece and never separates stone from mounting, and its two `overwrite` entries do not name this sentence. No second number can be computed, because nothing in the world or the charter states what the mounting alone is worth; recorded as an observation. Location: base `policies[tradein_valuation].rule`; `extended_policies[tradein_ext_item_valuation]`.

**O-7 — Observation (ladder tiers that would collapse on programmes neither task uses).** Three ladders mix a `K` constant with a `P` tier parameter whose value coincides on some programmes:
- `tradein_ext_upgrade_minimum_spend.factors[membership_upgrade_multiple]`: tier 1 is `K('multiple_preferred')` = 1.5 and the fall-through is `P('minimum_upgrade_multiple')`, which is **1.5** for Belrose Standard Trade-In and for Signature Collection Upgrade Privilege — on those programmes two tiers select the same value.
- `tradein_ext_credit_revaluation.factors[appraisal_fee_offset]`: tier 1 is `0.0` and the fall-through is `P('appraisal_fee')`, which is **0.0** for Belrose Standard Trade-In.
- `tradein_ext_item_valuation.factors[valuation_ceiling_held_to]`: tier 1 is `P('custody_insurance_cap')` and tier 2 is `K('ceiling_recent')` = 50000.0; `custody_insurance_cap` is **50000.0** for the Diamond Trade-Up Guarantee.
Neither task runs on one of those programmes (task 0 is Bridal Upgrade Guarantee, task 1 is Lifetime Diamond Upgrade Guarantee), so no consequence is demonstrable against these worlds; recorded as an observation. Location: the three `factors` blocks named.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk (2026-09-17). This section sits below the charter-global section and contains nothing that was used to build it.

**Status: the difficulty does NOT close.** Step 4's closing checklist is written only when all four relationships PASS on every task; here two of them fail, so the checklist is recorded as evaluated, with the items that hold and the items that do not.

| checklist item | holds? | evidence |
| --- | --- | --- |
| per-task audit files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them; old revisions traceable | yes | `0.md`, `1.md`, `_difficulty.md` in `audits/policy_task/trade_up_desk/`; first revision, no prior text to preserve |
| every comparison section carries a PASS | **no** | `0.md` → SOURCE-POLICY RED (policy self-consistency fails on F-1; tree, factors and unique solution pass); `1.md` → SOURCE-FACTOR RED (factors fail on F-4, F-5, F-6; policy self-consistency, tree and unique solution pass) |
| extended policies fully covered; the M tasks' scopes pairwise disjoint, each spanning its whole problem tree | yes | `charter_scope` of task 0 = component A (3 policies), of task 1 = component B (3 policies); disjoint, 6 of 6 covered; each scope contains its root and both prerequisite problems |
| task tools and GT closed; each task tool uses an independently generated, frozen uuid8 | yes | six tools, six distinct non-derived tails (`### action_binding_and_uuids`); every gold write is a task tool of the task's own scope |
| every tree has 1–3 prerequisite problems, >= max(n−1,1) `value_input` edges, >= 1 `owner=user` problem, no cycle; the whole difficulty's `prerequisite` edges a DAG with no cross-task cycle | yes | task 0: n=2, 2 `value_input`, root tool `owner=user`; task 1: n=2, 2 `value_input`, leaf tool `owner=user`; two disjoint components, no edge between them |
| every computation declares a self-sufficient baseline and 4–6 factors (>= 2 `parameter`, >= 1 `method`; per task >= 1 multi-source and >= 1 cross-difficulty), every ladder >= 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes realistic, every factor bearing weight against an honest baseline with the baseline alone giving a definite number different from gold | **no** | holds for the five computations of `tradein_ext_credit_revaluation`, `tradein_ext_upgrade_minimum_spend`, `tradein_ext_credit_redemption`, `tradein_ext_custody_declaration` and (label aside, F-4) `tradein_ext_item_valuation`; fails for `tradein_ext_credit_issue` — F-6 (a factor whose `baseline` is not what `baseline.rule` states, and two tiers that select one value) and F-5 (a `method` label on a ceiling number), leaving that policy with no surviving `method` factor |
| the instantiation-stage gates re-run once on the final form | not applicable | the artefacts were not changed by this audit (the auditor edits nothing); the gate snapshot supplied with the brief is the run on the current form, and it is green — which is consistent with every finding here, since none of F-1, F-4, F-5 or F-6 is a structural fact a script can see (a missing qualifier in prose, a label, a baseline sentence chosen from the wrong tier) |

**Per-task verdicts.**
- task 0 — **SOURCE-POLICY RED** (`0.md`, findings 1; charter-global F-1)
- task 1 — **SOURCE-FACTOR RED** (`1.md`, findings 1–3; charter-global F-4, F-5, F-6)

Both tasks' independent derivations reproduced the scored solution item for item and figure for figure on the reading `compute` implements; the red lights are defects of the charter's prose and factor declarations, not of the worlds, the personas, the tools or the scored numbers. No fix is proposed here.

## revision_2

Round-2 re-audit, 2026-09-17. Revision 1 above is left untouched. The coordinator supplied the re-run gate block (all OK, `check_traceability` excluded) and the rebuilt masked views; the auditor re-ran nothing.

### charter_global_frozen (revision 2)

- freeze hashes now: `tradein.extended.yaml` `ebca61489b528653` (184152 bytes; round 1 `8b59d76a9166cea9`), `task_tools.py` `6e29514e0a96dab6` (21205 bytes; round 1 `0f1ff84b7f10d684`) — verified by `sha256sum`. **Both moved**, so every charter-global section is re-derived below; nothing is carried forward by reference.
- masked views: `0.json` `5a7342c8f04c88cc`, `1.json` `7ddfab0197a67755` — **byte-identical to round 1**, verified. The worlds and personas did not move.
- fields permitted / masked: as in revision 1. This section and both tasks' `revision_2` derivations were written before the round-2 task JSONs were opened.
- what moved (diff of each policy against the round-1 copy kept in the auditor's scratchpad; base section still byte-identical to `blueprint/products/tradein.yaml`): `tradein_ext_credit_revaluation` (rule qualifier + defining sentence; `compute_basis.lab_report_value`/`.report_age_days` re-mapped), `tradein_ext_upgrade_minimum_spend` (rule qualifier + defining sentence; `multiple_preferred` 1.5 → 1.4 with the rule now saying "one and two fifths"), `tradein_ext_credit_redemption` (rule qualifier + defining sentence; new-piece-price sentence now "the spend that account records against its most recent merchandise sale"), `tradein_ext_item_valuation` (third `overwrite` naming base's stone-only sentence; new whole-piece sentence in rule and baseline; `ceiling_recent` 50000 → 45000 with the rule saying "forty-five thousand"; `upkeep_treatment` relabelled `parameter` with `value:` tiers), `tradein_ext_custody_declaration` (unchanged), `tradein_ext_credit_issue` (rebuilt: opening sentence, resting-figure ladder, baseline, overwrite `replaced_by`, `credit_ceiling_held_to` relabelled `parameter`). `task_tools.py`: every "before calling"/"before handing this over" removed from the `Args` blocks; `issue_upgrade_credit_f63e5226` gained `appraised_value: float` and now writes `tradein_credits.appraised_value`; nothing else in any body changed.

### round-1 items, verified on the artefacts

| item | claim | verified | status |
| --- | --- | --- | --- |
| F-1 | qualifier + defining sentence in all three rules | all three `rule`s now read "the sum of every entry booked to the registration **that moves the credit**, spends included" followed by "An entry moves the credit where it books the credit, revalues it upward, spends it or takes it away; a valuation entry and an inspection entry move nothing, whatever amount they carry." — those four families are exactly the four `event_type`s the three `SUM` expressions add; `compute_basis` now quotes the rule verbatim; the ladders match | **closed** (consequence re-checked in `0.md` revision_2) |
| F-2 | rule states compute's algorithm | `tradein_ext_credit_redemption.rule` now: "the price of the new piece is read as the spend that account records against its most recent merchandise sale" = `XLATEST(... earn_category='merchandise')`, = `compute_basis`, = ladder | **closed** |
| F-3 | compute_basis re-mapped | `compute_basis.lab_report_value` and `.report_age_days` both quote the appraisal-register sentence; `.own_valuation_value` keeps the own-entries sentence | **closed** |
| F-4 | `upkeep_treatment` → parameter | `effect: parameter`, tiers `value: K('upkeep_full')` / `K('upkeep_partial')` / `K('upkeep_lapsed')`; policy now 5 `parameter` + 1 `method` (`valuation_resting_figure`) | **closed** |
| F-5 | `credit_ceiling_held_to` → parameter | `effect: parameter`, tiers `P('maximum_credit_amount')` / the declared value / `F('original_purchase_price')` | **closed** |
| F-6 | credit-issue rebuilt | `baseline.rule` now retains "The credit rests on the price the piece originally sold for." — the fall-through sentence, and every sentence of it is verbatim in the rule; the factor's `baseline: {entries_valuation: F('original_purchase_price')}` is now exactly what the baseline states; the ladder is three pairwise-disjoint tiers with three distinct algorithms — `MAX` over the registration's valuation entries / `MN(MAX, original price)` / the original price — partitioned on (entries carry a valuation) × (an issued report within the validity window), the first two conjoining a `tradein_ledger` condition with an `appraisal_orders` condition (multi-source, `cross_difficulty: appraisal`); the aggregated opening sentence is gone ("The credit issued against a traded piece is worked out as follows."); `overwrite.replaced_by` is the rule's new sentence verbatim | **closed** (weight and honesty re-checked on task 1's world in `1.md` revision_2) |
| O-1 | ordering words removed | `grep -n "before"` over `task_tools.py` returns nothing; the only "after" is "the registration's standing after the spend" in a `Returns` block, a description of state | addressed |
| O-3 | second wording removed | see F-6 | addressed |
| O-6 | stone-only sentence | `tradein_ext_item_valuation.overwrite[2]` names base `tradein_valuation`'s clause "on the programmes that credit the stone alone the mounting is valued at nothing" (verbatim in base) and replaces it with "The valuation is taken on the piece as a whole, stone and mounting together, as the appraisal register values it." (verbatim in rule and in `baseline.rule`) | addressed — the override is now declared |
| O-7 | tier collapses | `multiple_preferred` 1.4 ≠ any programme's `minimum_upgrade_multiple` (1.5 / 2.0 / 0.0); `ceiling_recent` 45000 ≠ any `custody_insurance_cap`; **`appraisal_fee_offset` unchanged** — tier 1 `0.0` still equals `P('appraisal_fee')` = 0.0 on Belrose Standard Trade-In | two of three addressed; the third remains an observation (no task runs on that programme) |
| O-2, O-4, O-5 | left as recorded | unchanged in the charter, as the reworker states | remain observations |
| 0.md #6, 1.md #5 | proof-field day count; `appraised_value` left at 0 | checked after reveal in the task files | see task files |

### re-derived charter-global sections (revision 2)

- **policy_conflict_scan** — unchanged conclusions: subjects, triggers, tools, computes, state gates, time anchors, cross-category boundaries and the two-component scope partition are as in revision 1; the third override on `tradein_ext_item_valuation` removes the one inherited provision (stone-only) the extended valuation did not honour.
- **rule_compute_equivalence** — re-swept over all six policies on the new text. The three substantive divergences of revision 1 (F-1, F-2, F-3) are gone. No new divergence of substance: every `compute_basis` sentence is now verbatim in its rule (the paraphrase-only ladder wording noted in revision 1 remains, and remains not a defect). One latent shape recorded as N-1 below.
- **action_binding_and_uuids** — six tools, six distinct `(target_tool, computes)`, the same six uuid8 tails; bodies re-read: still `find` + write only, no status/history/date check anywhere; `issue_upgrade_credit_f63e5226` additionally writes `appraised_value` and folds it into `make_id`. Docstrings carry no ordering word and name no other tool.
- **prerequisite_graph / prerequisite_sentences** — the four edges are textually identical to revision 1; each `policy_source` re-verified verbatim in its own (new) rule, each `gate` present in the (new) compute, all four state-form, graph acyclic, no second wording anywhere (O-3 closed).
- **override_declarations** — seven declarations now (was six); all clauses verbatim in base, all replacements verbatim in the extended rule. `overwrite: []` policies re-swept sentence by sentence against their refs: unchanged conclusions, O-5 stands as an observation.
- **factor_ladders (revision 2)** — per policy: revaluation 5 (3p/2m), minimum spend 5 (3p/2m), redemption 6 (3p/3m), item valuation 6 (**5p/1m**), custody 4 (3p/1m), credit issue 5 (**4p/1m**). Every ladder three pairwise-disjoint tiers, each tier's condition and outcome in the rule, no two tiers of any ladder selecting one value or method on the programmes the tasks run on; every `method` label now names a factor whose tiers read different rows or apply a different operation; every fall-through equals the sentence its `baseline.rule` retains. Multi-source and cross-difficulty floors met in both components (the rebuilt `valuation_the_credit_rests_on` adds one of each to component B).

### new findings (revision 2)

**N-1 — Observation (a rule branch compute cannot evaluate; pre-existing shape the round-1 audit did not flag).** Four bindings take `DAYS(CFIELD('appraisal','issued_date', ...), NOW)`: `tradein_ext_credit_revaluation.report_age_days`, `tradein_ext_item_valuation.current_report_age_days`, `tradein_ext_custody_declaration.report_age_days`, `tradein_ext_credit_issue.current_report_age_days`. `CFIELD` returns `None` when no matching appraisal holding exists, and `DAYS(None, NOW)` does not evaluate. Each rule's fall-through ("otherwise" / "the register carries no report on it issued within that window") covers the no-report case in prose, so on a world with no issued report the rule gives a definite branch and the compute gives none. Both task worlds carry an issued report, so no consequence is demonstrable here; recorded as an observation. Location: the four `compute` bindings named.

**N-2 — Observation (declared reads incomplete).** `tradein_ext_credit_issue.cross_category[appraisal].reads` lists `appraisal_ledger.amount` and `appraisal_ledger.event_type` only, while the rebuilt compute also reads `appraisal_orders.issued_date` through `CFIELD`. The category is declared and the read is exercised, so the EXTENDED gate is right to pass it; the field list is documentation and understates what is read. Location: `extended_policies[tradein_ext_credit_issue].cross_category`.

**N-3 — Observation (a non-computed parameter added to a task tool).** `issue_upgrade_credit_f63e5226` now takes `appraised_value`, which no policy `computes`. Its docstring pins it to "the value the traded piece was appraised at, as recorded against the registration" — i.e. the `tradein_item_valuation_logged` entry the credit-issue rule already waits on. The closest alternative reading (the appraisal register's own `appraised_value`) is excluded in `1.md` revision_2 with world evidence. Recorded so the parameter's provenance is on the record; no defect.

### closing_checklist (revision 2)

Written after both round-2 comparisons were on disk. **Status: the difficulty closes.**

| checklist item | holds? | evidence |
| --- | --- | --- |
| per-task files one-to-one with the tasks, `_difficulty.md` alongside, old revisions traceable | yes | revision-1 text preserved verbatim in all three files; `## revision_2` appended below it |
| every comparison section carries a PASS | **yes** | `0.md` revision 2 PASS; `1.md` revision 2 PASS |
| extended policies fully covered; scopes pairwise disjoint, each spanning its whole tree | yes | unchanged: components A and B, 6 of 6 |
| task tools and GT closed; independent frozen uuid8s | yes | same six tails; the one added parameter (`appraised_value`) traces to a unique reading (N-3, `1.md`) |
| every tree 1–3 prerequisite problems, >= max(n−1,1) `value_input`, >= 1 `owner=user`, acyclic; whole-difficulty DAG | yes | unchanged: n=2 / 2 value_input / user tool in both; two disjoint components |
| every computation: self-sufficient honest baseline, 4–6 factors (>= 2 parameter, >= 1 method; per task >= 1 multi-source and >= 1 cross-difficulty), ladders of >= 3 disjoint tiers stated in full, tiers distinct, conditions and outcomes realistic, every factor bearing weight, baseline alone definite and ≠ gold | **yes** | all 31 factors move their number on their task's world; every baseline-alone figure equals the declared `baseline_result` and differs from gold (0.00 / 14760.00 / 3840.00; 9787.50 / 14500.00 / 10150.00); labels honest after F-4/F-5; F-6's ladder rebuilt |
| instantiation-stage gates re-run once on the final form | yes (by the coordinator) | the round-2 gate block in the brief: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK on the hashes audited here; `check_traceability` awaits the published KB |

**Per-task verdicts (revision 2):** task 0 — **PASS**; task 1 — **PASS**.

Observations left standing for the record, none with a demonstrable consequence on either world: O-2, O-4, O-5 (reasons now in `design_rationale`), O-7's third item (`appraisal_fee_offset` on Belrose Standard Trade-In), N-1 (`DAYS(CFIELD(...))` on a world with no issued report), N-2 (`cross_category.reads` understates `issued_date`), N-3 (provenance of `appraised_value`).
