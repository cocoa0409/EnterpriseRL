# Policy-task audit: pharmacy_prescription_care / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit). I did not write these artifacts.
- Freeze time: 2026-10-06T06:05Z. This section was written before any task's GT was revealed.
- Freeze hashes (sha256, recomputed by the auditor; they match the orchestrator's brief):
  - `tasks/pharmacy_prescription_care/rx.extended.yaml` `53f46ce9cfe0567d98e63d15b2edcc2c7d6da18466e77abca814b2e3fe5afc64`
  - `tasks/pharmacy_prescription_care/task_tools.py` `e8b94c3e6f9a006b97bec9c1778c9a0b0134f65de93ebbc41f85ed0bb6e9c166`
  - masked views `task_0.view.json` `7155120f…6a969f59` and `task_1.view.json` `347abdba…dcbcd` (both match the brief)
- Fields I read: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/rx.yaml, plus the autoship/member/vet charters for the cross-category reads), `rx.extended.yaml`, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state only), and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to get the exact semantics of COUNT/LATEST/MONTHS/DAYS/CFIELD/XCOUNT/RND).
- Masked fields I did not read before the freeze: every field of `tasks/*.json` other than the three in the views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the instantiate worklog `env/env_0040_pet_supplies_retailer/worklog.md`, and any earlier audit. No search was run over `tasks/`.
- Entry conditions (Step 0): the gate snapshot `/tmp/e40views/policy_task/pharmacy_prescription_care/gate_snapshot.txt` records check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire, all exit 0. check_traceability is deferred until the KB is published, as the brief states. The masked views and their hashes were supplied. The inputs are complete.

### policy_conflict_scan

- Base copy: I compared every top-level key of `rx.extended.yaml` other than `extended_policies` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) by structural equality against `blueprint/products/rx.yaml`. All are **identical**. The base copy is verbatim.
- Extended policies (4): `rx_ext_error_refund` (rx_error_refund/rx_fill_restore, amount_usd, agent tool), `rx_ext_controlled_renewal` (rx_order_create, days_supply_per_fill, user tool), `rx_ext_pharmacy_renewal` (rx_order_create, days_supply_per_fill, agent tool), `rx_ext_household_diet_order` (rx_order_create, days_supply_per_fill, user tool).
- Overlapping subjects. The three rx_order_create policies each declare a disjoint class scope:
  - controlled_renewal: classes with dea_prescriber_required. Only Rx Controlled Substance has it, and only exhausted or expired prescriptions are in scope.
  - pharmacy_renewal: classes with auto_renewal_request (Preventive, Maintenance, Diet, Compounded), prescription at refills_exhausted.
  - household_diet_order: new orders for Rx Prescription Diet with a household prescription.

  No class is in both renewal scopes, because Controlled has auto_renewal_request false. A new order is not a renewal. No two of them reach different conclusions on one subject.
- Eligibility and time anchors. All four inherit the base gates of rx_authorization (DEA, shipping state, weight age), rx_agg_multi_holding (one live prescription per pet, medication and strength) and rx_dispensing_errors (report window, one remedy per fill). None of the extended rules weakens any of them.
- Terminal states: renewal and new order leave pending_vet_authorization. A refund books an rx_error_refund plus an rx_fill_restore and fills_remaining+1, but the status is unchanged; per the base lifecycle a refills_exhausted prescription stays unfillable.
- Cross-category reads:
  - error_refund reads member (tier, status, enrolled_on).
  - controlled_renewal reads autoship (status, frequency of the subscription linked to the renewed prescription).
  - pharmacy_renewal reads member.
  - household reads autoship (pet + sku subscription; customer-wide autoship_events), member and vet (vet_plan_events).

  All are declared in `cross_category`.
- Conflict with a base measure: **conflict found**. See finding F1 below. The base measure `rx_msr_days_supply_dispensed` and the extended "days' supply dispensed" define the same quantity differently.
- Scope exclusivity: there are 4 policies and 2 tasks (M=2). The pairing I derive blind is task 0 = {controlled_renewal ← error_refund} and task 1 = {household_diet_order ← pharmacy_renewal}. The two scopes are disjoint and together cover all 4 extended policies. This is confirmed per task after reveal (charter_scope).

### rule_compute_equivalence

I swept each policy sentence by sentence, rule → compute_basis → compute and back.

- **rx_ext_error_refund**
  - Every binding has a verbatim compute_basis quotation.
  - claim_type, claim_merch, claim_discount, claim_billed, claim_channel, claim_ship and claim_fee are all `LATEST(... event_type='rx_fill')`. This matches "the most recent dispensed fill … is the claimed fill".
  - fills_12m is `COUNT(within_months=12)`. That matches "12 calendar months ending on the refund date", since the evaluator counts MONTHS(d, NOW) in [0, 12).
  - The courtesy_base, courtesy_rate, ship_part, fee_part and loyalty_makegood ladders each match their rule sentence tier for tier.
  - courtesy is rounded on its own, then the sum is rounded. Matches.
  - The scope sentence ("where … error_remake_allowed is false") has no binding. It is scope, not a quantity.
  - Observation O1: `RND` is Python `round` on a float, not strict half-up. On these worlds no value sits on a half cent after float error (3.0795 → 3.08), so there is no consequence.
