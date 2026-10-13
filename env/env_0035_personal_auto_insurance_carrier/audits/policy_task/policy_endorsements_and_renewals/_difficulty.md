# Policy-task audit — policy_endorsements_and_renewals / charter-global

## charter_global_frozen

- Scenario: env/env_0035_personal_auto_insurance_carrier; difficulty: policy_endorsements_and_renewals; category: auto; M=2 (tasks 0, 1).
- Auditor: erl-task-policy-audit (independent auditor agent; not the author of the artifacts).
- Freeze time: 2026-10-05T10:53Z (written before any task's GT was revealed; this section contains nothing derived from a revealed GT).
- Freeze hashes (verified by the auditor with sha256sum against both the masked views and the live files):
  - `91478d7116eadbf337ffc84fb850b25f3cc3bce0443daf0f5079855ab68d42ec  auto.extended.yaml`
  - `4cef862a0b9730e9885f1b3ee987e4927816be29cc4d39818678a7db11e1b303  task_tools.py`
  - `9b9c5dd0e4b9cd99cfd33faa003805ccc7b1a4c8fa3b645d0aecd4279e28fc89  task_0.view.json`
  - `85a822275d8e0a389a764cceebc9b0fcca0eaa1624c773ef7a2876360f5e6881  task_1.view.json`
- Permitted and read: blueprint/blueprint.yaml (grep only), blueprint/db_schema.json, blueprint/share_tools.py, blueprint/products/{auto,rental,roadside,physdmg,telematics,billing}.yaml, the masked views in /tmp/erl35_views/policy_endorsements_and_renewals/ (auto.extended.yaml, task_tools.py, task_*.view.json = frozen_time + user_scenario + initial_state), erlbench/ (listing), and the compute-DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/within_months/CFIELD/LATEST definitions only).
- Masked and not read before freezing: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty worklog.md, the scenario worklog.md, any prior audit.
- Entry conditions (Step 0): gate snapshot supplied (/tmp/erl35_views/policy_endorsements_and_renewals/GATES.txt): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred (KB unpublished). Masked views and MANIFEST.sha256 supplied; hashes re-verified (match). Input complete.
- Base copy: lines 1-1606 of auto.extended.yaml are byte-identical to blueprint/products/auto.yaml (diff shows only the appended banner + `extended_policies`).

### policy_conflict_scan

Extended policies (5) and their claims:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| auto_ext_rental_option_removal_credit | auto_coverage_change, auto_return_premium | record_rental_removal_credit_1b50ed15 (agent) | return_premium | [] |
| auto_ext_total_loss_vehicle_removal_credit | auto_return_premium | book_vehicle_removal_credit_524db3a4 (agent) | return_premium | <- rental credit (value_input, state) |
| auto_ext_insured_cancellation_refund | auto_insured_cancel, auto_return_premium | sign_cancellation_request_695fb1aa (user) | return_premium | <- vehicle removal credit (value_input, state) |
| auto_ext_driver_addition_premium | auto_additional_premium | book_driver_addition_premium_cd2c8cbf (agent) | additional_premium | [] |
| auto_ext_named_driver_exclusion_credit | auto_driver_exclude, auto_return_premium | sign_named_driver_exclusion_c094ed6f (user) | return_premium | <- driver addition premium (value_input, state) |

