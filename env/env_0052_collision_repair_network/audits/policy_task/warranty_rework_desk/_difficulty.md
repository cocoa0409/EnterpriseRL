# Policy-task audit — warranty_rework_desk / charter-global

## charter_global_frozen

- Scenario: `env/env_0052_collision_repair_network`; difficulty `warranty_rework_desk`; claimed scope category `[warranty]`, event types as listed in `blueprint/blueprint.yaml` difficulties -> warranty_rework_desk -> claim.
- Freeze inputs (re-hashed by the auditor, sha256 first 16 hex, match the brief):
  - `tasks/warranty_rework_desk/warranty.extended.yaml` = `9b2c9d0fa76ec3c3`
  - `tasks/warranty_rework_desk/task_tools.py` = `d5bb1f5fa4bc5246`
  - `.audit_views/policy/warranty_rework_desk/0.masked.json` = `4300cbe37d1426e0`; `1.masked.json` = `436b618a15a03698` (both carry only `frozen_time`, `user_scenario`, `initial_state`, `_masked_keys`).
- Freeze time of this section: 2026-10-11T03:39Z (system clock, `date -u`), written before any task JSON was opened.
- Auditor: independent policy-task auditor (Claude agent); did not author any artifact of this difficulty.
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{warranty,adas,glass,retail,rental,estimate}.yaml` (cross-category charters only for the fields the factors read), the extended charter, `task_tools.py`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (used read-only, imported into a scratch harness under `/tmp/audit_0052_wrd/` to replay the restricted expressions).
- Masked and not read before the per-task freezes: `tasks/warranty_rework_desk/tasks/*.json` (whole files), i.e. `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; other difficulties' tasks and audits; `worklog.md`.
- Entry conditions (Step 0): the brief supplies the gate snapshot (check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cache_diff / check_cross_fire all green, check_traceability deferred to KB render), the masked views with hashes and the freeze-input hashes. Entry conditions complete.
- Base copy: every top-level key of `blueprint/products/warranty.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) compares equal (parsed YAML) to the same key in `warranty.extended.yaml`. Base copy verbatim.

### policy_conflict_scan

Extended policies (6), with subject / computes / target tool / owner / trigger:

| policy | subject | computes | target_tool (owner) | trigger | plans in scope |
| --- | --- | --- | --- | --- | --- |
| warranty_ext_calibration_diagnostic_charge | warranty_charge | amount_usd | accept_calibration_diagnostic_charge_d9578b72 (user) | state_due | Calibration Workmanship Warranty, calibration_fault not covered |
| warranty_ext_calibration_goodwill | warranty_charge_waiver | amount_usd | grant_calibration_goodwill_f9a2e5bf (agent) | on_request | Calibration Workmanship Warranty |
| warranty_ext_electrical_diagnostic_charge | warranty_charge | amount_usd | accept_electrical_diagnostic_charge_607d2bcb (user) | state_due | Collision Lifetime / Certified Structural Lifetime, electrical_part not covered |
| warranty_ext_mechanical_diagnostic_charge | warranty_charge | amount_usd | accept_mechanical_diagnostic_charge_d69f0d58 (user) | state_due | Collision Lifetime / Certified Structural Lifetime, mechanical_part not covered |
| warranty_ext_rework_courtesy_rental | warranty_rework_authorize | courtesy_rental_days | sign_rework_authorization_70486d76 (user) | state_due | any plan with a network rework |
| warranty_ext_same_visit_courtesy | warranty_charge_waiver | amount_usd | book_same_visit_courtesy_9d7b5f0e (agent) | state_due | Collision Lifetime / Certified Structural Lifetime |

- Overlapping subjects: `warranty_charge` (three charge policies) are partitioned by (plan, concern_type): calibration_fault under CWW; electrical_part / mechanical_part under Collision/Structural. These are exactly the three (plan, fee-bearing type) pairs base `diagnostic_fee_concern_types` names, so the three overrides jointly cover the base fee scope with no overlap. `warranty_charge_waiver`: calibration goodwill (CWW only, on request) vs same-visit courtesy (Collision/Structural only, state_due) — disjoint by plan.
- Triggers / eligibility / time anchors: all "less than one whole calendar month" windows and "charge date / goodwill date / courtesy date" anchors are the booking date (`ctx.now()[:10]` in every tool). No two policies set different values for the same field of the same row.
- Terminal states: charges add `warranty_charge` rows; waivers add `warranty_charge_waiver` rows naming one charge; the rework policy adds one `warranty_rework_authorize` row. The base `charge_open` dedup and the per-charge goodwill cap (`diagnostic_waiver_authority_usd`) are inherited by both waiver policies (both rules restate the cap).
- Cross-category read boundaries: reads only (adas, glass, retail, rental, estimate); no policy writes another category. Declared `cross_category` blocks match the X/C-reads in compute (checked binding by binding).
- Scope across the M=2 tasks: from the masked worlds alone, task 0's world carries only a Calibration Workmanship Warranty not-covered calibration finding and task 1's only a Collision Lifetime visit with not-covered electrical + mechanical findings and a covered panel_fit finding; the gate snapshot reports "all policies are covered across the suite with disjoint scopes". Whether the declared `charter_scope` matches is checked per task after reveal (not here).
- Conflicts found: see findings F-1 (rule/compute non-equivalence on "network reworks") and the observations below; no base/extended conflict that changes a scored quantity was found.

### rule_compute_equivalence

Every `compute_basis` entry of every extended policy is a verbatim substring of that policy's `rule` (scripted check, zero misses). Binding-by-binding sweep:

- **calibration_diagnostic_charge**: procedure tier (static_and_dynamic / dynamic / else -> standard fee) = `procedure_fee`; alignment tier reads `XLATEST(adas_events, alignment_result/alignment_corrected, event_type=adas_alignment_check)` over the customer's orders = "the most recent four-wheel alignment check recorded on the customer's calibration orders"; check-fee value `CPARAM('adas','alignment_check_fee_usd', adas_order_id=source)` = "the alignment check fee of the calibration tier of the order the coverage was issued on"; scan tier = `src_systems`; history `XCOUNT(adas_attempt, failed)` = "calibration attempts recorded as failed on the customer's calibration orders"; recheck `COUNT(warranty_rework_complete, resolved, within_months=3/12)` = "network reworks completed on the coverage with the concern resolved ... less than three/twelve whole calendar months before the charge date" (see F-1 on "network"); `int(x/2)` = "halved and rounded down to the whole dollar"; `RND(...,2)` = "rounded to the cent". Equivalent except F-1 and the date-tie note (O-6).
- **calibration_goodwill**: `charge_amount` SUM of `warranty_charge` within 1 month = "calibration diagnostic charges booked on the coverage less than one whole calendar month before"; share ladder on `LATEST(exclusion_code, not_covered)`; low-use = (latest calibration_fault report odometer − odometer_at_issue) with `MONTHS(issued_date, NOW)`; glass `XCOUNT(glass_customer_payment, 36 months)`; calibration-order `XCOUNT(adas_payment, payer_kind=customer, 24 months)`; prior trouble `COUNT(inspection covered)`; timing on `DAYS(discovered, report)` of the latest calibration_fault report; ceil = "rounded up to the whole dollar"; cap `MN(..., diagnostic_waiver_authority_usd)`. Equivalent.
- **electrical_diagnostic_charge**: labor-hours tiers on `CFIELD(retail, quoted_labor_hours)`; network fee on `CFIELD(adas, status / dealer_invoice_usd, retail_repair_id=source)`; shared-visit on count of not_covered inspections on the latest not_covered date; part-age on `MONTHS(issued, NOW) − electrical_parts_months`; comeback on `COUNT(rework_complete, not_resolved)` ("network reworks ... not resolved", F-1); `MX(0, ...)` = "never below zero". Equivalent except F-1; `CFIELD` returns the first matching calibration order where several exist for one repair (O-7).
- **mechanical_diagnostic_charge**: road-test on latest concern report odometer vs `P(mechanical_parts_miles)` and `K(high_use_multiple)`; lift on `CFIELD(retail, variant_name)`; return-visit on `COUNT(rework_complete, resolved, within 1/3 months)` (F-1); multi-service on adas customer payments and rental customer payments within 36 months. Equivalent except F-1.
- **rework_courtesy_rental**: allowance method on source retail variant (ceil(days×1.4) / days+1 / days); comeback on not_resolved completions (F-1); refinish on the latest covered inspection's concern type and the paint-concern report count (">= 2" encodes "another paint ... concern", ">= 1" encodes "carries a paint ... concern"); source-repair on `DAYS(repair_started_date, ready_date)` ("drop-off date" per schema meaning of repair_started_date); paid-rental on `XSUM(rental_customer_charge, uncovered_days, days_count)` = "rental days the customer paid as uncovered days" (charge rows, not payment rows — wording "paid" vs "charged" noted, no divergence where charges were paid in full). Equivalent except F-1. The gate "When the plan's rework target business days exceed its courtesy rental minimum rework days ... otherwise it pays none" has no compute branch (O-3).
- **same_visit_courtesy**: visit charges SUM within 1 month; share ladder on covered count on the latest not_covered date and courtesy days of the latest covered finding's concern; estimate via `retail.booking_id -> estimate.estimate_total_usd`; covered history count; coverage age `MONTHS`; low use on latest concern report odometer; comeback adjustment on `COUNT(rework_complete, within 12 months)` "whatever their result" (F-1); ceil / cent / cap. Equivalent except F-1 and O-5.
- Every factor's ladder tier is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states (checked for all 33 factors).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct: (accept_calibration_diagnostic_charge_d9578b72, amount_usd), (grant_calibration_goodwill_f9a2e5bf, amount_usd), (accept_electrical_diagnostic_charge_607d2bcb, amount_usd), (accept_mechanical_diagnostic_charge_d69f0d58, amount_usd), (sign_rework_authorization_70486d76, courtesy_rental_days), (book_same_visit_courtesy_9d7b5f0e, amount_usd). Each claimed by exactly one policy.
- uuid8 tails `d9578b72, f9a2e5bf, 607d2bcb, d69f0d58, 70486d76, 9d7b5f0e`: six distinct values, no shared prefix, no sequence or adjacent-value pattern, none reused across tools.
- Tool bodies: each performs exactly one `ctx.create` with caller-supplied values; no tool reads history, computes an amount, checks a status or refuses (no branch other than `round`). The tool layer judges no prerequisite.
- Docstrings: no other tool named, no position in a sequence, no before/after/first. The word "then" appears three times (lines 133, 167, 204) only to describe the call's own effect on the history view ("the coverage's money history then shows ..."), not an order among actions — observation O-1, no consequence.
- Owners: the three charges and the rework authorization are `owner="user"` ("The customer accepts / signs"); the two waivers are `owner="agent"`. The blueprint difficulty summary says "The agent records reports, inspection outcomes, remedies, completions, charges ..." — the summary is not a charter policy and the base charter assigns no owner to these events, so this is observation O-2 (no scored consequence).
- `sign_rework_authorization_70486d76` hard-codes `rework_kind="network_rework"` and `calibration_needed=False` and its docstring limits it to "a rework that disturbs no driver-assistance sensor"; base `warranty_evt_rework` ("sensors the rework disturbs are recalibrated at no charge where recalibration_on_rework is true") and the base event trigger (`calibration_needed: true` opens an adas order) therefore have no tool in this difficulty. Observation O-4; it bites only a task whose covered rework disturbs a sensor.

### prerequisite_graph

- `prerequisite` present on all six policies; `[]` on calibration_diagnostic_charge, electrical, mechanical, rework_courtesy_rental.
- Edges (all `kind: value_input`, `form: state`, no `fallback_reason`):
  - E1 calibration_goodwill <- calibration_diagnostic_charge, gate `charge_amount` (binding exists), resolved_by accept_calibration_diagnostic_charge_d9578b72 (= that policy's target_tool).
  - E2 same_visit_courtesy <- electrical_diagnostic_charge, gate `visit_charges` (exists), resolved_by accept_electrical_diagnostic_charge_607d2bcb (= target_tool).
  - E3 same_visit_courtesy <- mechanical_diagnostic_charge, gate `visit_charges` (exists), resolved_by accept_mechanical_diagnostic_charge_d69f0d58 (= target_tool).
  - E4 same_visit_courtesy <- rework_courtesy_rental, gate `courtesy_share` (exists), resolved_by sign_rework_authorization_70486d76 (= target_tool).
- Every `problem` is an extended policy id of this file; none is a base policy or self. Graph: two stars of depth 1, acyclic.
- Every `policy_source` is a verbatim substring of the blocked policy's own `rule` (scripted) and of no depended-on policy's rule.
- `condition` vs sentence strength: E2/E3 match ("every not-covered ... finding of the visit"). E1's condition adds "booked less than one whole calendar month before", which the sentence does not carry (the window is in another sentence of the same rule); E4's condition adds "with courtesy_rental_days above zero", which the sentence ("carries its network rework authorization") does not carry. Both are observations O-5a/O-5b: under the charter, a rework authorization for an in-scope plan always carries ≥ 3 days (see factor_ladders), and no charge older than a month exists in either world.
- `effect` statements are accurate for the bindings (E1: charge_amount 0 -> charge; E2/E3: visit_charges grows; E4: visit_rental_days > 0 moves courtesy_share off the standard share).
- No authoring-viewpoint wording ("in this task", "at the opening", "current world") in any prerequisite field (scripted).

### prerequisite_sentences

- E1 "Calibration goodwill is figured only after the calibration diagnostic charge owed on the not-covered calibration finding stands on the coverage's account." — connective "only after"; waited-on object is a record-visible state (a diagnostic charge standing on the coverage's account = a `warranty_charge` row in the warranty money history for the not-covered calibration concern); no performer, tool, id or snake_case token. Writes of this difficulty that create a `warranty_charge` row: the three accept_* tools; only the calibration one is for a calibration-fault concern under a CWW (the other two docstrings and rules are restricted to electrical-/mechanical-part concerns under Collision/Structural plans), so exactly one write brings the state about. Derivation: sentence -> records show no charge on the not-covered calibration finding -> the rule that posts "one calibration diagnostic charge for that concern" is warranty_ext_calibration_diagnostic_charge -> its write is the customer's acceptance. Single reading.
- E2 "The same-visit courtesy is not worked out until the electrical diagnostic charge owed on every not-covered electrical-part finding of the visit stands on the coverage's account." — "not until"; state form; single resolving write (accept_electrical...). Single reading.
- E3 "The same-visit courtesy is figured only after the mechanical diagnostic charge owed on every not-covered mechanical-part finding of the visit stands on the coverage's account." — "only after"; state form; single resolving write. Single reading.
- E4 "The same-visit courtesy is booked only once the covered concern found at the visit carries its network rework authorization." — "only once"; state form (a `warranty_rework_authorize` row of kind network_rework on that concern); the only write of this difficulty that creates such a row is sign_rework_authorization_70486d76 (the rework-rental policy's tool). Single reading for a visit with one covered concern; for a visit with two or more covered concerns "the covered concern" is singular and does not say which (see O-5c).
- Second wording: the same-visit rule's opening scope sentence also states "and that covered concern carries a network rework authorization" as a condition of the courtesy being owed. This restates E4 as an eligibility condition (observation O-8; its reading on task 1 is examined in that task's file).
- Depended-on rules (calibration charge, electrical, mechanical, rework rental) do not restate any of these sentences; no rule names a tool, a policy id or a snake_case token (scripted: zero snake_case tokens in any extended rule).
- Undeclared cross-problem orders in extended rules: none found. Base rules carry cross-problem orders that ground no edge ("A concern was reported on the coverage before it is inspected."; "A remedy is authorized only for a covered concern.") — base sentences, no task tree rests on them; observation O-9.

### override_declarations

- **calibration_diagnostic_charge** vs `warranty_evt_diagnostic_fee`: sentence 1 (fee = diagnostic_fee_usd when type is fee-bearing; every other inspection free) — handled differently, declared in `overwrite` (superseded_clause verbatim). Sentence 2 (card, cash or check) — not touched. Sentence 3 (paid/waived in full takes no further payment/waiver) — inherited. Sentence 4 (billing_error removes a charge "posted against the rule above"; goodwill capped at authority) — inherited; "the rule above" now points at the replacement (observation O-10: an agent reading "the rule above" as the superseded base sentence could treat the computed charge as posted against it; no task here involves a billing_error waiver).
- **electrical_diagnostic_charge**, **mechanical_diagnostic_charge**: same base sentence 1, each declared. The three overwrite entries all supersede the whole of base sentence 1, but each `replaced_by` restates only its own scope plus "an inspection that finds a concern covered stays free"; the base clause "every other inspection is free" for not-covered, non-fee-bearing concerns is not restated by any replacement (observation O-11; neither task world has such a not-covered finding).
- **calibration_goodwill** (`overwrite: []`) vs `warranty_evt_diagnostic_fee`: base fixes only the cap and the decline of a larger request; the extended rule computes the amount within the same cap and restates the decline. No base sentence fixes a different amount, so no second defensible number. Follows.
- **rework_courtesy_rental** vs `warranty_evt_rework`: the courtesy-rental clause ("up to courtesy_rental_days days") is declared superseded; remedy-only-for-covered, network rework at any center, target days, courtesy ride, recalibration, outside-shop and escalation sentences inherited untouched.
- **same_visit_courtesy** (`overwrite: []`) vs `warranty_evt_diagnostic_fee`: books a goodwill waiver within the per-charge authority (restated); dedup inherited. No base sentence fixes a different amount. Follows.
- Disguised forms: no anonymous intermediate overriding a base quantity, no 0/1 multiplier zeroing a base amount, no dropped base branch; no rule or `compute_basis` calls a base output wrong.

### factor_ladders

| policy | factors | parameter / method | multi-source factors (tiers over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- |
| calibration_diagnostic_charge | 5 | 4 / 1 | none (alignment tiers are two fields of one adas_events row; recheck tiers one table two windows) | procedure, alignment, scan, history -> adas |
| calibration_goodwill | 6 | 5 / 1 | low_use (concern-report odometer row AND coverage row issued_date/odometer_at_issue) | order_loyalty -> adas (glass is not a difficulty, `null` correct) |
| electrical_diagnostic_charge | 5 | 4 / 1 | none (network fee tiers read status and dealer_invoice_usd of one adas_orders row) | sensor_network -> adas (retail not a difficulty) |
| mechanical_diagnostic_charge | 4 | 3 / 1 | multi_service (adas_ledger payment AND rental_ledger payment) | multi_service -> rental |
| rework_courtesy_rental | 5 | 4 / 1 | refinish (latest covered inspection + its concern report AND the paint-concern report count) | paid_rental -> rental |
| same_visit_courtesy | 6 | 5 / 1 | courtesy_share (covered inspections on the visit date AND the authorization row's courtesy days) | estimate_allowance -> estimate |

- Every ladder has exactly three tiers, pairwise disjoint as stated, fall-through = the factor's `baseline`, and each `baseline` equals what the policy's `baseline.rule` states for that input (standard fee / zero add-on / identity method / standard share / plan days counted one for one). Every `baseline.rule` is a sentence of the rule and is self-sufficient (gives a definite number from the plan parameter and the charge rows alone).
- Bindings of different factors are disjoint; no `decides` is `result`.
- No two tiers of a ladder select the same constant. One value-dependent collapse: calibration_alignment_fee tier 1 takes the source order tier's `alignment_check_fee_usd`, which is 0.00 for a Blind Spot Radar Calibration (adas.yaml), equal to the fall-through; not reachable in task 0 (source tier Multi-System, 59.95). Observation O-12.
- Per-task bounds (≥1 multi-source, ≥1 cross_difficulty over the task's computations) are met by the policy set any task claiming {calibration charge + goodwill} or {electrical + mechanical + rework rental + same-visit} would carry; verified per task.
- Labels: rework_courtesy_allowance_count switches between multiply-and-ceil, add-a-constant and identity — a genuine method switch. The other five `method` factors (calibration_recheck_rate, calibration_report_timing, electrical_shared_visit_rate, mechanical_return_visit_rate, same_visit_comeback_adjustment) each switch a multiplier together with the rounding rule (floor/ceil to the dollar vs round to the cent vs none). They change more than a number (the rounding operation changes), so they are not mislabelled under the letter of the test; recorded as observation O-13 because the "method" consists of a rate plus a rounding mode.
- Business reality of conditions/outcomes: every tier value is a K/P parameter of the charter. Conditions are ones a repair network plausibly weighs (source procedure/system complexity, source repair size, loyalty payments, prior comebacks, mileage/age bands, report promptness). Two observations: O-14 calibration_history_fee raises the customer's diagnostic charge because the network's own earlier calibration attempts failed — a surcharge few shops would publish, but it can be read as a difficult-vehicle surcharge, so not demonstrated unreal; O-15 same_visit_courtesy_share: within the policy's scope the visit always has ≥1 covered finding and, once E4 holds, the rework-rental rule gives that authorization ≥3 days for both in-scope plans (Collision: 3 days, target 5 > 1; Structural: 5 days, target 7 > 1), so the conjunct "courtesy rental days above zero" holds at this write for every customer except where the coverage's most recent covered finding post-dates the visit; the standard-share fall-through is reachable only in that edge. Not demonstrably universal, hence observation, but the ladder's live tiers are in practice the single- and multi-finding shares.

### findings

**F-1 — SOURCE-POLICY RED (charter-global; rule/compute non-equivalence on "network reworks").**
- Symptom: rules count "network reworks", compute counts every `warranty_rework_complete` row.
- Evidence: mechanical rule "The mechanical road-test fee is charged according to the network reworks completed on the coverage with the concern resolved: where one was completed less than the recent-visit months before the charge date, the mechanical road-test fee is halved ..."; compute `resolved_recent: COUNT('warranty_events', within_months=K('recent_visit_months'), event_type='warranty_rework_complete', rework_result='resolved')`. The base event `warranty_rework_complete` means "A network rework or outside-shop repair is finished" and carries no rework_kind; the kind lives on the matching `warranty_rework_authorize` row. Same pattern: electrical `unresolved_reworks`, rework-rental `unresolved_reworks`, same-visit `recent_reworks`, calibration `resolved_3m/resolved_12m`.
- Demonstrated consequence (same situation, two conclusions): a Collision Lifetime coverage (sublet_distance_miles 50, so outside_shop remedies exist) whose only completed remedy is an outside_shop repair completed resolved 10 days before a mechanical charge: the rule reads "no network rework completed" -> road-test fee in full; compute counts the row -> halved and floored. E.g. road-test 99.95 -> rule 99.95, compute 49. The same split hits the electrical comeback credit, the rework comeback days and the same-visit comeback multiplier. For the calibration charge it cannot occur (CWW sublet_distance_miles = 0).
- Affected: `warranty.extended.yaml` compute of warranty_ext_mechanical_diagnostic_charge, warranty_ext_electrical_diagnostic_charge, warranty_ext_rework_courtesy_rental, warranty_ext_same_visit_courtesy (and the wording of warranty_ext_calibration_diagnostic_charge, harmless there).
- Bears on: task 1 (demonstration in `1.md`; neither world seeds an outside-shop remedy, so the per-task consequence is checked there). Task 0: not reachable (CWW).

Observations (no demonstrated consequence on a scored value):
- O-1 "then" in three docstrings describes the call's own effect.
- O-2 blueprint summary says the agent records remedies and charges; tools make the charges and rework authorization customer acts.
- O-3 rework_courtesy_rental gate sentence ("When the plan's rework target business days exceed its courtesy rental minimum rework days ... otherwise it pays none") has no compute branch. Checked against every variant: the gate is true for every plan that can have a network rework (Calibration 1>0, Cosmetic 2>0, Glass 1>0, Collision 5>1, Structural 7>1; only the Chip Repair Guarantee, 0>0, is false and its remedy is a chip_credit, never a network rework), so the missing branch never changes a value. Consequence not demonstrable; observation. Side note: for Calibration/Cosmetic/Glass plans (courtesy_rental_days 0) the rule then pays the add-on days (comeback, refinish, source-repair, paid-rental) on a zero allowance — what the rule says, not a rule/compute gap.
- O-4 the rework-authorization tool cannot record a sensor-disturbing rework.
- O-5a/b E1/E4 conditions carry a window / a ">0 days" clause their sentences do not.
- O-5c same-visit rule: with ≥2 covered findings on the visit date, "the covered concern found at the visit", "that rework" and `LATEST(... determination='covered')` (strict-greater date comparison, tie resolved by row order) do not single out one concern — the multi-finding tier's own precondition makes the rule ambiguous. Not reachable in task 1 (one covered finding that day).
- O-6 date ties: "most recent alignment check" when two checks share a date is resolved by `XLATEST` row order, not check_number.
- O-7 `CFIELD` takes the first calibration order of a repair where several exist.
- O-8 same-visit scope sentence restates E4 as an "owed ... when" condition.
- O-9 base cross-problem order sentences ground no edge.
- O-10 billing_error waiver "posted against the rule above" after supersession.
- O-11 "every other inspection is free" lost from the three replacements.
- O-12 alignment tier-1 value collapses to 0 for a Blind Spot Radar source order.
- O-13 five `method` factors are rate + rounding-mode switches.
- O-14 calibration_history_fee surcharge on the network's own failed attempts.
- O-15 same-visit share conjunct "courtesy rental days above zero" is implied at handling time except in an edge.

(Closing checklist is appended below only after both tasks are frozen, revealed and compared.)

## closing_checklist

Written 2026-10-11T03:45Z, after both tasks were frozen (0.md 03:41:53Z, 1.md 03:43:13Z) and revealed (03:43:16Z). Nothing above this heading was changed after the reveal.

| item | status |
| --- | --- |
| per-task files one-to-one with tasks 0..1, `_difficulty.md` alongside | yes (`0.md`, `1.md`, `_difficulty.md`); first revision, no older revision to trace |
| every comparison section carries a PASS | **no** — task 0 SOURCE-FACTOR RED (T0-1), task 1 SOURCE-FACTOR RED (T1-1) |
| extended policies fully covered, scopes pairwise disjoint | yes — task 0 `charter_scope` {calibration charge, calibration goodwill}; task 1 {electrical, mechanical, rework courtesy rental, same-visit courtesy}; union = all six, intersection empty; tools likewise |
| task tools and GT closed; independently generated, frozen uuid8 | yes (§action_binding_and_uuids); every GT write uses one of the six tools with values my blind derivation reproduces |
| every tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, ≥1 owner=user problem, no cycle | yes — task 0: n=1, 1 value_input, user charge; task 1: n=3, 3 value_input, three user writes; difficulty graph acyclic, no cross-task edge |
| every computation: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), per task ≥1 multi-source and ≥1 cross-difficulty, ladders ≥3 tiers stated in the rule, distinct outcomes, real conditions, every factor bears weight against an honest baseline, whole baseline definite and ≠ gold | structure yes (§factor_ladders); weight yes on both worlds (all 31 factors bear weight; whole baselines 79.95/7.20/89.95/89.95/3/7.69 all ≠ gold); **but** task 0's cross-difficulty adas evidence contradicts the adas charter (T0-1) and task 1's proof carries a false world assertion (T1-1) |
| charter self-consistency | **SOURCE-POLICY RED F-1** ("network reworks" in four rules vs all `warranty_rework_complete` rows in compute); no task world in this suite demonstrates its consequence |
| instantiation-stage gates re-run on the final form | not re-run by this audit: the difficulty does not close; the latest snapshot on record is the coordinator's 2026-10-11 run in the brief (all green, traceability deferred) |

Difficulty result: **does not pass the source-layer audit.** Open items: F-1 (charter), T0-1 (task 0 seed vs adas charter), T1-1 (task 1 proof text). Observations O-1..O-15, T0-O*, T1-O* carry no demonstrated consequence.

## revision_2

### charter_global_frozen (revision 2)

- Inputs re-hashed by the auditor (sha256, first 16 hex; all match the round-2 brief): `warranty.extended.yaml` `4384624eebcd1c52` (changed from `9b2c9d0fa76ec3c3`, so every charter-global section below is re-derived in full, not carried forward); `task_tools.py` `d5bb1f5fa4bc5246` (unchanged); masked views `0.masked.json` `7eaa3d064f435b55`, `1.masked.json` `5ecdb9f1367bdfd8` (only `frozen_time`, `user_scenario`, `initial_state`, `_masked_keys`).
- Written 2026-10-11T05:0xZ (system clock), before either round-2 task JSON was opened. Nothing in this section is derived from a round-2 GT. The round-1 text above is left as it was.
- Base copy: every base key still compares equal to `blueprint/products/warranty.yaml`.
- Entry conditions: gate snapshot from the brief, all green, traceability deferred; masked views with hashes supplied. Complete.
- The reworker's list of closed items was not used as evidence. Each item was checked against the charter text and the replay below.

### policy_conflict_scan (r2)

The subjects, computed fields, target tools, owners, triggers and plan scopes are the same as in round 1 (same six policies, same tools). The charge partition by (plan, concern type) and the split of waivers by plan are unchanged, and no new overlap was found. Changed text: all three charge `replaced_by` clauses and rule openings now read "... and every other inspection stays free, whether it finds the concern covered or finds not covered a concern of a kind on which the plan charges no diagnostic fee."

### rule_compute_equivalence (r2)

Scripted check on the round-2 charter, all six policies:
- every compute binding has a `compute_basis` entry, and every entry is a verbatim substring of its rule (zero misses);
- `baseline.rule` appears in every rule;
- no snake_case token appears in any rule;
- factor bindings are disjoint.

Policy-level results:
- **F-1 (round 1) is closed.** The four rules that counted completions now say "the remedy attempts completed on the coverage with the concern resolved / not resolved, network reworks and outside-shop repairs alike". The calibration rule says the same. Their ladder tiers match (for example "a remedy attempt on the coverage (network rework or outside-shop repair) ..."). Compute still counts every `warranty_rework_complete` row, and that table holds exactly network-rework and outside-shop completions (base event meaning: "A network rework or outside-shop repair is finished"; a chip_credit remedy has no completion row). Rule and compute now count the same rows. The round-1 example (an outside-shop completion 10 days before a mechanical charge) now gives the halved fee under both readings.
- **calibration alignment fee (rewritten).** The rule is "follows the four-wheel alignment checks recorded as out of specification on the customer's calibration orders: two or more such checks, the alignment check fee of the calibration tier of the order the coverage was issued on; exactly one such check, the alignment verification fee; no such check, no calibration alignment fee". This equals `out_of_spec_checks: XCOUNT(adas_events, adas_alignment_check, alignment_result='out_of_spec')` plus `alignment_fee`. The `cross_category.reads` and `inputs.history` entries were updated to match: `alignment_corrected` is no longer read, and the history count is out_of_spec. The tier no longer depends on which check is most recent, so O-6 (date ties) no longer applies.
- **O-3 is closed.** The rework courtesy rental compute now ends `courtesy_days_figured: int(...)` and `result: courtesy_days_figured if P('rework_target_business_days') > P('courtesy_rental_min_rework_days') else 0`. The `result` basis is the gate sentence. That is the branch the gate sentence describes, so the gate now has a compute branch.
- Electrical, mechanical, goodwill and same-visit compute are otherwise unchanged from round 1 and were rechecked binding by binding. They remain equivalent.

### action_binding_and_uuids (r2)

`task_tools.py` is unchanged (`d5bb1f5fa4bc5246`). The round-1 conclusions above carry forward on that hash: six distinct `(target_tool, computes)` pairs; six independent uuid8s; tools write without checking anything; no ordering words in docstrings apart from the "then" noted in O-1. O-2 and O-4 (`calibration_needed` hard-coded false) still stand because the tool module did not change.

### prerequisite_graph (r2)

- The edges are the same E1–E4. All are `value_input` and `form: state`. `resolved_by` equals the depended-on policy's `target_tool` for each, every gate binding exists, and the graph is acyclic.
- Every `policy_source` is verbatim in the blocked policy's own rule and in no depended-on rule.
- **O-5a is closed.** The E1 condition is now "The coverage's money history carries a warranty_charge entry for the calibration_fault concern whose inspection determined not_covered." It no longer adds the one-month window.
- **O-5b is closed.** The E4 condition is now "... carries a warranty_rework_authorize entry of kind network_rework." It no longer adds "courtesy_rental_days above zero". The E4 `effect` still says "visit_rental_days rises above zero". That describes what the resolving write does under the rework-rental rule for the in-scope plans, not the gate, so it is accurate.
- E2 and E3 conditions still carry "booked less than one whole calendar month before", which their sentences do not. This was already present in round 1 and I did not flag it then; I am recording it now for completeness as observation O-16. Under the charter a charge is booked on the date the customer accepts it, so neither task world can show a consequence.

### prerequisite_sentences (r2)

The sentences are unchanged from round 1. The four-point test, the single resolving write for each state, and the derivations in the round-1 section all still hold. O-5c (several covered findings on one date) and O-8 (the owed-condition restatement in the same-visit scope sentence) still stand, because that rule text is unchanged. No undeclared cross-problem order appears in the rewritten sentences.

### override_declarations (r2)

- **O-11 is closed.** The three `replaced_by` clauses, and the opening sentences of the three charge rules, now restate that every other inspection stays free, covered or not covered and of a non-fee-bearing kind. Read together, the base clause's whole scope is restated across the three replacements, with no overlap: each replacement's "every other inspection" covers kinds the plan charges no fee on, which never includes another replacement's fee-bearing (plan, type) pair.
- The other conclusions from round 1 carry forward unchanged: goodwill and same-visit follow base, and the rework-rental override is declared. O-10 ("the rule above") still stands.

### factor_ladders (r2)

- Counts are unchanged: calibration charge 5 (4 parameter, 1 method), goodwill 6 (5, 1), electrical 5 (4, 1), mechanical 4 (3, 1), rework rental 5 (4, 1), same-visit 6 (5, 1). The cross_difficulty assignments are unchanged.
- calibration_alignment_fee now has three tiers by count of out-of-spec checks: ≥2, exactly 1, 0. They are disjoint, the fall-through 0 equals the baseline, and the tier values are the source tier's check fee, the verification fee and 0.
  - The ladder is real for this business: repeated alignment faults on the vehicle justify a full check at diagnosis, and a single past fault justifies verification.
  - O-12 still stands: for a Blind Spot Radar source order, tier 1's value is the 0.00 check fee, the same as the fall-through.
  - The factor is single-source (one table, one count). The calibration charge therefore still has no multi-source factor, and task 0 depends on the goodwill's low-use factor for that.
- O-13, O-14 and O-15 still stand (the text they concern is unchanged).

### findings (r2, charter-global)

- F-1: **closed** (see rule_compute_equivalence r2).
- O-3, O-5a, O-5b, O-11: **closed**.
- O-6: no longer applicable.
- Still open as observations, with no demonstrated consequence: O-1, O-2, O-4, O-5c, O-7, O-8, O-9, O-10, O-12, O-13, O-14, O-15, and new O-16.
- **No new charter-global RED.**

## closing_checklist (revision 2)

Written 2026-10-11T05:0xZ, after both round-2 freezes (0.md 05:05:28Z, 1.md 05:05:47Z) and the round-2 reveal (05:05:52Z). The revision_2 charter-global section above was written before the reveal and has not been edited since.

| Item | Status |
| --- | --- |
| Per-task files correspond one-to-one with the tasks; old revision kept | Yes. Round-1 text untouched; `## revision_2` appended to `_difficulty.md`, `0.md` and `1.md`. |
| Every comparison section carries a PASS | Yes. Task 0 and task 1 are PASS on all four relationships. |
| Policies fully covered; scopes pairwise disjoint | Yes. Task 0 claims {calibration charge, goodwill}; task 1 claims {electrical, mechanical, rework rental, same-visit}. |
| Tools and GT closed; independently generated uuid8s | Yes. The tool module is unchanged. |
| Problem trees | Task 0: n=1, one value_input edge, a user write. Task 1: n=3, three value_input edges, three user writes. Both acyclic, with no cross-task edge. |
| Computations | All six have a self-sufficient baseline and 4–6 factors (≥2 parameter, ≥1 method). Each task has ≥1 multi-source factor (task 0: low-use; task 1: multi-service, refinish, share) and ≥1 cross-difficulty factor. Every factor bears weight against an honest baseline. Whole-baseline numbers are 79.95 / 7.20 / 89.95 / 89.95 / 3 / 7.69, all different from gold. Cross-difficulty rows are consistent with their charters. |
| Charter self-consistency | F-1 closed. No new RED. |
| Round-1 REDs | F-1, T0-1 and T1-1 are all closed, verified independently against the charter text, the masked worlds and replay. |
| Reworker's other claimed closures | O-3, O-5a, O-5b, O-11, T0-O2, T1-O3, T1-O4 and T1-O6 are confirmed closed. |
| Regressions | None. Every scored value and every factor-sensitivity figure is identical to round 1. |
| Instantiation-stage gates on the final form | Not re-run by this auditor (Step 0 discipline). The coordinator's post-rework snapshot from the round-2 brief is the record: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, CACHE-DIFF info, forbidden tokens 0, traceability deferred to the KB step. |

Remaining observations, none with a demonstrated consequence:
- O-1, O-2, O-4, O-5c, O-7, O-8, O-9, O-10, O-12, O-13, O-14, O-15, O-16;
- T0-O3, T0-O4;
- T1-O2, T1-O5.

Difficulty result (revision 2): **passes the source-layer audit.**