- **rx_ext_controlled_renewal**
  - Every binding is quoted.
  - claims_open counts error fills minus refund rows minus remake rows in total. It does not match each claim to its fill through original_event_id, as the rule's "against that fill" says. That is equivalent whenever each remedy refers to an error fill (O5).
  - Observation O2: the rule sentence "The packages per fill of the renewal are its days' supply per fill multiplied by the packages the renewed prescription dispenses per day of supply…" has **no compute binding**, although `quantity_per_fill` is an argument of the target tool. The rule still determines the value uniquely, so I can show no consequence. It is an observation.
- **rx_ext_pharmacy_renewal**
  - Every binding is quoted.
  - bag_life (measured / blend / written), member, override (12 months, travel and lost_or_damaged), headroom, return (rx_diet_return_refund, 12 months) and coverage (authorized_on to NOW) all match their rule sentences.
  - "carries the renewed prescription's packages per fill" is carried out by the tool, which copies quantity_per_fill.
- **rx_ext_household_diet_order**
  - Every binding is quoted.
  - The compute runs on the household prescription as the holding: status, pending renewal requests on it, its fills, and its pet + sku Autoship subscription.
  - standing, delivery (XCOUNT autoship_events within 6 months: charge, declined), monitoring (XCOUNT vet_plan_events vet_service_redeem with urinalysis or blood_panel, 3 and 12 months) and tenure (MONTHS from enrolled_on) all match.
  - The CFIELD on autoship does not filter variant_name = 'Autoship Pharmacy', but no task world has a non-pharmacy subscription for the same pet and sku. Observation only.
- Factor tiers in both faces: every `factors[].ladder` tier is a sentence of its rule and a branch of its `decides` binding, and every branch is a stated tier. No tier lives in only one face.

### action_binding_and_uuids

- `(target_tool, computes)` pairs:
  - (refund_dispensing_error_93fa9db7, amount_usd)
  - (place_rx_renewal_order_580a75e8, days_supply_per_fill)
  - (place_pharmacy_renewal_864ea03f, days_supply_per_fill)
  - (place_rx_new_order_4605ac63, days_supply_per_fill)

  Each tool is claimed by exactly one policy.
- uuid8s `93fa9db7`, `580a75e8`, `864ea03f` and `4605ac63` share no prefix, are not sequential, and none is a re-tailed copy of another. They read as independently generated.
- Docstrings: none names another tool, a policy id, or an ordering word (before, after, first, then). One observation (O8): `place_rx_new_order_4605ac63.ships_with_rx_id` says "as returned by the prescription lookup **or by the receipt of the order that opened it**". That hints that the companion prescription may have been opened by an order earlier in the same contact. It bears on which row is the companion; see the task 1 file.
- Owners: refund is agent, controlled renewal order is user, pharmacy renewal is agent, new order is user. This matches each rule ("the customer places the renewal order personally", "owed by the pharmacy without the customer asking", "the customer places the new order personally").
- None of the tool bodies checks status, window, dedup or any prerequisite. Each body only creates or updates rows; I read every function body in `task_tools.py`.

### prerequisite_graph

- Every policy has `prerequisite` filled in: error_refund `[]`, pharmacy_renewal `[]`, controlled_renewal 1 edge, household_diet_order 1 edge.
- Edge A: controlled_renewal → `rx_ext_error_refund`.
  - kind value_input, gate `claims_open` (a real compute binding), form state, no fallback_reason (correct for state form).
  - resolved_by `refund_dispensing_error_93fa9db7`, which is the depended-on target_tool. It books rx_error_refund + rx_fill_restore, so claims_open falls by one and fills_delivered falls by one. `effect` holds.
- Edge B: household_diet_order → `rx_ext_pharmacy_renewal`.
  - kind value_input, gate `pending_renewal_requests` (a real binding), form state, no fallback_reason.
  - resolved_by `place_pharmacy_renewal_864ea03f`, the depended-on target_tool. It creates an rx_authorization_requests row with request_kind renewal and outcome pending against the renewed prescription, so pending_renewal_requests goes from 0 to 1. `effect` holds.
- Both `problem`s point to extended policy ids in this file, never to a base policy and never to the policy itself. The graph has 2 disjoint edges and no cycle.
- Both `policy_source`s are verbatim sentences of the blocked policy's own `rule`. I located each by string match.
- `condition` of edge A adds "which comes with its rx_fill_restore credit-back row" beyond the sentence. The only write that books a refund entry books both rows in one call, so this is no real strengthening (O10).
- `condition` of edge B names "status active, or an rx_authorization_requests row of request_kind renewal with outcome pending refers to it". That is exactly the sentence.
- Neither prerequisite field contains authoring-viewpoint wording.

### prerequisite_sentences

