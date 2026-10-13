# Policy-task audit — in_place_home_sale_approvals / charter-global

## charter_global_frozen

- Freeze time: 2026-10-09T00:16Z (written before any task GT was revealed; nothing in this section is derived from a revealed GT).
- Auditor: independent erl-task-policy-audit agent (not the instantiating agent).
- Frozen inputs (sha256 recomputed by the auditor, equal to the coordinator's HASHES.txt):
  - `tasks/in_place_home_sale_approvals/resale.extended.yaml` f53c9ed4a9fb14be48876e979b80efff0cf2327fbc948f5ee86b46e3ce9db00f
  - `tasks/in_place_home_sale_approvals/task_tools.py` 45ebb0cf5d2aaf5c4096ca773f41ca13ee8d0bc950dfc0f05c650b03df99787d
  - masked views `0.view.json` 48145d27…a91d2, `1.view.json` 2bfa94c1…a70c (fields kept: frozen_time, user_scenario, initial_state).
- Also read: `blueprint/blueprint.yaml`, `blueprint/products/resale.yaml` (base), `blueprint/products/{lease,rules,utility}.yaml` (variant parameters read by cross-category factors), `blueprint/db_schema.json`, `blueprint/share_tools.py` (finder list), `skills/erl-task-instantiate/scripts/check_compute.py` (semantics of MONTHS/DAYS/X*/CFIELD/RND as the runtime evaluates them).
- Masked and not read: `tasks/in_place_home_sale_approvals/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, closures), all other audits, other difficulties' tasks.

### entry_conditions (Step 0)
Gate snapshot supplied with the brief and on disk (`.audit_views/policy_task/in_place_home_sale_approvals/GATES.txt`): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred to render. Masked views and hashes supplied. Entry conditions complete.

### base copy
`diff` of `resale.extended.yaml` lines 1–954 against `blueprint/products/resale.yaml`: identical (only the extended_policies banner added). The base section is verbatim.

### policy_conflict_scan
Extended policies (5): `resale_ext_initial_inspection_charge` (post_inspection_fee_534473a1, agent), `resale_ext_vacant_home_check_charge` (post_vacant_home_check_55c2c08b, agent), `resale_ext_reinspection_booking_payment` (pay_reinspection_booking_26088ed0, user), `resale_ext_appraisal_charge` (post_appraisal_fee_5faa8f88, agent), `resale_ext_lowest_closing_price` (set_asking_price_9cfe4b28, user).

- Overlapping subjects: three policies write `resale_fee_charge` but each on its own charge_type (inspection_fee / vacant_home_check / appraisal_fee) and its own source object (initial inspection record / billing period / appraisal record) — no overlap. The two root policies (booking payment, lowest closing price) define `fees owed on the file` with the same sentence content ("every charge … less every payment, credit and proceeds deduction … never less than zero") and identical compute (`RND(MX(0, charges - payments - credits - deductions))`) — compatible.
- Triggers / eligibility: the three charge policies are `state_due`; the two roots `on_request`. Initial-inspection charge posts nothing at inspection_fee 0.00 (packages 5, 6); vacant-check posts nothing where the check is included (packages 4–6); the appraisal exists only on the guaranteed package (base guarantee_offered). No two policies fire on the same object.
- Time anchors: each charge dated on its own record (inspection record date, vacancy/first-of-month, appraisal record date); roots evaluated on the handling date. No conflict.
- Terminal states: charges raise fees_balance; payment lowers it; price change replaces list_price. No conflict.
- Cross-category read boundaries: reads only (lease, rules, utility, insurance, loan); no cross-category write.
- Inter-extended interaction: the booking policy's overwrite re-prices every re-inspection; the appraisal policy's condition-addendum reads inspection repair counts. Neither changes another extended policy's scored quantity.
- Scope partition (inferred pre-reveal from the prerequisite graph): tree A = {booking payment ← initial inspection charge, vacant-home check charge}; tree B = {lowest closing price ← appraisal charge}. The two trees are disjoint and together cover all five extended policies. To be confirmed against charter_scope after reveal (closing checklist).

### rule_compute_equivalence
Every compute binding of every extended policy has a verbatim `compute_basis` quotation that is a sentence (or clause) of the policy's own `rule`; every ladder tier in `factors[].ladder` is stated in the rule and implemented as a branch of the `decides` binding (checked tier by tier for all 25 declared factors). No compute branch without a rule sentence was found; no rule tier without a compute branch was found. Divergences found, none with a consequence on either task world of this difficulty (recorded as observations O1–O6 under findings):

- `resale_ext_vacant_home_check_charge`: rule ties the visit-frequency rate and site-crew credit to "the month charged" and the part-month rate to "the month in which the home became vacant", but compute evaluates `check_month = month(NOW)` and `vac_this_month = month(vac_date) == month(NOW)`; a back-month billing period cannot be computed. (O1)
- `resale_ext_initial_inspection_charge`: rule counts notices "served on the seller's site"; `XCOUNT('rules', …)` counts the customer's notices on any site. (O2)
- `resale_ext_reinspection_booking_payment`: `baseline.rule` adds "the package's reinspection_fee for the coming visit" unconditionally, while compute's `visit_fee` is 0 when the coming visit is an included re-inspection; on a package with included re-inspections remaining, substituting every factor baseline in compute gives fees owed + 0, while baseline.rule gives fees owed + reinspection_fee. (O3)
- `resale_ext_appraisal_charge`: rule "each appraisal recorded on the file is charged once"; compute prices only `LATEST(... resale_appraisal)`. Loan read `CFIELD('loan','funded_date', lease_id=…)` takes any loan status while the rule speaks of "the Hearthstone Home Finance loan on the home". (O4, O5)
- All policies: `RND` is Python `round(x, 2)`, not half-up; checked on both worlds with Decimal — no exact half-cent intermediate occurs. (O6)

### action_binding_and_uuids
- `(target_tool, computes)`: (post_inspection_fee_534473a1, amount), (post_vacant_home_check_55c2c08b, amount), (pay_reinspection_booking_26088ed0, amount), (post_appraisal_fee_5faa8f88, amount), (set_asking_price_9cfe4b28, new_list_price) — each claimed by exactly one policy.
- Owners: three `agent` charge tools, two `user` tools (payment, price change) — matching the blueprint's split (charges are agent service actions; paying and changing the price are the seller's own acts).
- Function bodies: each tool computes nothing, checks no status, no prerequisite, no amount; it writes one ledger row or one field and adjusts fees_balance. No confirmation/review/wait procedure is added.
- Docstrings name no other tool and state no position in a sequence. They contain the words "then" ("The seller then sees …") and "after" ("fees owed on the file after the charge/payment") only in the sense of the tool's own result (observation O9).
- uuid8s: 534473a1, 55c2c08b, 26088ed0, 5faa8f88, 9cfe4b28 — five distinct values, no shared prefix or tail, no sequential or adjacent pattern.

### prerequisite_graph
- `prerequisite` filled in on all five: `[]` on the three charge policies and on none other; the booking payment has two edges, the lowest closing price one.
- Edges: booking → resale_ext_initial_inspection_charge (value_input, gate fees_owed, state); booking → resale_ext_vacant_home_check_charge (value_input, gate fees_owed, state); lowest_closing_price → resale_ext_appraisal_charge (value_input, gate fees_owed, state). Every `problem` is an extended policy id in this file, none base, none self. Graph acyclic (depth 1, two disjoint stars).
- Each `policy_source` is a verbatim sentence of the blocked policy's own rule (booking rule sentences 2 and 3; lowest-price rule sentence 2).
- `form: state` on all three; no `fallback_reason` present, as required.
- `resolved_by` equals the depended-on policy's `target_tool` in all three; each tool's effect (a ledger charge raising fees_balance) changes `fees_owed`, the binding named in `gate`, which exists in the blocked policy's compute. `kind: value_input` matches.
- `condition` vs sentence: edges 1 and 2 match the sentence's scope (the "except …" clause of edge 1 and "except on a package whose check is included" of edge 2 are exactly the cases where no charge is "owed"). Edge 3's condition ("for every appraisal record on the file the ledger holds the fee charge of type appraisal_fee") drops the sentence's word "owed"; it diverges only on a redone appraisal at Hearthstone's cost (see O7). No authoring-viewpoint phrasing in any `prerequisite` field.

### prerequisite_sentences
Four-point test, each edge:

1. "The booking payment is fixed only after the file's ledger carries the inspection charge owed for every initial inspection recorded on the file." — connective "only after"; waited-on state "the file's ledger carries the inspection charge owed for every initial inspection recorded on the file", in table words (ledger, inspection charge, initial inspection record), no action/performer/tool; no tool, policy id, snake_case token or row id; strength matches the condition. Writes that can bring the state about in this difficulty: only post_inspection_fee_534473a1 (the only tool creating `charge_type=inspection_fee`). Derivation: sentence → reader looks for a policy whose rule charges the initial inspection → `resale_ext_initial_inspection_charge` ("The initial pre-sale inspection of a resale file is charged once, against the initial inspection record it bills…") → its target tool. Single reading.
2. "The booking payment is not worked out until the file's ledger carries the vacant-home check charge owed for every calendar month in which the occupancy recorded on the file has stood vacant." — connective "not … until"; record-visible state; no tool/id; matches the condition. Only post_vacant_home_check_55c2c08b creates `vacant_home_check` charges. Derivation → `resale_ext_vacant_home_check_charge` ("each month's check is charged within that month on its billing period…"). Single reading.
3. "Before the lowest closing price is worked out, the file's ledger must carry the appraisal fee owed for every appraisal recorded on the file." — connective "Before"; record-visible state; no tool/id. Only post_appraisal_fee_5faa8f88 creates `appraisal_fee` charges. Derivation → `resale_ext_appraisal_charge` ("each appraisal recorded on the file is charged once, against the appraisal record it bills…"). Single reading.

- No second wording of any dependency in the blocked rules; no tool name or other problem id anywhere in any rule. The depended-on rules (initial inspection, vacant check, appraisal) do not restate the sentences.
- Undeclared cross-problem orders: none found. The vacant-check rule reads "the file's winterization charges" (a base posting, not an extended problem); the lowest-price rule reads "a payoff statement on the loan" as a selector (it does not require one to be issued). Neither states an order between two problems of this difficulty.
- Base rule sentences stating a cross-problem order (e.g. base closing conditions, guaranteed terms "before the home is listed") ground no edge; no tree rests on them.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (finding half only; consequences are judged in the task files).

- `resale_ext_initial_inspection_charge` (refs: file_opening_terms, inspection_terms, closing_settlement, withdrawal_terms, vacant_home_terms): inspection_terms s2 (initial inspection charged at inspection_fee; none at 0.00) — handled differently, declared in `overwrite`, merged semantics unique (fee 0.00 still posts nothing; above 0.00 the subtotal × visit-timing rate). Other inspection_terms sentences (scheduling, re-inspection, repairs, coordination, validity) — not touched. file_opening_terms, closing_settlement (inspection-fee credit at closing on packages 3–4 credits "the initial inspection fee": the extended charge is the amount credited back — no conflict, closing not in scope), withdrawal_terms, vacant_home_terms — followed. Anonymous intermediate / 0-1 multiplier / dropped branch: the overdue tier multiplies by 0.0 — but that is the declared replacement itself (the replaced_by sentence includes the visit-timing rate), not an undeclared zeroing.
- `resale_ext_vacant_home_check_charge`: vacant_home_terms s2 — handled differently, declared; s1 (seller must report occupancy) followed and sharpened ("accepted occupancy report"); s3 winterization — followed (the winterization charge is only read). Others followed.
- `resale_ext_reinspection_booking_payment` (refs: fee_billing_terms, inspection_terms): inspection_terms s3 (re-inspection charged at reinspection_fee, first included ones credited) — handled differently, declared. fee_billing_terms s1 (paid through accepted channels), s2 (oldest charge first), s3–s4 (credits) — followed; a payment above fees owed leaves a credit, which base does not forbid.
- `resale_ext_appraisal_charge` (refs incl. guaranteed_terms): guaranteed_terms s2 (appraisal charged at appraisal_fee) — handled differently, declared. guaranteed_terms s4 ("an older appraisal is redone at Hearthstone's cost before the offer is made") — NOT named in `overwrite`, yet the extended rule says "each appraisal recorded on the file is charged once" and the edge-3 condition requires a charge for every appraisal record: on a file carrying a redone appraisal, base gives no charge, extended gives a charge. Undeclared override in the charter (finding O7); no world of this difficulty carries a redone appraisal, so no consequence is demonstrable here.
- `resale_ext_lowest_closing_price` (refs: listing_terms, closing_settlement, closing_conditions, purchase_contract_terms): closing_settlement s1 (commission) — handled differently (loyalty reduction), declared. closing_settlement s2–s7, closing_conditions s1–s8 — followed (the lowest closing price is a new quantity built from them; the horizon rent and projected payoff are the extended's own definition of what the closing will have to pay, not a replacement of a base quantity). listing_terms s3 ("asking price … changed … only while listed") followed; listing_terms s5 (guaranteed program: asking price never above list_price_max_pct_of_appraisal) — not addressed by the extended rule: where the lowest closing price exceeds the cap the charter does not say what happens (O8; not binding on task 1's world, see 1.md).

### factor_ladders
Effect labels as declared; P = parameter, M = method; MS = every non-fall-through fork a conjunction over distinct evidence (as check_compute measures it); XD = cross_difficulty.

| policy | factor | label | tiers | MS | XD | ladder in rule | honest label? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| initial_inspection | inspection_home_size_addition | P | 3 (55 / 40 / 0) | no | lease | yes | yes |
| | inspection_home_age_addition | P | 3 (35 / 15 / 0) | no | lease | yes | yes |
| | inspection_site_condition_addition | P | 3 (30 / 15 / 0) | no | rules | yes | yes |
| | inspection_repair_report_addition | P | 3 (30 / 15 / 0) | no | — | yes | yes |
| | inspection_visit_timing_rate | M | 3 (×0.0 / ×0.5 / ×1.0) | no | — | yes | **no — a rate substituted into `RND(subtotal × visit_rate)`** |
| vacant_check | check_visit_frequency_rate | M | 3 (×2.0 / ×1.5 / ×1.0) | yes (lease community ∧ month charged) | lease | yes | **no — a rate in `(…)×visit_rate×part_rate`** |
| | check_size_addition | P | 3 (15 / 10 / 0) | no | lease | yes | yes |
| | check_utility_walkthrough_addition | P | 4 (25 / 20 / 10 / 0) | no (tier 3 single) | utility | yes | yes |
| | check_site_crew_credit | P | 3 (20 / 10 / 0) | yes (rules plan ∧ month charged) | rules | yes | yes |
| | check_alarm_credit | P | 3 (15 / 5 / 0) | no | insurance | yes | yes |
| | check_part_month_rate | M | 3 (×0.5 / ×0.75 / ×1.0) | yes (both on the occupancy report + clock) | — | yes | **no — a rate in the same product** |
| booking | booking_items_fee | P | 3 (120 / 95 / reinspection_fee) | no | — | yes | yes |
| | booking_section_surcharge | P | 3 (30 / 15 / 0) | no | lease | yes | yes |
| | booking_repeat_visit_surcharge | P | 3 (60 / 35 / 0) | no | — | yes | yes |
| | booking_repair_window_rate | M | 3 (×2.0 / ×1.5 / ×1.0) | no | — | yes | **no — a rate in `RND((items+section+repeat)×window_rate)`** |
| appraisal | appraisal_home_length_addition | P | 3 (60 / 30 / 0) | no | lease | yes | yes |
| | appraisal_regional_panel_addition | P | 3 (75 / 40 / 0) | no | lease | yes | yes |
| | appraisal_condition_addendum_addition | P | 3 (50 / 25 / 0) | no | — | yes | yes |
| | appraisal_site_premium_addition | P | 3 (60 / 30 / 0) | no | lease | yes | yes |
| | appraisal_loan_update_rate | M | 3 (×0.6 / ×0.8 / ×1.0) | no | loan | yes | **no — a rate in `RND(sum×update_rate)`** |
| lowest_price | price_loyalty_reduction | P | 3 (1.0 / 0.5 / 0 pts) | yes (lease move-in ∧ loan status) | lease | yes | yes |
| | price_seasonal_market_days | P | 3 (30 / 20 / 0 days) | yes (lease community ∧ handling month) | lease | yes | yes |
| | price_payoff_figure | M | 3 (statement amount / projection formula / principal) | no | loan | yes | yes — three different algorithms |
| | price_site_lease_amount | M | 3 (balance+horizon rent+late cap / balance+horizon rent / max(0,balance)) | shape-yes, same lease record | lease | yes | yes — the horizon-rent sub-computation is included or not |

Structural facts common to all: every factor's `decides` is an input (never `result`), bindings disjoint across factors, every ladder ≥ 3 pairwise-disjoint tiers drawn from the policy's params / variant parameters, no two tiers of a ladder select the same value or method, every fall-through equals the factor's `baseline`, and every policy `baseline.rule` is a sentence of its rule and yields a definite number with no factor (inspection_fee; vacant_home_check_fee_monthly; fees owed + reinspection_fee; appraisal_fee; the standard lowest-closing-price formula).

Realism: every tier condition is one a manufactured-home resale operation plausibly weighs for that quantity (home size/age for inspection and appraisal effort; violation history and repair-report length for inspection effort; climate and storm checks, crew coverage and alarms for vacant-home checks; failing-item count, section type, repeat visits and lateness for re-inspection visits; regional panel, lot premium and an existing origination appraisal for the appraisal; tenure-with-affiliate-loan loyalty, seasonal market time, payoff statement currency and lease arrears for a break-even price). No condition holds of every customer who reaches its write, and no fall-through is a treatment such a business would not publish. No unreal ladder found.

Counts — declared vs surviving the label test (a mislabelled factor is struck, per the skill's counting rule):

| policy | declared (P/M/total) | surviving (P/M/total) | bounds 4–6, ≥2 P, ≥1 M |
| --- | --- | --- | --- |
| initial_inspection | 4/1/5 | 4/0/4 | **fails ≥1 M** |
| vacant_check | 4/2/6 | 4/0/4 | **fails ≥1 M** |
| booking | 3/1/4 | 3/0/3 | **fails ≥1 M and 4-factor floor** |
| appraisal | 4/1/5 | 4/0/4 | **fails ≥1 M** |
| lowest_price | 2/2/4 | 2/2/4 | passes |

Per task (inferred trees): tree A computations (initial inspection, vacant check, booking) — multi-source factors present only in the vacant check (visit-frequency, crew credit, part-month — each pairs one record with the month charged / the clock; see O11); cross-difficulty factors lease, rules, utility, insurance. Tree B (appraisal, lowest price) — multi-source `price_loyalty_reduction` (lease ∧ loan, two distinct records); cross-difficulty lease, loan.

### findings
- **F1 — SOURCE-FACTOR RED (charter-global finding; consequence demonstrated per task in 0.md and 1.md).** Symptom: five factors labelled `method` are multipliers whose tiers substitute a different number into an unchanged formula. Root cause: the effect label does not match the compute shape. Evidence: `inspection_visit_timing_rate` (`result: RND((std_fee + size_add + age_add + notice_add + report_add) * visit_rate)`, `visit_rate ∈ {1.0, K('late_visit_rate')=0.5, K('overdue_visit_rate')=0.0}`); `check_visit_frequency_rate` (`visit_rate ∈ {2.0, 1.5, 1.0}` in `(std_fee + size_add + utility_add) * visit_rate * part_rate`); `check_part_month_rate` (`part_rate ∈ {0.5, 0.75, 1.0}` in the same product); `booking_repair_window_rate` (`visit_fee: RND((items_fee + section_add + repeat_add) * window_rate)`, `window_rate ∈ {2.0, 1.5, 1.0}`); `appraisal_loan_update_rate` (`result: RND((…) * update_rate)`, `update_rate ∈ {0.6, 0.8, 1.0}`). In each, every tier evaluates the identical expression and only the numeric constant differs — the skill's definition of a mislabelled `method` ("tiers only substitute a different number into the same formula (a rate …)"). Consequence: struck from the count, four of five computations have zero honest `method` factors and the booking computation has three factors in all (table above). Bears on: task 0 (all three computations), task 1 (appraisal computation).
- O1 — vacant-check compute evaluates "the month charged" as month(NOW); rule ties it to the billing period. Tasks: none affected (task 0 charges only the current month).
- O2 — site-condition notices scoped to customer, rule says seller's site. Tasks: none (one site).
- O3 — booking baseline.rule vs included-reinspection branch. Tasks: none (task 0 package has 0 included re-inspections).
- O4 — appraisal compute prices only the latest appraisal. Tasks: none (one appraisal on task 1).
- O5 — appraisal loan read is status-blind. Tasks: none (task 1 loan active).
- O6 — RND not half-up. Tasks: none (no half-cent intermediates on either world, verified with Decimal).
- O7 — undeclared override of base guaranteed_terms s4 (redone appraisal at Hearthstone's cost) by "each appraisal recorded on the file is charged once"; edge-3 condition drops "owed". Under the RED threshold it is recorded as an observation: no world in this difficulty carries a redone appraisal, so no second answer is demonstrable. Bears on task 1 only potentially.
- O8 — the lowest-price rule is silent where the result exceeds the guaranteed program's list-price cap (base listing_terms s5). Bears on task 1 (not binding there).
- O9 — docstrings use "then"/"after" in the own-result sense only.
- O10 — the seeded re-inspection charge rows are checked against the extended re-pricing in each task file.
- O11 — "multi-source" in tree A: the only factors whose every non-fall-through tier is a conjunction pair one DB record with the month being charged (a property of the write / the clock) rather than with a second record; under a strict "distinct records" reading tree A has no multi-source factor (utility walkthrough comes closest, but its third tier is a single condition). Recorded as an observation because the reading of "record" is not settled by the artifacts.

## closing_checklist
Written 2026-10-09T09:25Z, after both reveals. The difficulty does **not** close: not every task passes all four relationships.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; first round, no older revisions. Comparison sections present; verdicts — task 0: SOURCE-FACTOR RED (F1) + SOURCE-TASK RED (false objective/necessity assertions); task 1: SOURCE-FACTOR RED (F1). Not every comparison carries a PASS.
- Coverage / scope: charter_scope task 0 = {initial_inspection_charge, vacant_home_check_charge, reinspection_booking_payment}, task 1 = {appraisal_charge, lowest_closing_price} — pairwise disjoint, jointly cover all five extended policies; scope spans each whole tree (matches the pre-reveal inference). Task tools and GT closed (each gold write uses its policy's target tool); uuid8s independent (§ action_binding_and_uuids).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user write (booking payment), acyclic; task 1 — 1 prerequisite problem, 1 value_input edge, user write (price change), acyclic; difficulty-wide graph acyclic, no cross-task edge. PASS.
- Factors: every computation declares a self-sufficient baseline whose fall-back differs from gold and every declared factor bears weight on its task's world; but four of five computations (initial inspection, vacant check, booking, appraisal) have no honestly labelled `method` factor and the booking computation has three surviving factors (F1). FAIL.
- Gates: not re-run by the auditor (Step 0: the auditor cites the coordinator's snapshot; no final form exists since the difficulty does not close).

## revision_2

### charter_global_frozen (revision 2)
- Freeze time: 2026-10-09T10:18Z, before any round-2 task JSON was opened. Auditor: same independent auditor as round 1.
- Inputs (sha256 recomputed, equal to the coordinator's list): `resale.extended.yaml` 98ed7d1fb389b444e761523192aaece9d23dd49529fc53b25c1b6e6229a3f762 (changed from f53c9ed4…), `task_tools.py` 4a74f3d235839c44ba98e6bfb9376c119aa780076a182c3f9da66ba09c5085fc (changed from 45ebb0cf…), `0.view.json` 48145d27… (unchanged), `1.view.json` d4a08731e822efeff1b32563a9e8e230c28d19e5e9941c5bb004c5ec7087f11b (changed). Gate snapshot (GATES.txt): all eight rc=0, traceability deferred. Entry conditions complete.
- Both shared inputs changed, so every charter-global section is re-derived in full below (the round-1 text above is left untouched).
- contamination_disclosure: the auditor read the round-1 GT of both tasks during round 1 (round-1 gold figures and the round-1 objective/necessity text). No round-2 task JSON had been opened when this section was written; nothing here depends on a task GT.

### base copy (rev 2)
Lines 1–954 of the new charter `diff` clean against `blueprint/products/resale.yaml`. Verbatim.

### policy_conflict_scan (rev 2)
Same five policies, same target tools and owners, same two-tree structure. Changes affect only how the amounts are computed, plus two sentences added to the lowest-closing-price rule (how tenure is measured; what happens at the guarantee's list-price ceiling) and one added to the appraisal rule (a redone appraisal carries no charge). Re-scanned: no two policies overlap on charge type or source object; both roots keep the identical fees-owed definition; time anchors unchanged; the new ceiling clause sends the lowest-price request to a human only where the figure exceeds the guarantee's ceiling, and touches no other policy. No conflict.

### rule_compute_equivalence (rev 2)
Every binding re-checked against its `compute_basis` quotation and the rule:
- initial inspection: `site_plan` (CFIELD rules_plan_id by lease) + `XCOUNT(..., rules_plan_id=site_plan)` = "notices served under the site-care plan record of the seller's site" (closes O1/O2 class item O2). `additions`, `timed_charge` (0 / additions / std_fee + additions) and `result` match rule s4 and s9 tier by tier.
- vacant check: new rule s2 "The month charged is the calendar month in progress on the day the check charge is worked out." now grounds `check_month = month(NOW)` (O1 closed as a rule/compute mismatch). `visit_charge` (×freeze_weekly_rate / + storm_followup_fee / subtotal), `crew_credit` (snow tier now also needs a freeze community; mowing tier = other community or non-winter month) and `result` match the rule. Residual: the edge-2 condition counts every month "from the month of the … occupancy report … through the month in progress", while the rule can only price the month in progress; on a file with an uncharged past vacant month the policy gives no amount for that month (O1-r, no world in this difficulty has one).
- booking: `window_fee` (inspection_fee replaces items fee / ×late_rate / sum) matches s10; `baseline.rule` now says "plus the package's reinspection_fee for the coming visit unless that visit is an included re-inspection", in line with compute's included branch (O3 closed).
- appraisal: `loan_funded` reads only active or delinquent loans = "the open (active or delinquent) Hearthstone Home Finance loan" (O5 closed); `loan_age_months` counts to `F('opened_date')` = "to the date the resale file was opened"; the LATEST-appraisal binding is gone, and the charge is per the appraisal record named in the call (O4 closed). `update_charge` (desktop_update_fee / sum × update_older_rate / sum) matches s7.
- lowest price: new s6 "The seller's tenure is counted in whole calendar months from the move-in date … whatever term is running." grounds `tenure_months = MONTHS(move_in, NOW)` (1.md round-1 O-c closed). New s11 (the guarantee's ceiling, then a human hand-off) is an eligibility outcome with no compute branch. It is a refusal path, not a figure, so compute has nothing to implement; observation O8-r (whether a world reaches it is checked per task).
- RND remains Python `round` (O6 unchanged; checked per task).
No compute branch without a rule sentence was found, and no rule tier without a branch.

### action_binding_and_uuids (rev 2)
`(target_tool, computes)` pairs and owners unchanged, one policy each. Function bodies unchanged in effect (one row / one field, fees_balance adjusted, no checks). Docstrings: "then" and "after" removed ("fees owed on the file including this charge", "net of this payment"). No ordering word, no other tool named (O9 closed). uuid8s unchanged: 534473a1, 55c2c08b, 26088ed0, 5faa8f88, 9cfe4b28 — distinct, not derived from one another.

### prerequisite_graph (rev 2)
Same three edges, ids, kinds, gates, forms and resolving tools. `policy_source` sentences byte-identical to round 1 and still verbatim in the blocked rules. Conditions: edge 1 now says "or the visit-timing method leaves nothing to charge" (matches the renamed method). Edge 3 now reads "For every appraisal record on the file that the seller owes … an older appraisal redone at Hearthstone's cost owes none", which matches the sentence's "owed" and the appraisal rule's new s2 (the edge-3 half of O7 closed). Acyclic, depth 1.

### prerequisite_sentences (rev 2)
The four-point test and the one-write derivations of round 1 (§ prerequisite_sentences above) still hold verbatim: same sentences, and the same single write creating each charge type. Re-checked the added rule sentences for undeclared cross-problem orders: vacant s2 (month charged), appraisal s2 (redo not charged), price s6 (tenure) and s11 (ceiling → human) each order nothing between two problems of this difficulty. No rule names a tool or another problem's id.

### override_declarations (rev 2)
- initial inspection: inspection_terms s2 is still the only base sentence handled differently; the `overwrite.replaced_by` is updated to the new method wording and equals rule s4. Declared; merged meaning unique (0.00 fee still posts nothing).
- vacant check: vacant_home_terms s2 replaced; `replaced_by` updated to the visit-frequency method wording, equal to rule s6. Declared.
- booking: inspection_terms s3, unchanged declaration.
- appraisal: guaranteed_terms s2 replaced ("that appraisal is charged to the seller once …"). guaranteed_terms s4 (redo at Hearthstone's cost) is now **followed**: rule s2 "An older appraisal redone at Hearthstone's cost before the guaranteed offer carries no charge to the seller." The undeclared override O7 is closed.
- lowest price: closing_settlement s1 declared as before. listing_terms s5 (the guarantee's ceiling) is now restated and given a defined outcome in rule s11 (O8 closed as a silence). The added outcome (leave the price, hand off) does not contradict base, which forbids the price.

### factor_ladders (rev 2)
| policy | factor | label | tiers | honest label? |
| --- | --- | --- | --- | --- |
| initial_inspection | home size / home age / site condition / repair report | P ×4 | 3 each | yes |
| | inspection_visit_timing_method | M | nothing charged / additions alone (fee waived) / fee + additions | yes — each tier bills a different set of components; not a rate on one formula |
| vacant_check | check_visit_frequency_method | M | subtotal × freeze_weekly_rate / subtotal + storm_followup_fee / subtotal | yes — multiplicative, additive and identity operations; the tiers do not share one formula |
| | check_size_addition / check_utility_walkthrough_addition / check_site_crew_credit / check_alarm_credit | P ×4 | 3 / 4 / 3 / 3 | yes |
| | check_part_month_rate | **P** (relabelled from M) | 0.5 / 0.75 / 1.0 | yes — a rate, now labelled parameter |
| booking | items fee / section surcharge / repeat visit | P ×3 | 3 each | yes |
| | booking_repair_window_method | M | inspection_fee replaces the items fee / sum × late_rate / sum | yes — tier 1 changes the inputs of the sum, tier 2 scales it |
| appraisal | length / panel / addendum / premium | P ×4 | 3 each | yes |
| | appraisal_loan_update_method | M | flat desktop_update_fee in place of the sum / sum × update_older_rate / sum | yes — flat-fee replacement vs scaling vs identity |
| lowest_price | loyalty reduction / seasonal days | P ×2 | 3 each | yes |
| | payoff figure / site-lease amount | M ×2 | 3 each | yes (as round 1) |

Counts (honest): initial 4P/1M = 5; vacant 5P/1M = 6; booking 3P/1M = 4; appraisal 4P/1M = 5; lowest price 2P/2M = 4. Every computation is within 4–6 with ≥2 P and ≥1 M. **F1 closed at the charter level.**
Structure re-checked for every factor: `decides` is an input, bindings disjoint, ≥3 pairwise-disjoint tiers drawn from params / variant parameters, no two tiers with the same outcome (the visit-frequency ladder's identity tier differs from ×2.0 and +30.00), every fall-through equals the factor baseline (`std_fee + additions`; `check_subtotal`; `items_fee + section_add + repeat_add`; `appraisal_sum`), and each policy `baseline.rule` yields a definite figure with no factor.
Multi-source: `check_site_crew_credit` tier 1 = plan includes snow (rules plan record) ∧ community (lease record) ∧ winter month; tier 2 = plan includes mowing (rules plan) ∧ (other community (lease) ∨ non-winter month). Both tiers combine two distinct records, so tree A now has a multi-source factor under the strict "distinct records" reading (O11 closed). Tree B keeps `price_loyalty_reduction` (lease ∧ loan).
Realism: the new tiers are things a resale operation would publish: fee waived when Hearthstone misses its own schedule and nothing charged when badly late; storm walk-throughs as an added flat fee; snow-crew credit only where snow plans operate; a desk update of a recent origination appraisal at a flat fee; a full re-inspection fee once the repair window lapses. No unreal ladder found.

### findings (rev 2)
- F1 — **closed** (charter-global): every computation now has ≥1 honestly labelled `method` factor and 4–6 factors. Per-task weight runs in 0.md / 1.md revision_2.
- O1 — closed as a rule/compute mismatch (rule s2 now defines the month charged). Residual O1-r (observation): an uncharged past vacant month cannot be priced by the rule, though edge 2 counts it. No world in this difficulty has one.
- O2, O3, O4, O5, O7, O9 — closed (see sections above).
- O8 — closed (silence replaced by rule s11). O8-r: the ceiling has no compute branch, by design (refusal path).
- O6 — unchanged (Python round); checked per task.
- O10, O11, O12 and the per-task observations — re-judged in the task files.
- New charter-global defects: none found.

### closing_checklist (revision 2)
Written 2026-10-09T10:20Z, after both round-2 reveals.
- Per-task files `0.md`, `1.md` each carry a revision_2 frozen section, a comparison and findings. The round-1 text is preserved above in each file. Both revision_2 comparisons PASS.
- Coverage / scope: charter_scope unchanged (task 0 = initial inspection, vacant check, booking; task 1 = appraisal, lowest price). Pairwise disjoint, jointly complete, each scope spanning its whole tree. Every gold write uses its policy's target tool. uuid8s independent and frozen.
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user write, acyclic; task 1 — 1 prerequisite problem, 1 value_input edge, user write, acyclic. Difficulty graph acyclic, no cross-task edge.
- Factors: every computation has a self-sufficient baseline whose fall-back differs from gold; 5 / 6 / 4 / 5 / 4 factors with ≥2 parameter and ≥1 honest method each; each task has a multi-source factor over distinct records (crew credit; loyalty reduction) and cross-difficulty factors with seeded rows; every ladder has ≥3 tiers, all in its rule, distinct outcomes, realistic conditions; every factor bears weight on its task's world.
- Round-1 REDs: F1 / T0-1 / T1-1 closed; T0-2 closed. Observations O1–O5 and O7–O12 closed or reduced to the residuals O1-r and O8-r. O6 unchanged. No new RED.
- Gates on the final form: the coordinator's round-2 snapshot (GATES.txt: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability deferred to render) is cited; the auditor does not run gates.
- **The difficulty passes the source-layer audit (revision 2).**

## revision_3

### charter_global_frozen (revision 3)
- Freeze time: 2026-10-10T14:02Z, before any round-3 task JSON was opened. Auditor: same independent auditor.
- Inputs (sha256 recomputed, equal to the coordinator's list): `resale.extended.yaml` a05c9084d9ee1804bd117945acfcba83cc4442c09cdc15c97e932a39f3f713f1 (changed from 98ed7d1f…); `task_tools.py` 4a74f3d2… (unchanged); `0.view.json` 48145d27… and `1.view.json` d4a08731… (both unchanged). GATES.txt: all nine rc=0, including TRACEABILITY OK.
- Trigger: render-layer note N1 (audits/policy_kb/in_place_home_sale_approvals/1.md, as relayed by the coordinator; the auditor did not open that file): in `resale_ext_lowest_closing_price`, the payoff rule and ladder text did not condition the statement tier on an open loan, while compute does (`hhf_open and stmt_good and DAYS(NOW, stmt_good) >= 0`).
- **Own miss acknowledged:** rounds 1 and 2 both recorded in § rule_compute_equivalence that no compute branch lacked a rule basis. That was wrong for this binding. The round-2 rule said "a payoff statement on the loan whose good-through date is the handling date or later supplies its payoff amount" with no open-loan condition. On a home whose Hearthstone loan is paid off but still carries a current payoff statement, that reading gives the statement amount, while compute gives the principal (zero). Neither task world reaches the case: task 1's loan is active and its statement expired; task 0 has no loan. So it would have been an observation, not a RED, but it should have been found. The round-1 and round-2 text is left as written.
- contamination_disclosure: round-1 and round-2 GT of both tasks known to the auditor from earlier rounds. No round-3 task JSON opened at this freeze.

### what moved (revision 3)
The charter's line count (1876), base section (lines 1–954, still verbatim against blueprint/products/resale.yaml) and policy offsets (960 / 1133 / 1347 / 1518 / 1683) are unchanged. Every compute expression of all five policies was re-read and matches the round-2 text quoted in this file, `payoff` included (`float(stmt_amount) if (hhf_open and stmt_good and DAYS(NOW, stmt_good) >= 0) else (RND(principal + loan_fees - loan_suspense + RND(principal * note_rate / 100 / 365 * horizon)) if hhf_open else principal)`). The rules of the other four policies, and the other sentences of this one, re-read with no change found. Changed lines: rule s10 (payoff), `compute_basis.stmt_good`, `.stmt_amount`, `.payoff`, and the three `price_payoff_figure` ladder conditions.

### N1 check (revision 3)
- Rule s10 now: "for an open (active or delinquent) Hearthstone Home Finance loan on the home, a payoff statement on that loan whose good-through date is the handling date or later supplies its payoff amount; failing such a statement, the open loan is projected …; a home with no open Hearthstone loan takes the unpaid principal of its loan, which is zero once paid off, whatever payoff statement remains on file."
- Ladder: tier 1 "open (active or delinquent) … loan with a payoff statement good through the handling date or later"; tier 2 "open … loan with no payoff statement good through the handling date"; fall-through "no open Hearthstone loan, whatever payoff statement remains on file". The tiers are pairwise disjoint and cover every case.
- compute_basis for stmt_good / stmt_amount / payoff quotes the new rule verbatim.
- compute: `hhf_open` = EXISTS(loan active) or EXISTS(loan delinquent) = "open (active or delinquent)". Tier 1 requires hhf_open ∧ a statement good through the handling date; tier 2 requires hhf_open without one; the fall-through returns principal. Rule, ladder, compute_basis and compute now agree in all three tiers. **N1 closed.**
- Residual (observation N1-r): compute reads `XLATEST` by notice_date over the customer's loan notices, i.e. only the most recent statement on any of the customer's loans, while the rule speaks of "a payoff statement on that loan whose good-through date is the handling date or later". The two differ only if the customer holds more than one loan, or an older statement on the open loan is good through a later date than the newest one. Task 1 has one loan and one statement, so there is no effect.

### charter-global sections (revision 3)
- base copy, policy_conflict_scan, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders: unchanged from § revision_2. The only edit adds an open-loan condition already present in compute and in the fall-through. It touches no edge, no sentence of another rule, no tool, no factor label, tier count or baseline (`price_payoff_figure` is still an honest method with baseline `principal`), and no override. Carried forward by reference: the tools hash is unchanged, and the charter change is confined to the lines listed above.
- rule_compute_equivalence: § revision_2 stands with the N1 correction above.
- New charter-global defects: none. Regressions: none.

### closing_checklist (revision 3)
Written 2026-10-10T14:03Z, after both round-3 reveals.
- Per-task files carry revision_3 frozen sections, comparisons and findings. Rounds 1–2 are preserved. Both comparisons PASS.
- N1 closed at the charter level, with the residual N1-r recorded as an observation. The rest of the charter, the tools and both views did not move. Scope, trees, factor counts and labels, baselines and weight figures are as in § closing_checklist (revision 2), re-confirmed against the round-3 task files.
- Gates on the final form: the coordinator's round-3 snapshot (GATES.txt: all nine rc=0 including TRACEABILITY OK; validate_scenario VALID, as reported by the coordinator) is cited; the auditor does not run gates.
- **The difficulty passes the source-layer audit (revision 3).**