- Overlapping subject `auto_return_premium` (four policies + base auto_insured_cancellation): each extended policy binds the RP to a distinct source object (the ended rental option's coverage change entry / the vehicle removal entry / the cancellation request / the exclusion endorsement). No two extended policies claim the same (tool, quantity). No trigger/eligibility/terminal-state conflict among the five extended policies themselves.
- Interplay checked: the removed vehicle's physical damage (PD) premium is treated as fully earned both in the vehicle removal credit (subtracted from the drop) and in the cancellation refund (subtracted from the returnable premium). This is not a double count: because the removal credit withholds the PD premium, the term's written premium still carries it whole, and the cancellation excludes it from the prorated base once.
- Interplay checked: the rental option premium enters the vehicle removal drop and the rental credit; the offset clause removes it from the drop once the rental credit's entry stands; no double credit.
- Cross-category read boundaries: CONFLICTS FOUND with sibling charters' published treatment of the same quantities (rental, roadside, physdmg, telematics) — see findings G2.
- Scope: task 0 = {rental credit, vehicle removal credit, cancellation refund}; task 1 = {driver addition premium, exclusion credit}. Pairwise disjoint, jointly complete over the five extended policies. Observation O8: the claimed event types include renewal events (auto_renewal_offer, auto_renew, auto_late_renewal) and many endorsement types (garaging, lienholder, rideshare, package change, vehicle add/replace, driver remove, flat cancel) that no extended policy of this difficulty instantiates.

### rule_compute_equivalence

Swept every compute binding of the five policies against `compute_basis` and back against the `rule`.

- auto_ext_rental_option_removal_credit: every binding quoted verbatim from the rule (term days, option premium with 12-month multiplier, paid days = days_billed on rental_vendor_payment + rental_reimbursement_payment within 6 months, credited share three tiers, hold share three tiers, credit start three tiers with the 30-day late-recording test, standing rate three tiers, single final half-up rounding). Equivalent both ways. Note: `rc_option_id` = CFIELD(status='removed') picks the customer's first removed rental option, and the rule's "the option that ended" is singular; harmless on both worlds (one option).
- auto_ext_total_loss_vehicle_removal_credit: equivalent both ways for drop, offset, PD premium (most recent coverage change entry), declared/paid total loss within 6 months, allowance by reason, credit start, recapture (XMAX of active_days on score postings vs half min_active_days), deletion rate. Observation O3: the rule says "every rental reimbursement option that ended on the removed vehicle earlier in the term", but `vr_rental_option` = CFIELD(vehicle_id) reads one option and never tests "ended earlier in the term"; no consequence on task 0 (one option, ended 2026-09-02 before the 2026-09-14 removal).
- auto_ext_insured_cancellation_refund: equivalent for written premium, unexpired/term days, roadside part, PD part, return share, plan takeback, charge. Observation O2: the rule waives charge and minimum earned premium only "when no vehicle is left on the schedule because every scheduled vehicle was sold or declared a total loss"; compute `cx_charge`/`cx_min_earned` waive on `cx_vehicles_left <= 0` for any removal reason — the reason clause is an empty promise in compute. No consequence on task 0 (one vehicle left). Observation O2b: `cx_pd_coverage` = CFIELD(policy_id) takes the first PD coverage of the policy while the rule says "the policy's physical damage coverage" (singular); harmless on task 0 (one PD coverage).
- auto_ext_driver_addition_premium: equivalent both ways (charge = after − before on the addition entry; charge start three tiers using the package's household_driver_report_days; coaching three tiers; loss load three tiers with a gap — payments >0 but below the minimum fall to nil, as the rule says "otherwise, nil"; loyalty three tiers).
- auto_ext_named_driver_exclusion_credit: equivalent both ways (charge carried from the AP entry booked for the addition, nil when none; credit start three tiers; retention three tiers; recapture three tiers; loss share three tiers; credit rate three tiers).
- Every declared factor's ladder tiers appear as rule sentences and as branches of the `decides` binding, and vice versa, with one exception noted for structure only: `payment_method_charge` binding `cx_charge` carries a fourth leading branch (`0 if cx_vehicles_left <= 0`) that is stated in the rule as a separate sentence (not a tier of the factor's ladder); not a missing tier, recorded with O2.
- Observation O1 (framework pattern): each rule states its baseline as flat sentences ("The credited share of the option is the whole option. The short-hold share is one. The payment-standing rate is 95 percent", "In a vehicle removal credit the earned physical damage premium is nil", "The credit days run from the addition's effective date…") and then, in the same rule, a ladder for the same quantity. Read as default-then-exception this is unique; read sentence-by-sentence the rule asserts two values for one quantity. Recorded as observation because the skill mandates baseline sentences in the rule.
- DSL rounding: `RND` is Python round (banker's on exact binary halves) while the rules say half up; none of the gold-path figures on either world lands on a half cent, so no consequence.

### action_binding_and_uuids

- Each (target_tool, computes) is claimed by exactly one policy (table above).
- uuid8 tails: 1b50ed15, 524db3a4, 695fb1aa, cd2c8cbf, c094ed6f — no shared prefix, no sequence, no adjacency; independently generated as far as can be judged.
- Tool bodies (task_tools.py lines 42-61, 85-99, 126-145, 170-186, 218-239): none validates eligibility, order, prerequisite or amount; none errors or hints when a prerequisite is unresolved. Each writes exactly the entries its docstring declares.
- Docstrings name no other tool and state no sequence. Observation O9: `book_vehicle_removal_credit_524db3a4` and `book_driver_addition_premium_cd2c8cbf` describe their object as "a vehicle removal / driver addition already recorded on an auto policy"; "already" qualifies the existing record the call keys on, not the call's position relative to another tool. The driver-addition docstring's "full-term premiums before and after" names fields, not order.
- Business reading of each target: unique. Terminal states: rental credit = auto_coverage_change(return, coverage_removed, source=option) + auto_return_premium; removal credit = auto_return_premium(source=removal); cancellation = request signed, policy cancelled with end_date = request date, RP; driver addition = auto_additional_premium(source=addition, copies before/after); exclusion = request signed, auto_driver_exclude + RP.

### prerequisite_graph

- `prerequisite` filled on all five policies ([] on rental credit and driver addition).
- Edges: E1 vehicle removal credit -> rental credit (gate vr_option_offset); E2 cancellation refund -> vehicle removal credit (gate cx_written); E3 exclusion credit -> driver addition premium (gate ex_charge). Every `problem` is an extended policy id of this file; no self-edge; graph acyclic (two chains: rental <- removal <- cancellation; addition <- exclusion).
- `policy_source` of E1, E2, E3 each verbatim locatable in the blocked policy's own rule (yaml lines 1965-1967, 2465-2466, 3270-3271).
- `form: state` on all three; no `fallback_reason` (correct for state form).
- `kind: value_input` on all three; each `gate` is a real compute binding of the blocked policy (vr_option_offset, cx_written, ex_charge).
- `resolved_by` = the depended-on policy's target_tool on all three, and its runnable effect makes `effect` true: E1 the rental tool writes an auto_coverage_change with reason coverage_removed, source=option, term_effective_date=current term, which flips `vr_option_offset` from 0 to the option premium; E2 the removal tool writes an RP in the current term, lowering `cx_written`; E3 the addition tool writes an AP with source=addition, flipping `ex_charge` from 0 to the addition's full-term difference.
- `condition` text vs sentence strength: E2 and E3 match. E1 does NOT — the condition requires "a coverage change entry with reason coverage removed", the sentence only "its own coverage change entry" — see finding G1.
- No authoring-viewpoint wording in any `prerequisite` field.

### prerequisite_sentences

E1 — "A vehicle removal credit is not booked until every rental reimbursement option that ended on the removed vehicle earlier in the term carries its own coverage change entry on the policy."
- Ordering connective: "not … until" (pass). Names no tool, policy id, snake_case token or row id (pass). State form: "carries its own coverage change entry on the policy" (record-visible state) (pass).
- Strength vs condition: FAIL. The sentence waits on any coverage change entry of the option; the condition (and the rule's own value sentence, "carries its own coverage change entry for its removal in the term") needs the entry for its removal. The ordinary lifecycle writes a coverage change entry when the option is attached (`coverage_added`, source = the option id), so every attached option already "carries its own coverage change entry" from the day it was added. Finding G1.
- One write brings the condition's state about: only `record_rental_removal_credit_1b50ed15` writes an auto_coverage_change of this difficulty. Derivation: sentence -> "coverage change entry" of an ended rental option -> the rental credit rule ("credited on the auto policy as one coverage change entry for that vehicle, pointing at the option that ended") -> that policy's write. Unique under the condition's reading.
- Depended-on rule does not restate the sentence (pass).

E2 — "The cancellation refund is fixed only after every vehicle removal recorded on the policy during the term carries its own return premium entry."
- Connective "only after"; state form; no tool/id; strength matches the condition (every current-term removal has an RP pointing at it). Pass.
- Unique resolving write: among this difficulty's writes only `book_vehicle_removal_credit_524db3a4` ties an RP to a removal (rental RP ties to its coverage change, exclusion RP to the exclusion, cancellation RP to nothing). Derivation: sentence -> "return premium entry" of a "vehicle removal" -> the removal credit rule ("credited by one return premium entry tied to that removal") -> its write. Single reading. Pass.

E3 — "The exclusion credit is not worked out until the excluded driver's addition carries its own additional premium entry on the policy."
- Connective "not … until"; state form; no tool/id; strength matches the condition (AP whose source is the excluded driver's addition entry). Pass.
- Unique resolving write: only `book_driver_addition_premium_cd2c8cbf` writes an AP. Derivation: sentence -> "additional premium entry" of "the driver's addition" -> the driver addition rule ("charged by one additional premium entry tied to that addition") -> its write. Pass.

- No rule carries a second wording, a tool name or another problem's id about a dependency; no cross-problem order is stated in any rule without a declared edge; no base sentence grounds an edge.
- Realism of the three prerequisites (declared priority of this run): all three are ordinary out-of-sequence endorsement handling in personal auto — an earlier-dated endorsement that was never posted (the rental option dropped 2026-09-02; the driver added but never billed) is posted before a later transaction that depends on it, and pending endorsement premium is settled before a final cancellation refund is fixed. The seeded "gap" states (an option removed in the rental system but not posted on the auto policy; a removal recorded without its RP; a driver addition recorded without its AP) are realistic back-office backlogs. The edges themselves are realistic; the defect is the wording of E1 (G1).

### override_declarations

Sentence-by-sentence against `base_policy_refs`:

- auto_evt_midterm_proration (cited by all five): "the difference is multiplied by the unexpired days … rounded to the cent" — superseded and replaced in all four credit/charge policies (declared). "For a cancellation, the return premium is the pro rata unearned premium …" — superseded in the cancellation policy (declared). "An endorsement effective date may be today or a later date … it may not be earlier than today except …" — NOT superseded by any extended policy, yet (i) the rental credit's entry is "dated the day it ended" and its credit-start tier 3 runs "from the date the option ended" (past), and (ii) the removal credit's tier 3 runs "from the removal's effective date" within a 10/30/60-day back-dating allowance. On both worlds the gold tiers taken coincide with the no-backdating reading for the credit days (task 0: rental start = recording day, removal start = recorded date), and the rental entry's date is supported by the rental charter's trigger (`rental_coverage_remove` -> auto_coverage_change with effective_date: end_date). Observation O4 (undeclared but without a demonstrated second answer on either world).
- auto_insured_cancellation: signature-processing sentence superseded (declared); pro-rata-less-fee clause superseded (declared); minimum-earned cap and "never below zero" followed; "No cancellation fee … when … every scheduled vehicle was sold or declared a total loss" followed in the rule (compute broader, O2); "takes effect on the date the named insured chose … never an earlier one" followed (request date 2026-10-25 is after signing).
- auto_driver_changes: signed-exclusion sentence superseded (declared); "takes effect on the date the form was signed or a later date the named insured chose" followed by signature_start tier 2; the late-report sentence ("effective the date of the request when reported later") is followed in effect by late_report_start tier 2.
- auto_vehicle_changes, auto_agg_household_vehicle_count, auto_evt_premium_rating, auto_combo_financial_responsibility: followed; no sentence handled differently that changes a scored quantity on either world (household vehicle count does not switch multi-car on any other policy: each customer holds one auto policy).
- Disguised forms: the exclusion's "charge carried is nil where the addition carries no additional premium entry" is a 0/1 existence multiplier over the base's rated difference; it is the declared replacement of "the difference is multiplied …" and is the mechanism of edge E3 — observation O6 (under base semantics alone the exclusion figure is reachable without the prerequisite).
- Sibling-charter clauses on the same quantities are not reachable by `overwrite` (which names base policies of this charter only) and are handled in G2.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source | cross_difficulty | label honest? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rental credit | rental_days_paid | method | rc_credited_share | 3 | yes (ledger days vs charter max) | rental | yes (usage-proportional vs fixed) |
| rental credit | option_hold_length | parameter | rc_hold_share | 3 | no | rental | yes |
| rental credit | late_recording_start | method | rc_credit_from | 3 | yes (end date, term start, recording day) | — | yes (date anchor) |
| rental credit | payment_standing | parameter | rc_standing_rate | 3 | yes (tenure + billing returns) | billing | yes |
| removal credit | total_loss_earning | parameter | vr_pd_earned | 3 | yes (declared + paid) | physdmg | yes |
| removal credit | deletion_allowance | parameter | vr_allowance | 3 | no | — | yes |
| removal credit | deletion_credit_start | method | vr_credit_from | 3 | yes | — | yes (date anchor) |
| removal credit | drivesense_recapture | parameter | vr_recapture_pct | 3 | yes (score + active days) | telematics | yes |
| removal credit | deletion_credit_rate | parameter | vr_deletion_rate | 3 | yes (tenure + autopay) | billing | yes |
| cancellation | roadside_use_earning | parameter | cx_roadside_earned | 3 | yes (dispatch − restored) | roadside | yes |
| cancellation | total_loss_term_earning | parameter | cx_pd_earned | 3 | yes | physdmg | yes |
| cancellation | tenure_return_share | method | cx_return_share | 3 | yes (tenure + lapse marker) | — | NO — three constants 1.0/0.95/0.9 multiplied into one formula (G3) |
| cancellation | plan_discount_takeback | parameter | cx_takeback_pct | 3 | no | billing | yes |
| cancellation | payment_method_charge | parameter | cx_charge | 3 | yes (autopay + returns) | billing | yes |
| driver addition | late_report_start | method | da_charge_from | 3 | yes | — | yes (date anchor) |
| driver addition | teen_coaching_discount | parameter | da_coach_pct | 3 | yes (program + score) | telematics | yes |
| driver addition | at_fault_loss_load | parameter | da_load_pct | 3 | yes (fault + payments) | physdmg | yes |
| driver addition | tenure_loyalty_credit | parameter | da_loyalty_pct | 3 | yes (tenure + lapse marker) | — | yes |
| exclusion | signature_start | method | ex_credit_from | 3 | yes | — | yes (date anchor) |
| exclusion | rated_period_retention | parameter | ex_retention | 3 | no | — | yes |
| exclusion | teen_coaching_recapture | parameter | ex_recapture_pct | 3 | yes | telematics | yes |
| exclusion | at_fault_loss_share | parameter | ex_loss_share | 3 | yes | physdmg | yes |
| exclusion | exclusion_credit_rate | parameter | ex_credit_rate | 3 | yes (tenure + returns) | billing | yes |

- Counts per computation (as declared): rental 4 (2 param, 2 method); removal 5 (4 param, 1 method); cancellation 5 (4 param, 1 method declared, 0 honest — G3); driver addition 4 (3 param, 1 method); exclusion 5 (4 param, 1 method). Per task: task 0 has multi-source and cross-difficulty factors (rental, billing, physdmg, telematics, roadside); task 1 likewise (telematics, physdmg, billing).
- Bindings disjoint within each policy; every `decides` is an input, never `result`; tiers pairwise disjoint as stated; no two tiers of one ladder share a value or method; every tier is stated in the rule (condition and value) and implemented in compute; every fall-through equals the policy's baseline; every baseline matches `baseline.rule`.
- Realism of conditions and outcomes (declared priority) — see G4 for the tiers that fail; observations O5 for tiers that are invented but plausible.

### findings

**G1 — SOURCE-POLICY RED — E1 prerequisite sentence is broader than its condition, and the seed satisfies the broad reading at the opening** (bears on task 0)
- Symptom: the sentence waits on the option "carries its own coverage change entry on the policy"; the condition requires one "with reason coverage removed".
- Root cause: the qualifier "for its removal", present in the rule's value sentence (yaml 1971-1974), was left out of the prerequisite sentence (yaml 1965-1967, `policy_source` 2004-2006).
- Evidence: condition text (yaml 2007-2009); every attached option carries a `coverage_added` coverage change entry (task 0 seed: auto_transactions 7a8ee1ce-5319-4b27-bb1a-4b4a5026dbf8, event_type auto_coverage_change, source_transaction_id 8dd2393c… = the rental option, reason coverage_added, term_effective_date 2026-07-01).
- Consequence (demonstrated in 0.md): reading the sentence as written, the prerequisite already holds at the opening, so no rental write is due; the removal credit is then 223.95 and the cancellation refund 204.77, against 214.44 / 207.08 on the condition's reading.
- Affected: auto.extended.yaml auto_ext_total_loss_vehicle_removal_credit.rule (sentence 2) and prerequisite[0].policy_source.

**G2 — SOURCE-POLICY RED — extended credits contradict the sibling charters' published treatment of the same premium quantities (undeclarable through `overwrite`)** (bears on task 0; task 1 observation)
- (a) Rental option removal: rental.yaml `rental_attach_eligibility` (lines 668-671): "it is a flat add-on on the auto policy, prorated for the rest of the term when the option is added, changed or removed, and returned on cancellation_premium_basis", every rental variant `cancellation_premium_basis: pro_rata` (line 87 meaning: "How unearned option premium is returned on removal (pro_rata)"). The extended rental credit returns the option premium × credited share × short-hold share × payment-standing rate × credit days / term days.
- (b) Physical damage on a removed/totalled vehicle: physdmg.yaml `physdmg_evt_premium` (lines 936-939): "every change to it during the term is prorated as additional or return premium on the auto policy". The removal credit and the cancellation refund make the PD premium wholly (or half) earned.
- (c) Roadside on cancellation: roadside.yaml (lines 633-635): "prorated when the option is added, changed or removed, and returned on cancellation_premium_basis" (pro_rata). The cancellation refund makes the roadside option fully/half earned by dispatch count.
- (d) DriveSense participation timing: telematics.yaml line 672 "The participation discount applies from participation_discount_applies_from", every safe-driving/Teen Coach variant `next_renewal_term_or_new_business`; line 655-660 the discount lowers the enrolled vehicle's share of the base premium. The removal credit "recaptures" a participation discount, and the driver addition charge grants (and the exclusion credit recaptures) a Teen Coach participation discount, all midterm.
- Root cause: the extended policies re-decide quantities that sibling charters already decide, and the `overwrite` mechanism can only name base sentences of this charter, so the contradiction is undeclared and both passages will be published.
- Consequence: demonstrated in 0.md for (a), (b), (c) (second readings 13.02 / 382.31 / 208.97); (d) is carried into G4 for task 0 and recorded as an observation in 1.md (the extended addition/exclusion pair is internally coherent there).
- Affected: rule sentences of auto_ext_rental_option_removal_credit (credited share, hold share, standing rate), auto_ext_total_loss_vehicle_removal_credit (earned PD premium, recapture), auto_ext_insured_cancellation_refund (roadside part, PD part), auto_ext_driver_addition_premium / auto_ext_named_driver_exclusion_credit (coaching).

**G3 — SOURCE-FACTOR RED — `tenure_return_share` is labelled `method` but only substitutes a number; the cancellation computation has no honest method factor** (bears on task 0)
- Evidence: compute `cx_return_share: K('share_long_tenure') if … else (K('share_mid_tenure') if … else K('share_short_rate'))` = 1.0 / 0.95 / 0.9, multiplied into the unchanged formula `cx_returnable * cx_unexpired_days / cx_term_days * cx_return_share * …`. The ladder text calls tiers "full pro rata", "reduced short rate", "standard short rate", but no tier changes the algorithm (no short-rate table, no different earning curve) — it is a rate, which the skill names as the canonical mislabel.
- Consequence: counting only honest labels, auto_ext_insured_cancellation_refund declares 5 parameter factors and 0 method factors (< 1 required).
- Affected: auto.extended.yaml auto_ext_insured_cancellation_refund.factors[tenure_return_share].effect.

**G4 — SOURCE-FACTOR RED — unreal ladders (realism priority)** (bears on tasks 0 and 1)
- (a) Credit-rate haircuts on midterm endorsement credits: `payment_standing` (rental credit; 100 / 97.5 / fall-through 95 percent), `deletion_credit_rate` (vehicle removal; 100 / 98 / fall-through 96 percent), `exclusion_credit_rate` (driver exclusion; 100 / 97.5 / fall-through 95 percent). In US personal auto, return premium on a midterm endorsement (dropping an optional coverage, deleting a vehicle, excluding a driver) is computed pro rata for every insured; a short-rate retention is a feature of insured-requested whole-policy cancellation, not of endorsements. The fall-through tier therefore withholds 4-5 percent of a pro-rata endorsement credit from the ordinary customer — "a default no such business applies to its ordinary customer". The conditions are also ones the line does not weigh for that quantity: returned payments (NSF/chargeback) and automatic-payment enrollment are weighed for billing fees and pay-plan eligibility, not for the size of an endorsement return premium. In-world corroboration: this scenario's own rental and roadside charters publish `cancellation_premium_basis: pro_rata`, and base auto_evt_midterm_proration is pure pro rata.
- (b) `drivesense_recapture` (vehicle removal): the ladder recaptures "the program's participation discount percentage" from any unscored enrollment with few active days, but nothing in the condition tests whether a participation discount was ever applied to the vehicle's premium; under telematics.yaml the participation discount of a midterm enrollment applies only from the next renewal term, so for a midterm enrollment the tier takes back a discount the customer never received. Demonstrated on task 0's world in 0.md.
- Consequence: per task — task 0 sits on the 100-percent tier of (a) for both rental and removal (the fall-through is not taken there, but the ladder is not one the line holds) and on the full-recapture tier of (b); task 1 sits on the 97.5-percent tier of `exclusion_credit_rate`. Demonstrations in the task files.

**Observations (charter-global, no demonstrated consequence)**
- O1 baseline sentences and ladder sentences for the same quantity stand side by side in each rule (framework-mandated).
- O2 / O2b cancellation waiver condition and PD coverage selector broader in compute than rule.
- O3 removal credit reads one rental option and does not test "ended earlier in the term".
- O4 the base no-backdating sentence of auto_evt_midterm_proration is not superseded although the rental and removal credit-start ladders admit back-dated starts.
- O5 invented-but-plausible tiers (realism noted, not red): option_hold_length (half credit under 90 days), rated_period_retention (75 percent under 90 days), at_fault_loss_share (credit halved after a paid at-fault loss — weak: an at-fault loss does not earn the driver's future-period premium in practice), deletion_allowance (a total loss gets the shortest back-dating allowance, 10 days, although the company's own claim file evidences the loss date — counter to practice, where total-loss deletions are back-dated to the loss/settlement), total-loss "declared but unpaid -> half earned" (no industry analogue), teen_coaching_discount granted midterm (G2d).
- O6 E3 is an existence multiplier: under the base's rated-difference semantics the exclusion figure is reachable without the prerequisite write.
- O7 seed states that contradict charters other than through the tasks' intended gaps: the rental option is `removed` with no auto_coverage_change although rental.yaml's `rental_coverage_remove` triggers one; the task-0 removal is effective 16 days before it was recorded (base forbids back-dated endorsements); the task-1 driver addition is effective on the licence date although it was reported 42 days later (base: "effective the date of the request when reported later"). The extended ladders reproduce the base outcome in the latter two (recorded-date start), so no second answer arises.
- O8 claimed renewal / other endorsement event types not instantiated.
- O9 "already" in two docstrings.

## closing_checklist

Written 2026-10-05T11:00Z, after both reveals (the section above was written at 10:54:38Z, before any reveal, and was not edited afterwards except for this heading's body).

- Per-task files: 0.md and 1.md correspond one-to-one with tasks 0 and 1; this file sits alongside; first revision, no older revisions. Comparison sections: **0.md SOURCE-POLICY RED + SOURCE-FACTOR RED; 1.md SOURCE-FACTOR RED + SOURCE-CHAIN RED** — not all PASS, so the difficulty is **not closed** and does not pass the source-layer audit.
- Coverage and scope: the five extended policies are fully covered; scopes {rental credit, removal credit, cancellation refund} and {driver addition premium, exclusion credit} are pairwise disjoint over whole trees; tools and GT closed; uuid8s independent — PASS.
- Trees: task 0 n=2 with 2 value_input edges; task 1 n=1 with 1 value_input edge; each root is an owner=user write; the difficulty-wide graph (rental <- removal <- cancellation; addition <- exclusion) is acyclic — PASS on structure; E1's sentence fails its condition's strength (G1).
- Factors: every computation has a definite baseline ≠ gold and 4-5 factors that each bear weight on its world; but the cancellation computation has no honest method factor (G3), and ladders that the line does not hold appear in four computations (G4a payment_standing, deletion_credit_rate, exclusion_credit_rate; G4b drivesense_recapture) — FAIL.
- Sibling-charter consistency of the published surface: FAIL (G2).
- Gates: not re-run by the auditor (outside this skill's remit; the conductor's snapshot is cited in §charter_global_frozen). The artifacts were not modified during the audit: auto.extended.yaml and task_tools.py hashes re-verified unchanged at 10:57Z; tasks/0.json 7166df2e…e508, tasks/1.json a8425e22…acc1.

## revision_2

### charter_global_frozen (revision_2)

- Written 2026-10-05T12:33Z, before any revision_2 task GT was revealed; nothing below is derived from revision_2 GT. Revision_1 text above is left untouched.
- Hashes (verified by the auditor against MANIFEST.sha256 of /tmp/erl35_views/policy_endorsements_and_renewals.r2/ and against the live files): auto.extended.yaml `9c9fc9e1…b7af` (r1 `91478d71…2ec`), task_tools.py `a2bc4ef5…519f` (r1 `4cef862a…303`), task_0.view.json `e159855c…ecde`, task_1.view.json `47fc9d35…df5b`. Both charter hashes changed, so every charter-global section is re-derived in full below (nothing carried forward by reference).
- Base copy: lines 1-1606 still byte-identical to blueprint/products/auto.yaml. Blueprint files (all products, schema, share tools) unmodified since before round 1 (mtimes 08:24-08:38Z).
- Gate snapshot supplied (r2 GATES.txt): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability deferred. Input complete.
- Masked until the freeze of both task derivations: tasks/0.json, tasks/1.json (all GT and proof fields), worklog.md.
- contamination_disclosure (difficulty level): the auditor revealed the revision_1 GT of both tasks in round 1. Task 0's world, package, tree and tools were rebuilt; task 1's world keeps its customer, policy, driver rows and exclusion form but changes package (Plus -> Standard), drops billing and telematics rows, and replaces two factors. Round-1 knowledge of task 1's addition entry, claim rows and form is therefore present in the auditor's context; no revision_2 scored value was seen before freezing.

### policy_conflict_scan (revision_2)

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| auto_ext_vehicle_addition_premium | auto_additional_premium | book_vehicle_addition_premium_9393c661 (agent) | additional_premium | [] |
| auto_ext_vehicle_removal_credit | auto_return_premium | book_vehicle_removal_credit_524db3a4 (agent) | return_premium | <- vehicle addition premium (value_input vr_written, state) |
| auto_ext_insured_cancellation_refund | auto_insured_cancel, auto_return_premium | sign_cancellation_request_695fb1aa (user) | return_premium | <- vehicle removal credit (value_input cx_written, state) |
| auto_ext_driver_addition_premium | auto_additional_premium | book_driver_addition_premium_cd2c8cbf (agent) | additional_premium | [] |
| auto_ext_named_driver_exclusion_credit | auto_driver_exclude, auto_return_premium | sign_named_driver_exclusion_c094ed6f (user) | return_premium | <- driver addition premium (value_input ex_written, state) |

- Shared subjects: auto_additional_premium (vehicle vs driver addition — distinct source objects: a vehicle add row vs a driver add row); auto_return_premium (removal / cancellation / exclusion — distinct sources). No (tool, quantity) claimed twice.
- Interplay: the AP booked by the vehicle addition policy is the base of the removal credit's tier 1 ("unearned share of what was actually charged"), and both enter the cancellation's written premium once each; the same pattern holds for driver addition -> exclusion. No double count found. Observation R2-O3 records that the "unearned share" denominator (days from the addition's effective date) is not the day basis the AP was charged on (charged days from the recorded date, floored by the minimum charge period).
- Sibling-charter read boundaries: the round-1 conflicts are gone — no policy now makes physical damage, rental or roadside premium earned (the cancellation rule now returns the optional-coverage part pro rata "as those coverages' own terms provide"), and no policy now applies or recaptures a DriveSense discount. The only cross-category reads left are billing (cancellation) and physdmg claims (driver addition / exclusion), neither of which re-decides a quantity another charter decides.
- Scope: task 0 = {vehicle addition premium, vehicle removal credit, cancellation refund}; task 1 = {driver addition premium, exclusion credit}. Pairwise disjoint, jointly complete. O8 (renewal event types claimed but uninstantiated) still applies.

### rule_compute_equivalence (revision_2)

- auto_ext_vehicle_addition_premium: charge, term days, charge start, minimum charge period, excess-vehicle share, loyalty all quoted and implemented. Divergence R2-O1: the rule measures report lateness from "the vehicle was acquired" (vehicles.acquisition_date) while `va_charge_from` measures from the addition's effective date; the two coincide whenever the add carries its acquisition date (task 0: both 2026-09-01), so no consequence here.
- auto_ext_vehicle_removal_credit: drop, credit base (three tiers), credit start, back-dating allowance, short-hold share implemented. **Divergence (finding R2-P2):** rule and ladder say "where the loan payoff was **recorded** fewer than 10 days before the removal took effect, 10 days less the calendar days from the payoff to the removal"; `vr_payoff_date` reads the payoff entry's **effective_date**. In the same rule "recorded" is used in contrast to "effective date" ("where the removal was recorded no more calendar days after its effective date …"), so the reader has textual ground to read the payoff entry's recorded_date. When a payoff is recorded after the removal took effect, the two readings take different tiers.
- auto_ext_insured_cancellation_refund: written premium, optional-coverage part (all coverage change entries added less removed), cancellation date anchor, refund days less loss payee notice, return share, takeback, charge, disposal waiver (now implemented with the sold/total-loss reason test — O2 closed) — equivalent. Observation R2-O4: tier 1 of the cancellation loss payee notice reads "a new loan is recorded with no loan payoff recorded after it"; compute nets policy-wide counts (new loans − payoffs) without pairing a payoff to its loan; equivalent under the natural per-lienholder pairing.
- auto_ext_driver_addition_premium: equivalent (operator share counts drivers added less excluded/removed vs vehicles added less removed).
- auto_ext_named_driver_exclusion_credit: equivalent (credit base three tiers, effective date anchor, retention, loss share).
- Every ladder tier is a rule sentence and a branch of its binding; every fall-through equals the baseline; every baseline matches `baseline.rule`.
- O1 (baseline sentences and ladder sentences for the same quantity side by side in one rule) persists in all five rules.

### action_binding_and_uuids (revision_2)

- Each (target_tool, computes) claimed by exactly one policy. uuid8s: 9393c661 (new tool), 524db3a4, 695fb1aa, cd2c8cbf, c094ed6f (unchanged tools) — distinct, no shared prefix or sequence.
- Tool bodies (r2 task_tools.py 35-51, 75-89, 119-138, 163-179, 211-232) validate nothing and never error on an unresolved prerequisite. `sign_cancellation_request_695fb1aa` now takes `cancellation_effective_date` from the caller (was read from the request in r1), so the date is a scored argument decided by the policy.
- Docstrings: no sequence words, no other tool named; "already" removed (O9 closed).

### prerequisite_graph (revision_2)

- Edges: E1' vehicle removal credit -> vehicle addition premium (gate vr_written); E2 cancellation -> vehicle removal credit (gate cx_written); E3' exclusion -> driver addition premium (gate ex_written). Acyclic; all `problem` ids are extended policies of this file; `policy_source` verbatim in each blocked rule (yaml 1934-1935, 2309-2310, 3070-3071 region); form state, no fallback; gates are real compute bindings and now carry the AP **amount** (vr_written, ex_written are SUMs of premium_amount), so both value_input edges pass a value, not only an existence switch (O6 closed); `resolved_by` = the depended-on target_tool and its effect makes `effect` true.
- Conditions of E1' and E3' add "in the current term"; the sentences do not. See R2-P1.

### prerequisite_sentences (revision_2)

- E1' "A vehicle removal credit is not booked until the removed vehicle's addition carries its own additional premium entry on the policy." — "not … until"; state form; no tool/id. Unique resolving write: only `book_vehicle_addition_premium_9393c661` writes an AP sourced to a vehicle add. Derivation: sentence -> "additional premium entry" of "the removed vehicle's addition" -> the vehicle addition rule ("charged by one additional premium entry tied to that addition") -> its write.
- E2 unchanged from r1 — passes (see r1 §prerequisite_sentences).
- E3' "The exclusion credit is not worked out until the excluded driver's addition carries its own additional premium entry on the policy." — passes the four-point test; unique resolving write `book_driver_addition_premium_cd2c8cbf`.
- **Scope test fails for E1' and E3' (finding R2-P1):** both sentences are unconditional — every removed vehicle / excluded driver must have an addition that "carries its own additional premium entry" — but an addition scheduled at issue (premium_effect none) or listed in a prior term never carries a current-term AP, and each rule's own ladder prices exactly that case in its fall-through ("otherwise, the full-term drop [charge] times the credit days divided by the days of the … term").
- Realism of the edges: posting an unbilled earlier add before crediting its removal / exclusion, and settling pending endorsement premium before fixing a cancellation refund, are ordinary out-of-sequence endorsement handling; the seeded gaps (an add recorded with premium effect but no AP; a removal recorded without its RP) are realistic backlogs.

### override_declarations (revision_2)

- auto_evt_midterm_proration: the multiplication clause is superseded in all four credit/charge policies and the cancellation (declared); the no-backdating sentence ("it may not be earlier than today except …") is now superseded in the removal credit (declared; O4 closed for removal). Back-dated starts elsewhere: vehicle addition from the acquisition date and driver addition from the licence/move-in date are base-sanctioned (newly acquired vehicle within its window; household member reported within household_driver_report_days); exclusion and cancellation never start before signature (base-consistent).
- auto_insured_cancellation: signature-processing and pro-rata-less-fee clauses superseded (declared); disposal waiver followed (rule and compute); "never an earlier one" followed by cancellation_date_anchor tier 2.
- auto_driver_changes, auto_vehicle_changes: late-report sentences followed in effect by the charge-start ladders (R2-O2 records that the seeded add rows of both tasks carry the early effective date base forbids).
- auto_evt_premium_rating: the excess-vehicle and operator shares multiply the rated full-term difference; this is within the declared replacement of "the difference is multiplied …". No undeclared override found with a consequence.

### factor_ladders (revision_2)

| policy | factor | label | tiers | multi-source | cross_difficulty | honest? |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle addition | late_report_charge_start | method | 3 | yes | — | yes (date anchor) |
| vehicle addition | minimum_charge_period | parameter | 3 | no | — | yes |
| vehicle addition | excess_vehicle_rating | parameter | 3 | yes (vehicle + driver rows) | — | yes |
| vehicle addition | addition_loyalty_credit | parameter | 3 | yes (tenure + lapse marker) | — | yes |
| removal credit | deletion_credit_basis | method | 3 | yes (AP + add effect + dates) | — | yes (three algorithms) |
| removal credit | deletion_credit_start | method | 3 | yes | — | yes |
| removal credit | deletion_backdating_allowance | parameter | 3 | no | — | yes |
| removal credit | loss_payee_notice | parameter | 3 | yes (loan + payoff entries) | — | yes |
| removal credit | short_hold_share | parameter | 3 | no | — | yes |
| cancellation | cancellation_date_anchor | method | 3 | yes | — | yes |
| cancellation | cancellation_loss_payee_notice | parameter | 3 | yes | — | yes |
| cancellation | tenure_return_share | parameter | 3 | yes | — | yes (G3 closed: relabelled) |
| cancellation | plan_discount_takeback | parameter | 3 | no | billing | yes |
| cancellation | payment_method_charge | parameter | 3 | yes | billing | yes |
| driver addition | late_report_start | method | 3 | yes | — | yes |
| driver addition | driver_minimum_charge_period | parameter | 3 | no | — | yes |
| driver addition | operator_assignment | parameter | 3 | yes | — | yes |
| driver addition | at_fault_loss_load | parameter | 3 | yes | physdmg | yes |
| driver addition | tenure_loyalty_credit | parameter | 3 | yes | — | yes |
| exclusion | exclusion_credit_basis | method | 3 | yes | — | yes |
| exclusion | signature_start | method | 3 | yes | — | yes |
| exclusion | rated_period_retention | parameter | 3 | no | — | yes |
| exclusion | at_fault_loss_share | parameter | 3 | yes | physdmg | yes |

- Counts: vehicle addition 4 (3p/1m); removal 5 (3p/2m); cancellation 5 (4p/1m); driver addition 5 (4p/1m); exclusion 4 (2p/2m). Per task: task 0 has multi-source factors and cross-difficulty factors only in the cancellation (billing); task 1 has physdmg in both computations. All within bounds.
- Tiers disjoint and distinct; fall-throughs equal baselines.
- Realism (declared priority):
  - Closed from r1: the tenure/NSF/autopay haircuts on endorsement credits are gone (payment_standing, deletion_credit_rate, exclusion_credit_rate removed); drivesense_recapture removed; the total-loss back-dating allowance is now the most generous (60 days), matching practice; the removal and cancellation loss payee notice tiers (10 days of coverage kept for an open lienholder interest) reflect the real 10-day lienholder notice; excess-vehicle and occasional-operator rating are real rating concepts.
  - **Fails (finding R2-F1):** `minimum_charge_period` and `driver_minimum_charge_period` charge a fixed 60 or 120 days whatever is left of the term. Any addition with fewer than 120 days left is billed for more days than the term has remaining, so the AP exceeds the full pro-rata premium to expiration. The ladder is also non-monotone at its first step: 59 days left bills 60, but 60 days left bills 120. Carriers set minimum premiums as dollar minimums or minimum-earned amounts; none bills an added vehicle or driver beyond the policy's expiration date.
  - Observations (R2-O5, carried from r1 O5): `short_hold_share` (removal credit cut to 75 % / 90 % for a vehicle held under 90 / 180 days, stacked on the minimum charge period for the same short-held vehicle), `rated_period_retention`, `at_fault_loss_share` (credit halved after a paid at-fault loss) — invented, plausible at best; `loss_payee_notice` tier 2 (notice days still deducted when the loan was paid off before the removal, i.e. after the loss payee's interest ended) — questionable.

### findings (revision_2)

**R2-P1 — SOURCE-POLICY RED — E1' and E3' block issue-time and prior-term additions forever, while their own ladders price those cases** (charter-global; bears on neither task's gold path)
- Evidence: E1' sentence (yaml 1934-1935) vs removal tier 3 "otherwise, the full-term drop times the credit days divided by the days of the removal's term" (yaml 1947-1949); E3' sentence vs exclusion tier 3 "otherwise, the full-term charge of the excluded driver times the credit days …". Conditions (yaml 1968-1970 and the E3' condition) demand an AP "in the current term".
- Demonstration on the task-0 world: removing the Ranger (add a1cdc4ef, 2018-07-01, premium_effect none, drop 301.60). The ladder gives credit base 301.60 × credit days / 184. Under the sentence, nothing can be booked until the 2018 add carries a current-term AP. The only write that creates one is the vehicle addition premium, whose tier 1 ("took effect before the current term began → from the term effective date") would bill the Ranger again for a term whose term premium already carries it. The two passages reach different conclusions in the same situation: credit now, versus no credit until a duplicate charge is booked. This was partly present in r1 E3 (the r1 exclusion rule credited such drivers nil); the r2 tier 3 makes the contradiction explicit.
- Affected: auto_ext_vehicle_removal_credit.rule sentence 2 and prerequisite[0]; auto_ext_named_driver_exclusion_credit.rule sentence 2 and prerequisite[0].

**R2-P2 — SOURCE-POLICY RED — loss payee notice tier 2: rule "recorded" vs compute effective_date** (bears on task 0)
- Evidence: yaml 1954-1956 (rule), 2199 (ladder text), 2010-2015 (compute uses effective_date).
- Consequence: demonstrated in 0.md revision_2.

**R2-F1 — SOURCE-FACTOR RED — minimum charge period bills beyond the term's end** (bears on tasks 0 and 1)
- Evidence: yaml 1655-1658 / 1814-1831 (vehicle), 2729-2732 and `driver_minimum_charge_period` (driver).
- Consequence: demonstrated in each task file.

**Observations (revision_2):** R2-O1 acquisition vs effective date in the vehicle late-report test; R2-O2 seeded add rows carry early effective dates base forbids for late reports (Kia, Tyler), with the charge-start ladders reproducing the base outcome; R2-O3 "unearned share" denominator inconsistent with the charge basis; R2-O4 cancellation loan/payoff pairing; R2-O5 invented-but-plausible tiers; R2-O6 tier 1 of both addition policies would bill a current-term AP for a prior-term addition already carried in the renewal term premium (no task path); O1, O8 persist.

**Status of revision_1 items (charter level):** G1 closed (rental edge removed; new edges assessed above). G2a/b/c/d closed (policies or tiers removed; cancellation returns optional coverages pro rata). G3 closed. G4a closed. G4b closed. O2, O2b, O3, O6, O9 closed. O4 closed for the removal credit (declared). O1, O7 (as R2-O2), O8 persist; O5 partly persists (R2-O5).

### closing_checklist (revision_2)

Written 2026-10-05T12:37Z, after both revision_2 reveals; the revision_2 charter-global section above was written at 12:33Z before any reveal and is not edited.

- Files: 0.md and 1.md each carry `## revision_2` (derivation frozen before reveal, then comparison and findings); revision_1 text untouched in all three files.
- Verdicts: **task 0 SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 SOURCE-FACTOR RED; charter-global SOURCE-POLICY RED R2-P1.** The difficulty is **not closed** and does not pass the source-layer audit.
- Round-1 REDs: all closed — G1, G2a, G2b, G2c, G2d/G4b, G3, G4a (charter), task 0 findings 1-6, task 1 findings 1-2. Round-1 observations: O2, O2b, O3, O4 (removal), O6, O9 closed; O1, O5 (partly), O7 (now R2-O2), O8 persist. One reworker claim is not borne out: 1.md r1 finding 6 (the late-report effective date on Tyler's addition row) is unchanged in the seed, and it remains an observation.
- New in revision_2 (regressions introduced by the rework): R2-P1 (unconditional E1'/E3' sentences contradict their own fall-through tiers; partly latent in r1 E3), R2-P2 (loss payee notice "recorded" vs effective date, second reading on task 0), R2-F1 (minimum charge period bills beyond expiration, on both tasks).
- Coverage, scope, trees, uuid8s: five extended policies covered; scopes disjoint; trees n=2 (two value_input) and n=1 (one value_input), roots owner=user, difficulty graph acyclic; uuid8s independent — PASS.
- Gates: not re-run by the auditor (cited from the conductor's r2 snapshot); charter and tool hashes unchanged at reveal (9c9fc9e1…, a2bc4ef5…).

## revision_3

### charter_global_frozen (revision_3)

- Written 2026-10-05T13:02Z, before any revision_3 task GT was revealed; nothing below derives from revision_3 GT. Revision_1 and revision_2 text above untouched.
- Hashes verified against /tmp/erl35_views/policy_endorsements_and_renewals.r3/MANIFEST.sha256 and the live files: auto.extended.yaml `ce0d832f…dc50a` (changed from r2), task_tools.py `a2bc4ef5…519f` (unchanged; byte-identical to r2), task_0.view.json `e854baa4…edd6` (changed), task_1.view.json `47fc9d35…df5b` (unchanged). Because the charter changed, every charter-global section is re-derived; the tool-module half of §action_binding_and_uuids is carried forward from revision_2 on the unchanged task_tools.py hash.
- Base copy lines 1-1606 still identical to blueprint/products/auto.yaml; blueprint unmodified since before round 1.
- Gate snapshot (r3 GATES.txt): all eight green; traceability deferred. Input complete.
- contamination_disclosure: the auditor revealed revision_1 and revision_2 GT of both tasks in earlier rounds. Task 0's r3 world differs from r2 in one seed row (the Kia payoff's effective date) and one persona sentence; task 1's world is unchanged. The auditor therefore knows the r2 gold figures; every r3 figure is recomputed from the r3 charter and no r3 scored value was seen before freezing.

### policy_conflict_scan (revision_3)

- Same five policies, targets, owners and edges as revision_2 (vehicle addition <- removal <- cancellation; driver addition <- exclusion). No (tool, quantity) claimed twice. Scopes disjoint and complete. No sibling-charter conflict (no policy re-decides physdmg/rental/roadside/telematics premium).
- Charge/credit consistency: the removal and exclusion credits now divide the booked charge by "the days that charge was written for", using the same report-window test as the addition policies (R2-O3 addressed).

### rule_compute_equivalence (revision_3)

- Vehicle addition: charge start now tests "recorded no more calendar days after its effective date (the acquisition date recorded on it)" — rule and compute agree (R2-O1 addressed). The report window is new (`va_window`: 14 + 30 if a new loan is recorded effective on the addition's effective date, + 14 if one is recorded on another date). Rule and compute agree. Tier 1 now charges nothing for an addition that took effect before the term (R2-O6 addressed).
- Removal credit: the loss payee notice is restated on the payoff's "effective date, whenever it was recorded", and compute reads effective_date — agree (R2-P2 closed). Tier 2 now counts the days from the credit start to a later payoff, capped at 10.
- Cancellation: notice tier 1 "more new loans than loan payoffs are recorded on the policy" matches the count-based compute (R2-O4 addressed); tier 2 runs on the payoff's effective date after the cancellation date.
- Driver addition: the new member report window (`da_window`: 30 + 15 for a licensed member, + 7 for a moved-in member, nothing with a lapse marker) agrees with the rule; the minimum charge period is gone.
- Exclusion: credit-base denominator mirrors the driver window; agree.
- O1 (baseline sentences beside ladders) persists.

### action_binding_and_uuids (revision_3)

- task_tools.py unchanged (hash a2bc4ef5…): revision_2 conclusions carried forward — one policy per (tool, quantity), independent uuid8s 9393c661 / 524db3a4 / 695fb1aa / cd2c8cbf / c094ed6f, no validation in any body, docstrings silent on sequence.

### prerequisite_graph and prerequisite_sentences (revision_3)

- E1'' "Where the removed vehicle was added during the current term with a premium effect, a vehicle removal credit is not booked until that addition carries its own additional premium entry on the policy." E3'' the same for the excluded driver. Both are now scoped to exactly the case their ladders' tier 2 prices as nil and match their conditions, so issue-time and prior-term additions are no longer blocked. **R2-P1 closed.** Four-point test passes; unique resolving writes unchanged (book_vehicle_addition_premium_9393c661 / book_driver_addition_premium_cd2c8cbf). E2 unchanged, passes.
- Graph acyclic; gates vr_written, cx_written, ex_written carry amounts; resolved_by/effect hold. Realism of the edges unchanged (out-of-sequence endorsement handling).

### override_declarations (revision_3)

- New declared overrides: (a) auto_vehicle_changes "The additional vehicle keeps its acquisition-date effective date only when it is reported no later than newly_acquired_additional_report_days calendar days after the customer acquired the vehicle." -> the financed-lengthened window; (b) auto_driver_changes household-report sentence -> the licensed/moved-in/lapse-lengthened window.
- **Undeclared conflict (finding R3-P1):** override (a) names one sentence of auto_vehicle_changes. The same rule keeps, unsuperseded, "A newly acquired additional vehicle is automatically covered from its acquisition date …, and that automatic coverage holds only if the vehicle is reported within newly_acquired_additional_report_days; in that case the add is effective on the acquisition date" and "A vehicle reported later is added effective the date of the request" (yaml 1250-1257). The parameter_schema also defines newly_acquired_additional_report_days as the days "within which an additional … vehicle must be reported to keep the automatic coverage". For a financed vehicle reported on day 15-44, the base sentences put the add on the request date (no automatic coverage), while the extended window keeps the acquisition date. Override (b) supersedes the whole household-report sentence, and no other base sentence states that window, so (b) is clean.
- Other base sentences: as in revision_2 (no further undeclared override with a consequence).

### factor_ladders (revision_3)

- Vehicle addition 4 (late_report_charge_start m; financed_report_window p; excess_vehicle_rating p; addition_loyalty_credit p); removal 5 (2m/3p); cancellation 5 (1m/4p); driver addition 5 (late_report_start m; member_report_window p; operator_assignment p; at_fault_loss_load p; tenure_loyalty_credit p); exclusion 4 (2m/2p). Labels honest; tiers disjoint and distinct; fall-throughs = baselines; ladders stated in full in the rules. Cross-difficulty: billing (cancellation), physdmg (driver addition, exclusion).
- **R2-F1 closed:** both minimum charge periods are removed.
- Realism of the two new ladders (finding R3-F1):
  - `financed_report_window` lengthens the newly-acquired-vehicle report window by 30 days if a loan starts on the acquisition date and by 14 days if a loan is recorded on another date. In personal auto the newly-acquired-vehicle reporting period is a contract term (commonly 14 or 30 days) that is the same for every insured. Whether the purchase was financed, or when a loan was booked, is not something the line weighs for it. A financed purchase is if anything reported sooner, because the lender demands proof of insurance at closing.
  - `member_report_window` lengthens the household-member report window by 15 days for a newly licensed member or 7 days for a member who moved in, but only "for a policy record that carries no lapse marker". The licensed/moved-in part is plausible, since a newly licensed teen's card arrives by mail. The lapse-marker part is a condition no business weighs for how long a household has to report a member. A prior lapse in Cardinal coverage bears on tenure and forgiveness, not on a reporting deadline.
  - If `financed_report_window` is struck as unreal, the vehicle addition computation holds 3 surviving factors, below the floor of 4.
- R2-O5 tiers (short_hold_share, rated_period_retention, at_fault_loss_share) kept — observation, as declared by the reworker.
- Loss payee notice tiers (removal and cancellation) now count coverage days the lender's interest actually stayed open (up to the payoff, at most 10) — realistic; the r2 questionable tier is gone.

### findings (revision_3)

**R3-P1 — SOURCE-POLICY RED (new) — financed report window conflicts with unsuperseded base sentences of auto_vehicle_changes** (bears on task 0)
- Evidence: overwrite (a) in auto_ext_vehicle_addition_premium vs base yaml 1250-1257 and parameter_schema line 64.
- Consequence: demonstrated in 0.md revision_3.

**R3-F1 — SOURCE-FACTOR RED (new) — the two new report-window ladders rest on conditions the line does not weigh** (`financed_report_window` bears on task 0; `member_report_window` bears on task 1)
- Consequence: demonstrated in each task file.

**Status of revision_2 items:** R2-P1 closed; R2-P2 closed; R2-F1 closed; R2-O1 closed; R2-O3 closed; R2-O4 closed; R2-O6 closed. R2-O2 (seeded add rows carry early effective dates base forbade): no longer contradicted by the published policy for either task. The reworker closed it by lengthening the report windows rather than changing the rows, and that lengthening is what R3-P1 and R3-F1 now find. R2-O5 kept (observation). O1, O8 persist.

### closing_checklist (revision_3)

Written 2026-10-05T13:05Z, after both revision_3 reveals; the revision_3 charter-global section above was written at 13:02Z before any reveal and is not edited.

- Verdicts: **task 0 SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 SOURCE-FACTOR RED.** No charter-global RED without a task consequence remains. The difficulty is **not closed**.
- Revision_2 REDs: R2-P1, R2-P2, R2-F1 all closed. Observations R2-O1, R2-O3, R2-O4, R2-O6 closed. R2-O5 kept. R2-O2 resolved by policy change, which introduced the new defects below.
- New in revision_3: R3-P1 (financed window overrides only one of the base sentences that fix the newly-acquired-vehicle window — second reading on task 0), R3-F1 (`financed_report_window` and the lapse-marker part of `member_report_window` are conditions the line does not weigh for a reporting window; each decides its task's tier).
- Nothing else regressed: trees, edges, scoping of E1''/E3'', tool module, uuid8s, sibling-charter boundaries, factor counts and weight all PASS; all r3 gold figures reproduced blind.
- Gates: cited from the conductor's r3 snapshot; charter hash ce0d832f… and tool hash a2bc4ef5… unchanged at reveal.

## revision_4

### charter_global_frozen (revision_4)

- Written 2026-10-05T13:14Z, before any revision_4 task GT was revealed. Earlier revisions untouched.
- Hashes verified (r4 MANIFEST and live files): auto.extended.yaml `f48404e1…1cbc` (changed), task_tools.py `a2bc4ef5…519f` (unchanged since r2), task_0.view.json `287c31bc…8f26`, task_1.view.json `347b3931…4729`. Charter changed, so the charter-global sections are re-derived; the tool-module conclusions of revision_2 carry forward on the unchanged tool hash. Base copy identical to blueprint; blueprint untouched. r4 gates all green (traceability deferred).
- contamination_disclosure: r1-r3 GT of both tasks were revealed in earlier rounds. The r4 worlds differ from r3 only in recorded dates (task 0: the Kia add and its loan recorded 2026-09-12 instead of 09-22; task 1: Tyler's add recorded 2026-09-11 instead of 09-25) and one persona sentence. No r4 scored value seen before freezing.

### policy_conflict_scan / rule_compute_equivalence / prerequisites (revision_4)

- Same five policies, tools, owners, edges (E1'', E2, E3'') and scopes as revision_3; acyclic; edges scoped and matching their conditions; unique resolving writes; tools silent. No sibling-charter conflict.
- Changes since r3, swept sentence by sentence:
  - Report windows reverted to the base parameters (newly_acquired_additional_report_days; household_driver_report_days) in the vehicle addition, driver addition, removal-credit and exclusion-credit rules and computes. Both r3 overrides of auto_vehicle_changes / auto_driver_changes report sentences are withdrawn. The charge-start ladders now apply the base windows exactly as base states them: inside the window from the effective/acquisition date, otherwise from the recorded (request) date. **R3-P1 closed**: no unsuperseded base sentence now disagrees.
  - The loyalty credit of both addition policies is split into `addition_loyalty_credit` / `tenure_loyalty_credit` (tenure only: 10 / 5 / nil) and a new `continuous_coverage_share` (lapse marker: none -> 1; marker 36+ months old -> 0.5; marker under 36 months -> nil), multiplied as loyalty % × share. Rule, compute_basis and compute agree (MONTHS(lapse marker, NOW) ≥ 36).
- O1 persists.

### factor_ladders (revision_4)

- Vehicle addition 4 (late_report_charge_start m; excess_vehicle_rating p; addition_loyalty_credit p; continuous_coverage_share p). Driver addition 5 (late_report_start m; operator_assignment p; at_fault_loss_load p; tenure_loyalty_credit p; continuous_coverage_share p). Removal 5, cancellation 5, exclusion 4 unchanged. Bounds met; labels honest; fall-throughs = baselines; ladders in the rules.
- **R3-F1 closed:** `financed_report_window` and `member_report_window` are removed.
- **The loyalty split, judged on its merits:**
  - Continuous coverage is a condition the line genuinely weighs for a loyalty/tenure credit. Carriers withdraw or cut loyalty and continuous-insurance credits after a lapse, and a lapse that is old weighs less than a recent one. So the lapse marker belongs to this quantity, unlike r3's reporting window.
  - Tiers are distinct (1 / 0.5 / 0). The fall-through (a lapse within 36 months -> no loyalty credit) is a real treatment for that situation and equals the baseline. `baseline.rule` states the share as nil, so the factor's `baseline` is honest by the charter's own standard method.
  - The two factors are independent inputs (tenure from inception; recency of a lapse) combined multiplicatively. Each bears weight only while the other is non-zero, which holds on both worlds (tenure 99 / 57 months, no lapse marker).
  - Observations (R4-O1):
    - The split raises the factor count on one quantity, the loyalty credit, from one compound factor to two.
    - The continuity ladder's ordinary case (no lapse) is its top tier, while its baseline (nil) is the exceptional recent-lapse case. An agent who finds the tenure document but not the continuity document computes nil loyalty, not the right credit, so the factor tests document discovery as intended.
  - Neither observation is a defect under the skill's tests.
- R2-O5 tiers kept (observation).

### findings (revision_4)

- No new charter-global RED. Status: R3-P1 closed; R3-F1 closed. R2-O2 is now genuinely closed: the reseeded add rows (Kia reported on day 11 of 14; Tyler on day 28 of 30) agree with base auto_vehicle_changes / auto_driver_changes as written. Observations O1, O8, R2-O5, R4-O1 persist.

### closing_checklist (revision_4)

Written 2026-10-05T13:14Z, after both revision_4 reveals. The revision_4 charter-global section above was written before any reveal and is not edited.

- Per-task files: 0.md and 1.md each carry revisions 1-4 in order, each with a frozen derivation before its comparison. **Task 0 revision_4: PASS. Task 1 revision_4: PASS.**
- Coverage and scope: five extended policies, all covered; scopes {vehicle addition, vehicle removal, cancellation} and {driver addition, exclusion} pairwise disjoint over whole trees; tools and GT closed; uuid8s 9393c661 / 524db3a4 / 695fb1aa / cd2c8cbf / c094ed6f independent — PASS.
- Trees: task 0 n=2 with 2 value_input edges, task 1 n=1 with 1 value_input edge; both roots owner=user (customer signs); the difficulty graph is acyclic; every edge is unmet at the opening and bears weight; prerequisite sentences are scoped exactly to their conditions; no waits; tools validate nothing — PASS.
- Factors: every computation has a definite, honest baseline ≠ gold. Factor counts: vehicle addition 4, removal 5, cancellation 5, driver addition 5, exclusion 4, each with ≥2 parameter and ≥1 method. Each task has multi-source and cross-difficulty factors (billing; physdmg) on seeded rows. Every factor bears weight on its world. Every ladder has 3 distinct tiers stated in its rule, on conditions the line weighs — PASS.
- Policy self-consistency, including sibling charters and base overrides — PASS. Unique solution: blind derivation equals GT on both tasks — PASS.
- Gates: the conductor's revision_4 snapshot (all eight green, traceability deferred until the KB is published) is cited. The auditor did not re-run the gates; charter f48404e1… and tools a2bc4ef5… were unchanged at reveal.
- Open observations (no rework required by this audit): O1 (baseline sentences beside ladders in every rule), O8 (renewal event types claimed but uninstantiated), R2-O5 (short_hold_share, rated_period_retention, at_fault_loss_share — invented, plausible at best), R4-O1 (loyalty split), R4-O2 (stale design_rationale sentence in task 1).
- **The difficulty passes the source-layer policy-task audit at revision_4.**