- **Edge A**: "The days' supply per fill a renewal order asks for is fixed only after every dispensed fill of the renewed prescription that carries a dispensing-error claim also carries a refund entry on the pharmacy ledger."
  - Four-point test:
    - (1) It joins the own result (days' supply per fill) to the waited-on state with "only after".
    - (2) It is in state form: a refund entry on the pharmacy ledger against each claimed fill, a record-visible state named in ledger words, with no tool and no performer.
    - (3) It has no tool name, policy id, snake_case or row id.
    - (4) Its strength matches the condition. The set is closed by kind: every claimed dispensed fill of the renewed prescription.
  - Which write brings the state about: only one write in this difficulty books a refund entry, `refund_dispensing_error_93fa9db7`. No other task tool writes rx_error_refund.
  - Derivation: the sentence says each claimed fill must carry a refund entry. The ledger is read through find_rx_events. The rule that books such an entry is `rx_ext_error_refund` ("the refund is paid to the original payment, and the refunded fill is credited back"), and its scope (class without free remake) is exactly the DEA class of the blocked policy. The resolving action is refunding the claimed fill. There is a single reading.
  - The depended-on rule does not restate the sentence.
  - The stability-ceiling sentence of the same rule also says "without a refund or free-remake entry". Remakes are impossible for the only in-scope class (error_remake_allowed false), so there is no second resolving action.
- **Edge B**: "A new order's days' supply per fill is not set until the household prescription is active or carries a renewal request still awaiting the veterinarian's answer."
  - Four-point test:
    - (1) "not until".
    - (2) State form: prescription status, or a pending renewal request recorded against it, read through find_rx_prescriptions and find_rx_authorization_requests.
    - (3) No tool name or id.
    - (4) Same strength as the condition.
  - Which write brings the state about: no write in this difficulty makes a prescription active, since authorization is a system transition. The only write that records a renewal request against a prescription is `place_pharmacy_renewal_864ea03f`.
  - Derivation: `rx_ext_pharmacy_renewal` says "The pharmacy sends that renewal to the prescribing veterinarian as a renewal request recorded against the renewed prescription, which stays awaiting the veterinarian's answer until it is approved or denied". That is the same words as the sentence. The resolving action is the pharmacy-placed renewal of the household prescription.
  - Observation O9: `place_rx_renewal_order_580a75e8` (user) opens a pending renewal prescription, which a reader might also call "a renewal request awaiting the vet". It records no authorization request, though, and its policy is limited to DEA classes, so it never applies to a prescription diet. There is no second candidate under the policies.
  - The depended-on rule does not restate the sentence.
- Undeclared cross-problem orders in rules: none found. The base summary's "a prescription is authorized before any fill and a fill exists before any remedy on it" is domain order and grounds no edge. No base sentence is used to ground an edge.

### override_declarations

- **rx_ext_error_refund** (refs rx_dispensing_errors, rx_evt_pricing, rx_agg_shipping):
  - rx_dispensing_errors:
    - Error definition: followed.
    - Report window: followed ("within the report window").
    - One remedy per fill: inherited.
    - "The customer chooses a free remake … where error_remake_allowed is true, otherwise a refund": followed (scope limited to remake-not-allowed).
    - Refund sentence: **declared** in overwrite, and the replacement is unique.
    - "never resold / need not be returned": inherited.
    - "dissatisfaction not covered": inherited.
  - rx_evt_pricing: "Amounts round half up to the cent" is followed. The other pricing sentences govern billing, not the refund.
  - rx_agg_shipping: the shipping-fee and threshold sentences govern charges on fills, not the refund. Observation O3: ship_part adds `rx_shipping_fee_usd` "so that the replacement order ships at no cost to the customer" even when the customer's active Tailwise Plus membership already pays no standard shipping under rx_agg_shipping. No scored quantity is decided two ways, so this is a business incoherence only. No task world has a Plus member on this policy.
  - Observation O4: for a severe Autoship claim the shipping portion is the standard fee alone, which can be less than the shipping actually charged on that fill. No task world has this.
- **rx_ext_controlled_renewal / rx_ext_pharmacy_renewal / rx_ext_household_diet_order** (refs rx_agg_multi_holding, rx_authorization, rx_renewals, rx_transfers):
  - multi_holding dedup: inherited.
  - rx_authorization gates (DEA, state, weight age), contact timing and approval terms: inherited and untouched.
  - rx_renewals:
    - "new prescription with origin renewal and renewal_of_rx_id": followed by both renewal tools.
    - "auto_renewal_request true → pharmacy places itself / false → customer must ask": followed. Controlled "customer places personally" narrows "must ask" to the owner of the write and changes no scored quantity.
    - "never extends the old prescription's expiry or restores its fills": followed.
    - Autoship relink once active: future, untouched.
  - rx_transfers: not touched.
  - `overwrite: []` is consistent with the sentence-level conclusions for these refs.
  - However, both renewal rules state a quantity that the base charter already defines under the same name in a base policy outside their refs. See F1.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source (non-fall-through tiers) | cross_difficulty | stated in rule / compute |
|---|---|---|---|---|---|---|---|
| error_refund | courtesy_basis | method | courtesy_base | 3 | yes (claimed-fill error_type + 12-month fill count) | - | yes / yes |
| error_refund | courtesy_percentage | parameter | courtesy_rate | 3 | tier + status of one membership row (one record) | member | yes / yes |
| error_refund | replacement_shipping | parameter | ship_part | 3 | error_type + fill_channel of one fill row (one record) | - | yes / yes |
| error_refund | replacement_service_fee | parameter | fee_part | 3 | fill row + class parameters | - | yes / yes |
| error_refund | loyalty_makegood | parameter | loyalty_makegood | 3 | fill row + membership enrolled_on | member | yes / yes |
| controlled_renewal | delivery_rhythm | method | fill_length | 3 | autoship status/frequency + class max; autoship + fill history | autoship | yes / yes |
| controlled_renewal | stability_ceiling | parameter | stability_ceiling | 3 | open claims + delivered (fills, refunds, restores) | - | yes / yes |
| controlled_renewal | adherence_ceiling | parameter | adherence_ceiling | 3 | days dispensed / authorized_on + fill count | - | yes / yes |
| controlled_renewal | exhaustion_ceiling | parameter | exhaustion_ceiling | 3 | status + closed_on / expires_on (one record) | - | yes / yes |
| pharmacy_renewal | bag_life | method | bag_life | 3 | fill count + override rows | - | yes / yes |
| pharmacy_renewal | member_supply_ceiling | parameter | member_supply_ceiling | 3 | membership + fill count | member | yes / yes |
| pharmacy_renewal | override_ceiling | parameter | override_ceiling | 3 | override rows + fill count | - | yes / yes |
| pharmacy_renewal | validity_headroom_ceiling | parameter | headroom_ceiling | 3 (2 reachable, see F3) | status + dates (one record) | - | yes / yes |
| pharmacy_renewal | return_ceiling | parameter | return_ceiling | 3 | return rows + fill count | - | yes / yes |
| pharmacy_renewal | supply_coverage_ceiling | parameter | coverage_ceiling | 3 | fills + authorized_on | - | yes / yes |
| household | household_length | method | household_length | 3 | household rx status / auth requests + autoship subscription | autoship | yes / yes |
| household | standing_ceiling | parameter | standing_ceiling | 3 | tier + status (one record) | member | yes / yes |
| household | delivery_record_ceiling | parameter | delivery_ceiling | 3 | charge rows + declined rows | autoship | yes / yes |
| household | monitoring_ceiling | parameter | monitoring_ceiling | 3 | urinalysis / blood panel rows over 2 windows | vet | yes / yes |
| household | tenure_ceiling | parameter | tenure_ceiling | 3 | enrolled_on + status (one record) | member | yes / yes |

- Counts per policy:
  - error_refund: 5 factors (1 method, 4 parameter). After F2 strikes replacement_service_fee: 4 (1 method, 3 parameter).
  - controlled_renewal: 4 (1, 3).
  - pharmacy_renewal: 6 (1, 5). After F3: 5.
  - household: 5 (1, 4).

  Every policy stays within 4 to 6 factors with ≥2 parameter and ≥1 method.
- Per task (blind pairing):
  - Task 0 has a multi-source factor (courtesy_basis, delivery_rhythm, stability) and cross-difficulty factors (member ×2, autoship).
  - Task 1 has a multi-source factor (household_length, delivery_record) and cross-difficulty factors (autoship ×2, member ×3, vet).
- Disjoint bindings and decides: each factor's `decides` is an input of `result`, never `result` itself. Binding sets are disjoint within each policy.
- Distinct outcomes: within every ladder, the tiers select different formulas or values. For example 20/15/0 percent; ship + std / std / ship; max / written + step / written; cadence / interval / default.
- Labels:
  - delivery_rhythm, bag_life and household_length are genuine method changes (cadence vs measured interval vs written/default).
  - courtesy_basis (O6) chooses which amount the percentage is figured on: whole billed vs merchandise net vs none. I accept it as a method, a gross vs net computation basis that retailers really do vary, but it sits on the boundary of "a different number substituted into the same formula".
  - All `parameter` labels select numbers.
- Baselines:
  - Every factor's fall-through equals its `baseline` binding.
  - Each policy's `baseline.rule` is a sentence of its rule and gives a definite number from the records:
    - refund = merchandise − discount + shipping + service fee, rounded
    - controlled renewal = renewed days, capped at the class max
    - pharmacy renewal = renewed days, capped at the class max
    - household = 30, capped at the class max
  - `baseline.params` names the keys actually used.
- Realism of conditions and outcomes:
  - **F2 (RED)**: replacement_service_fee is not a real ladder within its policy's scope.
  - **F3 (RED)**: validity_headroom_ceiling's status condition restates the policy's scope.
  - Observation O7: membership tier, membership tenure and Autoship payment record deciding a prescription's days' supply (household standing, tenure and delivery_record; pharmacy_renewal member_supply_ceiling) are weak business analogues. Payer benefit tiers do govern 30- vs 90-day supply in real pharmacy practice, so I cannot show that no such business would publish them. Observation only.

### findings

**F1. SOURCE-POLICY RED: "days' supply dispensed" is defined twice, as gross and as net of restored fills.**
- Bears on: task 0 (consequence shown there) and task 1 (cited; no consequence on its world).
- Symptom: the extended renewal rules use "the days' supply dispensed on the renewed prescription" to mean every rx_fill row's days_supply, restored fills included. The base charter defines the same quantity, under that name, net of restored fills.
- Evidence:
  - Base `measures` (verbatim copy, `rx.extended.yaml` L668-670): `rx_msr_days_supply_dispensed`, window "life of the prescription", measure "sum of days_supply of rx_fill rows of this prescription minus that of fills restored by rx_fill_restore". It is used by the base rx_evt_fill_eligibility: "for controlled substances the total rx_msr_days_supply_dispensed after the fill may not exceed controlled_quantity_limit_days".
  - `rx_ext_controlled_renewal.rule`: "The adherence ceiling compares the days' supply dispensed on the renewed prescription with the calendar days from its authorization date to the order date". Its compute is `days_dispensed: SUM('rx_events', 'days_supply', event_type='rx_fill')`, which is gross and does not subtract restores.
  - `rx_ext_pharmacy_renewal.rule` "takes the days' supply dispensed on the renewed prescription as a percentage…" has the same gross compute.
- Root cause: the extended rules reuse the base charter's named quantity with a different definition and do not declare the departure. Neither policy's `overwrite` names it, and rx_evt_fill_eligibility is not in their `base_policy_refs`.
- Consequence: wherever a restore row exists at handling time, the two definitions give different coverage percentages. On task 0 they give different scored days and packages (28/56 vs 21/42; see `0.md`).
- Affected: `rx.extended.yaml` → `rx_ext_controlled_renewal` (rule adherence sentence, compute `days_dispensed`) and `rx_ext_pharmacy_renewal` (rule coverage sentence, compute `days_dispensed`).

**F2. SOURCE-FACTOR RED: `rx_ext_error_refund.replacement_service_fee` is not a real ladder within the policy's scope.**
- Bears on: task 0.
- Evidence:
  - Scope sentence: "where the prescription's class does not allow a free remake (error_remake_allowed is false)". Variants: error_remake_allowed is false **only** for Rx Controlled Substance (L392). Preventive, Maintenance, Diet, Short-Course and Compounded are all true.
  - Tier 1: "severe AND the class requires an adult signature on delivery". Rx Controlled Substance has signature_required true (L382), so the class condition holds of **every** customer who reaches this write.
  - Tier 2: "severe AND the class carries a compounding fee above zero AND requires no adult signature". Only Rx Compounded Medication has compounding_fee_usd > 0 (L436), and it has error_remake_allowed true (L447), so it is outside the scope. **Tier 2 is unreachable.**
- Consequence: in practice the ladder is two tiers (severe / not severe). The class condition restates scope, and one of the three stated tiers can never be selected. The factor fails the real-ladder test. Once it is struck, error_refund still has 4 factors (1 method, 3 parameter), so the count bounds hold, but the factor is still recorded as failing.
- Affected: `rx_ext_error_refund.factors[replacement_service_fee]` and the matching rule sentence and `fee_part` compute.

**F3. SOURCE-FACTOR RED: `rx_ext_pharmacy_renewal.validity_headroom_ceiling` has a condition that restates the scope, and its fall-through is unreachable.**
- Bears on: task 1.
- Evidence:
  - Scope: "for a prescription whose class carries auto_renewal_request, once the prescription stands at refills_exhausted after its last authorized fill".
  - Tiers: "where it stands at refills_exhausted with at least headroom_days_min such days … ; where it stands at refills_exhausted with fewer such days … ; otherwise …".
  - Every customer who reaches this write stands at refills_exhausted, so the "otherwise" tier (the fall-through and the baseline) can never be selected.
- Consequence: the ladder has two reachable tiers (≥60 / <60 days), below the three-tier minimum, and the "stands at refills_exhausted" condition divides no customers. Once the factor is struck, pharmacy_renewal still has 5 factors, so the count bounds hold, but the factor is still recorded as failing.
- Affected: `rx_ext_pharmacy_renewal.factors[validity_headroom_ceiling]`, the rule's validity-headroom sentence and `headroom_ceiling` compute.

**Observations (no consequence shown):**
- O1: RND is float round, not strict half-up.
- O2: the packages-per-fill rule sentence of controlled_renewal has no compute binding.
- O3: the replacement shipping make-good ignores Plus free shipping.
- O4: a severe Autoship claim's shipping portion can be below the shipping charged.
- O5: claims_open counts totals, not per-fill matches.
- O6: courtesy_basis's method label is borderline.
- O7: realism of the membership, tenure and Autoship-payment ceilings on days' supply.
- O8: the `ships_with_rx_id` docstring hints at a companion opened by an order in the same contact.
- O9: the customer renewal-order tool could be misread as producing "a renewal request awaiting the vet".
- O10: edge A's condition mentions the credit-back row.

## closing_checklist

Written 2026-10-06T06:20Z, after both reveals. This section is post-reveal and separate from the frozen charter-global section above. **The difficulty does not close: not every task passes all four relationships.**

- Audit files: `0.md` and `1.md` correspond one to one with `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. This is the first revision; there are no older revisions.
- Per-task verdicts:
  - **Task 0**:
    - policy SOURCE-POLICY RED (F1, with a demonstrated second answer of 21 days / 42 tablets vs gold 28 / 56)
    - tree PASS
    - factors SOURCE-FACTOR RED (F2)
    - unique solution SOURCE-TASK RED (F1 consequence)
  - **Task 1**:
    - policy PASS (F1 cited, no consequence on this world)
    - tree SOURCE-CHAIN RED (closure gate `household_days` is not a binding)
    - factors SOURCE-FACTOR RED (F3; no near-miss in the pharmacy-renewal computation)
    - unique solution PASS
- Coverage and scopes:
  - charter_scope task 0 = {rx_ext_error_refund, rx_ext_controlled_renewal}; task 1 = {rx_ext_pharmacy_renewal, rx_ext_household_diet_order}.
  - The scopes are pairwise disjoint and cover all 4 extended policies and all 4 task tools.
  - Every uuid8 is independent (see `action_binding_and_uuids`).
- Trees:
  - Each task has 1 prerequisite problem, 1 value_input edge and an owner=user root write.
  - The difficulty graph has 2 disjoint edges and is acyclic. No cross-task reference creates a cycle.
- Factors:
  - Every computation's baseline is self-sufficient and gives a definite number ≠ gold (20.53 vs 39.06; 14 vs 28; 35 vs 40; 30 vs 40).
  - Every declared factor bears weight on its own world.
  - Counts stay within bounds even after striking F2 and F3.
  - Failures: the real-ladder test (F2, F3) and the near-miss test (task 1, pharmacy renewal).
- Gates on the final form: the artifacts are unchanged since the orchestrator's gate snapshot. The extended charter and task_tools hashes are identical to the brief, and the task JSONs were not modified by this audit. The auditor did not re-run the gates, because the difficulty does not close in this revision.

## revision_2

### charter_global_frozen (r2)
- Auditor: the same independent auditor. Freeze time: 2026-10-06T09:30Z, written before any round-2 task JSON was opened. Nothing in this section is derived from a round-2 GT.
- Round-1 text above is left untouched.
- Hashes, recomputed by the auditor and matching the coordinator's brief:
  - `rx.extended.yaml` `0d518436c482d09cda000f3cbe576350043ac02fa6bfbb28f6ced26ac1364315` (**changed** from r1 `53f46ce9…`)
  - `task_tools.py` `c8af296d5d6087227ceb68c65f4097b7180994331f555654ac9b4e374347868f` (**changed** from r1 `e8b94c3e…`)
  - views `task_0.r2.view.json` `890bb349…f688`, `task_1.r2.view.json` `40f0ceab…32e0`
  - blueprint files unchanged (mtime 04:34, before round 1)
- Both shared inputs changed, so every charter-global section below is **re-derived in full**, not carried forward. The reworker's item list was not used as evidence; every claim below is checked against the artifacts.
- Entry conditions: `/tmp/e40views/policy_task/pharmacy_prescription_care/gate_snapshot_r2.txt` records all 7 gates at exit 0 (replay now closes 26/26 rows for task 1). check_traceability is deferred. Inputs are complete.
- Masked until the per-task r2 derivations are frozen: everything in `tasks/*.json` outside the views, and the worklog.

### policy_conflict_scan (r2)
- Base copy: all 10 base keys are still structurally identical to `blueprint/products/rx.yaml`.
- What changed in the extended policies:
  - `rx_ext_error_refund`: the `replacement_service_fee` factor was removed. The service-fee portion is now simply "the service fee charged on the claimed fill". A new factor `waiting_credit` was added: if the claim is severe, ≥10 days from the claimed fill's dispense date to the refund date adds 4.00, and 5-9 days adds 2.00. `overwrite.replaced_by` was rewritten to match.
  - `rx_ext_controlled_renewal`: `rx_evt_fill_eligibility` was added to `base_policy_refs`. The adherence sentence now defines "the days' supply dispensed … which is the days' supply of its dispensed fills less the days' supply of the fills credited back to it". The compute `days_dispensed` now subtracts `SUM(days_supply of rx_fill_restore)`.
  - `rx_ext_pharmacy_renewal`: `rx_evt_fill_eligibility` was added to the refs. The scope now also covers a prescription that "stands at expired with fills still remaining because its renewal was not placed ahead of expires_on, and no renewal of it has been placed". The validity-headroom fall-through now reads "for a renewed prescription that stands at expired". Coverage is net of credited-back days.
  - `rx_ext_household_diet_order`: textually unchanged.
- What changed in the tools:
  - `refund_dispensing_error_93fa9db7` now writes `days_supply = <the refunded fill's days_supply>` on the `rx_fill_restore` row, and its docstring says so.
  - `place_rx_new_order_4605ac63.ships_with_rx_id` no longer says "or by the receipt of the order that opened it".
  - The other tool bodies are unchanged.
- Overlapping subjects:
  - The pharmacy_renewal scope (auto-renewal classes, exhausted or expired with fills) and the controlled_renewal scope (DEA class only, which has auto_renewal false) stay disjoint.
  - The expanded pharmacy_renewal scope agrees with base `rx_renewals`. The base says the pharmacy renews "renewal_request_lead_days … before expires_on when fills remain". An expired prescription with fills left and no renewal is that same obligation, missed.
  - No new conflict.
- **F1 is resolved at its root.**
  - "Days' supply dispensed" is now defined net of credited-back fills in both renewal rules. That matches base `rx_msr_days_supply_dispensed`.
  - The compute subtracts restore-row `days_supply`.
  - The tool now writes that field. The r1 restore row carried no `days_supply`, so without this change a net compute would silently have stayed gross.
  - The rule, the compute, the tool and the base now give one value.
- Scope partition: unchanged from r1. Four policies, two pairs, disjoint, all covered. Confirmed per task after reveal.

### rule_compute_equivalence (r2)
- `rx_ext_error_refund`:
  - `claim_fee` is quoted from "plus the service fee charged on that fill". `claim_date` and `days_waiting` are quoted from "counted in calendar days from the claimed fill's dispense date to the refund date" and computed as `DAYS(LATEST rx_fill event_date, NOW)`.
  - `waiting_credit` matches its three tiers sentence for sentence.
  - `result` sums merch + ship + claim_fee + courtesy + loyalty + waiting, which matches the rule's sum sentence and `overwrite.replaced_by` word for word.
  - No orphan bindings and no unimplemented sentence.
  - O1 (RND is float round) still applies. There is no half-cent value on these worlds.
- `rx_ext_controlled_renewal`: `days_dispensed` is quoted from the new net sentence and computed net. All other bindings are unchanged and still quoted. O2 (the packages-per-fill sentence has no binding) is **unchanged**.
- `rx_ext_pharmacy_renewal`: `days_dispensed` and `coverage` are net, quoting the new sentence. `headroom_ceiling`'s else-branch matches "otherwise, for a renewed prescription that stands at expired".
- The new scope clause ("and no renewal of it has been placed") is scope, not a quantity.
- One observation: the `inputs.history` block of `rx_ext_pharmacy_renewal` does not list the new `rx_fill_restore` days_supply sum. That block is descriptive metadata, not the compute, so there is no consequence (O11, new).
- `rx_ext_household_diet_order`: unchanged, and equivalent.
- In every policy, each factor tier appears in both the rule and the compute.

### action_binding_and_uuids (r2)
- The `(target_tool, computes)` pairs and the four uuid8s are unchanged and unique.
- Docstrings:
  - The refund docstring adds "carrying that fill's days' supply". It has no ordering word and names no other tool.
  - **O8 closed**: `ships_with_rx_id` now reads only "as returned by the prescription lookup".
- No tool body checks any precondition or prerequisite. The new line in the refund tool reads the refunded fill's own row to copy `days_supply`. It validates nothing.

### prerequisite_graph (r2)
- Both edges are byte-identical to r1 (problem, kind, gate, form, policy_source, condition, resolved_by, effect).
- Every `gate` is a real compute binding: `claims_open` in controlled_renewal and `pending_renewal_requests` in household.
- The graph is acyclic. Each `policy_source` is still a verbatim sentence of its own rule.
- O10 is unchanged.

### prerequisite_sentences (r2)
- Edge A and Edge B sentences are unchanged and pass the four-point test as in r1.
- Single writer for each:
  - Only `refund_dispensing_error_93fa9db7` books a refund entry.
  - Only `place_pharmacy_renewal_864ea03f` records a renewal request against a prescription.
- The expanded pharmacy_renewal scope does not add a second writer for Edge B: the same tool and policy cover both scope branches. The derivation from r1 stands.
- No new cross-problem order appears in any rule. The added scope clause "no renewal of it has been placed" is a scope condition on the policy itself, not a dependency on another problem.
- O9 is unchanged.

### override_declarations (r2)
- `rx_ext_error_refund`: the superseded clause is the same base sentence. `replaced_by` now names the new six-part sum, and the merged meaning is unique.
  - The removed service-fee surcharge leaves "the service fee charged on the claimed fill". That is consistent with the base, which refunds service fees where error_refund_includes_shipping is true, as it is for every class.
  - The new waiting credit is part of the declared replacement sum.
  - O3 and O4 are unchanged.
- `rx_ext_controlled_renewal` and `rx_ext_pharmacy_renewal` now cite `rx_evt_fill_eligibility`. Checked sentence by sentence:
  - fill gates (active, fills ≥ 1, before expiry, refill-too-soon): they govern fills, and the renewal is not a fill. Untouched.
  - days' supply per fill ≤ max_days_supply_per_fill: followed ("never more than the class maximum").
  - controlled total days via `rx_msr_days_supply_dispensed`: the extended now uses the same net definition. Consistent.
  - partial fill, compounding lead time, exhaustion and expiry transitions: untouched.

  `overwrite: []` therefore holds.
- **F1 closed.**

### factor_ladders (r2)

| policy | factor | effect | tiers (all reachable within scope?) | counts change |
|---|---|---|---|---|
| error_refund | courtesy_basis | method | 3 (yes) | — |
| error_refund | courtesy_percentage | parameter | 3 (yes) | — |
| error_refund | replacement_shipping | parameter | 3 (yes: a Controlled prescription may ship by Autoship, autoship_eligible true) | — |
| error_refund | **waiting_credit (new)** | parameter | 3 (≥10 d: 4.00 / 5-9 d: 2.00 / else: 0); all reachable for Controlled (report window 14 d) | replaces replacement_service_fee |
| error_refund | loyalty_makegood | parameter | 3 (yes) | — |
| controlled_renewal | delivery_rhythm, stability, adherence, exhaustion | 1 method, 3 parameter | 3 each (yes) | adherence now net |
| pharmacy_renewal | bag_life, member_supply, override, **validity_headroom**, return, supply_coverage | 1 method, 5 parameter | headroom: exhausted ≥60 / exhausted <60 / **expired with fills (now in scope)**; all reachable | — |
| household | household_length, standing, delivery_record, monitoring, tenure | 1 method, 4 parameter | unchanged | — |

- Counts: error_refund 5 (1 method, 4 parameter); controlled_renewal 4 (1, 3); pharmacy_renewal 6 (1, 5); household 5 (1, 4). All within bounds, with nothing struck.
- Distinct outcomes in every ladder. waiting_credit selects 4.00, 2.00 or 0.
- Each fall-through equals its baseline. The waiting_credit baseline is "0", the value baseline.rule gives, since baseline.rule has no waiting credit.
- Realism:
  - waiting_credit is a goodwill credit graded by how long the customer held the wrong product, a real make-good pattern. One sub-observation (O12, new): it counts from the dispense date, not from the report date, so it also rewards the customer's own delay in reporting. That is a judgment about design, not a demonstrable defect.
  - The validity-headroom tiers now divide real cases (exhausted early, exhausted late, expired with fills left).
  - O6 and O7 are unchanged.
- **F2 closed**: replacement_service_fee no longer exists, and its replacement is a real ladder on this scope.
- **F3 closed**: validity_headroom_ceiling's status condition now divides customers within scope, and its fall-through is reachable (expired with fills remaining).

### findings (r2, charter-global)
- F1: **closed** (rule, compute, tool and base agree on net days).
- F2: **closed**.
- F3: **closed**.
- O8: **closed** (docstring residue removed).
- O1 through O7, O9 and O10 are unchanged, and the reworker claimed no change for them. They remain observations.
- New observations: O11 (the `inputs.history` block omits the restore-day sum) and O12 (waiting_credit counts from the dispense date). No new RED at the charter level.

### closing_checklist (r2)
Written 2026-10-06T09:45Z, after both r2 reveals.

- Audit files: `0.md` and `1.md` each carry an r1 section and an appended `## revision_2`, with `_difficulty.md` alongside. The r1 text is untouched.
- Per-task verdicts:
  - **Task 0**: policy PASS, tree PASS, factors PASS, unique solution PASS.
  - **Task 1**: policy PASS, tree PASS, factors PASS, unique solution PASS.
- Coverage and scope: task 0 = {rx_ext_error_refund, rx_ext_controlled_renewal}; task 1 = {rx_ext_pharmacy_renewal, rx_ext_household_diet_order}. They are disjoint and cover all 4 extended policies and all 4 tools. The uuid8s are independent and unchanged.
- Trees: each task has 1 prerequisite, 1 value_input edge and an owner=user root. The difficulty graph has 2 disjoint edges and is acyclic.
- Factors: every computation's baseline is self-sufficient and gives a definite number different from gold:
  - refund 20.53 vs 37.56
  - controlled renewal 14 vs 21
  - pharmacy renewal 35 vs 40
  - new order 30 vs 40

  Counts are 5 / 4 / 6 / 5 factors (1 method each), all ladders have three reachable, distinct tiers, every factor bears weight, each task has a multi-source and a cross-difficulty factor, and each computation has a genuine near-miss.
- Status of every item:
  - **Closed:** F1, F2, F3, O8, T0-1, T0-2, T0-O2, T0-O5, T1-1, T1-2, T1-3, T1-O1, T1-O2.
  - **Unchanged observations:** O1-O7, O9, O10, T0-O1, T0-O3, T0-O4, T1-O3.
  - **New observations:** O11, O12, T1-O4, T1-O5.
  - New REDs: none. Regressions: none.
- Gates on the final form: the orchestrator's r2 snapshot (`gate_snapshot_r2.txt`) shows all 7 gates green. The audited hashes (`rx.extended.yaml` `0d518436…`, `task_tools.py` `c8af296d…`) were the ones in force during this audit. I did not re-run the gates myself, per Step 0.
- **The difficulty passes the source-layer audit in revision 2.** All four relationships hold for both tasks.
